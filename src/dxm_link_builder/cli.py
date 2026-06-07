from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import LinkToDxmPipeline


def load_links(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.strip().startswith("#")]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="链接转店小秘成品表格自动化系统")
    parser.add_argument("--links", required=True, type=Path, help="每行一个商品链接的 txt 文件")
    parser.add_argument("--template", required=True, type=Path, help="店小秘 Excel 模板路径")
    parser.add_argument("--output", required=True, type=Path, help="输出目录")
    parser.add_argument("--platform", default="default", help="目标平台：ozon/temu/etsy/aliexpress/amazon/mercado_libre")
    parser.add_argument("--accounts", default="account_1", help="逗号分隔的账号名，用于多账号差异化")
    parser.add_argument("--rules", type=Path, help="自定义平台规则 JSON")
    parser.add_argument("--use-playwright", action="store_true", help="requests 失败时使用 Playwright 渲染采集")
    args = parser.parse_args(argv)
    accounts = [item.strip() for item in args.accounts.split(",") if item.strip()]
    result = LinkToDxmPipeline(args.template, args.output, args.platform, accounts, args.rules, args.use_playwright).run(load_links(args.links))
    print("生成完成：")
    for key, value in result.items():
        print(f"- {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
