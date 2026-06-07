from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


class ImageGenerator:
    """可替换的图片生成接口。

    生产环境可在此类中接入自有 AI 图片 API；默认实现创建无 Logo、水印的占位图，
    并输出提示词，方便人工或外部服务二次生成。
    """

    def generate_placeholder(self, prompt: str, output_path: Path, label: str) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img = Image.new("RGB", (1200, 1200), (248, 248, 245))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 42)
            small = ImageFont.truetype("DejaVuSans.ttf", 28)
        except OSError:
            font = small = None
        draw.rectangle((90, 90, 1110, 1110), outline=(210, 210, 205), width=6)
        draw.text((130, 160), label[:38], fill=(45, 45, 45), font=font)
        wrapped = self._wrap(prompt, 42)[:10]
        y = 260
        for line in wrapped:
            draw.text((130, y), line, fill=(90, 90, 90), font=small)
            y += 44
        draw.text((130, 1060), "AI original image placeholder - no logo/watermark", fill=(120, 120, 120), font=small)
        img.save(output_path, quality=94)
        output_path.with_suffix(".prompt.txt").write_text(prompt, encoding="utf-8")
        return output_path

    def _wrap(self, text: str, width: int) -> list[str]:
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            if len(current) + len(word) + 1 > width:
                lines.append(current)
                current = word
            else:
                current = f"{current} {word}".strip()
        if current:
            lines.append(current)
        return lines
