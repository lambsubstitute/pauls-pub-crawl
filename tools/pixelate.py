"""Turn a Blender render into an Amiga-style 320x200 background.

    python3 tools/pixelate.py church_st [--colors 32]

Reads  art/renders/<room>.png  (any size, 16:10)
Writes game/rooms/<room>/props/bg_<room>.png  (320x200, <= N colours)
       art/previews/<room>_x3.png               (nearest-neighbour 3x preview)

Steps: night-sky stars/moon on the raw render -> area downscale -> gentle contrast and
saturation lift -> median-cut palette -> 4x4 ordered (Bayer) dither. Ordered dither gives the
regular cross-hatch texture of hand-dithered 32-colour art rather than error-diffusion noise.
"""
import argparse
import random
from pathlib import Path

from PIL import Image, ImageEnhance, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
BAYER4 = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]

ROOM_FX = {
    # sky_rows: how far down (in 320x200 px) stars may appear; moon: centre in game px
    "church_st": {"stars": 60, "sky_rows": 34, "moon": (276, 14, 7)},
    # accents: palette slots kept for small saturated details median-cut would merge into brown
    "cross_house_tavern": {"accents": [(70, 140, 255), (40, 70, 170), (70, 220, 100), (170, 35, 30), (255, 190, 70)]},
}


def add_sky(img, fx, seed=3):
    """Stars only where the render is already dark sky, plus a soft moon."""
    if not fx.get("stars"):
        return img
    w, h = img.size
    s = w / 320
    rng = random.Random(seed)
    px = img.load()
    d = ImageDraw.Draw(img)
    for _ in range(fx["stars"]):
        x = rng.randrange(0, w)
        y = rng.randrange(0, int(fx["sky_rows"] * s))
        r, g, b = px[x, y][:3]
        if r + g + b < 120 and b >= r:
            size = s * rng.choice([0.5, 0.5, 0.5, 1.0])
            c = rng.choice([(255, 250, 230), (210, 220, 255), (255, 240, 200)])
            d.rectangle([x, y, x + size, y + size], fill=c)
    if fx.get("moon"):
        mx, my, mr = (v * s for v in fx["moon"])
        glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse([mx - mr * 2.6, my - mr * 2.6, mx + mr * 2.6, my + mr * 2.6], fill=(150, 160, 210, 60))
        glow = glow.filter(ImageFilter.GaussianBlur(mr * 1.2))
        img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
        d = ImageDraw.Draw(img)
        d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(242, 236, 214))
        d.ellipse([mx - mr * 0.35, my - mr * 0.5, mx + mr * 0.05, my - mr * 0.1], fill=(214, 206, 186))
        d.ellipse([mx + mr * 0.2, my + mr * 0.1, mx + mr * 0.55, my + mr * 0.45], fill=(222, 214, 194))
    return img


def ordered_quantise(img, colors, accents=()):
    n = colors - len(accents)
    pal_img = img.quantize(colors=n, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    flat = pal_img.getpalette()[: n * 3]
    pal = [tuple(flat[i:i + 3]) for i in range(0, len(flat), 3)] + [tuple(a) for a in accents]
    # dither strength ~ half the average gap between neighbouring palette colours
    spread = 22.0
    cache = {}
    src = img.load()
    out = Image.new("RGB", img.size)
    dst = out.load()
    w, h = img.size
    for y in range(h):
        row = BAYER4[y % 4]
        for x in range(w):
            r, g, b = src[x, y][:3]
            t = (row[x % 4] / 16.0 - 0.5) * spread
            key = (int(r + t) >> 2, int(g + t) >> 2, int(b + t) >> 2)
            c = cache.get(key)
            if c is None:
                rr, gg, bb = r + t, g + t, b + t
                c = min(pal, key=lambda p: (p[0] - rr) ** 2 * 0.3 + (p[1] - gg) ** 2 * 0.59 + (p[2] - bb) ** 2 * 0.11)
                cache[key] = c
            dst[x, y] = c
    return out, pal


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("room")
    ap.add_argument("--colors", type=int, default=32)
    a = ap.parse_args()

    raw = Image.open(ROOT / "art" / "renders" / f"{a.room}.png").convert("RGB")
    raw = add_sky(raw, ROOM_FX.get(a.room, {}))
    small = raw.resize((320, 200), Image.Resampling.BOX)
    small = ImageEnhance.Contrast(small).enhance(1.12)
    small = ImageEnhance.Color(small).enhance(1.25)
    small = small.filter(ImageFilter.UnsharpMask(radius=1, percent=60, threshold=2))
    out, pal = ordered_quantise(small, a.colors, ROOM_FX.get(a.room, {}).get("accents", ()))

    dst = ROOT / "game" / "rooms" / a.room / "props" / f"bg_{a.room}.png"
    dst.parent.mkdir(parents=True, exist_ok=True)
    out.save(dst)
    prev = ROOT / "art" / "previews" / f"{a.room}_x3.png"
    prev.parent.mkdir(parents=True, exist_ok=True)
    out.resize((960, 600), Image.Resampling.NEAREST).save(prev)
    print(f"wrote {dst.relative_to(ROOT)} ({len(set(out.get_flattened_data()))} colours) and {prev.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
