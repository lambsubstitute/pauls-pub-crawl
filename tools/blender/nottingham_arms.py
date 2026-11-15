"""Inside the Nottingham Arms — Paul's Pub Crawl room background (stop 5, the pool pub).

    /Applications/Blender.app/Contents/MacOS/Blender -b -P tools/blender/nottingham_arms.py

A Victorian High Street front bar: taller ceiling with a couple of dark beams, bottle-green
dado and cream walls, scrubbed floorboards. Bar on the left (Jackie behind it), the front door
to High Street, the cue rack, the league chalkboard, a glowing jukebox and a small cast-iron
fireplace on the back wall; the pool table stands in the middle of the floor under its long
lamp, so Paul walks round it (the room cuts it out as a y-sorted sprite and a hole in the floor).

The cue butt in the rack, the pool rest leaning on the wall and the cue shaft Norman keeps by
the fireplace are separate sprites (they get picked up), so only unrendered marker boxes stand
in for them here.

The camera is higher and tilted down more than the Berkeley's so there's floor in front of and
behind the table; it is at the same distance, so figures are still ~46 px.

Writes art/renders/nottingham_arms.png, nottingham_arms_table.png (alpha mask of the table
alone, for the cut-out) and nottingham_arms.json (hotspots etc. in 320x200 game px).
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
rng = random.Random(129)
NO_RENDER = os.environ.get("NO_RENDER") == "1"

K.reset_scene()
K.world_sky(top=(0.0, 0.0, 0.0), mid=(0.0, 0.0, 0.0), horizon=(0.0, 0.0, 0.0), strength=0.0)

M = {
    "cream": K.mat("cream", (0.62, 0.54, 0.38), noise=0.15, scale=5, bump=0.3),
    "dado": K.mat("dado", (0.06, 0.20, 0.12), noise=0.18, scale=9, bump=0.3),          # bottle green
    "dado_rail": K.mat("dado_rail", (0.16, 0.08, 0.04), noise=0.2, scale=16, rough=0.4),
    "beam": K.mat("beam", (0.08, 0.045, 0.025), noise=0.3, scale=14, bump=0.5),
    "ceiling": K.mat("ceiling", (0.50, 0.43, 0.30), noise=0.15, scale=4),
    "wood": K.mat("wood", (0.20, 0.10, 0.045), noise=0.25, scale=18, rough=0.4),
    "bar_top": K.mat("bar_top", (0.26, 0.12, 0.05), noise=0.2, scale=20, rough=0.25),
    "brass": K.mat("brass", (0.9, 0.65, 0.25), rough=0.25, noise=0.05),
    "pump": K.mat("pump", (0.18, 0.08, 0.04), rough=0.3, noise=0.05),
    "iron": K.mat("iron", (0.03, 0.03, 0.035), rough=0.5),
    "door": K.mat("door", (0.10, 0.16, 0.10), noise=0.2, scale=14),                    # green front door
    "door_glass": K.glow_mat("door_glass", (0.30, 0.40, 0.78), 0.9),
    "baize": K.mat("baize", (0.05, 0.38, 0.14), noise=0.12, scale=30, rough=0.95,
                   emission=(0.02, 0.18, 0.06), estrength=0.25),
    "rail": K.mat("rail", (0.22, 0.10, 0.04), noise=0.2, scale=20, rough=0.3),
    "pocket": K.mat("pocket", (0.01, 0.01, 0.01), noise=0.0),
    "ball_red": K.mat("ball_red", (0.75, 0.06, 0.05), rough=0.2, noise=0.02, emission=(0.4, 0.03, 0.02), estrength=0.4),
    "ball_yel": K.mat("ball_yel", (0.95, 0.75, 0.10), rough=0.2, noise=0.02, emission=(0.5, 0.4, 0.05), estrength=0.4),
    "ball_white": K.mat("ball_white", (0.95, 0.94, 0.90), rough=0.2, noise=0.02, emission=(0.5, 0.5, 0.48), estrength=0.4),
    "lamp_shade": K.mat("lamp_shade", (0.06, 0.22, 0.10), rough=0.4, noise=0.05),
    "lamp_glow": K.glow_mat("lamp_glow", (1.0, 0.86, 0.6), 5.0),
    "wall_lamp": K.glow_mat("wall_lamp", (1.0, 0.68, 0.32), 3.0),
    "chalk": K.mat("chalk", (0.05, 0.07, 0.06), noise=0.2),
    "chalk_text": K.mat("chalk_text", (0.88, 0.88, 0.84), noise=0.1, emission=(0.6, 0.6, 0.55), estrength=0.5),
    "juke_body": K.mat("juke_body", (0.35, 0.10, 0.05), rough=0.3, noise=0.1),
    "juke_pink": K.glow_mat("juke_pink", (1.0, 0.18, 0.50), 1.1),
    "juke_amber": K.glow_mat("juke_amber", (1.0, 0.55, 0.10), 1.2),
    "juke_blue": K.glow_mat("juke_blue", (0.20, 0.45, 1.0), 1.1),
    "juke_chrome": K.mat("juke_chrome", (0.8, 0.8, 0.82), rough=0.15, noise=0.02),
    "fire": K.glow_mat("fire", (1.0, 0.42, 0.06), 4.5),
    "embers": K.glow_mat("embers", (1.0, 0.2, 0.02), 3.0),
    "tile": K.mat("tile", (0.45, 0.16, 0.10), noise=0.2, scale=14),
    "mirror": K.mat("mirror", (0.30, 0.30, 0.30), rough=0.05),
    "water": K.mat("water", (0.55, 0.75, 0.95), rough=0.05, noise=0.05, emission=(0.35, 0.55, 0.8), estrength=0.8),
    "photo": K.mat("photo", (0.45, 0.40, 0.32), noise=0.3, scale=8),
    "stool": K.mat("stool", (0.30, 0.14, 0.06), noise=0.2, scale=12),
    "cushion": K.mat("cushion", (0.40, 0.07, 0.06), noise=0.2, scale=10),
    "sign_text": K.mat("sign_text", (0.85, 0.68, 0.25), emission=(0.9, 0.7, 0.3), estrength=0.6),
}
bottle_cols = [(0.05, 0.25, 0.08), (0.35, 0.18, 0.04), (0.5, 0.05, 0.05), (0.7, 0.6, 0.2), (0.15, 0.2, 0.4)]
BOTTLES = [K.mat(f"bottle{i}", c, rough=0.1, noise=0.05, emission=c, estrength=0.6) for i, c in enumerate(bottle_cols)]
BOARDS = K.brick_mat("boards", brick=(0.30, 0.18, 0.09), mortar=(0.08, 0.05, 0.03), scale=1.4, vertical=False,
                     brick_width=1.6, row_height=0.12)

hot = {}
table_objs = []


def tag(name, *objs):
    hot.setdefault(name, []).extend(objs)


W = 17.0
BACK = 5.0
CEIL = 3.3
DADO = 1.0

# ----------------------------------------------------------------- shell ----
K.box("floor", (W + 2, 16, 0.05), (0, -1.5, -0.05), BOARDS)
K.box("back_wall", (W, 0.2, CEIL), (0, BACK + 0.1, 0), M["cream"])
K.box("dado", (W, 0.06, DADO), (0, BACK - 0.01, 0), M["dado"])
K.box("dado_rail", (W, 0.1, 0.07), (0, BACK - 0.04, DADO), M["dado_rail"])
K.box("skirting", (W, 0.08, 0.14), (0, BACK - 0.05, 0), M["dado_rail"])
K.box("picture_rail", (W, 0.06, 0.05), (0, BACK - 0.03, 2.55), M["dado_rail"])
K.box("left_wall", (0.2, 5, CEIL), (-W / 2 - 0.1, 2.5, 0), M["cream"])
K.box("right_wall", (0.2, 5, CEIL), (W / 2 + 0.1, 2.5, 0), M["cream"])
K.box("ceiling", (W + 2, 16, 0.08), (0, -2.5, CEIL), M["ceiling"])
for by in (-4.5, -1.0, 2.2):
    K.box("beam", (W + 2, 0.34, 0.3), (0, by, CEIL - 0.3), M["beam"])
for jx_ in (-7.5, -5.0, -2.5, 2.5, 5.0, 7.5):  # joists running back to the wall (none over the camera)
    K.box("joist", (0.14, 11.0, 0.14), (jx_, -0.5, CEIL - 0.14), M["beam"])
# a sash window on the back wall onto the yard: cold night blue against the warm room
wx = 4.25
K.box("window_frame", (0.95, 0.1, 1.45), (wx, BACK - 0.03, 1.05), M["dado_rail"])
K.box("window_glass", (0.8, 0.1, 1.3), (wx, BACK - 0.05, 1.12), K.glow_mat("night", (0.16, 0.24, 0.55), 0.7))
K.box("window_bar_h", (0.82, 0.12, 0.05), (wx, BACK - 0.07, 1.75), M["dado_rail"])
K.box("window_bar_v", (0.04, 0.12, 1.3), (wx, BACK - 0.07, 1.12), M["dado_rail"])
K.box("window_sill", (1.05, 0.2, 0.05), (wx, BACK - 0.1, 1.02), M["wood"])
K.box("back_beam", (W, 0.3, 0.3), (0, BACK - 0.1, CEIL - 0.3), M["beam"])

# ------------------------------------------------------------------ bar ----
bx0, bw = -6.2, 4.4
bar_y = 3.55
counter = K.box("bar_front", (bw, 0.7, 1.05), (bx0, bar_y, 0), M["wood"])
K.box("bar_top", (bw + 0.2, 0.9, 0.08), (bx0, bar_y, 1.05), M["bar_top"])
K.box("bar_plinth", (bw, 0.74, 0.14), (bx0, bar_y, 0), M["beam"])
for i in range(6):
    K.box("bar_panel", (0.06, 0.05, 0.8), (bx0 - bw / 2 + 0.4 + i * 0.72, bar_y - 0.37, 0.15), M["beam"])
K.box("foot_rail", (bw, 0.06, 0.06), (bx0, bar_y - 0.45, 0.22), M["brass"])
pumps = []
for i, px in enumerate((-7.0, -6.45, -5.9)):
    K.cyl("pump_base", 0.06, 0.12, (px, bar_y - 0.15, 1.13), M["brass"], verts=10)
    pumps.append(K.cyl("pump_handle", 0.045, 0.5, (px, bar_y - 0.15, 1.25), M["pump"], verts=10))
    pumps.append(K.box("pump_clip", (0.16, 0.03, 0.12), (px, bar_y - 0.2, 1.55),
                       K.mat(f"clip{i}", ((0.75, 0.6, 0.15), (0.6, 0.1, 0.08), (0.1, 0.3, 0.55))[i])))
tag("Pumps", *pumps)
jug = K.cyl("water_jug", 0.09, 0.26, (-4.0, bar_y - 0.12, 1.13), M["water"], verts=12)
K.cyl("jug_handle", 0.02, 0.17, (-3.89, bar_y - 0.12, 1.17), M["water"], verts=6)
for gx in (-4.3, -4.21):
    K.cyl("tumbler", 0.035, 0.09, (gx, bar_y - 0.25, 1.13), M["water"], verts=8)
tag("WaterJug", jug)
K.box("back_bar", (bw + 0.4, 0.5, 1.0), (bx0, BACK - 0.3, 0), M["wood"])
K.box("bar_mirror", (bw - 0.8, 0.05, 0.6), (bx0, BACK - 0.05, 1.15), M["mirror"])
for sz in (1.85, 2.25):
    K.box("shelf", (bw, 0.28, 0.04), (bx0, BACK - 0.18, sz), M["bar_top"])
    x = bx0 - bw / 2 + 0.25
    while x < bx0 + bw / 2 - 0.25:
        h = rng.uniform(0.18, 0.26)
        K.cyl("bottle", 0.045, h, (x, BACK - 0.18, sz + 0.04), rng.choice(BOTTLES), verts=8)
        x += rng.uniform(0.12, 0.18)
for i in range(8):  # glasses hanging from a rack over the bar
    K.cyl("glass", 0.045, 0.12, (bx0 - 1.7 + i * 0.48, bar_y + 0.1, 2.55), M["water"], verts=8)
K.box("glass_rack", (bw, 0.4, 0.05), (bx0, bar_y + 0.1, 2.67), M["beam"])
tag("Bar", counter)
K.point_light("bar_light", (bx0, bar_y + 0.4, 2.4), (1.0, 0.70, 0.40), 140, radius=0.5)

# ----------------------------------------------------- front door (exit) ----
ex = -2.75
door = K.box("exit_door", (1.0, 0.12, 2.05), (ex, BACK - 0.05, 0), M["door"])
for i in range(2):
    K.box("door_panel", (0.34, 0.14, 0.55), (ex - 0.21 + i * 0.42, BACK - 0.07, 0.2), M["dado_rail"])
K.box("door_glass", (0.76, 0.13, 0.75), (ex, BACK - 0.06, 1.05), M["door_glass"])
K.box("door_bar", (0.04, 0.15, 0.75), (ex, BACK - 0.07, 1.05), M["dado_rail"])
K.box("door_knob", (0.07, 0.17, 0.07), (ex + 0.38, BACK - 0.09, 0.95), M["brass"])
K.box("door_frame", (1.3, 0.16, 0.16), (ex, BACK - 0.08, 2.05), M["dado_rail"])
K.box("fanlight", (1.0, 0.12, 0.3), (ex, BACK - 0.05, 2.21), M["door_glass"])
K.box("fanlight_text", (0.6, 0.1, 0.07), (ex, BACK - 0.12, 2.3), M["sign_text"])
tag("ExitDoor", door)
K.point_light("door_lamp", (ex, BACK - 0.6, 2.4), (1.0, 0.7, 0.4), 25, radius=0.15)

# ------------------------------------------------------------- cue rack ----
# A wall rack of six slots, all empty bar one: the house cue's butt end (sprite in game).
crx = -1.15
rack = K.box("cue_rack_back", (0.7, 0.05, 1.5), (crx, BACK - 0.04, 0.55), M["wood"])
K.box("cue_rack_top", (0.74, 0.14, 0.07), (crx, BACK - 0.1, 1.95), M["dado_rail"])
K.box("cue_rack_foot", (0.74, 0.16, 0.08), (crx, BACK - 0.1, 0.55), M["dado_rail"])
for i in range(6):
    K.box("cue_clip", (0.03, 0.15, 0.03), (crx - 0.3 + i * 0.12, BACK - 0.12, 1.9), M["brass"])
tag("CueRack", rack)
butt_at = (crx + 0.18, BACK - 0.12)
bv = K.box("cue_butt_vol", (0.1, 0.06, 0.8), (butt_at[0], butt_at[1], 0.62), None)
bv.hide_render = True

# ---------------------------------------------------------- pool rest ----
rest_at = (-0.15, BACK - 0.1)
rv = K.box("pool_rest_vol", (0.25, 0.06, 1.7), (rest_at[0], rest_at[1], 0.0), None)
rv.hide_render = True
tag("PoolRest", rv)

# ------------------------------------------------------- league board ----
lbx = 1.05
board = K.box("league_board", (1.2, 0.05, 0.75), (lbx, BACK - 0.06, 1.5), M["chalk"])
K.box("league_frame", (1.28, 0.04, 0.83), (lbx, BACK - 0.04, 1.46), M["dado_rail"])
K.box("league_title", (0.9, 0.06, 0.06), (lbx, BACK - 0.09, 2.08), M["chalk_text"])
for i in range(4):
    K.box("league_line", (rng.uniform(0.5, 0.85), 0.06, 0.03), (lbx - 0.08, BACK - 0.09, 1.62 + i * 0.1), M["chalk_text"])
tag("LeagueBoard", board)

# ------------------------------------------------------------ jukebox ----
jx = 2.65
juke = K.box("juke_body", (0.85, 0.6, 1.25), (jx, BACK - 0.35, 0), M["juke_body"])
arch = K.cyl("juke_arch", 0.425, 0.6, (0, 0, 0), M["juke_body"], verts=24)
arch.rotation_euler = (math.pi / 2, 0, 0)
arch.location = (jx, BACK - 0.05, 1.25)
K.box("juke_window", (0.6, 0.05, 0.42), (jx, BACK - 0.66, 0.72), M["juke_amber"])
K.box("juke_buttons", (0.6, 0.05, 0.12), (jx, BACK - 0.67, 0.55), M["juke_chrome"])
K.box("juke_grille", (0.6, 0.05, 0.4), (jx, BACK - 0.66, 0.08), M["juke_blue"])
for side in (-1, 1):
    K.box("juke_tube", (0.07, 0.07, 1.2), (jx + side * 0.4, BACK - 0.66, 0.05), M["juke_pink"])
glow_arch = K.cyl("juke_arch_glow", 0.36, 0.05, (0, 0, 0), M["juke_pink"], verts=24)
glow_arch.rotation_euler = (math.pi / 2, 0, 0)
glow_arch.location = (jx, BACK - 0.62, 1.25)
tag("Jukebox", juke, arch)
K.point_light("juke_light", (jx, BACK - 1.2, 0.8), (1.0, 0.45, 0.6), 40, radius=0.3)

# ----------------------------------------------------------- fireplace ----
fx = 5.9
surround = K.box("fire_surround", (1.3, 0.25, 1.15), (fx, BACK - 0.12, 0), M["iron"])
K.box("fire_tiles_l", (0.18, 0.05, 0.85), (fx - 0.42, BACK - 0.26, 0.1), M["tile"])
K.box("fire_tiles_r", (0.18, 0.05, 0.85), (fx + 0.42, BACK - 0.26, 0.1), M["tile"])
grate = K.box("fire_grate", (0.6, 0.05, 0.55), (fx, BACK - 0.25, 0.1), M["iron"])
K.box("flames", (0.45, 0.06, 0.28), (fx, BACK - 0.28, 0.14), M["fire"])
K.box("embers", (0.5, 0.06, 0.06), (fx, BACK - 0.29, 0.12), M["embers"])
K.box("mantel", (1.6, 0.35, 0.08), (fx, BACK - 0.17, 1.15), M["wood"])
K.box("over_mirror", (1.0, 0.04, 0.8), (fx, BACK - 0.03, 1.5), M["mirror"])
K.box("over_mirror_frame", (1.1, 0.03, 0.9), (fx, BACK - 0.02, 1.45), M["brass"])
K.box("hearth", (1.6, 0.5, 0.05), (fx, BACK - 0.45, 0), M["tile"])
for i, cx in enumerate((fx - 0.55, fx + 0.55)):
    K.cyl("candlestick", 0.03, 0.2, (cx, BACK - 0.2, 1.23), M["brass"], verts=8)
K.cyl("clock", 0.12, 0.12, (fx, BACK - 0.2, 1.23), M["wood"], verts=12)
K.point_light("fire_light", (fx, BACK - 1.2, 0.35), (1.0, 0.42, 0.10), 110, radius=0.5)
tag("Fireplace", surround, grate)
# Norman's cue shaft leans against the wall right of the fireplace (sprite in game)
shaft_at = (fx + 1.15, BACK - 0.1)
sv = K.box("cue_shaft_vol", (0.2, 0.06, 1.45), (shaft_at[0], shaft_at[1], 0.0), None)
sv.hide_render = True
tag("CueShaft", sv)
# a high-backed chair and a little table for Norman's pint
K.box("chair_seat", (0.55, 0.5, 0.08), (fx + 1.9, BACK - 0.6, 0.45), M["stool"])
K.box("chair_back", (0.55, 0.08, 0.75), (fx + 1.9, BACK - 0.35, 0.45), M["stool"])
K.box("chair_cushion", (0.5, 0.45, 0.05), (fx + 1.9, BACK - 0.6, 0.53), M["cushion"])
for lx, ly in ((-0.22, -0.2), (0.22, -0.2), (-0.22, 0.2), (0.22, 0.2)):
    K.box("chair_leg", (0.05, 0.05, 0.45), (fx + 1.9 + lx, BACK - 0.6 + ly, 0), M["stool"])

# ---------------------------------------------------------- pool table ----
# pub table, 2.35 x 1.3 m outside (a shade over 7 ft so it reads at 320x200), baize at 0.8 m. Centre a little right of the room middle.
tx, ty = 1.15, 1.15
TL, TD, TH = 2.35, 1.3, 0.8
parts = [
    K.box("table_body", (TL - 0.2, TD - 0.2, 0.32), (tx, ty, TH - 0.4), M["rail"]),
    K.box("table_baize", (TL - 0.16, TD - 0.16, 0.06), (tx, ty, TH - 0.06), M["baize"]),
    K.box("table_coinbox", (0.5, 0.06, 0.18), (tx, ty - TD / 2 + 0.07, TH - 0.36), M["iron"]),
]
for side in (-1, 1):
    parts.append(K.box("rail_long", (TL, 0.1, 0.09), (tx, ty + side * (TD / 2 - 0.05), TH - 0.05), M["rail"]))
    parts.append(K.box("rail_end", (0.1, TD, 0.09), (tx + side * (TL / 2 - 0.05), ty, TH - 0.05), M["rail"]))
for lx in (-1, 1):
    for ly in (-1, 1):
        parts.append(K.box("table_leg", (0.16, 0.16, TH - 0.36), (tx + lx * (TL / 2 - 0.2), ty + ly * (TD / 2 - 0.2), 0), M["rail"]))
for px_ in (-1, 0, 1):
    for py_ in (-1, 1):
        parts.append(K.cyl("pocket", 0.06, 0.02, (tx + px_ * (TL / 2 - 0.1), ty + py_ * (TD / 2 - 0.1), TH - 0.01), M["pocket"], verts=10))
# a scatter of balls left from the last game (the cue ball's on the spot)
for i, (bx_, by_) in enumerate(((0.45, 0.1), (0.55, -0.12), (0.62, 0.14), (0.7, -0.02), (-0.3, 0.25), (0.2, -0.3), (-0.55, 0.0))):
    parts.append(K.cyl("ball", 0.03, 0.06, (tx + bx_, ty + by_, TH - 0.01), M["ball_red"] if i % 2 else M["ball_yel"], verts=10))
parts.append(K.cyl("cue_ball", 0.03, 0.06, (tx - 0.6, ty, TH - 0.01), M["ball_white"], verts=10))
table_objs.extend(parts)
tag("PoolTable", *parts)
# long lamp over the table
K.box("table_lamp", (1.5, 0.35, 0.18), (tx, ty, 2.1), M["lamp_shade"])
K.box("table_lamp_glow", (1.4, 0.3, 0.02), (tx, ty, 2.08), M["lamp_glow"])
for side in (-1, 1):
    K.box("lamp_chain", (0.02, 0.02, 1.0), (tx + side * 0.6, ty, 2.28), M["brass"])
K.point_light("table_light", (tx, ty, 1.85), (1.0, 0.9, 0.7), 70, radius=0.6)

# ---------------------------------------------------------- decoration ----
for (px_, pz, w, h) in ((-0.15, 2.05, 0.4, 0.32), (7.4, 1.6, 0.5, 0.4), (-8.0, 1.8, 0.4, 0.5)):
    K.box("photo_frame", (w, 0.04, h), (px_, BACK - 0.04, pz), M["dado_rail"])
    K.box("photo", (w - 0.08, 0.04, h - 0.08), (px_, BACK - 0.06, pz + 0.04), M["photo"])
# bar stools in front of the counter
for sx_ in (-7.2, -5.6):
    K.cyl("stool_seat", 0.2, 0.05, (sx_, bar_y - 0.75, 0.7), M["cushion"], verts=12)
    K.cyl("stool_leg", 0.04, 0.7, (sx_, bar_y - 0.75, 0), M["stool"], verts=8)

# ------------------------------------------------------------- lighting ----
for lx in (-3.9, 0.15, 4.2, 7.6):
    K.box("wall_lamp", (0.14, 0.1, 0.22), (lx, BACK - 0.1, 2.15), M["wall_lamp"])
    K.point_light("wall_lamp_light", (lx, BACK - 0.5, 2.15), (1.0, 0.68, 0.36), 26, radius=0.2)
for lx in (-5.0, 0.0, 5.0):
    K.point_light("room_light", (lx, 1.2, 2.8), (1.0, 0.70, 0.40), 80, radius=0.5)
for ly in (-1.5, -4.5):
    for lx in (-5.5, 0.0, 5.5):
        K.point_light("ceiling_wash", (lx, ly, 2.6), (1.0, 0.66, 0.36), 26, radius=0.6)
K.point_light("fill", (0, -6, 2.0), (0.40, 0.48, 0.85), 140, radius=3.0)
for lx in (-4.5, 0.0, 4.5):  # warm the ceiling so the beams read instead of going grey
    K.point_light("ceiling_glow", (lx, 3.0, 2.95), (1.0, 0.62, 0.32), 30, radius=0.4)
K.point_light("window_cold", (wx, BACK - 0.5, 1.6), (0.35, 0.45, 0.9), 15, radius=0.4)

# --------------------------------------------------------------- camera ----
# Higher than the Berkeley's (3 m, under a 3.3 m ceiling) and tipped 10 degrees down, so the
# floor band runs from just in front of the bar to the bottom of the game area.
CAM_Y = -11.5
cam = K.camera((0.0, CAM_Y, 3.0), (0.0, 0.0, 3.0 - 11.5 * math.tan(math.radians(10))), lens=35)

scn = bpy.context.scene
bpy.context.view_layer.update()  # world matrices for the projections below, even with NO_RENDER


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


if not NO_RENDER:
    scn.render.filepath = os.path.join(OUT, "nottingham_arms.png")
    bpy.ops.render.render(write_still=True)
    # Alpha mask of the table on its own: the layout tool cuts exactly these pixels out of the
    # background as the y-sorted table sprite (a plain rectangle would hide Paul behind wall).
    keep = set(table_objs)
    for o in scn.objects:
        if o.type == "MESH" and o not in keep:
            o.hide_render = True
    scn.render.film_transparent = True
    scn.render.filepath = os.path.join(OUT, "nottingham_arms_table.png")
    bpy.ops.render.render(write_still=True)

GUI_TOP = 150
JACKIE = (-5.25, bar_y + 0.75)   # behind the bar between the pumps and the water jug
GAZ = (tx + TL / 2 + 0.55, 0.2)      # chalking his cue at the right-hand end of the table
NORMAN = (4.15, 2.5)                 # by the window, within poking distance of the jukebox
FLOOR_BACK, FLOOR_FRONT = 2.95, -2.6
fl = [(-8.0, FLOOR_BACK), (8.0, FLOOR_BACK), (8.0, FLOOR_FRONT), (-8.0, FLOOR_FRONT)]
floor = [to_px((x, y, 0)) for x, y in fl]
floor = [(min(316, max(4, x)), min(GUI_TOP - 2, y)) for x, y in floor]
# the table's footprint (plus a body's width of clearance) is a hole in the walkable floor
pad = 0.12
hole = [to_px((tx + sx * (TL / 2 + pad), ty + sy * (TD / 2 + pad), 0))
        for sx, sy in ((-1, 1), (1, 1), (1, -1), (-1, -1))]
data = {
    "hotspots": {k: rect_of(v) for k, v in hot.items()},
    "walk_points": {
        "Bar": to_px((bx0 + 0.8, 2.75, 0)),
        "Pumps": to_px((-6.45, 2.75, 0)),
        "WaterJug": to_px((-4.0, 2.75, 0)),
        "ExitDoor": to_px((ex, 2.8, 0)),
        "CueRack": to_px((crx, 2.8, 0)),
        "PoolRest": to_px((rest_at[0], 2.8, 0)),
        "LeagueBoard": to_px((lbx, 2.8, 0)),
        "Jukebox": to_px((jx - 0.5, 2.6, 0)),
        "Fireplace": to_px((fx - 0.3, 2.8, 0)),
        "CueShaft": to_px((shaft_at[0] - 0.3, 2.8, 0)),
        "PoolTable": to_px((tx - 0.3, ty - TD / 2 - 0.45, 0)),
        "Jackie": to_px((JACKIE[0] + 0.6, 2.75, 0)),
        "Gaz": to_px((GAZ[0] - 0.75, GAZ[1] - 0.35, 0)),
        "Norman": to_px((NORMAN[0] - 0.8, NORMAN[1] - 0.15, 0)),
    },
    "npc": {
        "Jackie": to_px(JACKIE + (0,)),
        "Gaz": to_px((GAZ[0], GAZ[1], 0)),
        "Norman": to_px((NORMAN[0], NORMAN[1], 0)),
    },
    "spawn": {"from_high_st": to_px((ex, 2.6, 0))},
    "floor": [list(p) for p in floor],
    "floor_holes": [[list(p) for p in hole]],
    "table_baseline": to_px((tx, ty - TD / 2, 0))[1],
    "cue_butt": to_px((butt_at[0], butt_at[1], 0.62)),
    "pool_rest": to_px((rest_at[0], rest_at[1], 0.0)),
    "cue_shaft": to_px((shaft_at[0], shaft_at[1], 0.0)),
    "person_px": to_px((0, 1.2, 0))[1] - to_px((0, 1.2, 1.8))[1],
    "person_px_back": to_px((0, 2.8, 0))[1] - to_px((0, 2.8, 1.8))[1],
    "person_px_front": to_px((0, -2.4, 0))[1] - to_px((0, -2.4, 1.8))[1],
}
with open(os.path.join(OUT, "nottingham_arms.json"), "w") as f:
    json.dump(data, f, indent=1)
print("[blender] wrote", json.dumps(data))
