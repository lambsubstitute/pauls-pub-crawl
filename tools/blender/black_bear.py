"""Inside Ye Olde Black Bear — Paul's Pub Crawl room background (stop 6, the finale).

    /Applications/Blender.app/Contents/MacOS/Blender -b -P tools/blender/black_bear.py

68 High St, out at the Mythe end by the Avon: reputedly the oldest inn in Gloucestershire (1308).
Nothing in it is straight. Crooked low beams, dark oak panelling, a floor that runs downhill
towards the river, an inglenook big enough to sit in. Left to right: the bar (Rosie behind it),
the low front door to High Street, a little leaded window onto the river, the inglenook (Ursula
the Newfoundland asleep on the hearth), the champions' honours board, the dartboard, and the
pool table in the back right-hand corner, leaning with the floor (its short leg wants a wedge).

Ursula and the table wedge are sprites (she moves, it gets picked up), so only unrendered
marker boxes stand in for them here.

Same camera as the Berkeley Arms (2 m, just under the beams; figures ~46 px). Everything Paul
uses is on the back wall or behind the walk band, so there are no holes in the floor.

Writes art/renders/black_bear.png + .json (hotspots, walk points, NPC spots in 320x200 game px).
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
rng = random.Random(1308)
NO_RENDER = os.environ.get("NO_RENDER") == "1"

K.reset_scene()
K.world_sky(top=(0.0, 0.0, 0.0), mid=(0.0, 0.0, 0.0), horizon=(0.0, 0.0, 0.0), strength=0.0)

M = {
    "daub": K.mat("daub", (0.58, 0.47, 0.32), noise=0.25, scale=5, bump=0.6),       # smoke-yellowed limewash
    "oak": K.mat("oak", (0.065, 0.035, 0.02), noise=0.35, scale=16, bump=0.6),     # black old oak
    "panel": K.mat("panel", (0.19, 0.095, 0.042), noise=0.3, scale=14, bump=0.5, rough=0.45),
    "panel_lit": K.mat("panel_lit", (0.22, 0.11, 0.05), noise=0.3, scale=18, rough=0.4),
    "ceiling": K.mat("ceiling", (0.50, 0.42, 0.30), noise=0.22, scale=4),
    "bar_top": K.mat("bar_top", (0.25, 0.11, 0.04), noise=0.2, scale=20, rough=0.25),
    "brass": K.mat("brass", (0.9, 0.65, 0.25), rough=0.25, noise=0.05),
    "pump": K.mat("pump", (0.14, 0.06, 0.03), rough=0.3, noise=0.05),
    "brick": K.mat("brick", (0.32, 0.15, 0.09), noise=0.35, scale=12, bump=0.7),
    "soot": K.mat("soot", (0.035, 0.03, 0.025), noise=0.2),
    "fire": K.glow_mat("fire", (1.0, 0.42, 0.06), 5.0),
    "embers": K.glow_mat("embers", (1.0, 0.2, 0.02), 3.0),
    "copper": K.mat("copper", (0.75, 0.32, 0.14), rough=0.3, noise=0.1),
    "door": K.mat("door", (0.12, 0.07, 0.04), noise=0.25, scale=14),
    "iron": K.mat("iron", (0.03, 0.03, 0.035), rough=0.5),
    "lamp_glow": K.glow_mat("lamp_glow", (1.0, 0.66, 0.30), 3.0),
    "rug": K.mat("rug", (0.36, 0.08, 0.06), noise=0.3, scale=12),
    "honours": K.mat("honours", (0.10, 0.05, 0.03), noise=0.15, scale=10, rough=0.3),
    "gold": K.mat("gold", (0.85, 0.62, 0.20), noise=0.1, emission=(0.65, 0.45, 0.12), estrength=0.5),
    "board_black": K.mat("board_black", (0.03, 0.03, 0.03), noise=0.1),
    "board_cream": K.mat("board_cream", (0.80, 0.72, 0.55), noise=0.1),
    "board_red": K.mat("board_red", (0.75, 0.08, 0.06), noise=0.05, emission=(0.5, 0.05, 0.03), estrength=0.5),
    "board_green": K.mat("board_green", (0.06, 0.45, 0.16), noise=0.05, emission=(0.03, 0.3, 0.1), estrength=0.5),
    "oche": K.mat("oche", (0.92, 0.88, 0.70), noise=0.05, emission=(0.5, 0.45, 0.3), estrength=0.4),
    "baize": K.mat("baize", (0.05, 0.36, 0.14), noise=0.12, scale=30, rough=0.95,
                   emission=(0.02, 0.18, 0.06), estrength=0.3),
    "rail": K.mat("rail", (0.18, 0.08, 0.035), noise=0.2, scale=20, rough=0.3),
    "ball_red": K.mat("ball_red", (0.75, 0.06, 0.05), rough=0.2, noise=0.02, emission=(0.4, 0.03, 0.02), estrength=0.4),
    "ball_yel": K.mat("ball_yel", (0.95, 0.75, 0.10), rough=0.2, noise=0.02, emission=(0.5, 0.4, 0.05), estrength=0.4),
    "ball_white": K.mat("ball_white", (0.95, 0.94, 0.90), rough=0.2, noise=0.02, emission=(0.5, 0.5, 0.48), estrength=0.4),
    "lamp_shade": K.mat("lamp_shade", (0.30, 0.10, 0.05), rough=0.4, noise=0.05),
    "table_glow": K.glow_mat("table_glow", (1.0, 0.86, 0.6), 4.0),
    "night": K.glow_mat("night", (0.16, 0.26, 0.62), 1.3),
    "lead": K.mat("lead", (0.10, 0.10, 0.12), noise=0.05),
    "water": K.mat("water", (0.55, 0.75, 0.95), rough=0.05, noise=0.05, emission=(0.35, 0.55, 0.8), estrength=0.8),
    "sign": K.mat("sign", (0.85, 0.80, 0.62), noise=0.1, emission=(0.5, 0.45, 0.3), estrength=0.3),
    "sign_text": K.mat("sign_text", (0.85, 0.68, 0.25), emission=(0.9, 0.7, 0.3), estrength=0.6),
    "photo": K.mat("photo", (0.45, 0.40, 0.32), noise=0.3, scale=8),
    "settle": K.mat("settle", (0.10, 0.05, 0.025), noise=0.3, scale=14, rough=0.5),
}
bottle_cols = [(0.05, 0.25, 0.08), (0.35, 0.18, 0.04), (0.5, 0.05, 0.05), (0.7, 0.6, 0.2), (0.15, 0.2, 0.4)]
BOTTLES = [K.mat(f"bottle{i}", c, rough=0.1, noise=0.05, emission=c, estrength=0.6) for i, c in enumerate(bottle_cols)]
FLAGS = K.brick_mat("flags", brick=(0.27, 0.22, 0.18), mortar=(0.08, 0.07, 0.06), scale=1.6, vertical=False,
                    brick_width=0.7, row_height=0.45)

hot = {}


def tag(name, *objs):
    hot.setdefault(name, []).extend(objs)


W = 17.0
BACK = 5.0
CEIL = 2.55        # underside of the ceiling boards
BEAM_Z = 2.30      # underside of the cross beams (give or take: they're crooked)
SLOPE = 0.018      # the floor runs downhill to the right, towards the river (radians)

# ----------------------------------------------------------------- shell ----
K.box("floor", (W + 2, 16, 0.05), (0, -1.5, -0.05), FLAGS, rot=(0, SLOPE, 0))
K.box("back_wall", (W, 0.2, CEIL + 0.3), (0, BACK + 0.1, -0.3), M["daub"])
K.box("left_wall", (0.2, 5, CEIL), (-W / 2 - 0.1, 2.5, 0), M["daub"])
K.box("right_wall", (0.2, 5, CEIL + 0.3), (W / 2 + 0.1, 2.5, -0.3), M["daub"])
K.box("ceiling", (W + 2, 16, 0.08), (0, -2.5, CEIL), M["ceiling"], rot=(0, -0.01, 0))
# dark oak panelling to shoulder height on the back wall, framed into square panels
PANEL_TOP = 1.35
K.box("panelling", (W, 0.06, PANEL_TOP + 0.3), (0, BACK - 0.01, -0.3), M["panel"])
K.box("panel_rail", (W, 0.09, 0.08), (0, BACK - 0.04, PANEL_TOP), M["oak"], rot=(0, 0.012, 0))
K.box("panel_mid", (W, 0.08, 0.06), (0, BACK - 0.04, 0.68), M["oak"], rot=(0, 0.01, 0))
x = -W / 2 + 0.3
while x < W / 2:
    K.box("panel_stile", (0.07, 0.08, PANEL_TOP + 0.3), (x, BACK - 0.04, -0.3), M["oak"],
          rot=(0, rng.uniform(-0.025, 0.025), 0))
    x += 0.62
# close studding above the panelling, every stud a bit off true
K.box("wall_head", (W, 0.1, 0.2), (0, BACK - 0.03, CEIL - 0.2), M["oak"], rot=(0, -0.015, 0))
x = -W / 2 + 0.2
while x < W / 2:
    K.box("wall_stud", (0.13, 0.08, CEIL - PANEL_TOP), (x + rng.uniform(-0.05, 0.05), BACK - 0.02, PANEL_TOP),
          M["oak"], rot=(0, rng.uniform(-0.07, 0.07), 0))
    x += 0.5
for wx in (-7.9, 7.9):
    K.box("corner_post", (0.28, 0.28, CEIL + 0.3), (wx, BACK - 0.15, -0.3), M["oak"], rot=(0, 0.03 if wx > 0 else -0.02, 0))
# low, crooked cross beams and joists: each beam sags and twists a different way
beams = []
for i, by in enumerate((-6.4, -3.9, -1.6, 0.4, 2.0, 3.6)):
    sag = (-0.05, 0.04, -0.06, 0.05, -0.04, 0.035)[i]
    beams.append(K.box("beam", (W + 2, 0.34, CEIL - BEAM_Z + 0.05), (0, by, BEAM_Z + rng.uniform(-0.03, 0.03)),
                       M["oak"], rot=(rng.uniform(-0.04, 0.04), sag * 0.4, 0)))
for jx in range(-9, 10):
    K.box("joist", (0.12, 13.5, 0.1), (jx * 0.95 + rng.uniform(-0.08, 0.08), -3.0, CEIL - 0.1), M["oak"],
          rot=(0, 0, rng.uniform(-0.03, 0.03)))
# horse brasses nailed along the beam over the door
for i in range(9):
    hx = -4.6 + i * 0.55
    b = K.cyl("horse_brass", 0.07, 0.02, (0, 0, 0), M["brass"], verts=10)
    b.rotation_euler = (1.5708, 0, 0)
    b.location = (hx, 2.0 - 0.18, BEAM_Z - 0.06)
# the "mind your head" board on the beam nearest the door: the Beams hotspot
mind = K.box("mind_head", (1.0, 0.04, 0.16), (-2.55, 2.0 - 0.19, BEAM_Z - 0.2), M["sign"], rot=(0, 0.05, 0))
K.box("mind_text", (0.8, 0.03, 0.05), (-2.55, 2.0 - 0.22, BEAM_Z - 0.15), M["board_black"], rot=(0, 0.05, 0))
tag("Beams", mind)

# ------------------------------------------------------------------ bar ----
bx0, bw = -5.4, 4.6
bar_y = 2.4
counter = K.box("bar_front", (bw, 0.7, 1.05), (bx0, bar_y, 0), M["panel_lit"], rot=(0, 0.012, 0))
K.box("bar_top", (bw + 0.2, 0.9, 0.08), (bx0, bar_y, 1.05), M["bar_top"], rot=(0, 0.012, 0))
K.box("bar_plinth", (bw, 0.74, 0.14), (bx0, bar_y, -0.04), M["oak"])
for i in range(6):
    K.box("bar_panel", (0.06, 0.05, 0.8), (bx0 - bw / 2 + 0.4 + i * 0.76, bar_y - 0.37, 0.15), M["oak"])
K.box("foot_rail", (bw, 0.06, 0.06), (bx0, bar_y - 0.45, 0.22), M["brass"], rot=(0, 0.012, 0))
pumps = []
for i, px in enumerate((-5.0, -4.4, -3.8)):
    K.cyl("pump_base", 0.06, 0.12, (px, bar_y - 0.15, 1.12 - (px - bx0) * 0.012), M["brass"], verts=10)
    pumps.append(K.cyl("pump_handle", 0.045, 0.5, (px, bar_y - 0.15, 1.24 - (px - bx0) * 0.012), M["pump"], verts=10))
    pumps.append(K.box("pump_clip", (0.15, 0.03, 0.11), (px, bar_y - 0.2, 1.54 - (px - bx0) * 0.012),
                       K.mat(f"clip{i}", ((0.1, 0.1, 0.1), (0.75, 0.6, 0.15), (0.55, 0.1, 0.08))[i])))
tag("Pumps", *pumps)
jug = K.cyl("water_jug", 0.08, 0.24, (-3.35, bar_y - 0.12, 1.1), M["water"], verts=12)
K.cyl("jug_handle", 0.02, 0.16, (-3.25, bar_y - 0.12, 1.14), M["water"], verts=6)
for gx in (-3.6, -3.52):
    K.cyl("tumbler", 0.035, 0.09, (gx, bar_y - 0.25, 1.1), M["water"], verts=8)
tag("WaterJug", jug)
K.box("back_bar", (bw + 0.4, 0.5, 1.0), (bx0, BACK - 0.3, 0), M["panel"])
for sz in (1.45, 1.8):
    K.box("shelf", (bw, 0.28, 0.04), (bx0, BACK - 0.18, sz), M["bar_top"], rot=(0, 0.02, 0))
    x = bx0 - bw / 2 + 0.25
    while x < bx0 + bw / 2 - 0.25:
        h = rng.uniform(0.17, 0.25)
        K.cyl("bottle", 0.045, h, (x, BACK - 0.18, sz + 0.04 - (x - bx0) * 0.02), rng.choice(BOTTLES), verts=8)
        x += rng.uniform(0.12, 0.18)
for i in range(9):  # pewter tankards hanging off the beam over the bar
    K.cyl("tankard", 0.05, 0.12, (bx0 - 2.0 + i * 0.5, 2.0, BEAM_Z - 0.16), M["copper"], verts=8)
tag("Bar", counter)
K.point_light("bar_light", (bx0, bar_y + 0.4, 2.0), (1.0, 0.70, 0.40), 110, radius=0.5)

# ----------------------------------------------------- front door (exit) ----
ex = -2.55
door = K.box("exit_door", (0.85, 0.12, 1.72), (ex, BACK - 0.05, -0.04), M["door"], rot=(0, 0.04, 0))
for i in range(4):
    K.box("door_plank", (0.03, 0.14, 1.66), (ex - 0.3 + i * 0.2, BACK - 0.08, 0.0), M["oak"], rot=(0, 0.04, 0))
for hz in (0.35, 1.3):
    K.box("door_strap", (0.6, 0.15, 0.05), (ex - 0.08, BACK - 0.09, hz), M["iron"], rot=(0, 0.04, 0))
K.box("door_latch", (0.09, 0.17, 0.05), (ex + 0.32, BACK - 0.1, 0.95), M["iron"])
K.box("door_head", (1.15, 0.18, 0.2), (ex, BACK - 0.08, 1.72), M["oak"], rot=(0, -0.07, 0))
for side in (-1, 1):
    K.box("door_post", (0.14, 0.18, 1.8), (ex + side * 0.5, BACK - 0.08, -0.08), M["oak"], rot=(0, side * 0.03, 0))
tag("ExitDoor", door)
K.point_light("door_lamp", (ex, BACK - 0.6, 1.95), (1.0, 0.7, 0.4), 22, radius=0.15)

# ------------------------------------------------- the window onto the river ----
wx, wz, ww, wh = -1.3, 0.95, 0.75, 0.6
win = K.box("window_glass", (ww, 0.06, wh), (wx, BACK - 0.05, wz), M["night"], rot=(0, -0.05, 0))
K.box("window_frame", (ww + 0.18, 0.1, wh + 0.18), (wx, BACK - 0.02, wz - 0.09), M["oak"], rot=(0, -0.05, 0))
for i in range(1, 4):
    K.box("window_lead", (0.02, 0.07, wh), (wx - ww / 2 + ww * i / 4, BACK - 0.09, wz), M["lead"], rot=(0, -0.05, 0))
for j in range(1, 3):
    K.box("window_lead", (ww, 0.07, 0.02), (wx, BACK - 0.09, wz + wh * j / 3), M["lead"], rot=(0, -0.05, 0))
K.box("window_sill", (ww + 0.3, 0.2, 0.05), (wx, BACK - 0.12, wz - 0.12), M["oak"])
tag("Window", win)
K.point_light("window_cold", (wx, BACK - 0.5, 1.2), (0.35, 0.45, 0.9), 12, radius=0.4)

# ------------------------------------------------------------ inglenook ----
fx, fw = 0.6, 2.2
K.box("ingle_pier_l", (0.4, 0.6, 1.5), (fx - fw / 2 - 0.1, BACK - 0.3, -0.05), M["brick"], rot=(0, -0.03, 0))
K.box("ingle_pier_r", (0.4, 0.6, 1.5), (fx + fw / 2 + 0.1, BACK - 0.3, -0.05), M["brick"], rot=(0, 0.02, 0))
fire_back = K.box("ingle_back", (fw, 0.4, 1.45), (fx, BACK - 0.15, -0.05), M["soot"])
bress = K.box("bressummer", (fw + 0.7, 0.5, 0.3), (fx, BACK - 0.35, 1.38), M["panel_lit"], rot=(0, -0.045, 0))
K.box("ingle_chimney", (fw + 0.4, 0.5, CEIL - 1.65), (fx, BACK - 0.3, 1.65), M["daub"])
K.box("firedogs", (0.9, 0.3, 0.1), (fx, BACK - 0.4, 0.0), M["iron"])
K.box("logs", (0.8, 0.25, 0.12), (fx, BACK - 0.45, 0.05), M["oak"])
K.box("flames", (0.6, 0.12, 0.34), (fx, BACK - 0.45, 0.12), M["fire"])
K.box("embers", (0.9, 0.3, 0.05), (fx, BACK - 0.4, 0.06), M["embers"])
for i, cx in enumerate((fx - 0.75, fx - 0.25, fx + 0.25, fx + 0.75)):  # horse brasses along the bressummer
    K.cyl("brass", 0.06, 0.03, (cx, BACK - 0.62, 1.47 - 0.045 * (cx - fx)), M["brass"], verts=10).rotation_euler = (1.5708, 0, 0)
K.cyl("kettle", 0.12, 0.2, (fx - 0.65, BACK - 0.45, 0.04), M["copper"], verts=12)
K.box("hearth", (fw + 0.4, 0.8, 0.03), (fx, BACK - 0.75, -0.03), M["brick"])
K.box("hearth_rug", (1.7, 1.0, 0.012), (fx, BACK - 1.55, 0.0), M["rug"])
K.point_light("fire_light", (fx, BACK - 1.4, 0.45), (1.0, 0.42, 0.10), 150, radius=0.5)
tag("Fireplace", fire_back, bress)
# Ursula sleeps on the hearth rug (sprite in game); her marker volume is the hotspot. After she
# moves she lies under the window, by the door.
ursula_at = (fx + 0.05, BACK - 1.45)
ursula_moved_at = (wx - 0.15, BACK - 1.25)
uv = K.box("ursula_vol", (1.15, 0.6, 0.55), (ursula_at[0], ursula_at[1], 0.0), None)
uv.hide_render = True
tag("Ursula", uv)
wedge_at = (fx + 0.4, BACK - 1.55)
wv = K.box("wedge_vol", (0.35, 0.2, 0.16), (wedge_at[0], wedge_at[1], 0.0), None)
wv.hide_render = True
tag("Wedge", wv)
# a high-backed settle beside the fire
K.box("settle_seat", (0.5, 1.4, 0.06), (fx + 1.85, BACK - 1.1, 0.44), M["settle"], rot=(0, 0, 1.5708))
K.box("settle_back", (1.4, 0.08, 1.35), (fx + 1.85, BACK - 0.86, 0.0), M["settle"])

# ------------------------------------------------------- honours board ----
hbx = 2.5
honours = K.box("honours_board", (0.8, 0.05, 0.62), (hbx, BACK - 0.05, 1.42), M["honours"], rot=(0, 0.035, 0))
K.box("honours_title", (0.6, 0.06, 0.06), (hbx, BACK - 0.08, 1.92), M["gold"], rot=(0, 0.035, 0))
for i in range(5):
    K.box("honours_line", (rng.uniform(0.35, 0.6), 0.06, 0.03), (hbx - 0.05, BACK - 0.08, 1.52 + i * 0.07), M["gold"],
          rot=(0, 0.035, 0))
tag("HonoursBoard", honours)

# --------------------------------------------------------- darts corner ----
dbx = 3.55
DB_Z = 1.63    # a touch low: the floor's come up to meet it over the years
cab = K.box("cabinet_back", (0.74, 0.08, 0.76), (dbx, BACK - 0.04, DB_Z - 0.38), M["panel_lit"], rot=(0, -0.03, 0))
board_parts = [cab]
for r, m, dy in ((0.29, "board_black", 0.10), (0.26, "board_red", 0.115), (0.235, "board_black", 0.12),
                 (0.165, "board_green", 0.125), (0.14, "board_cream", 0.13), (0.095, "board_black", 0.135),
                 (0.045, "board_green", 0.14), (0.02, "board_red", 0.145)):
    d = K.cyl("board", r, 0.02, (0, 0, 0), M[m], verts=24)
    d.rotation_euler = (1.5708, 0, 0)
    d.location = (dbx, BACK - dy, DB_Z)
    board_parts.append(d)
K.box("board_lamp", (0.4, 0.2, 0.08), (dbx, BACK - 0.45, DB_Z + 0.48), M["brass"])
K.point_light("board_light", (dbx, BACK - 0.6, DB_Z + 0.4), (1.0, 0.85, 0.6), 12, radius=0.15)
tag("Dartboard", *board_parts)
oche_y = BACK - 0.1 - 2.37
K.box("oche", (1.0, 0.07, 0.025), (dbx, oche_y, 0.0), M["oche"])

# ---------------------------------------------------------- pool table ----
# in the back right-hand corner, behind the walk band. It leans with the floor: the right-hand
# end (towards the river) is lower and the balls have all rolled down to it.
tx, ty = 5.4, 3.0
TL, TD, TH = 2.2, 1.2, 0.8
TILT = 0.035
piv = bpy.data.objects.new("table_pivot", None)
bpy.context.scene.collection.objects.link(piv)
piv.location = (tx, ty, 0)
piv.rotation_euler = (0, TILT, 0)
parts = [
    K.box("table_body", (TL - 0.2, TD - 0.2, 0.32), (0, 0, TH - 0.4), M["rail"]),
    K.box("table_baize", (TL - 0.16, TD - 0.16, 0.06), (0, 0, TH - 0.06), M["baize"]),
]
for side in (-1, 1):
    parts.append(K.box("rail_long", (TL, 0.1, 0.09), (0, side * (TD / 2 - 0.05), TH - 0.05), M["rail"]))
    parts.append(K.box("rail_end", (0.1, TD, 0.09), (side * (TL / 2 - 0.05), 0, TH - 0.05), M["rail"]))
for lx in (-1, 1):
    for ly in (-1, 1):
        parts.append(K.box("table_leg", (0.16, 0.16, TH - 0.36 - (0.05 if lx > 0 else 0)),
                           (lx * (TL / 2 - 0.2), ly * (TD / 2 - 0.2), 0.05 if lx > 0 else 0), M["rail"]))
for i in range(7):  # all the balls, down at the river end
    parts.append(K.cyl("ball", 0.03, 0.06, (TL / 2 - 0.2 - (i % 3) * 0.07, -0.3 + (i // 3) * 0.12 + (i % 2) * 0.05,
                                            TH - 0.01), M["ball_red"] if i % 2 else M["ball_yel"], verts=10))
parts.append(K.cyl("cue_ball", 0.03, 0.06, (TL / 2 - 0.15, 0.32, TH - 0.01), M["ball_white"], verts=10))
for o in parts:
    o.parent = piv
tag("PoolTable", *parts)
K.box("table_lamp", (1.4, 0.32, 0.16), (tx, ty, BEAM_Z - 0.28), M["lamp_shade"])
K.box("table_lamp_glow", (1.3, 0.28, 0.02), (tx, ty, BEAM_Z - 0.3), M["table_glow"])
K.point_light("table_light", (tx, ty, 1.7), (1.0, 0.9, 0.7), 55, radius=0.6)
# the short leg (front, right-hand end): where the wedge goes
short_leg = (tx + TL / 2 - 0.2, ty - TD / 2 + 0.2)
# cue rack and an old photo of the 1974 darts team on the right wall corner
for i in range(3):
    K.box("cue", (0.03, 0.03, 1.4), (7.25 + i * 0.08, BACK - 0.1, 0.05), M["rail"], rot=(0, 0.08 + i * 0.02, 0))

# ---------------------------------------------------------- decoration ----
for (px_, pz, w, h) in ((6.9, 1.7, 0.42, 0.32), (-7.2, 1.6, 0.4, 0.46)):
    K.box("photo_frame", (w, 0.04, h), (px_, BACK - 0.04, pz), M["oak"], rot=(0, rng.uniform(-0.12, 0.12), 0))
    K.box("photo", (w - 0.08, 0.04, h - 0.08), (px_, BACK - 0.06, pz + 0.04), M["photo"], rot=(0, rng.uniform(-0.12, 0.12), 0))
for sx_ in (-6.8, -5.4, -4.0):  # bar stools
    K.cyl("stool_seat", 0.19, 0.05, (sx_, bar_y - 0.75, 0.68), M["rug"], verts=12)
    K.cyl("stool_leg", 0.04, 0.68, (sx_, bar_y - 0.75, 0), M["settle"], verts=8)

# ------------------------------------------------------------- lighting ----
for lx in (-6.6, -1.95, 4.65):
    K.box("wall_lamp", (0.14, 0.1, 0.2), (lx, BACK - 0.1, 1.8), M["lamp_glow"])
    K.point_light("wall_lamp_light", (lx, BACK - 0.5, 1.8), (1.0, 0.66, 0.34), 20, radius=0.2)
for lx in (-4.0, 0.5, 4.0):
    K.point_light("room_light", (lx, 1.2, 2.0), (1.0, 0.68, 0.38), 60, radius=0.5)
for ly in (-0.6, -2.8, -5.2, -8.0):
    for lx in (-5.5, 0.0, 5.5):
        K.point_light("ceiling_wash", (lx, ly, 1.85), (1.0, 0.64, 0.34), 20, radius=0.6)
K.point_light("fill", (0, -5, 1.4), (0.40, 0.48, 0.85), 110, radius=3.0)

# --------------------------------------------------------------- camera ----
# Berkeley Arms camera: eye level just under the beams, figures ~46 px.
cam = K.camera((0.0, -11.0, 2.0), (0.0, 0.0, 2.0), lens=35)
cam.data.shift_y = -0.078

scn = bpy.context.scene
bpy.context.view_layer.update()
if not NO_RENDER:
    scn.render.filepath = os.path.join(OUT, "black_bear.png")
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
ROSIE = (-6.1, bar_y + 0.9)
BERNIE = (dbx + 0.75, 1.15)
fl = [(-8.0, 1.7), (8.0, 1.7), (8.0, -2.4), (-8.0, -2.4)]
floor = [to_px((x, y, 0)) for x, y in fl]
floor = [(min(316, max(4, x)), min(GUI_TOP - 2, y)) for x, y in floor]
data = {
    "hotspots": {k: rect_of(v) for k, v in hot.items()},
    "walk_points": {
        "Bar": to_px((bx0 + 0.6, 1.45, 0)),
        "Pumps": to_px((-4.4, 1.45, 0)),
        "WaterJug": to_px((-3.35, 1.45, 0)),
        "ExitDoor": to_px((ex, 1.6, 0)),
        "Beams": to_px((-2.55, 1.3, 0)),
        "Window": to_px((wx, 1.6, 0)),
        "Fireplace": to_px((fx - 0.4, 1.6, 0)),
        "Ursula": to_px((ursula_at[0] - 0.5, 1.6, 0)),
        "Wedge": to_px((wedge_at[0], 1.6, 0)),
        "HonoursBoard": to_px((hbx, 1.6, 0)),
        "Dartboard": to_px((dbx - 0.3, 1.6, 0)),
        "PoolTable": to_px((tx - 0.6, 1.5, 0)),
        "Rosie": to_px((ROSIE[0] + 0.6, 1.45, 0)),
        "Bernie": to_px((BERNIE[0] - 0.75, BERNIE[1] - 0.2, 0)),
    },
    "npc": {
        "Rosie": to_px(ROSIE + (0,)),
        "Bernie": to_px(BERNIE + (0,)),
    },
    "spawn": {"from_high_st": to_px((ex, 1.35, 0))},
    "floor": [list(p) for p in floor],
    # Ursula's sprite anchors (bottom centre) asleep on the hearth and after she has moved, the
    # wedge where she was lying and under the table's short leg once it's levelled
    "ursula": to_px((ursula_at[0], ursula_at[1] - 0.3, 0)),
    "ursula_moved": to_px((ursula_moved_at[0], ursula_moved_at[1] - 0.3, 0)),
    "wedge": to_px((wedge_at[0], wedge_at[1], 0)),
    "wedge_table": to_px((short_leg[0], short_leg[1], 0)),
    "oche": to_px((dbx, oche_y, 0)),
    "person_px": to_px((0, 1.2, 0))[1] - to_px((0, 1.2, 1.8))[1],
    "dog_px": to_px((0, ursula_at[1], 0))[1] - to_px((0, ursula_at[1], 0.6))[1],
}
with open(os.path.join(OUT, "black_bear.json"), "w") as f:
    json.dump(data, f, indent=1)
print("[blender] wrote", json.dumps(data))
