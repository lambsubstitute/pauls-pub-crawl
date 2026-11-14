"""Inside the Cross House Tavern — Paul's Pub Crawl room background.

    /Applications/Blender.app/Contents/MacOS/Blender -b -P tools/blender/cross_house_tavern.py

Writes art/renders/cross_house_tavern.png + .json (hotspots in 320x200 game px).
"""
import json
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
rng = random.Random(5)

K.reset_scene()
K.world_sky(top=(0.0, 0.0, 0.0), mid=(0.0, 0.0, 0.0), horizon=(0.0, 0.0, 0.0), strength=0.0)

M = {
    "plaster": K.mat("plaster", (0.72, 0.62, 0.45), noise=0.2, scale=3),
    "beam": K.mat("beam", (0.08, 0.05, 0.03), noise=0.3, scale=18),
    "panel": K.mat("panel", (0.28, 0.14, 0.06), noise=0.25, scale=14, rough=0.5),
    "panel_trim": K.mat("panel_trim", (0.20, 0.10, 0.04), noise=0.2, scale=14, rough=0.5),
    "bar_top": K.mat("bar_top", (0.35, 0.18, 0.07), noise=0.2, scale=20, rough=0.25),
    "brass": K.mat("brass", (0.9, 0.65, 0.25), rough=0.25, noise=0.05),
    "pump": K.mat("pump", (0.9, 0.85, 0.75), rough=0.3, noise=0.05),
    "stone": K.mat("stone", (0.45, 0.40, 0.34), noise=0.3, scale=4, bump=0.8),
    "soot": K.mat("soot", (0.05, 0.04, 0.04), noise=0.2),
    "fire": K.glow_mat("fire", (1.0, 0.42, 0.06), 4.0),
    "embers": K.glow_mat("embers", (1.0, 0.2, 0.02), 3.0),
    "quiz_body": K.mat("quiz_body", (0.10, 0.18, 0.55), rough=0.35, noise=0.1),
    "quiz_screen": K.glow_mat("quiz_screen", (0.15, 0.45, 1.0), 2.0),
    "quiz_lights": K.glow_mat("quiz_lights", (1.0, 0.25, 0.5), 2.0),
    "quiz_gold": K.glow_mat("quiz_gold", (1.0, 0.75, 0.15), 1.5),
    "door": K.mat("door", (0.22, 0.12, 0.05), noise=0.25, scale=12),
    "glass_door": K.glow_mat("glass_door", (0.25, 0.35, 0.7), 0.6),
    "table": K.mat("table", (0.25, 0.12, 0.05), noise=0.2, scale=16, rough=0.4),
    "stool": K.mat("stool", (0.30, 0.15, 0.06), noise=0.2, scale=16),
    "dart_board": K.mat("dart_board", (0.08, 0.08, 0.06), noise=0.1),
    "dart_ring": K.mat("dart_ring", (0.7, 0.1, 0.08), noise=0.1),
    "dart_green": K.mat("dart_green", (0.05, 0.4, 0.15), noise=0.1),
    "lamp_glow": K.glow_mat("lamp_glow", (1.0, 0.65, 0.3), 2.5),
    "mirror": K.mat("mirror", (0.25, 0.22, 0.2), rough=0.05, noise=0.05),
    "red_rug": K.mat("red_rug", (0.35, 0.06, 0.05), noise=0.3, scale=12),
}
bottle_cols = [(0.05, 0.25, 0.08), (0.35, 0.18, 0.04), (0.5, 0.05, 0.05), (0.7, 0.6, 0.2), (0.15, 0.2, 0.4)]
BOTTLES = [K.mat(f"bottle{i}", c, rough=0.1, noise=0.05, emission=c, estrength=0.6) for i, c in enumerate(bottle_cols)]
FLOOR = K.brick_mat("boards", brick=(0.30, 0.16, 0.07), mortar=(0.08, 0.04, 0.02), scale=1.0, vertical=False,
                    brick_width=2.4, row_height=0.16)

hot = {}


def tag(name, *objs):
    hot.setdefault(name, []).extend(objs)


W, D, H = 17.0, 9.0, 3.3  # room x -8.5..8.5, y -4..5, floor..ceiling (cutaway: no front wall)
BACK = 5.0

# --------------------------------------------------------------- shell ----
K.box("floor", (W + 2, D + 2, 0.05), (0, 0.5, -0.05), FLOOR)
K.box("back_wall", (W, 0.2, H), (0, BACK + 0.1, 0), M["plaster"])
K.box("left_wall", (0.2, 4, H), (-W / 2 - 0.1, 3.0, 0), M["plaster"])
K.box("right_wall", (0.2, 4, H), (W / 2 + 0.1, 3.0, 0), M["plaster"])
K.box("ceiling", (W + 1, 2.5, 0.1), (0, BACK - 1.0, H), M["plaster"])  # only the back strip; camera looks in from outside
# wainscot panelling along back + side walls
K.box("wainscot_back", (W, 0.08, 1.15), (0, BACK - 0.02, 0), M["panel"])
K.box("wainscot_rail", (W, 0.14, 0.08), (0, BACK - 0.05, 1.15), M["panel_trim"])
for i in range(21):
    K.box("panel_stile", (0.06, 0.1, 1.15), (-W / 2 + 0.4 + i * 0.8, BACK - 0.06, 0), M["panel_trim"])
for side in (-1, 1):
    K.box("wainscot_side", (0.08, D, 1.15), (side * (W / 2 - 0.02), 0.5, 0), M["panel"])
# ceiling beams + wall posts
for i in range(3):
    K.box("ceiling_beam", (W, 0.28, 0.3), (0, BACK - 0.4 - i * 1.6, H - 0.3), M["beam"])
for x in (-6.0, -2.0, 2.0, 6.0):
    K.box("cross_beam", (0.28, 3.4, 0.3), (x, BACK - 1.6, H - 0.3), M["beam"])
for x in (-7.2, -4.4, -0.2, 5.2, 7.8):
    K.box("wall_post", (0.25, 0.2, H), (x, BACK - 0.05, 0), M["beam"])
K.box("wall_plate", (W, 0.2, 0.22), (0, BACK - 0.05, 2.15), M["beam"])

# ---------------------------------------------------------- fireplace ----
fx = -5.6
K.box("hearth_surround", (2.2, 0.6, 2.0), (fx, BACK - 0.3, 0), M["stone"])
K.box("firebox", (1.3, 0.4, 1.1), (fx, BACK - 0.45, 0.08), M["soot"])
K.box("mantel", (2.6, 0.5, 0.18), (fx, BACK - 0.55, 2.0), M["beam"])
K.box("chimney_breast", (2.0, 0.4, 1.1), (fx, BACK - 0.2, 2.18), M["plaster"])
for i in range(5):
    K.box("log", (0.9, 0.18, 0.18), (fx + rng.uniform(-0.2, 0.2), BACK - 0.55, 0.1 + i * 0.05), M["beam"],
          rot=(0, 0, rng.uniform(-0.3, 0.3)))
K.box("flames", (0.8, 0.12, 0.45), (fx, BACK - 0.7, 0.25), M["fire"])
K.box("embers", (1.0, 0.25, 0.08), (fx, BACK - 0.6, 0.08), M["embers"])
K.point_light("fire_light", (fx, BACK - 1.3, 0.6), (1.0, 0.42, 0.10), 220, radius=0.5)
for i, c in enumerate(((0.9, 0.65, 0.25), (0.5, 0.5, 0.55), (0.9, 0.65, 0.25))):  # mantel ornaments
    K.cyl("ornament", 0.08, 0.3, (fx - 0.7 + i * 0.7, BACK - 0.55, 2.18), K.mat(f"orn{i}", c, rough=0.3), verts=10)
# dartboard on the back wall by the fire
db_x = -3.2
board = K.cyl("dartboard", 0.32, 0.06, (db_x, BACK - 0.05, 1.55), M["dart_board"], verts=24)
board.rotation_euler = (1.5708, 0, 0)
board.location.z = 1.75
ring = K.cyl("dart_ring", 0.22, 0.07, (db_x, BACK - 0.07, 1.75), M["dart_ring"], verts=24)
ring.rotation_euler = (1.5708, 0, 0)
bull = K.cyl("dart_bull", 0.05, 0.08, (db_x, BACK - 0.09, 1.75), M["dart_green"], verts=12)
bull.rotation_euler = (1.5708, 0, 0)
tag("Dartboard", board)

# ---------------------------------------------------------------- bar ----
bx0, bw = 2.4, 5.6
bar_y = 2.6
counter = K.box("bar_front", (bw, 0.7, 1.05), (bx0, bar_y, 0), M["panel"])
K.box("bar_top", (bw + 0.2, 0.9, 0.08), (bx0, bar_y, 1.05), M["bar_top"])
K.box("foot_rail", (bw, 0.06, 0.06), (bx0, bar_y - 0.45, 0.2), M["brass"])
for i in range(7):
    K.box("bar_panel", (0.05, 0.05, 0.85), (bx0 - bw / 2 + 0.35 + i * 0.75, bar_y - 0.37, 0.1), M["panel_trim"])
for i in range(4):  # hand pumps
    px = bx0 - 1.2 + i * 0.75
    K.cyl("pump_base", 0.06, 0.12, (px, bar_y - 0.15, 1.13), M["brass"], verts=10)
    K.cyl("pump_handle", 0.045, 0.5, (px, bar_y - 0.15, 1.25), M["pump"], verts=10)
    K.box("pump_clip", (0.14, 0.03, 0.1), (px, bar_y - 0.2, 1.55), K.mat(f"clip{i}", rng.choice(bottle_cols)))
# back bar: mirror + shelves of bottles
K.box("back_bar", (bw, 0.5, 1.0), (bx0, BACK - 0.3, 0), M["panel"])
K.box("mirror", (bw - 0.6, 0.05, 1.0), (bx0, BACK - 0.03, 1.2), M["mirror"])
for sz in (1.35, 1.85):
    K.box("shelf", (bw - 0.4, 0.3, 0.05), (bx0, BACK - 0.2, sz), M["bar_top"])
    x = bx0 - bw / 2 + 0.4
    while x < bx0 + bw / 2 - 0.4:
        h = rng.uniform(0.22, 0.34)
        K.cyl("bottle", 0.05, h, (x, BACK - 0.2, sz + 0.05), rng.choice(BOTTLES), verts=8)
        x += rng.uniform(0.13, 0.2)
K.point_light("bar_light", (bx0, bar_y + 0.6, 2.7), (1.0, 0.72, 0.42), 160, radius=0.6)
tag("Bar", counter)

# --------------------------------------------------------- quiz machine ----
qx = -1.4
quiz = K.box("quiz_cabinet", (0.9, 0.7, 1.9), (qx, 3.6, 0), M["quiz_body"])
K.box("quiz_screen", (0.65, 0.05, 0.5), (qx, 3.23, 1.15), M["quiz_screen"])
K.box("quiz_marquee", (0.8, 0.06, 0.22), (qx, 3.23, 1.72), M["quiz_gold"])
for i in range(3):
    K.box("quiz_btn", (0.12, 0.06, 0.08), (qx - 0.22 + i * 0.22, 3.2, 0.95), M["quiz_lights"])
K.box("quiz_coin", (0.1, 0.05, 0.14), (qx + 0.3, 3.22, 0.65), M["brass"])
K.point_light("quiz_glow", (qx, 2.6, 1.3), (0.3, 0.5, 1.0), 15, radius=0.3)
tag("QuizMachine", quiz)

# ----------------------------------------------------------- exit door ----
ex = 6.6
door = K.box("exit_door", (1.1, 0.12, 2.2), (ex, BACK - 0.05, 0), M["door"])
K.box("exit_glass", (0.6, 0.13, 0.6), (ex, BACK - 0.06, 1.3), M["glass_door"])
K.box("exit_frame", (1.35, 0.16, 0.15), (ex, BACK - 0.08, 2.2), M["beam"])
K.box("exit_sign", (0.5, 0.05, 0.18), (ex, BACK - 0.1, 2.45), K.glow_mat("exit_sign", (0.2, 0.9, 0.3), 1.5))
tag("ExitDoor", door)

# ---------------------------------------------------- tables & stools ----
for tx, ty in ((-5.0, 1.0), (-1.2, 0.2), (6.2, 1.2)):
    K.box("table_top", (1.2, 0.8, 0.06), (tx, ty, 0.72), M["table"])
    K.cyl("table_leg", 0.06, 0.72, (tx, ty, 0), M["table"], verts=8)
    for sx in (-0.8, 0.8):
        K.cyl("stool", 0.2, 0.05, (tx + sx, ty, 0.45), M["stool"], verts=12)
        K.cyl("stool_leg", 0.035, 0.45, (tx + sx, ty, 0), M["stool"], verts=6)
    K.cyl("pint_glass", 0.05, 0.16, (tx + 0.2, ty, 0.78), K.mat("ale", (0.8, 0.45, 0.1), emission=(0.6, 0.3, 0.05), estrength=0.6), verts=10)
for bsx in (0.0, 1.0, 2.0, 3.0):  # bar stools
    K.cyl("bar_stool", 0.2, 0.05, (bx0 - 1.6 + bsx * 1.05, bar_y - 0.9, 0.75), M["stool"], verts=12)
    K.cyl("bar_stool_leg", 0.035, 0.75, (bx0 - 1.6 + bsx * 1.05, bar_y - 0.9, 0), M["stool"], verts=6)
K.box("rug", (2.6, 1.6, 0.01), (-5.4, 2.6, 0.0), M["red_rug"])

# ------------------------------------------------- hanging lamps / fill ----
for lx in (-4.5, 0.4, 4.6):
    K.box("lamp_chain", (0.02, 0.02, 0.5), (lx, 2.6, H - 0.5), M["beam"])
    K.box("lamp_shade", (0.35, 0.35, 0.2), (lx, 2.6, H - 0.7), M["lamp_glow"])
    K.point_light("lamp", (lx, 2.2, H - 0.85), (1.0, 0.65, 0.35), 110, radius=0.3)
K.point_light("fill", (0, -4, 3.0), (0.45, 0.55, 0.9), 260, radius=3.0)

# ------------------------------------------- foreground beam with hops ----
# Frames the top of the cutaway (rows ~0-30) the way a real low pub ceiling would.
K.box("front_beam", (W + 2, 0.5, 0.9), (0, -3.0, 3.85), M["beam"])
HOPS = K.mat("hops", (0.25, 0.42, 0.12), noise=0.4, scale=30, bump=1.0)
HOP_LEAF = K.mat("hop_leaf", (0.12, 0.25, 0.08), noise=0.4, scale=30, bump=1.0)
x = -W / 2
while x < W / 2:
    sag = abs(((x * 0.9) % 2.0) - 1.0)  # garland swags
    bpy.ops.mesh.primitive_ico_sphere_add(radius=rng.uniform(0.09, 0.15), subdivisions=1,
                                          location=(x, -2.7, 3.8 - sag * 0.35 + rng.uniform(-0.05, 0.05)))
    bpy.context.active_object.data.materials.append(HOPS if rng.random() < 0.6 else HOP_LEAF)
    x += rng.uniform(0.08, 0.16)

# ------------------------------------------------------------- camera ----
# Cutaway: camera sits outside the (missing) front wall, high and level, lens-shifted so the
# horizon is near row 24 -> back wall rows ~38-102, walkable floor rows ~102-148.
cam = K.camera((0.0, -11.0, 4.0), (0.0, 0.0, 4.0), lens=35)
cam.data.shift_y = -0.2375

scn = bpy.context.scene
scn.render.filepath = os.path.join(OUT, "cross_house_tavern.png")
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
fl = [(-8.0, 1.9), (8.0, 1.9), (8.0, -1.2), (-8.0, -1.2)]
floor = [to_px((x, y, 0)) for x, y in fl]
floor = [(min(316, max(4, x)), min(GUI_TOP - 2, y)) for x, y in floor]
data = {
    "hotspots": {k: rect_of(v) for k, v in hot.items()},
    "walk_points": {
        "Bar": to_px((bx0, 1.6, 0)),
        "QuizMachine": to_px((qx, 2.4, 0)),
        "ExitDoor": to_px((ex, 1.6, 0)),
        "Dartboard": to_px((db_x, 2.3, 0)),
        "Landlord": to_px((bx0 + 0.3, 1.6, 0)),
    },
    "landlord_pos": to_px((bx0 + 0.3, bar_y + 0.9, 0)),
    "spawn": {"from_street": to_px((ex, 1.4, 0))},
    "floor": [list(p) for p in floor],
    "person_px": to_px((0, 1.2, 0))[1] - to_px((0, 1.2, 1.8))[1],
}
with open(os.path.join(OUT, "cross_house_tavern.json"), "w") as f:
    json.dump(data, f, indent=1)
print("[blender] wrote", scn.render.filepath, json.dumps(data))
