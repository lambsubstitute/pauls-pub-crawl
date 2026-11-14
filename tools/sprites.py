"""Character sprite sheets for Paul's Pub Crawl.

    python3 tools/sprites.py

Each character is drawn as vector shapes and rasterised fresh at every target height, so the
30 px street version and the 46 px pub version are both crisp pixel art (never resampled).
Sheet layout, one row, facing right:
    frame 0      idle
    frames 1-6   walk cycle
    frame 7      talk (mouth open)
Writes game/characters/<name>/<name>_<height>.png and art/previews/sprites_x4.png.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
FRAMES = 8
OUTLINE = (24, 16, 20, 255)

CHARS = {
    "paul": {
        "skin": (236, 182, 146), "skin_d": (196, 132, 104),
        "hair": (92, 60, 36), "hair_d": (58, 36, 22),
        "top": (54, 104, 186), "top_d": (32, 62, 128),
        "legs": (58, 72, 112), "legs_d": (36, 44, 74),
        "shoe": (236, 236, 228), "shoe_d": (160, 160, 156),
        "build": 1.0, "hair_style": "short", "beard": False, "apron": False, "collar": (240, 240, 236),
    },
    "landlord": {
        "skin": (226, 168, 132), "skin_d": (184, 120, 94),
        "hair": (120, 112, 104), "hair_d": (78, 72, 68),
        "top": (236, 232, 220), "top_d": (176, 170, 158),
        "legs": (44, 40, 40), "legs_d": (26, 24, 24),
        "shoe": (40, 26, 20), "shoe_d": (24, 16, 12),
        "build": 1.18, "hair_style": "bald", "beard": True, "apron": (44, 92, 64), "apron_d": (26, 58, 40),
        "collar": None,
    },
}
SIZES = {"paul": (30, 46), "landlord": (30, 46)}


def poly(d, pts, fill, s, ox, oy):
    d.polygon([(ox + x * s, oy + y * s) for x, y in pts], fill=fill)


def ell(d, cx, cy, rx, ry, fill, s, ox, oy):
    d.ellipse([ox + (cx - rx) * s, oy + (cy - ry) * s, ox + (cx + rx) * s, oy + (cy + ry) * s], fill=fill)


def limb(d, x0, y0, x1, y1, w0, w1, fill, s, ox, oy):
    """Tapered quad from (x0,y0) to (x1,y1)."""
    ang = math.atan2(y1 - y0, x1 - x0) + math.pi / 2
    dx, dy = math.cos(ang), math.sin(ang)
    pts = [(x0 + dx * w0, y0 + dy * w0), (x1 + dx * w1, y1 + dy * w1),
           (x1 - dx * w1, y1 - dy * w1), (x0 - dx * w0, y0 - dy * w0)]
    poly(d, pts, fill, s, ox, oy)


def draw(c, H, frame):
    """Character in a 100-unit-tall design space, scaled to H px. Origin = feet centre."""
    W = int(H * 0.62) + 4
    img = Image.new("RGBA", (W, H + 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = H / 100.0
    ox, oy = W / 2, H + 1 - 0.5          # feet at bottom-centre
    k = c["build"]

    walk = 1 <= frame <= 6
    ph = (frame - 1) / 6 * 2 * math.pi if walk else 0.0
    swing = math.sin(ph) * 13 if walk else 0.0
    bob = -abs(math.sin(ph)) * 2.0 if walk else 0.0
    lift_a = max(0.0, math.sin(ph)) * 6 if walk else 0.0
    lift_b = max(0.0, -math.sin(ph)) * 6 if walk else 0.0
    y = lambda v: -v + bob  # design y-up -> image y-down

    hip_y, knee_y = 48, 25
    # ---- back leg (darker) then back arm, so the near side overlaps
    def leg(sign, colors, lift):
        hx = -2 * k + sign * 2
        kx = hx + sign * swing * 0.6
        fx = hx + sign * swing
        limb(d, hx, y(hip_y), kx, y(knee_y + lift * 0.5), 6 * k, 5, colors[0], s, ox, oy)
        limb(d, kx, y(knee_y + lift * 0.5), fx, y(4 + lift), 5, 4.2, colors[0], s, ox, oy)
        poly(d, [(fx - 5, y(lift)), (fx + 10, y(lift)), (fx + 10, y(4 + lift)), (fx - 4, y(7 + lift))], colors[1], s, ox, oy)

    leg(-1, (c["legs_d"], c["shoe_d"]), lift_b)

    def arm(sign, col, hand):
        sx, sy = 1 * k, 72
        ex = sx - sign * swing * 0.5
        hx = sx - sign * swing * 0.9 + 2
        limb(d, sx, y(sy), ex, y(58), 4.5 * k, 4, col, s, ox, oy)
        limb(d, ex, y(58), hx, y(46), 4, 3.5, col if c.get("collar") is None else col, s, ox, oy)
        ell(d, hx + 0.5, y(44), 3.6, 3.6, hand, s, ox, oy)

    arm(1, c["top_d"], c["skin_d"])

    # ---- torso
    torso = [(-11 * k, y(48)), (11 * k, y(48)), (12 * k, y(73)), (6 * k, y(78)), (-7 * k, y(78)), (-12 * k, y(73))]
    poly(d, torso, c["top"], s, ox, oy)
    poly(d, [(-11 * k, y(48)), (-3 * k, y(48)), (-4 * k, y(78)), (-7 * k, y(78)), (-12 * k, y(73))], c["top_d"], s, ox, oy)
    if c.get("apron"):
        poly(d, [(-6 * k, y(66)), (11 * k, y(66)), (12 * k, y(30)), (-5 * k, y(30))], c["apron"], s, ox, oy)
        poly(d, [(-6 * k, y(66)), (-1 * k, y(66)), (0, y(30)), (-5 * k, y(30))], c["apron_d"], s, ox, oy)
    if c.get("collar"):
        poly(d, [(-1, y(78)), (8, y(78)), (6, y(73)), (2, y(74))], c["collar"], s, ox, oy)
    # belt line / hips
    poly(d, [(-11 * k, y(49)), (11 * k, y(49)), (11 * k, y(46)), (-11 * k, y(46))], c["legs_d"], s, ox, oy)

    leg(1, (c["legs"], c["shoe"]), lift_a)

    # ---- head (3/4 facing right)
    hx, hy = 2, 88
    poly(d, [(-1, y(76)), (5, y(76)), (5, y(81)), (-1, y(81))], c["skin_d"], s, ox, oy)  # neck
    ell(d, hx, y(hy), 9.5, 11, c["skin"], s, ox, oy)
    ell(d, hx - 4, y(hy), 5.5, 9.5, c["skin_d"], s, ox, oy)       # shadow side of face
    ell(d, hx + 9.5, y(hy - 1), 2.2, 3, c["skin"], s, ox, oy)      # nose
    ell(d, hx - 6, y(hy), 2.4, 3.2, c["skin_d"], s, ox, oy)        # ear
    if c["hair_style"] == "short":
        poly(d, [(hx - 10, y(hy + 1)), (hx - 9, y(hy + 9)), (hx - 2, y(hy + 13)), (hx + 7, y(hy + 12)),
                 (hx + 10, y(hy + 6)), (hx + 6, y(hy + 7)), (hx - 2, y(hy + 6)), (hx - 6, y(hy + 2))], c["hair"], s, ox, oy)
        poly(d, [(hx - 10, y(hy + 1)), (hx - 9, y(hy + 9)), (hx - 4, y(hy + 11)), (hx - 6, y(hy + 2))], c["hair_d"], s, ox, oy)
    else:  # bald on top, grey at the sides
        poly(d, [(hx - 10, y(hy - 2)), (hx - 9, y(hy + 5)), (hx - 5, y(hy + 4)), (hx - 6, y(hy - 3))], c["hair"], s, ox, oy)
        ell(d, hx + 2, y(hy + 7), 3, 1.5, (255, 220, 190, 255), s, ox, oy)  # shine
    if c["beard"]:
        poly(d, [(hx - 5, y(hy - 2)), (hx + 9, y(hy - 3)), (hx + 8, y(hy - 10)), (hx + 2, y(hy - 13)),
                 (hx - 4, y(hy - 9))], c["hair"], s, ox, oy)
        poly(d, [(hx - 5, y(hy - 2)), (hx - 1, y(hy - 3)), (hx, y(hy - 12)), (hx - 4, y(hy - 9))], c["hair_d"], s, ox, oy)
    # eye + brow + mouth
    ex = hx + 5
    d.point((ox + ex * s, oy + y(hy + 1) * s), fill=(20, 16, 18, 255))
    if H >= 40:
        d.point((ox + ex * s, oy + y(hy + 1) * s + 1), fill=(20, 16, 18, 255))
        d.line([ox + (ex - 2) * s, oy + y(hy + 4.5) * s, ox + (ex + 2) * s, oy + y(hy + 5) * s],
               fill=c["hair_d"] if c["hair_style"] == "short" else c["hair"])
    talking = frame == 7
    mouth_col = (110, 40, 40, 255)
    if talking:
        ell(d, hx + 6, y(hy - 6), 2.0, 2.2 if H >= 40 else 1.4, mouth_col, s, ox, oy)
    else:
        d.line([ox + (hx + 4) * s, oy + y(hy - 6) * s, ox + (hx + 7.5) * s, oy + y(hy - 6) * s], fill=mouth_col)

    arm(-1, c["top"], c["skin"])
    return outline(img)


def outline(img):
    """1px dark outline around opaque pixels (classic sprite readability)."""
    w, h = img.size
    a = img.getchannel("A").load()
    out = img.copy()
    p = out.load()
    for yy in range(h):
        for xx in range(w):
            if a[xx, yy] > 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = xx + dx, yy + dy
                if 0 <= nx < w and 0 <= ny < h and a[nx, ny] > 0:
                    p[xx, yy] = OUTLINE
                    break
    # harden alpha so there are no half-transparent edge pixels
    al = out.getchannel("A").point(lambda v: 255 if v > 90 else 0)
    out.putalpha(al)
    return out


def sheet(name, H):
    frames = [draw(CHARS[name], H, f) for f in range(FRAMES)]
    fw, fh = frames[0].size
    sh = Image.new("RGBA", (fw * FRAMES, fh), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        sh.paste(f, (i * fw, 0))
    dst = ROOT / "game" / "characters" / name / f"{name}_{H}.png"
    sh.save(dst)
    return sh, fw, fh


if __name__ == "__main__":
    previews = []
    meta = {}
    for name, heights in SIZES.items():
        for H in heights:
            sh, fw, fh = sheet(name, H)
            meta[f"{name}_{H}"] = (fw, fh)
            previews.append(sh)
            print(f"wrote game/characters/{name}/{name}_{H}.png  frame {fw}x{fh}")
    pw = max(p.width for p in previews)
    ph = sum(p.height + 4 for p in previews)
    prev = Image.new("RGBA", (pw, ph), (40, 34, 48, 255))
    yy = 0
    for p in previews:
        prev.alpha_composite(p, (0, yy))
        yy += p.height + 4
    (ROOT / "art" / "previews").mkdir(parents=True, exist_ok=True)
    prev.resize((pw * 4, ph * 4), Image.Resampling.NEAREST).save(ROOT / "art" / "previews" / "sprites_x4.png")
