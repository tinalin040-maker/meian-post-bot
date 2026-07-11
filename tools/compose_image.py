"""
把商品的照片+文案合成一張圖片，並上傳到 catbox.moe（免帳號）取得公開網址。

背景：LINE 的 Flex Message（圖文合一卡片）使用者長按後沒有「轉傳」選項，這是 LINE
平台限制，不是程式錯誤。改成把照片+文字合成一張真正的圖片，用 LINE 原生「圖片訊息」
發送，才能被使用者長按轉傳/分享到其他群組。

文字裡的 emoji 用 Windows 內建的 Segoe UI Emoji（彩色字型）畫出來，中文/英數字用微軟
正黑體，同一行裡混排兩種字型（emoji 用 embedded_color 保留原本顏色）。
"""

import io
import re

import requests
from PIL import Image, ImageDraw, ImageFont

TEXT_FONT_PATH = "C:/Windows/Fonts/msjh.ttc"
EMOJI_FONT_PATH = "C:/Windows/Fonts/seguiemj.ttf"
PHOTO_SIZE = 340
CANVAS_WIDTH = PHOTO_SIZE * 3
MARGIN = 24
COLOR_TEXT = (40, 40, 40)
COLOR_GREY = (150, 150, 150)
COLOR_PRICE = (230, 0, 35)
COLOR_CTA = (20, 150, 70)

_EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002190-\U000023FF"
    "\U00002460-\U000027BF"
    "\U0001F1E6-\U0001F1FF"
    "\U00002B00-\U00002BFF"
    "\U0000FE0F"
    "\U0000200D"
    "]"
)


def _is_emoji(ch: str) -> bool:
    return bool(_EMOJI_RE.match(ch))


def _text_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(TEXT_FONT_PATH, size, index=1 if bold else 0)


def _emoji_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(EMOJI_FONT_PATH, size)


def _char_width(draw: ImageDraw.ImageDraw, ch: str, text_font, emoji_font) -> float:
    font = emoji_font if _is_emoji(ch) else text_font
    return draw.textlength(ch, font=font)


def _wrap_mixed(draw: ImageDraw.ImageDraw, text: str, text_font, emoji_font, max_width: int) -> list[str]:
    lines = []
    for raw_line in text.split("\n"):
        raw_line = raw_line.strip()
        if not raw_line:
            lines.append("")
            continue
        current = ""
        current_w = 0.0
        for ch in raw_line:
            ch_w = _char_width(draw, ch, text_font, emoji_font)
            if current and current_w + ch_w > max_width:
                lines.append(current)
                current = ch
                current_w = ch_w
            else:
                current += ch
                current_w += ch_w
        if current:
            lines.append(current)
    return lines


def _draw_mixed_line(draw: ImageDraw.ImageDraw, xy: tuple[int, int], line: str, text_font, emoji_font, fill) -> None:
    x, y = xy
    if not line:
        return
    run = line[0]
    run_is_emoji = _is_emoji(line[0])
    for ch in line[1:]:
        ch_is_emoji = _is_emoji(ch)
        if ch_is_emoji == run_is_emoji:
            run += ch
            continue
        x = _draw_run(draw, (x, y), run, run_is_emoji, text_font, emoji_font, fill)
        run = ch
        run_is_emoji = ch_is_emoji
    _draw_run(draw, (x, y), run, run_is_emoji, text_font, emoji_font, fill)


def _draw_run(draw, xy, run, is_emoji, text_font, emoji_font, fill) -> float:
    x, y = xy
    if is_emoji:
        draw.text((x, y), run, font=emoji_font, embedded_color=True)
        return x + draw.textlength(run, font=emoji_font)
    draw.text((x, y), run, font=text_font, fill=fill)
    return x + draw.textlength(run, font=text_font)


_DOWNLOAD_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}


def _download_image(url: str) -> Image.Image:
    resp = requests.get(url, headers=_DOWNLOAD_HEADERS, timeout=15)
    resp.raise_for_status()
    img = Image.open(io.BytesIO(resp.content)).convert("RGB")
    side = min(img.size)
    left = (img.width - side) // 2
    top = (img.height - side) // 2
    img = img.crop((left, top, left + side, top + side))
    return img.resize((PHOTO_SIZE, PHOTO_SIZE))


def build_composite_image(item: dict, out_path: str) -> None:
    photos = [_download_image(url) for url in item.get("images", [])[:3]]

    dummy = Image.new("RGB", (10, 10))
    draw = ImageDraw.Draw(dummy)

    font_name = _text_font(81, bold=True)
    font_price_sale = _text_font(77, bold=True)
    font_price_orig = _text_font(50)
    font_desc = _text_font(54)
    font_cta = _text_font(63, bold=True)
    emoji_name = _emoji_font(81)
    emoji_price_sale = _emoji_font(77)
    emoji_price_orig = _emoji_font(50)
    emoji_desc = _emoji_font(54)
    emoji_cta = _emoji_font(63)

    max_text_width = CANVAS_WIDTH - MARGIN * 2

    name_lines = _wrap_mixed(draw, item["name"].strip(), font_name, emoji_name, max_text_width)
    price_orig_lines = (
        _wrap_mixed(draw, f"原價 {item['price_original']}", font_price_orig, emoji_price_orig, max_text_width)
        if item.get("price_original")
        else []
    )
    price_sale_lines = _wrap_mixed(draw, item["price_sale"], font_price_sale, emoji_price_sale, max_text_width)
    desc_lines = _wrap_mixed(draw, item.get("desc", "").strip(), font_desc, emoji_desc, max_text_width)
    cta_lines = _wrap_mixed(
        draw, "📩 馬上私訊 Ethan我，優惠價格就入手！", font_cta, emoji_cta, max_text_width
    )

    line_h_name = font_name.size + 12
    line_h_price_orig = font_price_orig.size + 12
    line_h_price_sale = font_price_sale.size + 12
    line_h_desc = font_desc.size + 12
    line_h_cta = font_cta.size + 12
    gap_name_to_price = line_h_desc * 2
    gap_price_to_desc = line_h_desc * 2
    gap_desc_to_cta = line_h_desc * 2

    text_height = (
        MARGIN
        + len(name_lines) * line_h_name
        + gap_name_to_price
        + len(price_orig_lines) * line_h_price_orig
        + len(price_sale_lines) * line_h_price_sale
        + gap_price_to_desc
        + len(desc_lines) * line_h_desc
        + gap_desc_to_cta
        + len(cta_lines) * line_h_cta
        + MARGIN
    )

    canvas_height = (PHOTO_SIZE if photos else 0) + text_height
    canvas = Image.new("RGB", (CANVAS_WIDTH, canvas_height), (255, 255, 255))

    x = 0
    for photo in photos:
        canvas.paste(photo, (x, 0))
        x += PHOTO_SIZE

    draw = ImageDraw.Draw(canvas)
    y = (PHOTO_SIZE if photos else 0) + MARGIN

    for line in name_lines:
        _draw_mixed_line(draw, (MARGIN, y), line, font_name, emoji_name, COLOR_TEXT)
        y += line_h_name
    y += gap_name_to_price

    for line in price_orig_lines:
        draw.text((MARGIN, y), line, font=font_price_orig, fill=COLOR_GREY)
        bbox = draw.textbbox((MARGIN, y), line, font=font_price_orig)
        strike_y = (bbox[1] + bbox[3]) // 2
        draw.line((bbox[0], strike_y, bbox[2], strike_y), fill=COLOR_GREY, width=2)
        y += line_h_price_orig

    for line in price_sale_lines:
        _draw_mixed_line(draw, (MARGIN, y), line, font_price_sale, emoji_price_sale, COLOR_PRICE)
        y += line_h_price_sale
    y += gap_price_to_desc

    for line in desc_lines:
        _draw_mixed_line(draw, (MARGIN, y), line, font_desc, emoji_desc, COLOR_TEXT)
        y += line_h_desc
    y += gap_desc_to_cta

    for line in cta_lines:
        _draw_mixed_line(draw, (MARGIN, y), line, font_cta, emoji_cta, COLOR_CTA)
        y += line_h_cta

    canvas.save(out_path, format="JPEG", quality=90)


def upload_to_catbox(path: str) -> str:
    with open(path, "rb") as f:
        resp = requests.post(
            "https://catbox.moe/user/api.php",
            data={"reqtype": "fileupload"},
            files={"fileToUpload": f},
            timeout=30,
        )
    resp.raise_for_status()
    url = resp.text.strip()
    if not url.startswith("http"):
        raise RuntimeError(f"catbox 上傳失敗: {url}")
    return url
