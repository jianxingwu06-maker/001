"""创建一个最小店小秘模板示例。

运行前请安装项目依赖：pip install -e .
"""

from openpyxl import Workbook

wb = Workbook()
ws = wb.active
ws.title = "DXM模板"
ws.append([
    "商品标题", "商品描述", "SKU", "规格名", "规格值", "颜色", "尺寸", "重量", "体积", "类目 ID",
    "属性", "主图", "附图", "详情图", "库存", "售价", "物流信息"
])
wb.save("examples/dxm_template.xlsx")
print("已生成 examples/dxm_template.xlsx")
