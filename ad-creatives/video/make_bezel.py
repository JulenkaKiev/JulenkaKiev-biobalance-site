from PIL import Image, ImageDraw, ImageFilter
import numpy as np, math

W, H = 1080, 1920
DARK = (21, 16, 12)
DARK2 = (33, 26, 20)
GOLD = (201, 161, 90)

# background (matches brand aurora look)
base = Image.new("RGB", (W, H), DARK)
aurora = Image.new("RGB", (W, H), (0,0,0))
blobs = [(W*0.8, H*0.15, 600, (201,161,90)), (W*0.15, H*0.7, 550, (233,196,132)), (W*0.7, H*0.9, 500,(169,130,47))]
aurora_arr = np.zeros((H,W,3), dtype=np.float32)
for bx,by,br,color in blobs:
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.sqrt((xx-bx)**2 + (yy-by)**2)
    t = np.clip(1 - dist/br, 0, 1) ** 1.6
    for c in range(3):
        aurora_arr[:,:,c] += t * color[c] * 0.5
aurora_arr = np.clip(aurora_arr, 0, 255)
base_arr = np.array(base).astype(np.float32)
screened = 255 - ((255-base_arr)*(255-aurora_arr)/255)
bg = Image.fromarray(screened.clip(0,255).astype('uint8')).filter(ImageFilter.GaussianBlur(2))

# Bezel frame (RGBA) - opaque dark frame with rounded transparent screen cutout
screen_x0, screen_y0, screen_x1, screen_y1 = 30, 96, 1050, 1824
bezel = Image.new("RGBA", (W, H), (0,0,0,0))
bd = ImageDraw.Draw(bezel)
frame_radius = 64
# outer frame shape (rounded rect) filled with dark2, then cut the screen area transparent
bd.rounded_rectangle([0,0,W-1,H-1], radius=frame_radius, fill=(28,22,17,255))
mask = Image.new("L", (W,H), 0)
md = ImageDraw.Draw(mask)
screen_radius = 46
md.rounded_rectangle([screen_x0,screen_y0,screen_x1,screen_y1], radius=screen_radius, fill=255)
bezel_arr = np.array(bezel)
mask_arr = np.array(mask)
bezel_arr[...,3] = np.where(mask_arr>0, 0, bezel_arr[...,3])
bezel = Image.fromarray(bezel_arr)
bd = ImageDraw.Draw(bezel)
# thin gold outline around screen
bd.rounded_rectangle([screen_x0-2,screen_y0-2,screen_x1+2,screen_y1+2], radius=screen_radius+2, outline=(201,161,90,220), width=4)
# (no notch - cleaner device frame)

bg.save("/Users/juliaknyazskaya/glp1-guide-site/ad-creatives/video/phone_bg.png")
bezel.save("/Users/juliaknyazskaya/glp1-guide-site/ad-creatives/video/phone_bezel.png")
print("saved", screen_x0, screen_y0, screen_x1, screen_y1, screen_x1-screen_x0, screen_y1-screen_y0)
