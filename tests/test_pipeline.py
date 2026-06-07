from pathlib import Path

import pytest

from dxm_link_builder.compliance import ComplianceRewriter
from dxm_link_builder.models import RawProduct


def test_compliance_removes_brand_and_limits_title():
    rules = {"title_max_length": 30, "brand_words": ["amazon"], "prohibited_words": ["官方"]}
    raw = RawProduct(url="https://x.test", source_platform="supplier", title="Amazon 官方收纳盒", description="适合家庭使用。方便收纳。")
    version = ComplianceRewriter(rules).make_versions(raw, ["shop_a"], "temu")[0]
    assert "Amazon" not in version.title
    assert "官方" not in version.title
    assert len(version.title) <= 30


def test_excel_writer_preserves_template_and_writes_rows(tmp_path: Path):
    openpyxl = pytest.importorskip("openpyxl")
    from dxm_link_builder.excel_writer import DxmExcelWriter

    template = tmp_path / "template.xlsx"
    out = tmp_path / "out.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["商品标题", "SKU", "主图", "售价", "库存", "隐藏公式"])
    ws.column_dimensions["F"].hidden = True
    ws["F2"] = "=1+1"
    wb.save(template)

    raw = RawProduct(url="https://x.test", source_platform="supplier", title="便携水杯", description="适合日常")
    version = ComplianceRewriter({}).make_versions(raw, ["abc"], "default")[0]
    version.main_image = "images/main.jpg"
    DxmExcelWriter(template, out).write([version])

    result = openpyxl.load_workbook(out, data_only=False)
    ws2 = result.active
    assert ws2["A2"].value == version.title
    assert ws2["C2"].value == "images/main.jpg"
    assert ws2.column_dimensions["F"].hidden is True
    assert ws2["F2"].value == "=1+1"
