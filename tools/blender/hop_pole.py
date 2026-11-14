"""Inside the Royal Hop Pole — Paul's Pub Crawl room background.

    /Applications/Blender.app/Contents/MacOS/Blender -b -P tools/blender/hop_pole.py

Georgian coaching-inn bar: green panelling, red carpet, bar on the left, fireplace with a
portrait of a (fictional) founder, and a skittle alley running back through an archway.
Writes art/renders/hop_pole.png + .json (hotspots in 320x200 game px).
"""
import json
import math
import os
import random
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

sys.path.insert(0, os.path.dirname(__file__))
import scene_kit as K  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "art", "renders")
os.makedirs(OUT, exist_ok=True)
rng = random.Random(9)

K.reset_scene()
K.world_sky(top=(0.0, 0.0, 0.0), mid=(0.0, 0.0, 0.0), horizon=(0.0, 0.0, 0.0), strength=0.0)

M = {
    "wall": K.mat("wall", (0.16, 0.30, 0.22), noise=0.15, scale=3),            # Georgian green
    "panel": K.mat("panel", (0.20, 0.10, 0.05), noise=0.25, scale=14, rough=0.4),
    "trim": K.mat("trim", (0.80, 0.76, 0.66), noise=0.05),                      # painted mouldings
    "gilt": K.mat("gilt", (0.85, 0.62, 0.20), rough=0.3, noise=0.15, scale=20),
    "beam": K.mat("beam", (0.10, 0.06, 0.04), noise=0.3, scale=18),
    "ceiling": K.mat("ceiling", (0.80, 0.74, 0.62), noise=0.1, scale=3),
    "bar_top": K.mat("bar_top", (0.30, 0.15, 0.06), noise=0.2, scale=20, rough=0.25),
    "brass": K.mat("brass", (0.9, 0.65, 0.25), rough=0.25, noise=0.05),
    "pump": K.mat("pump", (0.92, 0.88, 0.80), rough=0.3, noise=0.05),
    "mirror": K.mat("mirror", (0.30, 0.28, 0.25), rough=0.05, noise=0.05),
    "stone": K.mat("stone", (0.70, 0.66, 0.58), noise=0.2, scale=4, bump=0.5),
    "soot": K.mat("soot", (0.05, 0.04, 0.04), noise=0.2),
    "fire": K.glow_mat("fire", (1.0, 0.42, 0.06), 4.0),
    "embers": K.glow_mat("embers", (1.0, 0.2, 0.02), 3.0),
    "canvas": K.mat("canvas", (0.12, 0.09, 0.06), noise=0.3, scale=6),
    "coat": K.mat("coat", (0.35, 0.08, 0.06), noise=0.2, scale=8),
    "face": K.mat("face", (0.75, 0.55, 0.42), noise=0.1),
    "wig": K.mat("wig", (0.82, 0.80, 0.76), noise=0.2, scale=10),
    "door": K.mat("door", (0.28, 0.06, 0.07), noise=0.2, scale=12),
    "alley": K.mat("alley", (0.55, 0.36, 0.17), noise=0.25, scale=6, rough=0.3),
    "cushion": K.mat("cushion", (0.18, 0.08, 0.04), noise=0.2, scale=10),
    "pin": K.mat("pin", (0.92, 0.88, 0.80), rough=0.3, noise=0.05),
    "pin_band": K.mat("pin_band", (0.7, 0.10, 0.08), noise=0.05),
    "ball": K.mat("ball", (0.12, 0.07, 0.04), rough=0.3, noise=0.1),
    "lamp_glow": K.glow_mat("lamp_glow", (1.0, 0.70, 0.35), 2.5),
    "candle": K.glow_mat("candle", (1.0, 0.8, 0.45), 4.0),
    "table": K.mat("table", (0.22, 0.10, 0.04), noise=0.2, scale=16, rough=0.4),
    "chair": K.mat("chair", (0.30, 0.08, 0.06), noise=0.2, scale=12),
    "chalk": K.mat("chalk", (0.06, 0.08, 0.07), noise=0.2),
    "chalk_text": K.mat("chalk_text", (0.85, 0.85, 0.8), noise=0.1, emission=(0.6, 0.6, 0.55), estrength=0.4),
}
bottle_cols = [(0.05, 0.25, 0.08), (0.35, 0.18, 0.04), (0.5, 0.05, 0.05), (0.7, 0.6, 0.2), (0.15, 0.2, 0.4)]
BOTTLES = [K.mat(f"bottle{i}", c, rough=0.1, noise=0.05, emission=c, estrength=0.6) for i, c in enumerate(bottle_cols)]
CARPET = K.brick_mat("carpet", brick=(0.42, 0.07, 0.07), mortar=(0.55, 0.40, 0.12), scale=2.2, vertical=False,
                     brick_width=0.5, row_height=0.5)

hot = {}


def tag(name, *objs):
    hot.setdefault(name, []).extend(objs)


W, H = 17.0, 3.4
BACK = 5.0

# --------------------------------------------------------------- shell ----
K.box("floor", (W + 2, 11, 0.05), (0, 0.5, -0.05), CARPET)
# Back wall is built in pieces around the skittle-alley archway (x = ARCH_X0..ARCH_X1, up to 2.6m).
# Wide enough that the camera (at x=0) can see past the left pier to the pins at the back.
ARCH_X0, ARCH_X1, ARCH_TOP = 2.9, 8.4, 2.6


def wall_run(name, x0, x1, z0, z1, mat, y=BACK + 0.1, depth=0.2):
    K.box(name, (x1 - x0, depth, z1 - z0), ((x0 + x1) / 2, y, z0), mat)


wall_run("back_wall_l", -W / 2, ARCH_X0, 0, H, M["wall"])
wall_run("back_wall_r", ARCH_X1, W / 2, 0, H, M["wall"])
wall_run("back_wall_top", ARCH_X0, ARCH_X1, ARCH_TOP, H, M["wall"])
K.box("left_wall", (0.2, 4, H), (-W / 2 - 0.1, 3.0, 0), M["wall"])
K.box("right_wall", (0.2, 4, H), (W / 2 + 0.1, 3.0, 0), M["wall"])
K.box("ceiling", (W + 1, 2.5, 0.1), (0, BACK - 1.0, H), M["ceiling"])
for (x0, x1) in ((-W / 2, ARCH_X0), (ARCH_X1, W / 2)):
    wall_run("dado", x0, x1, 0, 1.0, M["panel"], y=BACK - 0.02, depth=0.08)
    wall_run("dado_rail", x0, x1, 1.0, 1.07, M["trim"], y=BACK - 0.05, depth=0.14)
    x = x0 + 0.4
    while x < x1 - 0.2:
        K.box("dado_stile", (0.05, 0.1, 1.0), (x, BACK - 0.06, 0), M["trim"])
        x += 0.78
K.box("cornice", (W, 0.3, 0.25), (0, BACK - 0.1, H - 0.25), M["trim"])
# ceiling beams across the cutaway's top edge
K.box("front_beam", (W + 2, 0.5, 0.9), (0, -3.0, 3.85), M["beam"])

# ---------------------------------------------------------------- bar ----
bx0, bw = -5.0, 5.2
bar_y = 2.4
counter = K.box("bar_front", (bw, 0.7, 1.05), (bx0, bar_y, 0), M["panel"])
K.box("bar_top", (bw + 0.2, 0.9, 0.08), (bx0, bar_y, 1.05), M["bar_top"])
K.box("foot_rail", (bw, 0.06, 0.06), (bx0, bar_y - 0.45, 0.2), M["brass"])
for i in range(7):
    K.box("bar_panel", (0.05, 0.05, 0.85), (bx0 - bw / 2 + 0.35 + i * 0.75, bar_y - 0.37, 0.1), M["trim"])
for i in range(5):
    px = bx0 - 1.5 + i * 0.7
    K.cyl("pump_base", 0.06, 0.12, (px, bar_y - 0.15, 1.13), M["brass"], verts=10)
    K.cyl("pump_handle", 0.045, 0.5, (px, bar_y - 0.15, 1.25), M["pump"], verts=10)
    K.box("pump_clip", (0.14, 0.03, 0.1), (px, bar_y - 0.2, 1.55), K.mat(f"clip{i}", rng.choice(bottle_cols)))
K.box("back_bar", (bw, 0.5, 1.0), (bx0, BACK - 0.3, 0), M["panel"])
K.box("bar_mirror", (bw - 0.6, 0.05, 1.1), (bx0, BACK - 0.03, 1.15), M["mirror"])
K.box("bar_mirror_frame", (bw - 0.4, 0.06, 0.1), (bx0, BACK - 0.05, 2.25), M["gilt"])
for sz in (1.35, 1.85):
    K.box("shelf", (bw - 0.4, 0.3, 0.05), (bx0, BACK - 0.2, sz), M["bar_top"])
    x = bx0 - bw / 2 + 0.4
    while x < bx0 + bw / 2 - 0.4:
        h = rng.uniform(0.22, 0.34)
        K.cyl("bottle", 0.05, h, (x, BACK - 0.2, sz + 0.05), rng.choice(BOTTLES), verts=8)
        x += rng.uniform(0.13, 0.2)
K.point_light("bar_light", (bx0, bar_y + 0.6, 2.8), (1.0, 0.72, 0.42), 150, radius=0.6)
tag("Bar", counter)

# ----------------------------------------------------------- exit door ----
ex = -1.3
door = K.box("exit_door", (1.1, 0.12, 2.25), (ex, BACK - 0.05, 0), M["door"])
K.box("exit_fanlight", (1.1, 0.12, 0.35), (ex, BACK - 0.06, 2.3), K.glow_mat("fan", (0.35, 0.45, 0.8), 0.7))
K.box("exit_architrave", (1.4, 0.16, 0.15), (ex, BACK - 0.08, 2.68), M["trim"])
for side in (-0.62, 0.62):
    K.box("exit_post", (0.12, 0.16, 2.7), (ex + side, BACK - 0.08, 0), M["trim"])
tag("ExitDoor", door)

# --------------------------------------------- fireplace and portrait ----
fx = 1.6
K.box("mantel_surround", (2.2, 0.5, 1.4), (fx, BACK - 0.25, 0), M["stone"])
K.box("firebox", (1.2, 0.35, 0.9), (fx, BACK - 0.4, 0.05), M["soot"])
K.box("mantel_shelf", (2.6, 0.55, 0.12), (fx, BACK - 0.45, 1.4), M["stone"])
K.box("flames", (0.7, 0.12, 0.38), (fx, BACK - 0.62, 0.15), M["fire"])
K.box("embers", (0.9, 0.25, 0.06), (fx, BACK - 0.55, 0.06), M["embers"])
K.point_light("fire_light", (fx, BACK - 1.3, 0.5), (1.0, 0.42, 0.10), 160, radius=0.5)
for i, cx in enumerate((-0.9, 0.9)):  # candlesticks on the mantel
    K.cyl("candlestick", 0.05, 0.3, (fx + cx, BACK - 0.45, 1.52), M["brass"], verts=8)
    K.box("candle_flame", (0.05, 0.05, 0.08), (fx + cx, BACK - 0.45, 1.84), M["candle"])
# portrait: gilt frame, a red-coated gentleman in a white wig (fictional founder)
pf = K.box("portrait_frame", (1.5, 0.1, 1.25), (fx, BACK - 0.08, 1.75), M["gilt"])
K.box("portrait_canvas", (1.25, 0.1, 1.0), (fx, BACK - 0.12, 1.87), M["canvas"])
K.box("portrait_coat", (0.7, 0.08, 0.45), (fx, BACK - 0.16, 1.87), M["coat"])
K.cyl("portrait_face", 0.14, 0.08, (fx, BACK - 0.17, 2.42), M["face"], verts=12).rotation_euler = (1.5708, 0, 0)
K.box("portrait_wig", (0.38, 0.08, 0.22), (fx, BACK - 0.16, 2.48), M["wig"])
K.point_light("portrait_lamp", (fx, BACK - 0.8, 3.0), (1.0, 0.8, 0.55), 30, radius=0.2)
tag("Portrait", pf)

# ------------------------------------------------------- skittle alley ----
# An archway in the back wall; the alley runs back to y=19 with nine pins in a diamond.
ax, aw = 5.6, 2.0
K.box("arch_left", (0.3, 0.4, ARCH_TOP), (ARCH_X0 - 0.15, BACK, 0), M["trim"])
K.box("arch_right", (0.3, 0.4, ARCH_TOP), (ARCH_X1 + 0.15, BACK, 0), M["trim"])
K.box("arch_lintel", (ARCH_X1 - ARCH_X0 + 0.6, 0.45, 0.35), (ax, BACK, ARCH_TOP - 0.1), M["trim"])
K.box("alley_wall_l", (0.15, 9, 2.6), (ARCH_X0, BACK + 4.5, 0), M["wall"])
K.box("alley_room_floor", (ARCH_X1 - ARCH_X0, 9, 0.04), ((ARCH_X0 + ARCH_X1) / 2, BACK + 4.5, -0.02), M["panel"])
K.box("alley_dado", (0.08, 9, 1.0), (ARCH_X1 - 0.1, BACK + 4.5, 0), M["panel"])
K.box("alley_wall_r", (0.15, 9, 2.6), (ARCH_X1, BACK + 4.5, 0), M["wall"])
K.box("alley_ceiling", (ARCH_X1 - ARCH_X0 + 0.4, 9, 0.1), ((ARCH_X0 + ARCH_X1) / 2, BACK + 4.5, 2.6), M["ceiling"])
alley = K.box("alley_floor", (aw, 10, 0.06), (ax, BACK + 4.0, 0.0), M["alley"])
for side in (-1, 1):
    K.box("alley_cushion", (0.25, 10, 0.18), (ax + side * (aw / 2 + 0.12), BACK + 4.0, 0.0), M["cushion"])
K.box("alley_back", (ARCH_X1 - ARCH_X0, 0.2, 2.6), ((ARCH_X0 + ARCH_X1) / 2, BACK + 9.0, 0), M["wall"])
K.box("alley_backstop", (aw + 0.7, 0.25, 1.1), (ax, BACK + 8.8, 0), M["panel"])
pin_objs = []
pin_y0 = BACK + 6.6
spacing = 0.5
for r, cols in enumerate((1, 2, 3, 2, 1)):  # diamond: rows of 1,2,3,2,1 pins
    for cidx in range(cols):
        px = ax + (cidx - (cols - 1) / 2) * spacing
        py = pin_y0 + r * spacing * 0.75
        p = K.cyl("pin", 0.09, 0.48, (px, py, 0.06), M["pin"], verts=10)
        K.cyl("pin_band", 0.095, 0.06, (px, py, 0.40), M["pin_band"], verts=10)
        pin_objs.append(p)
K.point_light("alley_light", (ax, pin_y0 + 0.4, 2.3), (1.0, 0.85, 0.55), 450, radius=0.4)
K.point_light("alley_mid", (ax, BACK + 2.5, 2.3), (1.0, 0.75, 0.45), 180, radius=0.4)
for i in range(3):  # wooden "cheeses" (skittle balls) in a rack by the arch
    K.cyl("ball", 0.12, 0.12, (ax - aw / 2 - 1.1 + i * 0.28, BACK - 0.6, 0.55), M["ball"], verts=14)
K.box("ball_rack", (1.0, 0.4, 0.55), (ax - aw / 2 - 0.82, BACK - 0.6, 0), M["panel"])
# scoreboard chalkboard on the arch pier
K.box("scoreboard", (0.9, 0.06, 0.7), (ARCH_X1 + 0.9, BACK - 0.12, 1.4), M["chalk"])
for i in range(3):
    K.box("score_line", (0.6, 0.05, 0.04), (ARCH_X1 + 0.9, BACK - 0.16, 1.55 + i * 0.15), M["chalk_text"])
tag("SkittleAlley", alley, *pin_objs)

# ---------------------------------------------------- tables & chairs ----
for tx, ty in ((-1.6, 1.0), (2.4, 0.4)):
    K.cyl("table_top", 0.5, 0.05, (tx, ty, 0.72), M["table"], verts=16)
    K.cyl("table_leg", 0.06, 0.72, (tx, ty, 0), M["table"], verts=8)
    for a in (0, math.pi):
        cx, cy = tx + math.cos(a) * 0.75, ty + math.sin(a) * 0.3
        K.box("chair_seat", (0.45, 0.45, 0.06), (cx, cy, 0.45), M["chair"])
        K.box("chair_back", (0.06 if a == 0 else 0.06, 0.45, 0.5), (cx + (0.2 if a == 0 else -0.2), cy, 0.5), M["chair"])
        for lx in (-0.18, 0.18):
            K.box("chair_leg", (0.04, 0.04, 0.45), (cx + lx, cy, 0), M["chair"])
    K.cyl("candle_jar", 0.06, 0.1, (tx, ty, 0.77), M["candle"], verts=8)

# ---------------------------------------------------------- lighting ----
for lx in (-4.5, 0.2):
    K.box("chandelier_chain", (0.02, 0.02, 0.5), (lx, 2.4, H - 0.5), M["brass"])
    K.box("chandelier", (0.6, 0.6, 0.18), (lx, 2.4, H - 0.75), M["gilt"])
    for k in range(5):
        a = k / 5 * 2 * math.pi
        K.box("chandelier_candle", (0.05, 0.05, 0.1), (lx + math.cos(a) * 0.3, 2.4 + math.sin(a) * 0.3, H - 0.62), M["candle"])
    K.point_light("chandelier_light", (lx, 2.2, H - 0.9), (1.0, 0.70, 0.40), 110, radius=0.4)
for sx in (-7.5, 2.4, 9.2):
    K.box("sconce", (0.15, 0.1, 0.25), (sx, BACK - 0.1, 1.9), M["lamp_glow"])
    K.point_light("sconce_light", (sx, BACK - 0.5, 1.9), (1.0, 0.7, 0.4), 35, radius=0.2)
K.point_light("fill", (0, -4, 3.0), (0.45, 0.55, 0.9), 240, radius=3.0)

# ------------------------------------------------------------- camera ----
cam = K.camera((0.0, -11.0, 4.0), (0.0, 0.0, 4.0), lens=35)
cam.data.shift_y = -0.2375

scn = bpy.context.scene
scn.render.filepath = os.path.join(OUT, "hop_pole.png")
bpy.ops.render.render(write_still=True)


def to_px(world):
    co = world_to_camera_view(scn, cam, Vector(world))
    return (co.x * 320.0, (1.0 - co.y) * 200.0)


def rect_of(objs, pad=1):
    xs, ys = [], []
    for o in objs:
        for c in o.bound_box:
            x, y = to_px(o.matrix_world @ Vector(c))
            xs.append(x)
            ys.append(y)
    return [max(0, int(min(xs)) - pad), max(0, int(min(ys)) - pad),
            min(320, int(max(xs)) + pad), min(150, int(max(ys)) + pad)]


GUI_TOP = 150
fl = [(-8.0, 1.7), (8.0, 1.7), (8.0, -1.2), (-8.0, -1.2)]
floor = [to_px((x, y, 0)) for x, y in fl]
floor = [(min(316, max(4, x)), min(GUI_TOP - 2, y)) for x, y in floor]
data = {
    "hotspots": {k: rect_of(v) for k, v in hot.items()},
    "walk_points": {
        "Bar": to_px((bx0 + 0.8, 1.4, 0)),
        "ExitDoor": to_px((ex, 1.6, 0)),
        "Portrait": to_px((fx, 1.6, 0)),
        "SkittleAlley": to_px((ax, 1.6, 0)),
        "Barmaid": to_px((bx0 + 0.5, 1.4, 0)),
        "Reg": to_px((ax - 2.0, 0.9, 0)),
    },
    "npc": {
        "Barmaid": to_px((bx0 + 0.3, bar_y + 0.9, 0)),
        "Reg": to_px((ax - 0.9, 1.4, 0)),
    },
    "spawn": {"from_street": to_px((ex, 1.4, 0))},
    "floor": [list(p) for p in floor],
    "person_px": to_px((0, 1.2, 0))[1] - to_px((0, 1.2, 1.8))[1],
}
with open(os.path.join(OUT, "hop_pole.json"), "w") as f:
    json.dump(data, f, indent=1)
print("[blender] wrote", scn.render.filepath, json.dumps(data))
