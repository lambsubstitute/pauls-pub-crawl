"""Placeholder pixel art for the vertical slice.

Draws 320x200 room backgrounds and small character/item sprites straight with PIL,
then quantises to a shared 32-colour palette. These get replaced by Blender renders
later (see DESIGN.md "Art pipeline"); hotspot/walkable polygons in the rooms are laid
out to match the coordinates used here.

    python3 tools/placeholder_art.py
"""
from pathlib import Path
import random

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
W, H = 320, 200
HORIZON = 152  # GUI panel covers the bottom ~50px

PAL = {
    "night0": (24, 20, 48), "night1": (44, 36, 84), "dusk0": (112, 64, 112),
    "dusk1": (196, 104, 96), "dusk2": (236, 164, 100), "stone0": (92, 84, 92),
    "stone1": (140, 128, 120), "stone2": (184, 168, 148), "plaster": (226, 214, 188),
    "plaster_d": (180, 168, 146), "beam": (40, 28, 24), "brick": (128, 56, 44),
    "brick_d": (90, 40, 34), "road": (56, 56, 64), "road_l": (76, 76, 84),
    "pave": (120, 112, 104), "pave_d": (96, 90, 86), "glass": (60, 72, 96),
    "glow": (250, 210, 120), "glow_d": (200, 140, 60), "wood0": (60, 36, 24),
    "wood1": (96, 60, 36), "wood2": (140, 92, 52), "green": (40, 84, 56),
    "gold": (216, 176, 64), "red": (176, 48, 48), "blue": (56, 88, 160),
    "denim": (52, 64, 100), "skin": (232, 176, 140), "hair": (72, 48, 32),
    "white": (244, 240, 230), "black": (12, 10, 14),
}


def palette_image():
    p = Image.new("P", (1, 1))
    flat = [c for rgb in PAL.values() for c in rgb]
    p.putpalette(flat + [0] * (768 - len(flat)))
    return p


def quantise(img):
    rgb = img.convert("RGB").quantize(palette=palette_image(), dither=Image.Dither.NONE)
    out = rgb.convert("RGBA")
    if img.mode == "RGBA":
        out.putalpha(img.getchannel("A"))
    return out


def dither_gradient(d, x0, y0, x1, y1, c0, c1):
    """Vertical 2-colour ordered-dither gradient."""
    bayer = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0 - 1) * 16
        for x in range(x0, x1):
            d.point((x, y), fill=c1 if bayer[y % 4][x % 4] < t else c0)


def timber_front(d, x, y, w, h, seed):
    r = random.Random(seed)
    d.rectangle([x, y, x + w, y + h], fill=PAL["plaster"])
    d.rectangle([x, y, x + w, y + h], outline=PAL["beam"])
    for bx in range(x, x + w, 12):
        d.line([bx, y, bx, y + h], fill=PAL["beam"], width=2)
    for by in (y + h // 3, y + 2 * h // 3):
        d.line([x, by, x + w, by], fill=PAL["beam"], width=2)
    for bx in range(x, x + w - 12, 24):
        if r.random() < 0.6:
            d.line([bx, y + h // 3, bx + 12, y], fill=PAL["beam"])
    for wx in range(x + 4, x + w - 10, 18):
        d.rectangle([wx, y + 6, wx + 8, y + h // 3 - 6], fill=PAL["glow" if r.random() < .4 else "glass"])
    # gable
    d.polygon([(x - 2, y), (x + w // 2, y - 18), (x + w + 2, y)], fill=PAL["brick_d"])


def church_st():
    img = Image.new("RGB", (W, H), PAL["black"])
    d = ImageDraw.Draw(img)
    dither_gradient(d, 0, 0, W, 40, PAL["night1"], PAL["dusk0"])
    dither_gradient(d, 0, 40, W, 80, PAL["dusk0"], PAL["dusk1"])
    dither_gradient(d, 0, 80, W, 100, PAL["dusk1"], PAL["dusk2"])
    # Abbey tower (Norman, squat, distant) at left
    d.rectangle([20, 22, 64, 100], fill=PAL["stone1"])
    d.rectangle([20, 22, 64, 100], outline=PAL["stone0"])
    for bx in range(20, 66, 6):
        d.rectangle([bx, 16, bx + 3, 22], fill=PAL["stone1"])
    for ty in (32, 50, 68):
        for tx in range(24, 62, 8):
            d.arc([tx, ty, tx + 6, ty + 10], 180, 360, fill=PAL["stone0"])
            d.line([tx, ty + 5, tx, ty + 12], fill=PAL["stone0"])
            d.line([tx + 6, ty + 5, tx + 6, ty + 12], fill=PAL["stone0"])
    d.rectangle([0, 84, 90, 100], fill=PAL["green"])  # Abbey lawn trees
    for tx in range(0, 92, 10):
        d.ellipse([tx, 76, tx + 14, 92], fill=PAL["green"])
    # Street frontage
    timber_front(d, 92, 46, 70, 54, 1)
    # Cross House Tavern (brick, sign, door)
    d.rectangle([166, 40, 252, 100], fill=PAL["brick"])
    for by in range(42, 100, 4):
        off = 0 if (by // 4) % 2 else 4
        for bx in range(166 + off, 252, 8):
            d.point((bx, by), fill=PAL["brick_d"])
    d.polygon([(164, 40), (209, 22), (254, 40)], fill=PAL["stone0"])
    d.rectangle([176, 50, 196, 66], fill=PAL["glow"]); d.rectangle([222, 50, 242, 66], fill=PAL["glow"])
    d.line([186, 50, 186, 66], fill=PAL["beam"]); d.line([232, 50, 232, 66], fill=PAL["beam"])
    d.rectangle([200, 72, 218, 100], fill=PAL["wood0"])  # door
    d.rectangle([202, 74, 216, 98], fill=PAL["wood1"])
    d.point((214, 87), fill=PAL["gold"])
    d.rectangle([176, 72, 196, 92], fill=PAL["glow_d"]); d.rectangle([222, 72, 242, 92], fill=PAL["glow_d"])
    d.line([254, 54, 262, 54], fill=PAL["beam"])  # hanging sign
    d.rectangle([256, 56, 276, 70], fill=PAL["green"], outline=PAL["gold"])
    timber_front(d, 256, 48, 64, 52, 2)
    d.rectangle([256, 56, 276, 70], fill=PAL["green"], outline=PAL["gold"])
    # Pavement + road
    d.rectangle([0, 100, W, 112], fill=PAL["pave"])
    for px in range(0, W, 10):
        d.line([px, 100, px - 4, 112], fill=PAL["pave_d"])
    d.line([0, 112, W, 112], fill=PAL["stone2"])
    d.rectangle([0, 113, W, HORIZON], fill=PAL["road"])
    for px in range(0, W, 24):
        d.rectangle([px, 130, px + 12, 131], fill=PAL["white"])
    # Bench (right of tavern)
    d.rectangle([272, 92, 304, 94], fill=PAL["wood2"])
    d.rectangle([272, 86, 304, 88], fill=PAL["wood1"])
    d.line([274, 94, 274, 101], fill=PAL["black"]); d.line([302, 94, 302, 101], fill=PAL["black"])
    d.point((288, 101), fill=PAL["gold"])  # the coin under the bench
    # Lamp post
    d.line([150, 60, 150, 104], fill=PAL["black"], width=2)
    d.rectangle([146, 54, 154, 60], fill=PAL["glow"])
    return quantise(img)


def tavern():
    img = Image.new("RGB", (W, H), PAL["black"])
    d = ImageDraw.Draw(img)
    # Panelled walls
    d.rectangle([0, 0, W, 96], fill=PAL["wood1"])
    for px in range(0, W, 32):
        d.rectangle([px + 2, 40, px + 30, 92], outline=PAL["wood0"])
    d.rectangle([0, 0, W, 38], fill=PAL["plaster_d"])
    for bx in range(0, W, 40):
        d.rectangle([bx, 0, bx + 4, 38], fill=PAL["beam"])
    d.rectangle([0, 0, W, 4], fill=PAL["beam"])
    # Back bar shelves + bottles
    d.rectangle([100, 14, 230, 16], fill=PAL["wood2"]); d.rectangle([100, 28, 230, 30], fill=PAL["wood2"])
    r = random.Random(3)
    for bx in range(104, 228, 6):
        for sy in (8, 22):
            d.rectangle([bx, sy, bx + 3, sy + 6], fill=PAL[r.choice(["green", "red", "gold", "glass"])])
    # Bar counter
    d.rectangle([90, 70, 240, 74], fill=PAL["wood2"])
    d.rectangle([92, 74, 238, 104], fill=PAL["wood0"])
    for px in range(96, 236, 20):
        d.rectangle([px, 78, px + 16, 100], outline=PAL["wood1"])
    for hx in (130, 150, 170, 190):  # hand pumps
        d.rectangle([hx, 58, hx + 2, 70], fill=PAL["black"])
        d.rectangle([hx - 1, 54, hx + 3, 58], fill=PAL["white"])
    # Quiz machine (left)
    d.rectangle([20, 44, 54, 104], fill=PAL["blue"], outline=PAL["black"])
    d.rectangle([24, 50, 50, 70], fill=PAL["night0"])
    for ly in range(53, 68, 4):
        d.line([27, ly, 47, ly], fill=PAL["glow"])
    d.rectangle([24, 74, 50, 78], fill=PAL["gold"])
    for bx in (25, 33, 41):
        d.rectangle([bx, 84, bx + 6, 88], fill=PAL["red"])
    d.text((25, 92), "QUIZ", fill=PAL["white"])
    # Exit door (right)
    d.rectangle([272, 34, 304, 104], fill=PAL["beam"])
    d.rectangle([275, 37, 301, 104], fill=PAL["wood2"])
    d.rectangle([279, 42, 297, 58], fill=PAL["dusk1"])
    d.point((298, 76), fill=PAL["gold"])
    # Floorboards
    d.rectangle([0, 104, W, HORIZON], fill=PAL["wood2"])
    for fy in range(104, HORIZON, 6):
        d.line([0, fy, W, fy], fill=PAL["wood1"])
    for fx in range(0, W, 28):
        d.line([fx, 104, fx - 30, HORIZON], fill=PAL["wood1"])
    return quantise(img)


def person(shirt, legs, hair, apron=False, beard=False, tall=40):
    img = Image.new("RGBA", (16, tall), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([5, 0, 10, 2], fill=PAL[hair])
    d.rectangle([5, 2, 10, 8], fill=PAL["skin"])
    d.point((9, 4), fill=PAL["black"])
    if beard:
        d.rectangle([5, 6, 10, 9], fill=PAL[hair])
    d.rectangle([3, 9, 12, 23], fill=PAL[shirt])
    d.rectangle([1, 10, 2, 21], fill=PAL[shirt]); d.rectangle([13, 10, 14, 21], fill=PAL[shirt])
    d.point((1, 22), fill=PAL["skin"]); d.point((14, 22), fill=PAL["skin"])
    if apron:
        d.rectangle([4, 14, 11, 28], fill=PAL["white"])
    d.rectangle([4, 24, 7, tall - 3], fill=PAL[legs]); d.rectangle([8, 24, 11, tall - 3], fill=PAL[legs])
    d.rectangle([3, tall - 2, 7, tall - 1], fill=PAL["black"]); d.rectangle([8, tall - 2, 12, tall - 1], fill=PAL["black"])
    return quantise(img)


def icon(kind):
    img = Image.new("RGBA", (24, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if kind == "coin":
        d.ellipse([7, 3, 16, 12], fill=PAL["gold"], outline=PAL["glow_d"])
        d.text((9, 2), "1", fill=PAL["glow_d"])
    elif kind == "pint":
        d.rectangle([8, 2, 15, 14], fill=PAL["glow_d"], outline=PAL["white"])
        d.rectangle([8, 2, 15, 4], fill=PAL["white"])
        d.rectangle([16, 5, 18, 10], outline=PAL["white"])
    elif kind == "crawl_card":
        d.rectangle([3, 2, 20, 13], fill=PAL["white"], outline=PAL["beam"])
        for cx in range(5, 19, 5):
            d.rectangle([cx, 7, cx + 3, 10], outline=PAL["red"])
        d.line([5, 4, 18, 4], fill=PAL["beam"])
    return quantise(img)


def save(img, rel):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    img.save(p)
    print("wrote", rel)


if __name__ == "__main__":
    save(church_st(), "game/rooms/church_st/props/bg_church_st.png")
    save(tavern(), "game/rooms/cross_house_tavern/props/bg_cross_house_tavern.png")
    save(person("blue", "denim", "hair"), "game/characters/paul/paul.png")
    save(person("red", "beam", "stone0", apron=True, beard=True), "game/characters/landlord/landlord.png")
    for k in ("coin", "pint", "crawl_card"):
        save(icon(k), f"game/inventory_items/{k}/{k}.png")
