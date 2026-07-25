#!/usr/bin/env python3
"""Meta ad creatives — dark-espresso/gold editorial style, no bodies, no clinical imagery."""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W = H = 1080
FONT_DIR = "/Users/juliaknyazskaya/glp1-guide-site/ad-creatives/fonts"

DARK = (21, 16, 12)
DARK2 = (33, 26, 20)
DARK_EDGE = (10, 8, 6)
CREAM = (247, 241, 231)
GOLD = (201, 161, 90)
GOLD_SOFT = (224, 187, 124)
GOLD_DEEP = (169, 130, 47)
MUTED_GOLD = (184, 160, 120)


def load_font(path, size, weight=None):
    f = ImageFont.truetype(path, size)
    if weight is not None:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def playfair(size, weight=800):
    return load_font(f"{FONT_DIR}/PlayfairDisplay-Variable.ttf", size, weight)


def playfair_italic(size, weight=700):
    return load_font(f"{FONT_DIR}/PlayfairDisplay-Italic-Variable.ttf", size, weight)


def inter(size, weight=600):
    return load_font(f"{FONT_DIR}/Inter-Variable.ttf", size, weight)


def make_background():
    """Dark espresso ground with a soft warm-gold aurora glow (matches site hero)."""
    base = Image.new("RGB", (W, H), DARK)

    # subtle diagonal vignette gradient dark -> darker edge
    grad = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(grad)
    cx, cy = W * 0.78, H * 0.08
    max_r = math.hypot(W, H)
    for r in range(int(max_r), 0, -6):
        t = r / max_r
        val = int(255 * (1 - t) * 0.9)
        gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=val)
    glow_layer = Image.new("RGB", (W, H), DARK2)
    base = Image.composite(glow_layer, base, grad)

    # aurora blobs (screen-like additive glow), blurred
    aurora = Image.new("RGB", (W, H), (0, 0, 0))
    ad = ImageDraw.Draw(aurora)
    blobs = [
        (W * 0.78, H * 0.12, 480, (201, 161, 90)),
        (W * 0.15, H * 0.85, 420, (233, 196, 132)),
        (W * 0.85, H * 0.9, 380, (169, 130, 47)),
    ]
    for bx, by, br, color in blobs:
        layer = Image.new("L", (W, H), 0)
        ld = ImageDraw.Draw(layer)
        for r in range(br, 0, -4):
            t = r / br
            val = int(120 * (1 - t) ** 1.6)
            ld.ellipse([bx - r, by - r, bx + r, by + r], fill=val)
        colored = Image.new("RGB", (W, H), color)
        aurora = Image.composite(colored, aurora, layer.point(lambda p: 0) if False else layer)
        # additive blend
        import numpy as np  # noqa
    aurora = aurora.filter(ImageFilter.GaussianBlur(70))

    import numpy as np
    base_arr = np.array(base).astype(int)
    aurora_arr = np.array(aurora).astype(int)
    screened = 255 - ((255 - base_arr) * (255 - aurora_arr) // 255)
    out = Image.fromarray(screened.clip(0, 255).astype("uint8"), "RGB")

    # fine grain for texture (very subtle, editorial paper feel)
    noise = (np.random.default_rng(7).normal(0, 3.2, (H, W, 1))).clip(-14, 14)
    arr = np.array(out).astype(int) + noise
    out = Image.fromarray(arr.clip(0, 255).astype("uint8"), "RGB")

    # vignette darken corners slightly for focus
    vignette = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vignette)
    vd.rectangle([0, 0, W, H], fill=0)
    cx2, cy2 = W / 2, H / 2
    maxr = math.hypot(cx2, cy2)
    for r in range(int(maxr), 0, -4):
        t = r / maxr
        val = int(80 * max(0, t - 0.55) / 0.45)
        vd.ellipse([cx2 - r, cy2 - r, cx2 + r, cy2 + r], fill=val)
    dark_layer = Image.new("RGB", (W, H), DARK_EDGE)
    out = Image.composite(dark_layer, out, vignette)

    return out


def draw_hairline(draw, x1, y, x2, color=GOLD, width=2):
    draw.line([(x1, y), (x2, y)], fill=color, width=width)


def draw_doc_icon(draw, cx, cy, scale=1.0, color=GOLD):
    """Minimal abstract document/guide icon — no photography, just geometry."""
    w, h = 46 * scale, 58 * scale
    x0, y0 = cx - w / 2, cy - h / 2
    x1, y1 = cx + w / 2, cy + h / 2
    fold = 14 * scale
    draw.rounded_rectangle([x0, y0, x1, y1], radius=6 * scale, outline=color, width=max(2, int(2 * scale)))
    for i, frac in enumerate([0.42, 0.58, 0.74]):
        ly = y0 + h * frac
        lx1 = x0 + 8 * scale
        lx2 = x1 - 8 * scale - (10 * scale if i == 2 else 0)
        draw.line([(lx1, ly), (lx2, ly)], fill=color, width=max(2, int(1.6 * scale)))


def wrap_text(draw, text, font, max_width):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render_headline_segments(img, draw, segments, max_width, start_y, font_size, line_gap=1.14, weight=800, italic_weight=700):
    """segments: list of (text, is_emph). Wraps as continuous words, colors emphasized words gold-italic."""
    reg_font = playfair(font_size, weight)
    ital_font = playfair_italic(font_size, italic_weight)

    tokens = []
    for text, emph in segments:
        for w in text.split(" "):
            if w:
                tokens.append((w, emph))

    lines = []
    cur, cur_w = [], 0
    space_w = draw.textlength(" ", font=reg_font)
    for word, emph in tokens:
        f = ital_font if emph else reg_font
        ww = draw.textlength(word, font=f)
        extra = (space_w if cur else 0) + ww
        if cur_w + extra <= max_width or not cur:
            cur.append((word, emph))
            cur_w += extra
        else:
            lines.append(cur)
            cur = [(word, emph)]
            cur_w = ww
    if cur:
        lines.append(cur)

    line_h = int(font_size * line_gap)
    y = start_y
    for line in lines:
        total_w = 0
        widths = []
        for i, (word, emph) in enumerate(line):
            f = ital_font if emph else reg_font
            ww = draw.textlength(word, font=f)
            widths.append(ww)
            total_w += ww + (space_w if i > 0 else 0)
        x = (W - total_w) / 2
        for (word, emph), ww in zip(line, widths):
            f = ital_font if emph else reg_font
            color = GOLD_SOFT if emph else CREAM
            draw.text((x, y), word, font=f, fill=color)
            x += ww + space_w
        y += line_h
    return y


def badge_pill(draw, cx, cy, text, font, pad_x=26, pad_y=14):
    tw = draw.textlength(text, font=font)
    th = font.size
    x0, y0 = cx - tw / 2 - pad_x, cy - th / 2 - pad_y
    x1, y1 = cx + tw / 2 + pad_x, cy + th / 2 + pad_y
    draw.rounded_rectangle([x0, y0, x1, y1], radius=(y1 - y0) / 2, fill=GOLD)
    draw.text((cx - tw / 2, cy - th * 0.62), text, font=font, fill=(21, 16, 12))
    return y1


def make_creative(filename, eyebrow, segments, badge_text, font_size=76):
    img = make_background()
    draw = ImageDraw.Draw(img)

    margin = 90

    # eyebrow
    eb_font = inter(24, 700)
    eb_text = eyebrow.upper()
    # letter-spacing manual
    spaced = "  ".join(list(eb_text)) if False else eb_text
    ebw = draw.textlength(eb_text, font=eb_font)
    ebx = (W - ebw) / 2
    eby = 118
    draw.text((ebx, eby), eb_text, font=eb_font, fill=GOLD)
    draw_hairline(draw, W / 2 - 30, eby + 44, W / 2 + 30, color=GOLD_DEEP, width=2)

    # headline block, vertically centered-ish in remaining space
    max_text_width = W - margin * 2
    headline_start_y = 300
    end_y = render_headline_segments(img, draw, segments, max_text_width, headline_start_y, font_size)

    # small doc icon top-right corner
    draw_doc_icon(draw, W - 96, 96, scale=1.0, color=GOLD)

    # badge near bottom
    badge_font = inter(30, 700)
    badge_cy = H - 132
    badge_pill(draw, W / 2, badge_cy, badge_text, badge_font)

    # wordmark footer
    wm_font = inter(22, 700)
    wm_text = "простий · гід"
    wmw = draw.textlength(wm_text, font=wm_font)
    draw.text(((W - wmw) / 2, H - 66), wm_text, font=wm_font, fill=MUTED_GOLD)

    out_path = f"/Users/juliaknyazskaya/glp1-guide-site/ad-creatives/out/{filename}"
    img.save(out_path, "PNG")
    print("saved", out_path, "headline block ended at y=", end_y, "badge starts at y=", badge_cy - 40)
    return out_path


if __name__ == "__main__":
    make_creative(
        "creative_1_curiosity.png",
        "Простий гайд для новачків",
        [
            ("Про ці ін'єкції говорить весь інтернет.", False),
            ("Але ", False), ("ніхто не пояснив просто.", True),
        ],
        "PDF-ГАЙД · 399 ГРН",
        font_size=74,
    )
    make_creative(
        "creative_2_authority.png",
        "36 сторінок замість хаосу",
        [
            ("36 сторінок", True),
            (" замість тисячі суперечливих порад у TikTok.", False),
        ],
        "PDF-ГАЙД · 399 ГРН",
        font_size=74,
    )
    make_creative(
        "creative_3_reassurance.png",
        "Простими словами",
        [
            ("Це не «чарівна пігулка».", False),
            ("Це ", False), ("інструмент", True), (" — і ось як він працює.", False),
        ],
        "PDF-ГАЙД · 399 ГРН",
        font_size=72,
    )
