"""Church Street, Tewkesbury at dusk — Paul's Pub Crawl room background.

    /Applications/Blender.app/Contents/MacOS/Blender -b -P tools/blender/church_st.py

Writes:
    art/renders/church_st.png        1280x800 raw render
    art/renders/church_st.json       hotspot rects + floor polygon in 320x200 game pixels
Then run tools/pixelate.py to make the in-game 32-colour background.
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
rng = random.Random(11)

K.reset_scene()
K.world_sky(top=(0.01, 0.015, 0.06), mid=(0.10, 0.06, 0.20), horizon=(0.75, 0.30, 0.18), strength=0.45)

M = {
    "plaster": K.mat("plaster", (0.80, 0.74, 0.60), noise=0.18, scale=4),
    "plaster2": K.mat("plaster2", (0.78, 0.70, 0.52), noise=0.2, scale=5),
    "beam": K.mat("beam", (0.05, 0.035, 0.03), noise=0.3, scale=20),
    "roof": K.mat("roof", (0.22, 0.10, 0.08), noise=0.35, scale=30, bump=0.8),
    "slate": K.mat("slate", (0.12, 0.12, 0.16), noise=0.3, scale=30, bump=0.8),
    "frame": K.mat("frame", (0.85, 0.83, 0.78), noise=0.05),
    "glass_lit": K.glow_mat("glass_lit", (1.0, 0.50, 0.15), 2.2),
    "glass_dark": K.mat("glass_dark", (0.05, 0.06, 0.10), rough=0.15, noise=0.1),
    "door": K.mat("door", (0.10, 0.18, 0.12), noise=0.15, scale=12),
    "iron": K.mat("iron", (0.03, 0.03, 0.035), rough=0.5),
    "lamp": K.glow_mat("lamp", (1.0, 0.75, 0.40), 5.0),
    "stone": K.mat("stone", (0.62, 0.56, 0.46), noise=0.25, scale=3, bump=0.6),
    "stone_dark": K.mat("stone_dark", (0.40, 0.36, 0.32), noise=0.25, scale=3, bump=0.6),
    "tree": K.mat("tree", (0.03, 0.06, 0.05), noise=0.5, scale=3, bump=1.0),
    "asphalt": K.mat("asphalt", (0.07, 0.07, 0.08), noise=0.4, scale=40, bump=0.3),
    "kerb": K.mat("kerb", (0.45, 0.43, 0.40), noise=0.2, scale=10),
    "line_white": K.mat("line_white", (0.85, 0.85, 0.80), noise=0.1),
    "line_yellow": K.mat("line_yellow", (0.85, 0.65, 0.10), noise=0.1),
    "wood": K.mat("wood", (0.32, 0.18, 0.09), noise=0.3, scale=25),
    "gold": K.mat("gold", (1.0, 0.75, 0.2), rough=0.2, emission=(1.0, 0.8, 0.3), estrength=1.5),
    "sign": K.mat("sign", (0.06, 0.22, 0.12), noise=0.1),
    "sign_text": K.mat("sign_text", (0.85, 0.68, 0.25), emission=(0.9, 0.7, 0.3), estrength=0.6),
}
BRICK = K.brick_mat("brick", brick=(0.50, 0.17, 0.09), mortar=(0.62, 0.58, 0.52), scale=2.2)
FLAGS = K.brick_mat("flags", brick=(0.36, 0.34, 0.31), mortar=(0.16, 0.15, 0.14), scale=1.0, vertical=False)

hotspots = {}  # name -> list of objects whose screen bbox defines it


def tag(name, *objs):
    hotspots.setdefault(name, []).extend(objs)


# --------------------------------------------------------------- ground ----
K.box("road", (60, 14, 0.02), (0, -10, -0.02), M["asphalt"])
pav = K.box("pavement", (60, 3.2, 0.14), (0, -1.6, 0), FLAGS)
K.box("kerb", (60, 0.25, 0.16), (0, -3.25, 0), M["kerb"])
for side_y in (-3.55, -3.7):
    K.box("dyl", (60, 0.08, 0.005), (0, side_y, 0.0), M["line_yellow"])
for i in range(-12, 13):
    K.box("centre_line", (2.2, 0.12, 0.005), (i * 4.5, -9.5, 0.0), M["line_white"])
K.box("far_pavement", (60, 3, 0.14), (0, -17.5, 0), FLAGS)

# ---------------------------------------------------------- the Abbey ----
# Norman crossing tower: big square tower with tiers of round-arched arcading.
ax, ay = -21.0, 40.0
tower = K.box("abbey_tower", (7, 7, 13), (ax, ay, 0), M["stone"])
K.box("abbey_nave", (18, 7, 9), (ax + 11, ay + 3, 0), M["stone_dark"])
K.gable_roof("abbey_nave_roof", 18, 7, 3, (ax + 11, ay + 3, 9), M["slate"], ridge_along_x=True)
for tier_z in (6.4, 8.6, 10.8):
    for i in range(7):
        bx = ax - 2.85 + i * 0.95
        K.box("arcade_dark", (0.45, 0.2, 1.5), (bx, ay - 3.55, tier_z), M["stone_dark"])
        K.cyl("arcade_arch", 0.225, 0.22, (bx, ay - 3.55, tier_z + 1.5), M["stone_dark"], verts=10)
    K.box("string_course", (7.3, 0.4, 0.3), (ax, ay - 3.6, tier_z - 0.4), M["stone"])
for i in range(7):  # battlements
    K.box("merlon", (0.5, 7.2, 0.8), (ax - 3.2 + i * 1.07, ay, 13), M["stone"])
for cx in (-3.5, 3.5):  # corner pinnacles
    for cy in (-3.5, 3.5):
        K.box("pinnacle", (0.6, 0.6, 2.2), (ax + cx, ay + cy, 13), M["stone"])
tag("Abbey", tower)

# trees between street and Abbey
for i in range(14):
    tx = -24 + i * 2.6 + rng.uniform(-0.8, 0.8)
    if -2 < tx < 4:
        continue  # buildings hide these anyway
    r = rng.uniform(2.2, 3.4)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=r, subdivisions=2, location=(tx, 14 + rng.uniform(0, 6), r * 1.6))
    t = bpy.context.active_object
    t.scale = (1, 1, 1.25)
    t.data.materials.append(M["tree"])

# ------------------------------------------------------------ frontage ----
tudor_mats = {"plaster": M["plaster"], "beam": M["beam"], "roof": M["roof"], "frame": M["frame"],
              "glass_lit": M["glass_lit"], "glass_dark": M["glass_dark"], "door": M["door"]}
K.tudor_house(-10.2, 4.0, 6, 2, rng, tudor_mats)
K.tudor_house(-5.6, 4.6, 6, 2, rng, tudor_mats, door=True)

# Cross House Tavern: Georgian brick, three bays, lit bar windows, central door
tx0, tw = 0.6, 6.4
th = 5.4
K.box("tavern", (tw, 7, th), (tx0, 3.5, 0), BRICK)
K.box("tavern_parapet", (tw + 0.3, 0.4, 0.5), (tx0, -0.1, th), M["stone"])
K.box("tavern_cornice", (tw + 0.4, 0.5, 0.25), (tx0, -0.15, th - 0.3), M["frame"])
K.gable_roof("tavern_roof", tw, 7, 2.2, (tx0, 3.5, th), M["slate"], ridge_along_x=True)
K.box("chimney", (0.9, 0.9, 1.8), (tx0 - 2.2, 4, th + 1.2), BRICK)
K.box("chimney", (0.9, 0.9, 1.8), (tx0 + 2.2, 4, th + 1.2), BRICK)
for wx in (-2.1, 0, 2.1):
    for wz in (3.4,):
        K.window(tx0 + wx, 0, wz, 1.0, 1.6, M["frame"], M["glass_lit"] if rng.random() < 0.5 else M["glass_dark"],
                 panes=(2, 3))
# ground floor: shopfront-style bar windows either side of the door
K.box("fascia", (tw, 0.15, 0.6), (tx0, -0.1, 2.75), M["sign"])
K.box("fascia_text", (3.6, 0.05, 0.28), (tx0, -0.2, 2.9), M["sign_text"])
for wx in (-2.05, 2.05):
    K.window(tx0 + wx, 0, 0.75, 1.7, 1.8, M["frame"], M["glass_lit"], panes=(3, 2))
door = K.box("tavern_door", (1.15, 0.2, 2.35), (tx0, -0.05, 0.12), M["door"])
K.box("door_surround", (1.6, 0.18, 0.3), (tx0, -0.1, 2.47), M["frame"])
K.box("door_step", (1.6, 0.5, 0.12), (tx0, -0.3, 0.12), M["stone"])
K.box("door_knob", (0.08, 0.08, 0.08), (tx0 + 0.4, -0.18, 1.1), M["gold"])
tag("TavernDoor", door)
K.point_light("door_light", (tx0, -1.2, 2.8), (1.0, 0.65, 0.3), 40, radius=0.4)
# hanging pub sign on a bracket
K.box("sign_bracket", (1.2, 0.08, 0.08), (tx0 + tw / 2 + 0.5, -0.6, 4.3), M["iron"], rot=(1.5708, 0, 0))
K.box("sign_arm", (0.08, 1.2, 0.08), (tx0 + tw / 2 - 0.1, -0.6, 4.3), M["iron"])
K.box("pub_sign", (0.08, 1.0, 0.75), (tx0 + tw / 2 - 0.1, -1.0, 3.45), M["sign"])
K.box("pub_sign_face", (0.1, 0.8, 0.5), (tx0 + tw / 2 - 0.1, -1.0, 3.57), M["sign_text"])

K.tudor_house(7.2, 4.4, 6, 2, rng, tudor_mats, gable=False)
K.tudor_house(11.6, 4.0, 6, 2, rng, tudor_mats, roof_rise=2.6)

# ------------------------------------------------------- street props ----
K.lamp_post(-2.7, -2.75, {"iron": M["iron"], "lamp": M["lamp"]}, light_energy=500)
K.lamp_post(9.2, -2.75, {"iron": M["iron"], "lamp": M["lamp"]}, light_energy=400)

# bench (with a pound coin glinting underneath)
bx, by = 6.6, -1.2
seat = K.box("bench_seat", (2.0, 0.45, 0.07), (bx, by, 0.48), M["wood"])
back = K.box("bench_back", (2.0, 0.07, 0.4), (bx, by + 0.22, 0.62), M["wood"])
for lx in (-0.85, 0.85):
    K.box("bench_leg", (0.08, 0.45, 0.48), (bx + lx, by, 0.14), M["iron"])
coin = K.cyl("coin", 0.06, 0.02, (bx + 0.3, by - 0.15, 0.14), M["gold"], verts=12)
tag("Bench", seat, back)

# bollards and a bin for clutter
for i, bxp in enumerate((-8.0, -7.0, 4.6)):
    K.cyl("bollard", 0.12, 0.9, (bxp, -2.9, 0.14), M["iron"], verts=10)
K.cyl("bin", 0.28, 0.9, (-0.9, -2.6, 0.14), K.mat("bin", (0.05, 0.12, 0.08)), verts=12)

# ------------------------------------------------------------- lights ----
K.sun("moon", (0.9, 0.25, -0.5), (0.50, 0.62, 1.0), 0.9)
K.sun("dusk_fill", (1.35, 0.0, 2.6), (1.0, 0.50, 0.30), 0.12)

# ------------------------------------------------------------- camera ----
cam = K.camera((0.8, -15.0, 6.0), (0.8, 0.0, 6.0), lens=24)
# Level camera keeps verticals straight; lens shift drops the horizon to ~row 33 so we see sky
# over the roofs AND a deep pavement band (rows ~118-148) above the 9-verb panel.
cam.data.shift_y = -0.21

# ---------------------------------------------------------- render ----
scn = bpy.context.scene
scn.render.filepath = os.path.join(OUT, "church_st.png")
bpy.ops.render.render(write_still=True)


# ------------------------------------------------- screen-space export ----
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
            min(320, int(max(xs)) + pad), min(152, int(max(ys)) + pad)]


GUI_TOP = 150
floor = [to_px((-14, -0.5, 0.14)), to_px((14, -0.5, 0.14)), to_px((14, -6.5, 0)), to_px((-14, -6.5, 0))]
floor = [(min(316, max(4, x)), min(GUI_TOP - 2, y)) for x, y in floor]
data = {
    "hotspots": {k: rect_of(v) for k, v in hotspots.items()},
    "walk_points": {
        "TavernDoor": to_px((tx0, -1.0, 0.14)),
        "Bench": to_px((bx, -2.2, 0.14)),
        "Abbey": to_px((-4.0, -2.4, 0.14)),
    },
    "spawn": {"start": to_px((-6.0, -2.3, 0.14)), "from_tavern": to_px((tx0, -1.2, 0.14))},
    "floor": [list(p) for p in floor],
    # how tall a 1.8 m person is, in game pixels, standing on the pavement
    "person_px": to_px((0, -2.2, 0.14))[1] - to_px((0, -2.2, 1.94))[1],
    "coin": to_px((bx + 0.3, by - 0.15, 0.16)),
}
with open(os.path.join(OUT, "church_st.json"), "w") as f:
    json.dump(data, f, indent=1)
print("[blender] wrote", scn.render.filepath, json.dumps(data))
