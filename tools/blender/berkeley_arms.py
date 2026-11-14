"""Inside the Berkeley Arms — Paul's Pub Crawl room background.

    /Applications/Blender.app/Contents/MacOS/Blender -b -P tools/blender/berkeley_arms.py

A 15th-century two-bar pub: low beamed ceiling, close-studded oak walls with limewashed panels,
flagstones, an inglenook, the bar on the left and the darts corner on the right (board in its
cabinet, oche on the floor, chalk scoreboard). The house darts are stuck in a beam over the oche;
they are a separate sprite (they fall when Paul thumps the oak post), so they are not rendered.

The camera sits at 2 m, just under the beams, so the ceiling closes in over the top of the frame;
it is at the Hop Pole's distance so figures are still ~46 px. Everything the player can click is
on the back wall or the floor in plain view (no arches hiding hotspots).

Writes art/renders/berkeley_arms.png + .json (hotspots in 320x200 game px).
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
rng = random.Random(31)

K.reset_scene()
K.world_sky(top=(0.0, 0.0, 0.0), mid=(0.0, 0.0, 0.0), horizon=(0.0, 0.0, 0.0), strength=0.0)

M = {
    "daub": K.mat("daub", (0.66, 0.56, 0.40), noise=0.22, scale=5, bump=0.5),     # limewash, yellowed
    "oak": K.mat("oak", (0.09, 0.05, 0.03), noise=0.35, scale=16, bump=0.6),
    "oak_lit": K.mat("oak_lit", (0.22, 0.12, 0.06), noise=0.3, scale=18, rough=0.45),
    "ceiling": K.mat("ceiling", (0.60, 0.52, 0.38), noise=0.2, scale=4),
    "bar_top": K.mat("bar_top", (0.28, 0.13, 0.05), noise=0.2, scale=20, rough=0.25),
    "brass": K.mat("brass", (0.9, 0.65, 0.25), rough=0.25, noise=0.05),
    "pump": K.mat("pump", (0.92, 0.88, 0.80), rough=0.3, noise=0.05),
    "brick": K.mat("brick", (0.30, 0.16, 0.11), noise=0.3, scale=12, bump=0.6),
    "soot": K.mat("soot", (0.04, 0.035, 0.03), noise=0.2),
    "fire": K.glow_mat("fire", (1.0, 0.42, 0.06), 4.5),
    "embers": K.glow_mat("embers", (1.0, 0.2, 0.02), 3.0),
    "copper": K.mat("copper", (0.75, 0.32, 0.14), rough=0.3, noise=0.1),
    "door": K.mat("door", (0.16, 0.09, 0.05), noise=0.25, scale=14),
    "iron": K.mat("iron", (0.03, 0.03, 0.035), rough=0.5),
    "lamp_glow": K.glow_mat("lamp_glow", (1.0, 0.68, 0.32), 3.0),
    "candle": K.glow_mat("candle", (1.0, 0.8, 0.45), 4.0),
    "table": K.mat("table", (0.20, 0.10, 0.04), noise=0.2, scale=16, rough=0.4),
    "cushion": K.mat("cushion", (0.36, 0.08, 0.06), noise=0.2, scale=10),
    "chalk": K.mat("chalk", (0.05, 0.07, 0.06), noise=0.2),
    "chalk_text": K.mat("chalk_text", (0.88, 0.88, 0.84), noise=0.1, emission=(0.6, 0.6, 0.55), estrength=0.5),
    "board_black": K.mat("board_black", (0.03, 0.03, 0.03), noise=0.1),
    "board_cream": K.mat("board_cream", (0.80, 0.72, 0.55), noise=0.1),
    "board_red": K.mat("board_red", (0.75, 0.08, 0.06), noise=0.05, emission=(0.5, 0.05, 0.03), estrength=0.5),
    "board_green": K.mat("board_green", (0.06, 0.45, 0.16), noise=0.05, emission=(0.03, 0.3, 0.1), estrength=0.5),
    "oche": K.mat("oche", (0.92, 0.88, 0.70), noise=0.05, emission=(0.5, 0.45, 0.3), estrength=0.4),
    "mat_green": K.mat("mat_green", (0.08, 0.18, 0.10), noise=0.2, scale=20),
    "hops": K.mat("hops", (0.42, 0.45, 0.18), noise=0.4, scale=30, bump=0.8),
    "water": K.mat("water", (0.55, 0.75, 0.95), rough=0.05, noise=0.05, emission=(0.35, 0.55, 0.8), estrength=0.8),
    "sign_text": K.mat("sign_text", (0.85, 0.68, 0.25), emission=(0.9, 0.7, 0.3), estrength=0.6),
    "photo": K.mat("photo", (0.45, 0.40, 0.32), noise=0.3, scale=8),
}
bottle_cols = [(0.05, 0.25, 0.08), (0.35, 0.18, 0.04), (0.5, 0.05, 0.05), (0.7, 0.6, 0.2), (0.15, 0.2, 0.4)]
BOTTLES = [K.mat(f"bottle{i}", c, rough=0.1, noise=0.05, emission=c, estrength=0.6) for i, c in enumerate(bottle_cols)]
FLAGS = K.brick_mat("flags", brick=(0.30, 0.26, 0.22), mortar=(0.10, 0.09, 0.08), scale=1.6, vertical=False,
                    brick_width=0.62, row_height=0.42)

hot = {}


def tag(name, *objs):
    hot.setdefault(name, []).extend(objs)


W = 17.0
BACK = 5.0
CEIL = 2.55        # underside of the ceiling boards
BEAM_Z = 2.30      # underside of the cross beams

# ----------------------------------------------------------------- shell ----
K.box("floor", (W + 2, 16, 0.05), (0, -1.5, -0.05), FLAGS)
K.box("back_wall", (W, 0.2, CEIL), (0, BACK + 0.1, 0), M["daub"])
K.box("left_wall", (0.2, 5, CEIL), (-W / 2 - 0.1, 2.5, 0), M["daub"])
K.box("right_wall", (0.2, 5, CEIL), (W / 2 + 0.1, 2.5, 0), M["daub"])
K.box("ceiling", (W + 2, 16, 0.08), (0, -2.5, CEIL), M["ceiling"])
# close-studded oak framing on the back wall: sill, rail, head and studs every ~0.55 m
K.box("wall_sill", (W, 0.08, 0.18), (0, BACK - 0.02, 0), M["oak"])
K.box("wall_rail", (W, 0.08, 0.12), (0, BACK - 0.02, 1.15), M["oak"])
K.box("wall_head", (W, 0.1, 0.2), (0, BACK - 0.03, CEIL - 0.2), M["oak"])
x = -W / 2 + 0.2
while x < W / 2:
    K.box("wall_stud", (0.12, 0.08, CEIL), (x + rng.uniform(-0.03, 0.03), BACK - 0.02, 0), M["oak"])
    x += 0.55
for wx in (-7.8, 7.8):  # side-wall posts
    K.box("corner_post", (0.25, 0.25, CEIL), (wx, BACK - 0.15, 0), M["oak"])
# cross beams with joists between them, low over everyone's head
for by in (-6.4, -3.9, -1.6, 0.4, 1.95, 3.6):
    K.box("beam", (W + 2, 0.32, CEIL - BEAM_Z), (0, by, BEAM_Z), M["oak"])
for jx in range(-9, 10):
    K.box("joist", (0.12, 13.5, 0.1), (jx * 0.95, -3.0, CEIL - 0.1), M["oak"])

# ------------------------------------------------------------------ bar ----
bx0, bw = -5.4, 4.6
bar_y = 2.4
counter = K.box("bar_front", (bw, 0.7, 1.05), (bx0, bar_y, 0), M["oak_lit"])
K.box("bar_top", (bw + 0.2, 0.9, 0.08), (bx0, bar_y, 1.05), M["bar_top"])
K.box("bar_plinth", (bw, 0.74, 0.14), (bx0, bar_y, 0), M["oak"])
for i in range(6):
    K.box("bar_panel", (0.06, 0.05, 0.8), (bx0 - bw / 2 + 0.4 + i * 0.76, bar_y - 0.37, 0.15), M["oak"])
K.box("foot_rail", (bw, 0.06, 0.06), (bx0, bar_y - 0.45, 0.22), M["brass"])
pumps = []
for i, px in enumerate((-5.0, -4.4, -3.8)):
    K.cyl("pump_base", 0.06, 0.12, (px, bar_y - 0.15, 1.13), M["brass"], verts=10)
    pumps.append(K.cyl("pump_handle", 0.045, 0.5, (px, bar_y - 0.15, 1.25), M["pump"], verts=10))
    pumps.append(K.box("pump_clip", (0.15, 0.03, 0.11), (px, bar_y - 0.2, 1.55),
                       K.mat(f"clip{i}", ((0.6, 0.1, 0.08), (0.1, 0.25, 0.5), (0.75, 0.6, 0.15))[i])))
tag("Pumps", *pumps)
# glass water jug and a couple of tumblers at the right-hand end of the bar
jug = K.cyl("water_jug", 0.08, 0.24, (-3.35, bar_y - 0.12, 1.13), M["water"], verts=12)
K.cyl("jug_handle", 0.02, 0.16, (-3.25, bar_y - 0.12, 1.17), M["water"], verts=6)
for gx in (-3.6, -3.52):
    K.cyl("tumbler", 0.035, 0.09, (gx, bar_y - 0.25, 1.13), M["water"], verts=8)
tag("WaterJug", jug)
# back bar: shelves of bottles, a mirror, glasses hanging from the beam
K.box("back_bar", (bw + 0.4, 0.5, 1.0), (bx0, BACK - 0.3, 0), M["oak_lit"])
K.box("bar_mirror", (bw - 0.8, 0.05, 0.5), (bx0, BACK - 0.05, 1.12), K.mat("mirror", (0.30, 0.28, 0.25), rough=0.05))
for sz in (1.65, 2.0):
    K.box("shelf", (bw, 0.28, 0.04), (bx0, BACK - 0.18, sz), M["bar_top"])
    x = bx0 - bw / 2 + 0.25
    while x < bx0 + bw / 2 - 0.25:
        h = rng.uniform(0.18, 0.26)
        K.cyl("bottle", 0.045, h, (x, BACK - 0.18, sz + 0.04), rng.choice(BOTTLES), verts=8)
        x += rng.uniform(0.12, 0.18)
for i in range(9):  # pint pots hanging over the bar
    K.cyl("tankard", 0.05, 0.13, (bx0 - 1.9 + i * 0.45, 3.6, BEAM_Z - 0.16), M["copper"] if i % 3 == 0 else M["brass"], verts=8)
tag("Bar", counter)
K.point_light("bar_light", (bx0, bar_y + 0.4, 2.15), (1.0, 0.70, 0.40), 120, radius=0.5)

# ------------------------------------------------------- snug doorway ----
sx = -2.9
snug = K.box("snug_opening", (0.75, 0.1, 1.8), (sx, BACK - 0.02, 0), K.mat("snug_dark", (0.10, 0.05, 0.03), noise=0.2))
K.box("snug_glow", (0.55, 0.05, 1.2), (sx, BACK + 0.03, 0.2), K.glow_mat("snug_glow", (1.0, 0.55, 0.2), 0.6))
K.box("snug_head", (1.0, 0.14, 0.16), (sx, BACK - 0.06, 1.8), M["oak"])
K.box("snug_sign", (0.6, 0.06, 0.16), (sx, BACK - 0.08, 2.0), M["board_black"])
K.box("snug_sign_text", (0.44, 0.04, 0.06), (sx, BACK - 0.12, 2.05), M["sign_text"])
tag("Snug", snug)

# ----------------------------------------------------- front door (exit) ----
ex = -1.55
door = K.box("exit_door", (0.95, 0.12, 1.85), (ex, BACK - 0.05, 0), M["door"])
for i in range(4):
    K.box("door_plank", (0.025, 0.14, 1.82), (ex - 0.36 + i * 0.24, BACK - 0.07, 0.01), M["oak"])
for hz in (0.4, 1.45):
    K.box("strap_hinge", (0.6, 0.15, 0.05), (ex - 0.15, BACK - 0.08, hz), M["iron"])
K.box("door_latch", (0.1, 0.16, 0.05), (ex + 0.33, BACK - 0.09, 0.95), M["iron"])
K.box("door_light", (0.3, 0.13, 0.22), (ex, BACK - 0.06, 1.45), K.glow_mat("door_window", (0.3, 0.4, 0.75), 0.8))
K.box("door_head", (1.25, 0.16, 0.18), (ex, BACK - 0.08, 1.85), M["oak"])
tag("ExitDoor", door)

# ------------------------------------------------------------- inglenook ----
fx = 0.7
K.box("ingle_pier_l", (0.45, 0.6, 1.55), (fx - 1.05, BACK - 0.3, 0), M["brick"])
K.box("ingle_pier_r", (0.45, 0.6, 1.55), (fx + 1.05, BACK - 0.3, 0), M["brick"])
fire_back = K.box("ingle_back", (1.7, 0.4, 1.5), (fx, BACK - 0.15, 0), M["soot"])
bress = K.box("bressumer", (2.6, 0.5, 0.3), (fx, BACK - 0.35, 1.5), M["oak_lit"])
K.box("ingle_chimney", (2.2, 0.5, 0.75), (fx, BACK - 0.3, 1.8), M["daub"])
K.box("hearth", (2.0, 0.8, 0.06), (fx, BACK - 0.6, 0), M["brick"])
K.box("flames", (0.6, 0.12, 0.34), (fx, BACK - 0.45, 0.12), M["fire"])
K.box("logs", (0.8, 0.25, 0.12), (fx, BACK - 0.45, 0.05), M["oak"])
K.box("embers", (0.9, 0.3, 0.05), (fx, BACK - 0.4, 0.06), M["embers"])
K.point_light("fire_light", (fx, BACK - 1.4, 0.45), (1.0, 0.42, 0.10), 170, radius=0.5)
K.cyl("kettle", 0.12, 0.2, (fx - 0.6, BACK - 0.45, 0.06), M["copper"], verts=12)
for i in range(5):  # horse brasses along the bressumer
    K.cyl("brass", 0.06, 0.03, (fx - 1.0 + i * 0.5, BACK - 0.62, 1.6), M["brass"], verts=10).rotation_euler = (1.5708, 0, 0)
tag("Fireplace", fire_back, bress)
# settle beside the fire
K.box("settle_seat", (1.3, 0.5, 0.08), (fx + 2.0, BACK - 0.45, 0.42), M["oak_lit"])
K.box("settle_back", (1.3, 0.08, 1.2), (fx + 2.0, BACK - 0.2, 0.0), M["oak_lit"])
K.box("settle_cushion", (1.2, 0.45, 0.06), (fx + 2.0, BACK - 0.45, 0.5), M["cushion"])

# --------------------------------------------------- the oak post ----
# A free-standing post holding up the summer beam. Thump it hard enough and the whole ceiling
# shivers (the room script drops the house darts out of the beam over the oche).
ppx, ppy = 1.85, 1.95
post = K.box("oak_post", (0.28, 0.28, BEAM_Z), (ppx, ppy, 0), M["oak_lit"])
K.box("post_base", (0.36, 0.36, 0.12), (ppx, ppy, 0), M["oak"])
for bz, side in ((1.85, -1), (1.85, 1)):  # knee braces up into the beam
    K.box("knee_brace", (0.75, 0.12, 0.12), (ppx + side * 0.3, ppy, bz + 0.12), M["oak"], rot=(0, side * 0.7, 0))
for hz in (1.0, 1.3, 1.6):
    K.cyl("post_brass", 0.055, 0.03, (ppx, ppy - 0.16, hz), M["brass"], verts=10).rotation_euler = (1.5708, 0, 0)
tag("Post", post)

# --------------------------------------------------------- darts corner ----
dbx = 4.85                        # board centre x on the back wall
DB_Z = 1.73                       # regulation bull height
cab = K.box("cabinet_back", (0.78, 0.08, 0.8), (dbx, BACK - 0.04, DB_Z - 0.4), M["oak_lit"])
for side in (-1, 1):  # open cabinet doors, angled out
    K.box("cabinet_door", (0.4, 0.04, 0.8), (dbx + side * 0.58, BACK - 0.16, DB_Z - 0.4), M["oak_lit"],
          rot=(0, 0, side * 0.5))
board_parts = [cab]
# a touch over regulation size (0.45 m) so it still reads as a dartboard at 320x200
for r, m, dy in ((0.30, "board_black", 0.10), (0.27, "board_red", 0.115), (0.245, "board_black", 0.12),
                 (0.17, "board_green", 0.125), (0.145, "board_cream", 0.13), (0.10, "board_black", 0.135),
                 (0.045, "board_green", 0.14), (0.02, "board_red", 0.145)):
    d = K.cyl("board", r, 0.02, (0, 0, 0), M[m], verts=24)
    d.rotation_euler = (1.5708, 0, 0)
    d.location = (dbx, BACK - dy, DB_Z)
    board_parts.append(d)
K.box("board_lamp", (0.4, 0.2, 0.08), (dbx, BACK - 0.45, DB_Z + 0.6), M["brass"])
K.point_light("board_light", (dbx, BACK - 0.6, DB_Z + 0.5), (1.0, 0.85, 0.6), 12, radius=0.15)
tag("Dartboard", *board_parts)
# oche: a brass-edged line 2.37 m from the board face, on a rubber mat
oche_y = BACK - 0.1 - 2.37
K.box("dart_mat", (1.0, 2.3, 0.01), (dbx, oche_y + 1.17, 0.0), M["mat_green"])
oche = K.box("oche", (1.1, 0.07, 0.025), (dbx, oche_y, 0.0), M["oche"])
# chalk scoreboard to the left of the board
sbx = 3.65
score = K.box("scoreboard", (0.62, 0.05, 0.62), (sbx, BACK - 0.06, 1.35), M["chalk"])
K.box("scoreboard_frame", (0.68, 0.04, 0.68), (sbx, BACK - 0.04, 1.32), M["oak"])
K.box("score_rule", (0.03, 0.06, 0.5), (sbx, BACK - 0.09, 1.41), M["chalk_text"])
for i in range(4):
    for side in (-1, 1):
        K.box("score_mark", (rng.uniform(0.12, 0.2), 0.06, 0.03), (sbx + side * 0.15, BACK - 0.09, 1.48 + i * 0.11),
              M["chalk_text"])
K.box("chalk_tray", (0.5, 0.08, 0.03), (sbx, BACK - 0.1, 1.3), M["oak"])
tag("Scoreboard", score)
# the house darts live in the beam over the oche (sprite in game): an unrendered box marks them
darts_at = (dbx - 0.25, 3.6 - 0.16, BEAM_Z)
dv = K.box("beam_darts_vol", (0.6, 0.1, 0.34), (darts_at[0], darts_at[1], BEAM_Z - 0.3), None)
dv.hide_render = True
tag("BeamDarts", dv)

# ---------------------------------------------------------- decoration ----
for i, (px_, pz) in enumerate(((-7.0, 1.45), (6.6, 1.5), (7.4, 1.55))):  # old photos of darts teams
    K.box("photo_frame", (0.42, 0.04, 0.32), (px_, BACK - 0.04, pz), M["oak"])
    K.box("photo", (0.34, 0.04, 0.24), (px_, BACK - 0.06, pz + 0.04), M["photo"])
# dried hops along the summer beam
for i in range(26):
    hx = -7.5 + i * 0.6 + rng.uniform(-0.1, 0.1)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.06, subdivisions=1, location=(hx, 1.75, BEAM_Z - 0.04))
    bpy.context.active_object.data.materials.append(M["hops"])
# a table and stools in the far right corner, clear of the walk band
K.cyl("table_top", 0.4, 0.04, (6.6, 3.9, 0.7), M["table"], verts=16)
K.cyl("table_leg", 0.05, 0.7, (6.6, 3.9, 0), M["table"], verts=8)
K.cyl("candle_jar", 0.05, 0.08, (6.6, 3.9, 0.74), M["candle"], verts=8)
for sx_ in (6.0, 7.2):
    K.cyl("stool", 0.18, 0.5, (sx_, 3.9, 0), M["oak_lit"], verts=10)

# ------------------------------------------------------------- lighting ----
for lx in (-6.6, -2.2, 2.9, 6.9):
    K.box("wall_lamp", (0.14, 0.1, 0.22), (lx, BACK - 0.1, 1.85), M["lamp_glow"])
    K.point_light("wall_lamp_light", (lx, BACK - 0.5, 1.85), (1.0, 0.68, 0.36), 22, radius=0.2)
for lx in (-4.0, 0.5, 4.0):
    K.point_light("room_light", (lx, 1.2, 2.1), (1.0, 0.70, 0.40), 70, radius=0.5)
# warm light up under the near beams so the low ceiling reads instead of going black
for ly in (-0.6, -2.8, -5.2, -8.0):
    for lx in (-5.5, 0.0, 5.5):
        K.point_light("ceiling_wash", (lx, ly, 1.9), (1.0, 0.66, 0.36), 22, radius=0.6)
K.point_light("door_lamp", (ex, BACK - 0.6, 2.05), (1.0, 0.7, 0.4), 25, radius=0.15)
K.point_light("fill", (0, -5, 1.4), (0.40, 0.48, 0.85), 120, radius=3.0)

# --------------------------------------------------------------- camera ----
# Eye level just under the beams: floor at y~1.2 lands on row ~126 and a 1.8 m figure is ~46 px.
cam = K.camera((0.0, -11.0, 2.0), (0.0, 0.0, 2.0), lens=35)
cam.data.shift_y = -0.078

scn = bpy.context.scene
scn.render.filepath = os.path.join(OUT, "berkeley_arms.png")
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
fl = [(-8.0, 1.7), (8.0, 1.7), (8.0, -2.4), (-8.0, -2.4)]
floor = [to_px((x, y, 0)) for x, y in fl]
floor = [(min(316, max(4, x)), min(GUI_TOP - 2, y)) for x, y in floor]
data = {
    "hotspots": {k: rect_of(v) for k, v in hot.items()},
    "walk_points": {
        "Bar": to_px((bx0 + 0.6, 1.45, 0)),
        "Pumps": to_px((-4.4, 1.45, 0)),
        "WaterJug": to_px((-3.35, 1.45, 0)),
        "Snug": to_px((sx, 1.6, 0)),
        "ExitDoor": to_px((ex, 1.6, 0)),
        "Fireplace": to_px((fx, 1.6, 0)),
        "Post": to_px((ppx - 0.5, 1.45, 0)),
        "Scoreboard": to_px((sbx, 1.6, 0)),
        "Dartboard": to_px((dbx - 0.5, 1.6, 0)),
        "BeamDarts": to_px((dbx - 0.6, 1.5, 0)),
        "Clive": to_px((bx0 + 0.4, 1.45, 0)),
        "Dot": to_px((dbx - 0.95, 1.0, 0)),
    },
    "npc": {
        "Clive": to_px((-6.2, bar_y + 0.9, 0)),
        "Dot": to_px((dbx + 0.2, 1.0, 0)),
    },
    "spawn": {"from_street": to_px((ex, 1.35, 0))},
    "floor": [list(p) for p in floor],
    # where the darts sprite hangs: the point on the beam's underside it is stuck into
    "beam_darts": to_px(darts_at),
    "oche": to_px((dbx, oche_y, 0)),
    "person_px": to_px((0, 1.2, 0))[1] - to_px((0, 1.2, 1.8))[1],
}
with open(os.path.join(OUT, "berkeley_arms.json"), "w") as f:
    json.dump(data, f, indent=1)
print("[blender] wrote", scn.render.filepath, json.dumps(data))
