from __future__ import annotations

import importlib.util
import json
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .models import HUMAN_CONFIRM, RawProduct

PLATFORM_HINTS = {
    "ozon": "ozon",
    "aliexpress": "aliexpress",
    "1688": "1688",
    "amazon": "amazon",
    "etsy": "etsy",
    "temu": "temu",
    "mercadolibre": "mercado_libre",
    "mercado": "mercado_libre",
}


def detect_platform(url: str) -> str:
    host = urlparse(url).netloc.lower()
    for hint, platform in PLATFORM_HINTS.items():
        if hint in host:
            return platform
    return "supplier"


class ProductScraper:
    def __init__(self, timeout: int = 25, use_playwright: bool = False):
        self.timeout = timeout
        self.use_playwright = use_playwright
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            }
        )

    def scrape(self, url: str) -> RawProduct:
        platform = detect_platform(url)
        product = RawProduct(url=url, source_platform=platform)
        try:
            html = self._fetch_html(url)
        except Exception as exc:  # noqa: BLE001 - convert all fetch failures into review flags
            if self.use_playwright:
                try:
                    html = self._fetch_html_with_playwright(url)
                except Exception as pw_exc:  # noqa: BLE001 - mark both collectors as failed
                    product.warnings.append(f"网页无法访问或触发反爬：requests={exc}; playwright={pw_exc}")
                    return product
            else:
                product.warnings.append(f"网页无法访问或触发反爬：{exc}")
                return product
        if self._looks_blocked(html):
            product.warnings.append("页面可能需要登录、验证码或触发反爬")
        self._parse_html(html, product)
        self._mark_missing(product)
        return product

    def _fetch_html(self, url: str) -> str:
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def _fetch_html_with_playwright(self, url: str) -> str:
        if importlib.util.find_spec("playwright") is None:
            raise RuntimeError("playwright 未安装，请执行 pip install -e .[playwright]")
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(locale="zh-CN")
            page.goto(url, wait_until="networkidle", timeout=self.timeout * 1000)
            html = page.content()
            browser.close()
            return html

    def _looks_blocked(self, html: str) -> bool:
        sample = html[:5000].lower()
        blocked_terms = ["captcha", "verify", "robot", "login", "access denied", "人机", "验证码", "登录"]
        return any(term in sample for term in blocked_terms)

    def _parse_html(self, html: str, product: RawProduct) -> None:
        soup = BeautifulSoup(html, "html.parser")
        jsonld = self._extract_jsonld_product(soup)
        if jsonld:
            product.title = str(jsonld.get("name") or product.title).strip() or HUMAN_CONFIRM
            product.description = str(jsonld.get("description") or product.description).strip() or HUMAN_CONFIRM
            image = jsonld.get("image")
            product.images.extend(self._normalize_images(image))
            offers = jsonld.get("offers") or {}
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            if isinstance(offers, dict):
                price = offers.get("price") or offers.get("lowPrice")
                if price:
                    product.price = str(price)
            if jsonld.get("category"):
                product.category = str(jsonld["category"])
        if product.title == HUMAN_CONFIRM:
            product.title = self._meta(soup, "og:title") or (soup.title.text.strip() if soup.title else HUMAN_CONFIRM)
        if product.description == HUMAN_CONFIRM:
            product.description = self._meta(soup, "og:description") or self._meta_name(soup, "description") or HUMAN_CONFIRM
        product.images.extend(self._collect_meta_images(soup))
        product.images = list(dict.fromkeys([img for img in product.images if img]))[:20]
        self._infer_attributes(product)

    def _extract_jsonld_product(self, soup: BeautifulSoup) -> dict:
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
            except json.JSONDecodeError:
                continue
            nodes = data if isinstance(data, list) else [data]
            for node in nodes:
                if isinstance(node, dict) and node.get("@graph"):
                    nodes.extend(node["@graph"])
                if isinstance(node, dict) and str(node.get("@type", "")).lower() == "product":
                    return node
        return {}

    def _normalize_images(self, value) -> list[str]:
        if not value:
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            out = []
            for item in value:
                if isinstance(item, str):
                    out.append(item)
                elif isinstance(item, dict) and item.get("url"):
                    out.append(str(item["url"]))
            return out
        if isinstance(value, dict) and value.get("url"):
            return [str(value["url"])]
        return []

    def _meta(self, soup: BeautifulSoup, prop: str) -> str | None:
        tag = soup.find("meta", property=prop)
        return tag.get("content", "").strip() if tag else None

    def _meta_name(self, soup: BeautifulSoup, name: str) -> str | None:
        tag = soup.find("meta", attrs={"name": name})
        return tag.get("content", "").strip() if tag else None

    def _collect_meta_images(self, soup: BeautifulSoup) -> list[str]:
        images = []
        for prop in ["og:image", "twitter:image", "og:image:secure_url"]:
            value = self._meta(soup, prop)
            if value:
                images.append(value)
        return images

    def _infer_attributes(self, product: RawProduct) -> None:
        text = f"{product.title} {product.description}".lower()
        patterns = {
            "material": r"(cotton|polyester|stainless steel|silicone|wood|plastic|棉|涤纶|不锈钢|硅胶|木|塑料)",
            "size": r"(\d+(?:\.\d+)?\s?(?:cm|mm|inch|in|厘米|毫米))",
            "weight": r"(\d+(?:\.\d+)?\s?(?:kg|g|lb|oz|千克|克))",
            "quantity": r"(\d+\s?(?:pcs|pieces|pack|件|个|只|套))",
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.I)
            product.attributes[key] = match.group(1) if match else HUMAN_CONFIRM

    def _mark_missing(self, product: RawProduct) -> None:
        checks = {"标题": product.title, "描述": product.description, "图片": product.images, "价格": product.price, "类目": product.category}
        for name, value in checks.items():
            if value == HUMAN_CONFIRM or value == []:
                product.warnings.append(f"{name}缺失，{HUMAN_CONFIRM}")
