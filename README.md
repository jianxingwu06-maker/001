# 链接转店小秘成品表格自动化系统

这是一个长期可复用的 Python 自动化系统，用于把商品链接批量转换为可上传店小秘的 Excel 成品文件，并同步输出图片文件夹、图片风险清单、合规检查报告、多账号差异化版本表格、异常问题报告和产品处理日志。

> 合规原则：系统不会把竞品标题、描述、品牌词、Logo、官方图直接复制到成品表格。链接内容仅作为参考；无法确认的信息统一标记为 `需要人工确认`。

## 功能范围

- 链接采集：使用 `requests` + HTML/JSON-LD 解析提取标题、描述、图片、价格、类目和可推断属性。
- 合规重构：删除品牌词、平台词、禁用词、夸大宣传词和官方承诺表达，生成原创标题、描述、卖点和 SKU。
- 店小秘 Excel：使用 `openpyxl` 读取模板并只写入匹配列，尽量保留原模板表头、隐藏列、公式、样式和格式。
- 图片处理：低风险图可下载后统一转 1:1 白底图；高风险或缺失图片生成 AI 原创替代图方案和占位图。
- 多账号差异化：同一链接按账号生成不同标题、描述、卖点顺序、SKU 和图片组合。
- 平台适配：平台标题长度、语言、禁用词、图片规则等配置集中放在 `config/platform_rules.json`。

## 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

如需 Playwright 或 OpenCV 扩展：

```bash
pip install -e '.[playwright,opencv]'
playwright install chromium
```

## 输入文件

### 1. 商品链接文本

`input/links.txt` 每行一个链接（仓库已保留占位文件，直接修改即可）：

```txt
https://example.com/product-a
https://www.amazon.com/example-product/dp/xxxx
https://www.etsy.com/listing/xxxx/example
```

### 2. 店小秘模板

仓库保留了 `input/template.xlsx` 占位说明文件，方便固定运行入口和避免 GitHub 二进制模板冲突。它不是真实 Excel 工作簿；正式运行前，请从店小秘后台下载真实导入模板，并在本机覆盖 `input/template.xlsx`，或通过 `--template` 指定其他模板路径。系统会自动查找包含 `商品标题`、`SKU`、`主图`、`售价`、`库存` 等字段的表头行。

## 运行

```bash
dxm-link-builder \
  --links input/links.txt \
  --template input/template.xlsx \
  --output output \
  --platform temu \
  --accounts account_a,account_b,account_c
```

Windows 用户也可以双击仓库根目录的 `Windows 双击运行.bat`。脚本会创建虚拟环境、安装依赖，并默认读取 `input/links.txt` 和 `input/template.xlsx`，输出到 `output/`。

也可以直接使用模块运行：

```bash
python -m dxm_link_builder.cli --links input/links.txt --template input/template.xlsx --output output --platform amazon --accounts shop1,shop2
```

## 输出目录

运行完成后会生成：

```txt
output/
├── dxm_ready_upload.xlsx                 # 可上传店小秘的 Excel 成品表格
├── images/                               # 处理后的图片文件夹
│   └── <sku>/
│       ├── main.jpg
│       ├── scene_1.jpg
│       ├── scene_2.jpg
│       ├── scene_3.jpg
│       ├── detail.jpg
│       ├── size.jpg
│       └── package.jpg
└── reports/
    ├── image_risk_list.csv               # 图片风险清单
    ├── compliance_report.json            # 合规检查报告
    ├── multi_account_versions.xlsx       # 多账号差异化版本表格
    ├── exceptions.csv                    # 异常问题报告
    ├── product_logs.json                 # 每个产品处理日志
    └── excel_export_report.json          # Excel 写入报告
```

## 字段缺失策略

以下场景不会乱填，会标记为 `需要人工确认`：

- 网页无法访问、需要登录、验证码、反爬。
- 原网页没有提供重量、包装尺寸、材质、颜色、数量等字段。
- 类目 ID 无法从店铺规则或外部类目映射确定。
- 图片无法下载或图片风险较高。
- 物流信息没有在配置中明确指定。

## 图片生成接口替换

默认 `ImageGenerator` 会生成无 Logo、无水印的占位图和 `.prompt.txt` 提示词文件。生产环境可在 `src/dxm_link_builder/image_generation.py` 中替换为自有 AI 图片 API，保持 `generate_placeholder(prompt, output_path, label)` 返回本地图片路径即可。

## 自定义平台规则

默认规则在 `config/platform_rules.json`。你可以复制一份后通过 `--rules custom_rules.json` 指定。常用字段包括：

- `title_max_length`
- `language`
- `required_fields`
- `prohibited_words`
- `brand_words`
- `image`
- `default_stock`
- `default_logistics`
- `default_category_id`

## Git 跟踪策略

- `input/links.txt` 会保留在仓库中，作为商品链接输入文件。
- `input/template.xlsx` 会保留为可合并的文本占位说明；真实店小秘 Excel 模板属于本地输入，不应提交。
- `output/` 会保留目录本身，但运行生成的 Excel、图片、CSV、JSON 报告等会被 `.gitignore` 忽略。
- 生成/下载的商品图片、缓存文件和临时 Excel 文件不会进入 Git，避免再次出现二进制文件合并冲突。

## 注意事项

- 本系统以合规重构和风控标记为目标，不用于规避平台审核。
- 对供应商授权、类目 ID、物流模板、平台必填属性等需要业务侧确认的信息，请在配置或模板中补齐。
- 对带品牌、Logo、水印、官方包装、模特脸部或版权元素的图片，系统默认按高风险处理，不直接复用。
