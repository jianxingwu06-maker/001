from __future__ import annotations

import hashlib
from pathlib import Path
from urllib.parse import urlparse

import requests
from PIL import Image, ImageOps, UnidentifiedImageError

from .image_generation import ImageGenerator
from .models import HUMAN_CONFIRM, ImageAsset, ListingVersion, RawProduct

RISK_TERMS = ["logo", "watermark", "official", "brand", "amazon", "etsy", "temu", "aliexpress", "1688", "ozon"]
ROLES = ["main", "scene_1", "scene_2", "scene_3", "detail", "size", "package"]


class ImageProcessor:
    def __init__(self, output_dir: Path, generator: ImageGenerator | None = None, timeout: int = 20):
        self.output_dir = Path(output_dir)
        self.generator = generator or ImageGenerator()
        self.timeout = timeout

    def process(self, raw: RawProduct, versions: list[ListingVersion]) -> list[ImageAsset]:
        assets: list[ImageAsset] = []
        base_risk = self._image_risk(raw.images)
        for version in versions:
            product_dir = self.output_dir / self._safe(version.sku)
            paths = []
            for role in ROLES:
                filename = f"{role}.jpg"
                out = product_dir / filename
                if base_risk[0] == "low" and raw.images and role == "main":
                    ok = self._download_and_optimize(raw.images[0], out)
                    if ok:
                        assets.append(ImageAsset(raw.images[0], out, "low", base_risk[1], role))
                        paths.append(str(out))
                        continue
                prompt = self._prompt(version, role)
                self.generator.generate_placeholder(prompt, out, f"{version.title} - {role}")
                assets.append(ImageAsset(raw.images[0] if raw.images else HUMAN_CONFIRM, out, "high", base_risk[1], role))
                paths.append(str(out))
            version.main_image = paths[0]
            version.gallery_images = paths[1:4]
            version.detail_images = paths[4:]
        return assets

    def _image_risk(self, urls: list[str]) -> tuple[str, str]:
        if not urls:
            return "high", "来源图片缺失，需要生成原创替代图"
        joined = " ".join(urls).lower()
        if any(term in joined for term in RISK_TERMS):
            return "high", "图片链接或文件名包含平台/品牌/水印风险词"
        return "low", "未发现明显 Logo、水印或平台词；仍建议人工复核授权"

    def _download_and_optimize(self, url: str, output: Path) -> bool:
        try:
            response = requests.get(url, timeout=self.timeout, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            output.parent.mkdir(parents=True, exist_ok=True)
            tmp = output.with_suffix(".download")
            tmp.write_bytes(response.content)
            with Image.open(tmp) as img:
                img = ImageOps.exif_transpose(img).convert("RGB")
                img.thumbnail((1200, 1200))
                canvas = Image.new("RGB", (1200, 1200), "white")
                canvas.paste(img, ((1200 - img.width) // 2, (1200 - img.height) // 2))
                canvas.save(output, quality=94)
            tmp.unlink(missing_ok=True)
            return True
        except (requests.RequestException, UnidentifiedImageError, OSError):
            return False

    def _prompt(self, version: ListingVersion, role: str) -> str:
        style = {
            "main": "clean white background product hero image",
            "scene_1": "bright home lifestyle scene",
            "scene_2": "minimal office or daily use scene",
            "scene_3": "organized storage or travel scene",
            "detail": "close-up material and texture detail",
            "size": "simple size comparison layout without exact unverified numbers",
            "package": "neutral packaging and bundle display",
        }[role]
        return f"Create a 1:1 high-resolution ecommerce image for: {version.title}. Style: {style}. No logo, no watermark, no brand marks, no copyrighted characters, no human face, neutral realistic lighting."

    def _safe(self, text: str) -> str:
        digest = hashlib.sha1(text.encode()).hexdigest()[:6]
        parsed = urlparse(text)
        base = parsed.netloc or text
        return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in base)[:60] + "_" + digest
