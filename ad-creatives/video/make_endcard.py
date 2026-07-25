from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, math

W, H = 1080, 1920
FONT_DIR = "/Users/juliaknyazskaya/glp1-guide-site/ad-creatives/fonts"
DARK = (21, 16, 12)
DARK2 = (33, 26, 20)
CREAM = (247, 241, 231)
GOLD = (201, 161, 90)
GOLD_SOFT = (224, 187, 124)
GOLD_DEEP = (169, 130, 47)

def playfair(size, weight=800):
    f = ImageFont.truetype(f"{FONT_DIR}/PlayfairDisplay-Variable.ttf", size)
    f.set_variation_by_axes([weight])
    return f

def inter(size, weight=700):
    f = ImageFont.truetype(f"{FONT_DIR}/Inter-Variable.ttf", size)
    f.set_variation_by_axes([weight])
    return f

base = Image.new("RGB", (W, H), DARK)
aurora = Image.new("RGB", (W, H), (0,0,0))
ad = ImageDraw.Draw(aurora)
blobs = [(W*0.75, H*0.15, 650, (201,161,90)), (W*0.2, H*0.5, 550, (233,196,132)), (W*0.6, H*0.85, 600,(169,130,47))]
for bx,by,br,color in blobs:
    layer = Image.new("L",(W,H),0)
    ld = ImageDraw.Draw(layer)
    for r in range(br,0,-4):
        t = r/br
        val = int(130*(1-t)**1.6)
        ld.ellipse([bx-r,by-r,bx+r,by+r], fill=val)
    colored = Image.new("RGB",(W,H),color)
    aurora = Image.composite(colored, aurora, layer)
aurora = aurora.filter(ImageFilter.GaussianBlur(90))
base_arr = np.array(base).astype(int)
aurora_arr = np.array(aurora).astype(int)
screened = 255 - ((255-base_arr)*(255-aurora_arr)//255)
out = Image.fromarray(screened.clip(0,255).astype('uint8'))

draw = ImageDraw.Draw(out)

# Wordmark
wm_font = inter(40, 800)
w1 = "Bio"; w2 = "Balance"
w1w = draw.textlength(w1, font=wm_font)
w2w = draw.textlength(w2, font=wm_font)
total_w = w1w + w2w
x = (W-total_w)/2
y = 260
draw.text((x, y), w1, font=wm_font, fill=CREAM)
draw.text((x+w1w, y), w2, font=wm_font, fill=GOLD)

# Headline
head_font = playfair(84, 800)
lines = ["Твоя ясність", "починається", "з одного рішення"]
ly = 520
for line in lines:
    lw = draw.textlength(line, font=head_font)
    draw.text(((W-lw)/2, ly), line, font=head_font, fill=CREAM)
    ly += 100

# Price pill
price_font = inter(46, 800)
price_text = "399 ГРН"
pw = draw.textlength(price_text, font=price_font)
pad_x, pad_y = 46, 26
px0 = (W-pw)/2 - pad_x
py0 = 940
px1 = (W+pw)/2 + pad_x
py1 = py0 + price_font.size + pad_y*2
draw.rounded_rectangle([px0,py0,px1,py1], radius=(py1-py0)/2, fill=GOLD)
draw.text(((W-pw)/2, py0+pad_y-4), price_text, font=price_font, fill=DARK)

# CTA button
cta_font = inter(42, 800)
cta_text = "Забрати гайд зі знижкою →"
cw = draw.textlength(cta_text, font=cta_font)
bpad_x, bpad_y = 50, 30
bx0 = (W-cw)/2 - bpad_x
by0 = 1150
bx1 = (W+cw)/2 + bpad_x
by1 = by0 + cta_font.size + bpad_y*2
draw.rounded_rectangle([bx0,by0,bx1,by1], radius=(by1-by0)/2, fill=None, outline=GOLD, width=3)
draw.text(((W-cw)/2, by0+bpad_y-2), cta_text, font=cta_font, fill=GOLD_SOFT)

# small disclaimer-ish footer
foot_font = inter(26, 600)
foot_text = "PDF-гайд · миттєвий доступ після оплати"
fw = draw.textlength(foot_text, font=foot_font)
draw.text(((W-fw)/2, 1300), foot_text, font=foot_font, fill=(184,160,120))

out.save("/Users/juliaknyazskaya/glp1-guide-site/ad-creatives/video/endcard.png")
print("saved")
