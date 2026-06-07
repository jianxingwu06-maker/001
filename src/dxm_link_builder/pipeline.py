from __future__ import annotations

from pathlib import Path

from .compliance import ComplianceRewriter
from .config import PlatformRules
from .excel_writer import DxmExcelWriter
from .images import ImageProcessor
from .reports import ReportWriter
from .scraper import ProductScraper


class LinkToDxmPipeline:
    def __init__(self, template: Path, output_dir: Path, target_platform: str, accounts: list[str], rules_path: Path | None = None, use_playwright: bool = False, excel_filename: str = "店小秘可上传成品表格.xlsx"):
        self.template = Path(template)
        self.output_dir = Path(output_dir)
        self.target_platform = target_platform
        self.accounts = accounts
        self.rules = PlatformRules(rules_path) if rules_path else PlatformRules()
        self.use_playwright = use_playwright
        self.excel_filename = excel_filename

    def run(self, links: list[str]) -> dict[str, str]:
        rules = self.rules.get(self.target_platform)
        scraper = ProductScraper(use_playwright=self.use_playwright)
        rewriter = ComplianceRewriter(rules)
        image_processor = ImageProcessor(self.output_dir / "images")
        raw_products = []
        versions = []
        image_assets = []
        for url in links:
            raw = scraper.scrape(url)
            raw_products.append(raw)
            product_versions = rewriter.make_versions(raw, self.accounts, self.target_platform)
            image_assets.extend(image_processor.process(raw, product_versions))
            versions.extend(product_versions)
        excel_path = self.output_dir / self.excel_filename
        excel_info = DxmExcelWriter(self.template, excel_path).write(versions)
        ReportWriter(self.output_dir / "reports").write_all(raw_products, versions, image_assets, excel_info)
        return {
            "excel": str(excel_path),
            "images": str(self.output_dir / "images"),
            "reports": str(self.output_dir / "reports"),
            "multi_account_versions": str(self.output_dir / "reports" / "multi_account_versions.xlsx"),
        }
