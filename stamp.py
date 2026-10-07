"""APPROVED stamp image generation (Pillow, supersampled)."""

from datetime import datetime
from io import BytesIO
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

import config

FONT_PATH = Path(__file__).parent / "fonts" / "DejaVuSans-BoldOblique.ttf"

# Proportions measured from the Adobe reference stamp (box 594 x 116 px).
ASPECT = 594 / 116            # width / height
BORDER = 0.022                # border width, fraction of height
RADIUS = 0.11                 # corner radius, fraction of height
PAD_X = 0.027                 # left/right text padding, fraction of width
LINE1_CAP = 0.285             # "APPROVED" cap height, fraction of height
LINE1_BASE = 0.457            # "APPROVED" baseline, fraction of height
LINE2_CAP = 0.18              # max cap height of the second line, fraction of height
LINE2_BASE = 0.81             # second line baseline, fraction of height

GREEN = (0x3F, 0x6B, 0x1F, 255)
# Chosen so that over a white page they match the reference (#F4F8EE -> #D7E5CF).
FILL_LEFT = (0xF2, 0xF7, 0xEB)
FILL_RIGHT = (0xD0, 0xE0, 0xC6)
FILL_ALPHA = 215              # slight transparency of the background

SUPERSAMPLE = 4


TITLE = "SCHVÁLENO"


def format_time(now: datetime | None = None) -> str:
    """Czech time stamp like '16:28, 7. 10. 2026' in the configured time zone."""
    now = now or datetime.now(ZoneInfo(config.TIMEZONE))
    return f"{now.hour}:{now.minute:02d}, {now.day}. {now.month}. {now.year}"


def stamp_text(name: str, now: datetime | None = None) -> str:
    return f"{name}, {format_time(now)}"


def _font_for_cap_height(cap: float) -> ImageFont.FreeTypeFont:
    """Font whose capital letter height is approximately `cap` pixels."""
    probe = ImageFont.truetype(str(FONT_PATH), 1000)
    cap_ratio = -probe.getbbox("H", anchor="ls")[1] / 1000
    return ImageFont.truetype(str(FONT_PATH), max(1, round(cap / cap_ratio)))


def render_stamp(name: str, width: int = 1600, now: datetime | None = None) -> bytes:
    """Render the stamp as a transparent PNG `width` pixels wide."""
    height = round(width / ASPECT)
    W, H = width * SUPERSAMPLE, height * SUPERSAMPLE

    # Horizontal background gradient, clipped to a rounded rectangle.
    # linear_gradient runs black (top) to white (bottom); rotated it runs black (left) to white (right).
    gradient = Image.linear_gradient("L").rotate(90).resize((W, H))
    img = Image.composite(
        Image.new("RGB", (W, H), FILL_RIGHT), Image.new("RGB", (W, H), FILL_LEFT), gradient
    ).convert("RGBA")
    mask = Image.new("L", (W, H), 0)
    border = max(1, round(BORDER * H))
    box = (border / 2, border / 2, W - 1 - border / 2, H - 1 - border / 2)
    ImageDraw.Draw(mask).rounded_rectangle(box, radius=RADIUS * H, fill=FILL_ALPHA)
    img.putalpha(mask)

    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(box, radius=RADIUS * H, outline=GREEN, width=border)

    pad = PAD_X * W
    font1 = _font_for_cap_height(LINE1_CAP * H)
    draw.text((pad, LINE1_BASE * H), TITLE, font=font1, fill=GREEN, anchor="ls")

    line2 = stamp_text(name, now)
    font2 = _font_for_cap_height(LINE2_CAP * H)
    text_w = draw.textlength(line2, font=font2)
    if text_w > W - 2 * pad:
        font2 = font2.font_variant(size=int(font2.size * (W - 2 * pad) / text_w))
    draw.text((pad, LINE2_BASE * H), line2, font=font2, fill=GREEN, anchor="ls")

    img = img.resize((width, height), Image.Resampling.LANCZOS)
    out = BytesIO()
    img.save(out, format="PNG", optimize=True)
    return out.getvalue()
