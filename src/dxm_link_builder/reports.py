from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from .models import ImageAsset, ListingVersion, RawProduct


class ReportWriter:
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_all(self, raw_products: list[RawProduct], versions: list[ListingVersion], image_assets: list[ImageAsset], excel_info: dict) -> None:
        self._write_json("product_logs.json", [asdict(p) for p in raw_products])
        self._write_json("compliance_report.json", [self._compliance_row(v) for v in versions])
        self._write_json("excel_export_report.json", excel_info)
        pd.DataFrame([self._image_row(a) for a in image_assets]).to_csv(self.output_dir / "image_risk_list.csv", index=False)
        pd.DataFrame([self._exception_row(p) for p in raw_products]).to_csv(self.output_dir / "exceptions.csv", index=False)
        pd.DataFrame([self._version_row(v) for v in versions]).to_excel(self.output_dir / "multi_account_versions.xlsx", index=False)

    def _write_json(self, name: str, data) -> None:
        (self.output_dir / name).write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    def _image_row(self, asset: ImageAsset) -> dict:
        return {"source_url": asset.source_url, "output_path": str(asset.output_path), "risk_level": asset.risk_level, "reason": asset.reason, "role": asset.role}

    def _exception_row(self, product: RawProduct) -> dict:
        return {"url": product.url, "source_platform": product.source_platform, "warnings": "；".join(product.warnings)}

    def _compliance_row(self, version: ListingVersion) -> dict:
        risky = [flag for flag in version.flags if "缺失" in flag or "反爬" in flag or "登录" in flag]
        return {"sku": version.sku, "account": version.account, "target_platform": version.target_platform, "status": "需复核" if risky else "已重构", "notes": "；".join(risky)}

    def _version_row(self, v: ListingVersion) -> dict:
        return {"account": v.account, "platform": v.target_platform, "url": v.url, "title": v.title, "sku": v.sku, "price": v.price, "main_image": v.main_image, "flags": "；".join(v.flags)}
