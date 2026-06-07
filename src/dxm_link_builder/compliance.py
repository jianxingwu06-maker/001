from __future__ import annotations

import hashlib
import re
from typing import Any

from .models import HUMAN_CONFIRM, ListingVersion, RawProduct

FALLBACK_BULLETS = ["日常使用方便", "外观简洁百搭", "适合多种生活场景", "易于收纳和维护"]


class ComplianceRewriter:
    def __init__(self, rules: dict[str, Any]):
        self.rules = rules
        self.prohibited = [w.lower() for w in rules.get("prohibited_words", [])]
        self.brand_words = [w.lower() for w in rules.get("brand_words", [])]

    def make_versions(self, raw: RawProduct, accounts: list[str], target_platform: str) -> list[ListingVersion]:
        versions = []
        for idx, account in enumerate(accounts, start=1):
            clean_title = self._clean_text(raw.title)
            title = self._build_title(clean_title, idx)
            bullets = self._build_bullets(raw, idx)
            description = self._build_description(title, bullets, idx)
            sku_seed = hashlib.sha1(f"{raw.url}-{account}".encode()).hexdigest()[:8].upper()
            attrs = raw.attributes
            flags = list(raw.warnings)
            versions.append(
                ListingVersion(
                    account=account,
                    target_platform=target_platform,
                    url=raw.url,
                    title=title,
                    description=description,
                    bullet_points=bullets,
                    sku=f"{account[:3].upper()}-{sku_seed}",
                    spec_name="款式",
                    spec_value=f"版本{idx}",
                    color=str(attrs.get("color", HUMAN_CONFIRM)),
                    size=str(attrs.get("size", HUMAN_CONFIRM)),
                    material=str(attrs.get("material", HUMAN_CONFIRM)),
                    quantity=str(attrs.get("quantity", HUMAN_CONFIRM)),
                    weight=str(attrs.get("weight", HUMAN_CONFIRM)),
                    package_size=str(attrs.get("package_size", HUMAN_CONFIRM)),
                    price=raw.price,
                    category_id=str(self.rules.get("default_category_id", HUMAN_CONFIRM)),
                    attributes={k: v for k, v in attrs.items()},
                    stock=int(self.rules.get("default_stock", 100)),
                    logistics=str(self.rules.get("default_logistics", HUMAN_CONFIRM)),
                    main_image=HUMAN_CONFIRM,
                    gallery_images=[],
                    detail_images=[],
                    flags=flags,
                )
            )
        return versions

    def _clean_text(self, text: str) -> str:
        if not text or text == HUMAN_CONFIRM:
            return HUMAN_CONFIRM
        cleaned = re.sub(r"https?://\S+", " ", text)
        for word in self.prohibited + self.brand_words:
            cleaned = re.sub(re.escape(word), " ", cleaned, flags=re.I)
        cleaned = re.sub(r"\b(official|authentic|genuine|logo|brand)\b", " ", cleaned, flags=re.I)
        cleaned = re.sub(r"[™®©]", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" -_|,/，。")
        return cleaned or HUMAN_CONFIRM

    def _build_title(self, clean_title: str, variant: int) -> str:
        title_max = int(self.rules.get("title_max_length", 120))
        if clean_title == HUMAN_CONFIRM:
            base = "多场景实用商品"
        else:
            base = clean_title
        suffixes = ["家用便携款", "简约耐用款", "日常实用款", "轻巧收纳款"]
        title = f"{base} {suffixes[(variant - 1) % len(suffixes)]}"
        return title[:title_max].strip()

    def _build_bullets(self, raw: RawProduct, variant: int) -> list[str]:
        source = self._clean_text(raw.description)
        candidates = []
        if source != HUMAN_CONFIRM:
            for part in re.split(r"[。.!！；;\n]", source):
                part = part.strip()
                if 8 <= len(part) <= 80:
                    candidates.append(part)
        candidates.extend(FALLBACK_BULLETS)
        shift = (variant - 1) % len(candidates)
        rotated = candidates[shift:] + candidates[:shift]
        return list(dict.fromkeys(rotated))[:5]

    def _build_description(self, title: str, bullets: list[str], variant: int) -> str:
        intro = ["为日常使用场景设计", "适合家庭、办公或外出携带", "注重实用性与整洁展示"][(variant - 1) % 3]
        bullet_text = "\n".join(f"- {item}" for item in bullets)
        return f"{title}\n\n{intro}，页面内容已做原创化整理，不含品牌承诺或夸大表述。\n\n核心卖点：\n{bullet_text}\n\n温馨提示：尺寸、重量、材质和包装信息如未能从来源确认，已标记为需要人工确认。"
