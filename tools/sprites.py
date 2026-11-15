"""Character sprite sheets for Paul's Pub Crawl.

    python3 tools/sprites.py

Each character is drawn as vector shapes and rasterised fresh at every target height, so the
30 px street version and the 46 px pub version are both crisp pixel art (never resampled).
Sheet layout, one row, facing right:
    frame 0      idle
    frames 1-8   walk cycle (contact, down, passing, up for each leg)
    frame 9      talk (mouth open)
Writes game/characters/<name>/<name>_<height>.png and art/previews/sprites_x4.png.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
WALK_N = 8
FRAMES = WALK_N + 2
TALK_FRAME = WALK_N + 1
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
    "barmaid": {
        "skin": (240, 196, 164), "skin_d": (204, 146, 118),
        "hair": (226, 180, 92), "hair_d": (170, 120, 50),
        "top": (124, 30, 52), "top_d": (82, 16, 32),
        "legs": (34, 32, 40), "legs_d": (20, 18, 24),
        "shoe": (30, 22, 22), "shoe_d": (18, 12, 12),
        "build": 0.92, "hair_style": "bun", "beard": False, "apron": False, "collar": (236, 230, 220),
    },
    "reg": {
        "skin": (222, 166, 134), "skin_d": (178, 118, 92),
        "hair": (196, 192, 186), "hair_d": (140, 136, 132),
        "top": (70, 96, 58), "top_d": (44, 62, 36),
        "legs": (96, 92, 86), "legs_d": (64, 60, 56),
        "shoe": (60, 36, 24), "shoe_d": (36, 22, 14),
        "build": 1.05, "hair_style": "cap", "cap": (118, 92, 62), "cap_d": (80, 60, 40),
        "beard": False, "apron": False, "collar": (214, 206, 186),
    },
    # Berkeley Arms: Clive behind the bar, Dot the darts champion (small, permed, sharp-eyed)
    "clive": {
        "skin": (238, 186, 156), "skin_d": (198, 138, 110),
        "hair": (186, 92, 40), "hair_d": (128, 58, 24),
        "top": (106, 30, 34), "top_d": (68, 16, 22),
        "legs": (40, 38, 44), "legs_d": (24, 22, 28),
        "shoe": (30, 22, 20), "shoe_d": (18, 12, 12),
        "build": 1.1, "hair_style": "short", "beard": True, "apron": False, "collar": (240, 238, 230),
    },
    "dot": {
        "skin": (236, 196, 172), "skin_d": (196, 150, 128),
        "hair": (214, 212, 222), "hair_d": (156, 154, 170),
        "top": (150, 110, 180), "top_d": (100, 70, 128),
        "legs": (88, 84, 96), "legs_d": (58, 54, 64),
        "shoe": (70, 40, 50), "shoe_d": (44, 24, 30),
        "build": 0.9, "hair_style": "perm", "beard": False, "apron": False, "collar": (240, 236, 226),
        "stature": 0.88, "glasses": True,
    },
    # Nottingham Arms: Jackie the landlady (auburn bob), Gaz the pool king (waistcoat, tache),
    # Norman the old regular (bald, white walrus moustache, glasses, cardigan, a bit stooped)
    "jackie": {
        "skin": (238, 190, 160), "skin_d": (198, 140, 114),
        "hair": (150, 52, 34), "hair_d": (98, 30, 20),
        "top": (40, 118, 128), "top_d": (24, 76, 84),
        "legs": (36, 34, 44), "legs_d": (22, 20, 28),
        "shoe": (40, 24, 24), "shoe_d": (24, 14, 14),
        "build": 0.98, "hair_style": "bob", "beard": False, "apron": False, "collar": (240, 236, 226),
        "earrings": (250, 204, 80),
    },
    "gaz": {
        "skin": (230, 174, 140), "skin_d": (188, 126, 98),
        "hair": (40, 32, 30), "hair_d": (22, 18, 16),
        "top": (236, 234, 228), "top_d": (180, 178, 172),
        "legs": (30, 30, 36), "legs_d": (18, 18, 22),
        "shoe": (20, 18, 18), "shoe_d": (10, 10, 10),
        "build": 0.96, "hair_style": "short", "beard": False, "apron": False, "collar": None,
        "waistcoat": (36, 34, 40), "waistcoat_d": (20, 18, 24), "tache": True, "tie": (150, 24, 30),
    },
    "norman": {
        "skin": (232, 182, 156), "skin_d": (190, 132, 110),
        "hair": (232, 232, 228), "hair_d": (176, 176, 172),
        "top": (132, 98, 58), "top_d": (92, 66, 36),
        "legs": (84, 80, 70), "legs_d": (56, 52, 46),
        "shoe": (58, 34, 22), "shoe_d": (34, 20, 12),
        "build": 1.04, "hair_style": "bald", "beard": False, "apron": False, "collar": (226, 222, 208),
        "tache": True, "glasses": True, "stature": 0.93,
    },
}
SIZES = {"paul": (30, 46), "landlord": (30, 46), "barmaid": (30, 46), "reg": (30, 46),
         "clive": (30, 46), "dot": (30, 46), "jackie": (30, 46), "gaz": (30, 46), "norman": (30, 46)}


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
    s = H / 100.0 * c.get("stature", 1.0)   # stature < 1 draws a shorter person on the same sheet
    ox, oy = W / 2, H + 1 - 0.5          # feet at bottom-centre
    k = c["build"]

    walk = 1 <= frame <= WALK_N
    ph = (frame - 1) / WALK_N * 2 * math.pi if walk else 0.0
    # Body is lowest at heel-strike (|cos|=1) and highest when the legs pass (|cos|=0).
    up = (1 - abs(math.cos(ph))) * 3.0 if walk else 0.0
    y = lambda v: -(v + up)   # upper body: design y-up -> image y-down, with bob
    g = lambda v: -v          # ground-anchored parts (feet) never bob

    SX, LIFT = 14.0, 10.0     # foot reach either side of the hip, and swing-foot lift
    THIGH, SHIN = 23.0, 22.0
    hip_y = 48

    def knee_for(hx, hy, ax, ay):
        """Two-bone IK in y-up design space; knee always bends forward (+x)."""
        dx, dy = ax - hx, ay - hy
        dist = max(1e-3, min(math.hypot(dx, dy), THIGH + SHIN - 0.01))
        a = math.acos(max(-1.0, min(1.0, (THIGH ** 2 + dist ** 2 - SHIN ** 2) / (2 * THIGH * dist))))
        base = math.atan2(dy, dx)
        c1 = (hx + THIGH * math.cos(base + a), hy + THIGH * math.sin(base + a))
        c2 = (hx + THIGH * math.cos(base - a), hy + THIGH * math.sin(base - a))
        return c1 if c1[0] > c2[0] else c2

    def leg(p, colors):
        hx, hy = -1 * k, hip_y + up
        if walk:
            fx = SX * math.cos(p)                  # p=0 heel-strike in front, p=pi push-off behind
            lift = LIFT * max(0.0, -math.sin(p))   # foot only leaves the ground while swinging forward
        else:
            fx, lift = (2.0 if colors[0] == c["legs"] else -3.0), 0.0
        ax, ay = fx, 5 + lift
        kx, ky = knee_for(hx, hy, ax, ay)
        limb(d, hx, -hy, kx, -ky, 6 * k, 5, colors[0], s, ox, oy)
        limb(d, kx, -ky, ax, -ay, 5, 4.2, colors[0], s, ox, oy)
        toe_tilt = lift * 0.35
        poly(d, [(fx - 5, g(lift)), (fx + 10, g(lift + toe_tilt)), (fx + 10, g(4 + lift + toe_tilt)),
                 (fx - 4, g(7 + lift))], colors[1], s, ox, oy)

    near_p, far_p = ph, ph + math.pi
    leg(far_p, (c["legs_d"], c["shoe_d"]))

    def arm(p, col, hand):
        # arms swing opposite to the leg on the same side
        sw = 10 * math.cos(p + math.pi) if walk else 0.0
        sx, sy = 1 * k, 72
        ex = sx + sw * 0.55
        hx = sx + sw + 2
        limb(d, sx, y(sy), ex, y(58), 4.5 * k, 4, col, s, ox, oy)
        limb(d, ex, y(58), hx, y(46 + abs(sw) * 0.25), 4, 3.5, col, s, ox, oy)
        ell(d, hx + 0.5, y(44 + abs(sw) * 0.25), 3.6, 3.6, hand, s, ox, oy)

    arm(far_p, c["top_d"], c["skin_d"])

    # ---- torso
    torso = [(-11 * k, y(48)), (11 * k, y(48)), (12 * k, y(73)), (6 * k, y(78)), (-7 * k, y(78)), (-12 * k, y(73))]
    poly(d, torso, c["top"], s, ox, oy)
    poly(d, [(-11 * k, y(48)), (-3 * k, y(48)), (-4 * k, y(78)), (-7 * k, y(78)), (-12 * k, y(73))], c["top_d"], s, ox, oy)
    if c.get("apron"):
        poly(d, [(-6 * k, y(66)), (11 * k, y(66)), (12 * k, y(30)), (-5 * k, y(30))], c["apron"], s, ox, oy)
        poly(d, [(-6 * k, y(66)), (-1 * k, y(66)), (0, y(30)), (-5 * k, y(30))], c["apron_d"], s, ox, oy)
    if c.get("collar"):
        poly(d, [(-1, y(78)), (8, y(78)), (6, y(73)), (2, y(74))], c["collar"], s, ox, oy)
    if c.get("waistcoat"):
        # open-fronted waistcoat over the shirt: shirt shows in a V down the chest, with a tie
        poly(d, [(-11 * k, y(48)), (11 * k, y(48)), (12 * k, y(73)), (6 * k, y(78)), (4, y(77)), (5, y(56)),
                 (3, y(50)), (-7 * k, y(78)), (-12 * k, y(73))], c["waistcoat"], s, ox, oy)
        poly(d, [(-11 * k, y(48)), (-3 * k, y(48)), (-4 * k, y(78)), (-7 * k, y(78)), (-12 * k, y(73))],
             c["waistcoat_d"], s, ox, oy)
        if c.get("tie"):
            poly(d, [(3, y(77)), (6, y(77)), (6, y(58)), (4.5, y(55)), (3, y(58))], c["tie"], s, ox, oy)
    # belt line / hips
    poly(d, [(-11 * k, y(49)), (11 * k, y(49)), (11 * k, y(46)), (-11 * k, y(46))], c["legs_d"], s, ox, oy)

    leg(near_p, (c["legs"], c["shoe"]))

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
    elif c["hair_style"] == "bun":
        poly(d, [(hx - 10, y(hy - 4)), (hx - 10, y(hy + 8)), (hx - 3, y(hy + 13)), (hx + 7, y(hy + 12)),
                 (hx + 10, y(hy + 5)), (hx + 5, y(hy + 7)), (hx - 3, y(hy + 5)), (hx - 6, y(hy - 4))], c["hair"], s, ox, oy)
        ell(d, hx - 10, y(hy + 7), 4.5, 4.5, c["hair"], s, ox, oy)          # the bun
        ell(d, hx - 11, y(hy + 6), 2.5, 2.5, c["hair_d"], s, ox, oy)
        poly(d, [(hx - 10, y(hy - 4)), (hx - 10, y(hy + 8)), (hx - 5, y(hy + 10)), (hx - 6, y(hy - 4))], c["hair_d"], s, ox, oy)
    elif c["hair_style"] == "cap":
        poly(d, [(hx - 10, y(hy - 3)), (hx - 9, y(hy + 4)), (hx - 5, y(hy + 3)), (hx - 6, y(hy - 4))], c["hair"], s, ox, oy)
        poly(d, [(hx - 11, y(hy + 4)), (hx - 9, y(hy + 11)), (hx + 3, y(hy + 13)), (hx + 9, y(hy + 9)),
                 (hx + 15, y(hy + 6)), (hx + 14, y(hy + 4)), (hx + 6, y(hy + 5))], c["cap"], s, ox, oy)  # flat cap + peak
        poly(d, [(hx - 11, y(hy + 4)), (hx - 9, y(hy + 11)), (hx - 3, y(hy + 12)), (hx - 4, y(hy + 4))], c["cap_d"], s, ox, oy)
    elif c["hair_style"] == "bob":
        # chin-length bob with a fringe, swinging forward past the cheek
        poly(d, [(hx - 11, y(hy - 9)), (hx - 11, y(hy + 7)), (hx - 4, y(hy + 13)), (hx + 6, y(hy + 13)),
                 (hx + 11, y(hy + 7)), (hx + 10, y(hy + 3)), (hx + 3, y(hy + 5)), (hx - 3, y(hy + 3)),
                 (hx - 4, y(hy - 9))], c["hair"], s, ox, oy)
        poly(d, [(hx - 11, y(hy - 9)), (hx - 11, y(hy + 7)), (hx - 6, y(hy + 10)), (hx - 6, y(hy - 9))],
             c["hair_d"], s, ox, oy)
    elif c["hair_style"] == "perm":
        # tight grey curls: a cloud of small blobs over the crown and down to the ears
        for (dx, dy, r) in ((-9, 2, 4.2), (-8, 7, 4.4), (-4, 11, 4.6), (2, 12.5, 4.6), (6, 11, 3.8),
                            (-10, -3, 3.6), (-5, 6, 4.0), (3, 8, 3.6)):
            ell(d, hx + dx, y(hy + dy), r, r, c["hair"], s, ox, oy)
        for (dx, dy, r) in ((-10, 3, 2.4), (-9, -3, 2.2), (-6, 10, 2.2), (0, 13, 2.0)):
            ell(d, hx + dx, y(hy + dy), r, r, c["hair_d"], s, ox, oy)
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
    if c.get("tache"):
        # bushy moustache under the nose (Norman's is white, Gaz's is dark)
        poly(d, [(hx + 2, y(hy - 3)), (hx + 11, y(hy - 3)), (hx + 11, y(hy - 6)), (hx + 7, y(hy - 5)),
                 (hx + 3, y(hy - 6))], c["hair"], s, ox, oy)
    if c.get("earrings") and H >= 40:
        d.point((ox + (hx - 6) * s, oy + y(hy - 4) * s), fill=(*c["earrings"], 255))
    if c.get("glasses"):
        # thin silver rims: a bar across the eye line plus the arm back to the ear (a black
        # outline at this size reads as a mask)
        gcol = (96, 84, 110, 255)
        d.line([ox + (ex - 2.5) * s, oy + y(hy + 3) * s, ox + (ex + 3) * s, oy + y(hy + 3) * s], fill=gcol)
        d.line([ox + (hx - 4) * s, oy + y(hy + 2) * s, ox + (ex - 2.5) * s, oy + y(hy + 3) * s], fill=gcol)
        if H >= 40:
            d.point((ox + (ex + 3) * s, oy + y(hy + 1) * s), fill=gcol)
    talking = frame == TALK_FRAME
    mouth_col = (110, 40, 40, 255)
    if talking:
        ell(d, hx + 6, y(hy - 6), 2.0, 2.2 if H >= 40 else 1.4, mouth_col, s, ox, oy)
    else:
        d.line([ox + (hx + 4) * s, oy + y(hy - 6) * s, ox + (hx + 7.5) * s, oy + y(hy - 6) * s], fill=mouth_col)

    arm(near_p, c["top"], c["skin"])
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


# ------------------------------------------------------------ skittle pin ----
def pin_sprite(h):
    """Wooden skittle pin, h px tall: cream body, red neck band, dark outline."""
    w = max(5, round(h * 0.5))
    img = Image.new("RGBA", (w + 2, h + 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = (w + 2) / 2
    body, shade, band = (236, 226, 200, 255), (186, 170, 140, 255), (176, 34, 30, 255)
    # silhouette: round head, narrow neck, fat belly, flat base
    for yy in range(h):
        t = yy / (h - 1)
        if t < 0.18:
            r = 0.30 * math.sin(math.pi * (t / 0.18) * 0.5 + 0.6)
        elif t < 0.32:
            r = 0.22
        else:
            r = 0.22 + 0.28 * math.sin(math.pi * min(1.0, (t - 0.32) / 0.62))
            if t > 0.94:
                r = 0.34
        half = max(0.6, r * w)
        col = band if 0.20 <= t <= 0.28 else body
        d.line([cx - half, yy + 1, cx + half - 1, yy + 1], fill=col)
        d.point((cx - half, yy + 1), fill=shade if col == body else band)
    return outline(img)


def pin_icon():
    icon = Image.new("RGBA", (24, 16), (0, 0, 0, 0))
    p = pin_sprite(14).rotate(-35, expand=True, resample=Image.Resampling.NEAREST)
    icon.alpha_composite(p, ((24 - p.width) // 2, (16 - p.height) // 2))
    return icon


if __name__ == "__main__":
    pin = pin_sprite(12)
    pin.save(ROOT / "game" / "rooms" / "cross_house_tavern" / "props" / "doorstop_pin.png")
    pin_icon().save(ROOT / "game" / "inventory_items" / "skittle_pin" / "skittle_pin.png")
    print("wrote doorstop_pin.png and skittle_pin.png")


# ------------------------------------------------------------- house darts ----
def darts_sprite():
    """Three darts stuck point-up into the underside of a beam: shafts and flights hang down."""
    img = Image.new("RGBA", (9, 9), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for x0, tilt, flight in ((1, 1, (190, 30, 24, 255)), (4, 0, (30, 140, 60, 255)), (7, -1, (190, 30, 24, 255))):
        d.line([x0, 0, x0 + tilt, 4], fill=(200, 196, 186, 255))        # steel barrel + shaft
        d.point((x0 + tilt, 5), fill=flight)                             # flight
        d.point((x0 + tilt - 1, 6), fill=flight)
        d.point((x0 + tilt + 1, 6), fill=flight)
    return img


def darts_icon():
    icon = Image.new("RGBA", (24, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(icon)
    for i, col in enumerate(((190, 30, 24, 255), (30, 140, 60, 255), (190, 30, 24, 255))):
        y0 = 4 + i * 4
        d.line([3, y0 + 2, 15, y0 - 1], fill=(205, 200, 190, 255))      # barrel
        d.line([8, y0 + 1, 12, y0], fill=(120, 110, 100, 255))            # knurled grip
        d.polygon([(15, y0 - 1), (20, y0 - 4), (21, y0), (17, y0 + 1)], fill=col)  # flight
        d.point((2, y0 + 2), fill=(240, 240, 240, 255))                   # point
    return outline(icon)


if __name__ == "__main__":
    darts_sprite().save(ROOT / "game" / "rooms" / "berkeley_arms" / "props" / "beam_darts.png")
    darts_icon().save(ROOT / "game" / "inventory_items" / "darts" / "darts.png")
    print("wrote beam_darts.png and darts.png")


# --------------------------------------------------- Nottingham Arms props ----
WOOD, WOOD_D, BRASS = (196, 148, 92, 255), (120, 80, 44, 255), (230, 180, 70, 255)


def cue_butt_sprite():
    """The house cue's butt end standing in the wall rack: thick dark-wood half with a brass
    joint at the top (the shaft screws in there)."""
    img = Image.new("RGBA", (5, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([1, 3, 3, 15], fill=(70, 36, 20, 255))       # ebony butt
    d.line([1, 3, 1, 15], fill=(40, 20, 12, 255))
    d.rectangle([1, 9, 3, 11], fill=(150, 30, 30, 255))       # red wrap
    d.rectangle([1, 1, 3, 2], fill=BRASS)                     # joint
    d.point((2, 0), fill=BRASS)
    return img


def cue_shaft_sprite():
    """Norman's 'jukebox poker': the house cue's top half, light ash, blue chalky tip,
    leaning against the wall."""
    img = Image.new("RGBA", (6, 27), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.line([1, 0, 4, 24], fill=WOOD)
    d.line([2, 0, 5, 24], fill=WOOD_D)
    d.point((1, 0), fill=(70, 110, 220, 255))                 # chalked tip
    d.rectangle([3, 24, 5, 26], fill=BRASS)                   # brass joint at the bottom
    return img


def pool_rest_sprite():
    """The pool rest leaning on the wall: long stick with a brass X head at the top."""
    img = Image.new("RGBA", (9, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.line([3, 5, 5, 31], fill=WOOD_D)
    d.line([4, 5, 6, 31], fill=WOOD)
    d.line([0, 0, 7, 6], fill=BRASS)                          # cross head
    d.line([7, 0, 0, 6], fill=BRASS)
    d.point((4, 3), fill=(150, 110, 40, 255))
    return img


def _icon_stick(parts):
    icon = Image.new("RGBA", (24, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(icon)
    for (x0, y0, x1, y1), col in parts:
        d.line([x0, y0, x1, y1], fill=col, width=2)
    return icon


def cue_icons():
    tip = (70, 110, 220, 255)
    butt = _icon_stick([((3, 13, 12, 7), (70, 36, 20, 255)), ((7, 10, 9, 9), (150, 30, 30, 255)),
                        ((12, 7, 14, 6), BRASS)])
    shaft = _icon_stick([((8, 11, 20, 3), WOOD), ((6, 12, 8, 11), BRASS), ((20, 3, 21, 2), tip)])
    cue = _icon_stick([((2, 14, 9, 10), (70, 36, 20, 255)), ((9, 10, 10, 9), BRASS), ((10, 9, 21, 2), WOOD),
                       ((21, 2, 22, 1), tip)])
    rest = _icon_stick([((3, 14, 16, 5), WOOD), ((15, 2, 21, 8), BRASS), ((21, 2, 15, 8), BRASS)])
    return {"cue_butt": butt, "cue_shaft": shaft, "house_cue": cue, "pool_rest": rest}


if __name__ == "__main__":
    props = ROOT / "game" / "rooms" / "nottingham_arms" / "props"
    props.mkdir(parents=True, exist_ok=True)
    cue_butt_sprite().save(props / "cue_butt.png")
    outline(cue_shaft_sprite()).save(props / "cue_shaft.png")
    outline(pool_rest_sprite()).save(props / "pool_rest.png")
    for k, im in cue_icons().items():
        outline(im).save(ROOT / "game" / "inventory_items" / k / f"{k}.png")
    print("wrote Nottingham Arms props and cue/rest icons")
