# 新手使用说明：链接转店小秘成品表格 Windows 双击运行版

这个版本是给非程序员使用的。你不需要手动打开 cmd，不需要输入 pip、python 命令，只要按下面 4 步操作。

## 使用前准备：确认电脑已安装 Python

如果你的电脑还没有安装 Python，请先安装一次：

1. 打开 Python 官网：https://www.python.org/downloads/windows/
2. 下载 Python 3.10 或更高版本。
3. 安装时一定要勾选 **Add python.exe to PATH**。
4. 安装完成后回到本项目文件夹，继续下面步骤。

如果没有安装 Python，双击运行时会出现中文提示，提醒你先安装 Python 并勾选 **Add python.exe to PATH**。

## 第一步：放链接

打开项目里的 `input` 文件夹。

在 `input/links.txt` 里放商品链接：

- 一行一个商品链接。
- 可以放 Ozon、AliExpress、1688、Amazon、Etsy、TEMU、供应商商品链接等。
- 如果没有 `links.txt`，请自己新建一个文本文件，并命名为 `links.txt`。

示例：

```txt
https://example.com/product-1
https://example.com/product-2
```

## 第二步：放店小秘模板

把店小秘导出的 Excel 模板放到 `input` 文件夹。

文件名必须改成：

```txt
template.xlsx
```

也就是说，最终路径应该是：

```txt
input/template.xlsx
```

## 第三步：双击运行

回到项目根目录，双击：

```txt
双击运行.bat
```

双击后程序会自动完成：

- 创建 `input/`、`output/`、`output/images/`、`output/reports/` 文件夹。
- 检查 `input/links.txt` 是否存在。
- 检查 `input/template.xlsx` 是否存在。
- 检查电脑是否安装 Python。
- 自动创建专用运行环境 `.venv`。
- 自动安装依赖。
- 自动采集商品链接。
- 自动进行合规重构。
- 自动处理图片。
- 自动填写店小秘模板。
- 自动生成报告。
- 运行完成后自动打开 `output` 文件夹。

如果缺少 `links.txt` 或 `template.xlsx`，不会出现英文报错，会弹出中文提示，并自动打开 `input` 文件夹让你补文件。

## 第四步：拿 output 里的表格上传店小秘

运行完成后，打开 `output` 文件夹，主文件是：

```txt
店小秘可上传成品表格.xlsx
```

你可以优先检查这个文件，然后上传店小秘。

同时，`output` 里还会有：

```txt
output/images/      处理后的图片
output/reports/     风险清单、异常报告、合规报告、处理日志
```

## 合规说明

系统会尽量避免直接复制竞品内容：

- 不直接复制竞品品牌词。
- 不直接使用带 Logo、水印、官方包装、官方品牌元素的高风险图片。
- 不写夸大宣传、虚假承诺、平台禁用词。
- 无法确认的重量、尺寸、材质、类目、物流等字段会标记为：`需要人工确认`。

如果报告里出现 `需要人工确认`，请人工复核后再上传。

## 常见问题

### 1. 双击后提示缺少 Python 怎么办？

去 Python 官网安装 Python 3.10 或更高版本，并在安装界面勾选 **Add python.exe to PATH**。

### 2. 提示依赖安装失败怎么办？

通常是网络无法下载依赖，可能是公司网络、代理或防火墙拦截。请换网络后重新双击，或把窗口截图发给技术人员。

### 3. 生成的内容还有“需要人工确认”怎么办？

说明原链接没有提供可靠信息，或网页无法访问、反爬、图片高风险。请打开 `output/reports/` 查看具体原因，并人工补充。
