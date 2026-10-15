# Regenerates every Windows/Android/in-app icon from .github/interlan/icon.png.
# Run from the repo root after changing the source icon: python .github/interlan/make_icons.py
from PIL import Image, ImageChops, ImageDraw

SRC = Image.open(".github/interlan/icon.png").convert("RGBA")
RES = "flutter/android/app/src/main/res"
DENSITIES = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}


def glyph():
    """The blue letterform alone, cut out of the light rounded-square background."""
    r, _, b, a = SRC.split()
    blueness = ImageChops.subtract(b, r).point(lambda v: max(0, min(255, (v - 40) * 255 // 120)))
    mask = ImageChops.multiply(blueness, a)
    out = SRC.copy()
    out.putalpha(mask)
    return out.crop(mask.getbbox())


def fit(img, canvas, ratio, bg=(0, 0, 0, 0)):
    """img scaled so its longer side is ratio*canvas, centred on a canvas x canvas square."""
    side = round(canvas * ratio)
    scale = side / max(img.size)
    small = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.LANCZOS)
    out = Image.new("RGBA", (canvas, canvas), bg)
    out.alpha_composite(small, ((canvas - small.width) // 2, (canvas - small.height) // 2))
    return out


def circle(canvas, img):
    out = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    mask = Image.new("L", (canvas * 4, canvas * 4), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, canvas * 4 - 1, canvas * 4 - 1), fill=255)
    out.paste(img, (0, 0), mask.resize((canvas, canvas), Image.LANCZOS))
    return out


G = glyph()

# Windows: exe resource, tray, flutter runner, and the custom-client assets used for shortcuts/tray.
SRC.save("res/icon.png")
SRC.save("res/icon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
SRC.save("res/tray-icon.ico", sizes=[(16, 16), (20, 20), (24, 24), (32, 32), (48, 48), (64, 64)])
SRC.save("flutter/windows/runner/resources/app_icon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (256, 256)])
SRC.resize((512, 512), Image.LANCZOS).save("flutter/assets/icon.png")
SRC.save("flutter/assets/icon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

# Linux: hicolor icons shipped in the .deb (scalable.svg just wraps the PNG).
for size, path in [(32, "res/32x32.png"), (64, "res/64x64.png"), (128, "res/128x128.png"), (256, "res/128x128@2x.png")]:
    SRC.resize((size, size), Image.LANCZOS).save(path)
with open("res/scalable.svg", "w", encoding="utf-8") as f:
    import base64, io
    buf = io.BytesIO()
    SRC.resize((512, 512), Image.LANCZOS).save(buf, "PNG")
    f.write('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            'width="512" height="512" viewBox="0 0 512 512"><image width="512" height="512" '
            f'xlink:href="data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"/></svg>\n')

# Android launcher (legacy square + round), adaptive foreground (108dp, glyph inside the 66dp safe zone)
# and the notification icon (white silhouette).
white_disc = None
for name, k in DENSITIES.items():
    d = f"{RES}/mipmap-{name}"
    s = round(48 * k)
    SRC.resize((s, s), Image.LANCZOS).save(f"{d}/ic_launcher.png")
    circle(s, fit(G, s, 0.6, (255, 255, 255, 255))).save(f"{d}/ic_launcher_round.png")
    fit(G, round(108 * k), 0.5).save(f"{d}/ic_launcher_foreground.png")
    n = round(24 * k)
    stat = fit(G, n, 0.92)
    Image.merge("LA", (Image.new("L", stat.size, 255), stat.getchannel("A"))).save(f"{d}/ic_stat_logo.png")

print("icons regenerated")
