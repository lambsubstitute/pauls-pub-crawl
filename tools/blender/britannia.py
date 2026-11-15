"""Inside the Britannia Inn — Paul's Pub Crawl room background.

    /Applications/Blender.app/Contents/MacOS/Blender -b -P tools/blender/britannia.py

30 High St: a Georgian front bar. Navy-painted panelled dado, red flock wallpaper above a picture
rail, a plaster ceiling with a cornice, scrubbed floorboards. Bar on the left (Gwen behind it,
three pumps and a water jug). Along the back wall: the street door, a 1990s "Magic Eye" picture
that nobody can see the hidden image in (a bare stretch of wallpaper beside it is where the
double-vision copy floats), a long-case clock, the shove ha'penny table with its board tipped up
for the camera and the chalked rules above it, and a curtained sash window.

Camera as the Berkeley Arms/Hop Pole: figures ~46 px, floor rows ~124-147.

Writes art/renders/britannia.png + .json (hotspots in 320x200 game px).
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
rng = random.Random(44)

K.reset_scene()
K.world_sky(top=(0.0, 0.0, 0.0), mid=(0.0, 0.0, 0.0), horizon=(0.0, 0.0, 0.0), strength=0.0)

M = {
    "paper": K.mat("paper", (0.42, 0.08, 0.08), noise=0.3, scale=26, bump=0.4),      # red flock
    "dado": K.mat("dado", (0.07, 0.11, 0.24), noise=0.12, scale=8, rough=0.4),       # navy paint
    "trim": K.mat("trim", (0.86, 0.82, 0.72), noise=0.05, rough=0.4),
    "ceiling": K.mat("ceiling", (0.78, 0.72, 0.60), noise=0.12, scale=4),
    "oak": K.mat("oak", (0.12, 0.06, 0.03), noise=0.3, scale=16, bump=0.5),
    "mahog": K.mat("mahog", (0.26, 0.09, 0.04), noise=0.25, scale=18, rough=0.3),
    "bar_top": K.mat("bar_top", (0.30, 0.12, 0.05), noise=0.2, scale=20, rough=0.25),
    "brass": K.mat("brass", (0.9, 0.65, 0.25), rough=0.25, noise=0.05),
    "pump": K.mat("pump", (0.92, 0.88, 0.80), rough=0.3, noise=0.05),
    "door": K.mat("door", (0.08, 0.20, 0.13), noise=0.2, scale=14),
    "iron": K.mat("iron", (0.03, 0.03, 0.035), rough=0.5),
    "lamp_glow": K.glow_mat("lamp_glow", (1.0, 0.70, 0.36), 3.0),
    "water": K.mat("water", (0.55, 0.75, 0.95), rough=0.05, noise=0.05, emission=(0.35, 0.55, 0.8), estrength=0.8),
    "clock_face": K.mat("clock_face", (0.90, 0.86, 0.74), noise=0.05, emission=(0.5, 0.48, 0.4), estrength=0.3),
    "slate": K.mat("slate", (0.20, 0.07, 0.03), noise=0.15, scale=12, rough=0.55),     # polished mahogany board
    "chalk": K.mat("chalk", (0.05, 0.07, 0.06), noise=0.2),
    "chalk_text": K.mat("chalk_text", (0.88, 0.88, 0.84), noise=0.1, emission=(0.6, 0.6, 0.55), estrength=0.5),
    "curtain": K.mat("curtain", (0.36, 0.30, 0.10), noise=0.25, scale=14),
    "night": K.glow_mat("night", (0.10, 0.16, 0.38), 0.6),
    "gilt": K.mat("gilt", (0.75, 0.55, 0.20), rough=0.3, noise=0.15),
    "print": K.mat("print", (0.55, 0.50, 0.38), noise=0.3, scale=8),
    "sea": K.mat("sea", (0.15, 0.28, 0.40), noise=0.3, scale=10),
    "table": K.mat("table", (0.20, 0.10, 0.04), noise=0.2, scale=16, rough=0.4),
    "candle": K.glow_mat("candle", (1.0, 0.8, 0.45), 4.0),
}
bottle_cols = [(0.05, 0.25, 0.08), (0.35, 0.18, 0.04), (0.5, 0.05, 0.05), (0.7, 0.6, 0.2), (0.15, 0.2, 0.4)]
BOTTLES = [K.mat(f"bottle{i}", c, rough=0.1, noise=0.05, emission=c, estrength=0.6) for i, c in enumerate(bottle_cols)]
BOARDS = K.brick_mat("boards", brick=(0.36, 0.22, 0.12), mortar=(0.12, 0.07, 0.04), scale=1.4, vertical=False,
                     brick_width=1.6, row_height=0.14)


def magic_eye_mat():
    """Random-dot stereogram: tight bright noise through a rainbow ramp (it dithers into dots)."""
    m = bpy.data.materials.new("magic_eye")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 0.85
    tex = nt.nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = 16.0
    tex.inputs["Detail"].default_value = 0.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.interpolation = "CONSTANT"
    cols = [(0.9, 0.1, 0.6), (0.1, 0.7, 0.9), (0.95, 0.85, 0.1), (0.2, 0.85, 0.3), (0.6, 0.2, 0.9)]
    cr.elements[0].color = (*cols[0], 1)
    cr.elements[1].position = 0.6
    cr.elements[1].color = (*cols[-1], 1)
    for i, c in enumerate(cols[1:-1]):
        e = cr.elements.new(0.42 + i * 0.05)
        e.color = (*c, 1)
    nt.links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


hot = {}


def tag(name, *objs):
    hot.setdefault(name, []).extend(objs)


W = 17.0
BACK = 5.0
CEIL = 3.0
DADO = 1.0
RAIL = 2.2

# ----------------------------------------------------------------- shell ----
K.box("floor", (W + 2, 16, 0.05), (0, -1.5, -0.05), BOARDS)
K.box("back_wall", (W, 0.2, CEIL), (0, BACK + 0.1, 0), M["paper"])
K.box("left_wall", (0.2, 5, CEIL), (-W / 2 - 0.1, 2.5, 0), M["paper"])
K.box("right_wall", (0.2, 5, CEIL), (W / 2 + 0.1, 2.5, 0), M["paper"])
K.box("ceiling", (W + 2, 16, 0.08), (0, -2.5, CEIL), M["ceiling"])
K.box("dado", (W, 0.06, DADO), (0, BACK - 0.01, 0), M["dado"])
K.box("dado_rail", (W, 0.1, 0.07), (0, BACK - 0.04, DADO), M["trim"])
K.box("skirting", (W, 0.08, 0.18), (0, BACK - 0.05, 0), M["trim"])
K.box("picture_rail", (W, 0.08, 0.05), (0, BACK - 0.03, RAIL), M["trim"])
K.box("cornice", (W, 0.3, 0.22), (0, BACK - 0.1, CEIL - 0.22), M["trim"])
x = -W / 2 + 0.3
while x < W / 2:
    K.box("dado_stile", (0.05, 0.08, DADO - 0.2), (x, BACK - 0.05, 0.15), M["trim"])
    x += 0.7
K.box("ceiling_rose", (0.6, 0.6, 0.06), (0.5, 0.8, CEIL - 0.06), M["trim"])
for by in (-4.5, -1.2, 2.2):  # boxed plaster beams break up the flat ceiling
    K.box("ceiling_beam", (W + 2, 0.4, 0.25), (0, by, CEIL - 0.25), M["trim"])
    K.box("ceiling_beam_shadow", (W + 2, 0.06, 0.04), (0, by - 0.23, CEIL - 0.29), M["oak"])

# ------------------------------------------------------------------ bar ----
bx0, bw = -5.4, 4.6
bar_y = 2.4
counter = K.box("bar_front", (bw, 0.7, 1.05), (bx0, bar_y, 0), M["mahog"])
K.box("bar_top", (bw + 0.2, 0.9, 0.08), (bx0, bar_y, 1.05), M["bar_top"])
K.box("bar_plinth", (bw, 0.74, 0.14), (bx0, bar_y, 0), M["oak"])
for i in range(6):
    K.box("bar_panel", (0.6, 0.05, 0.6), (bx0 - bw / 2 + 0.45 + i * 0.74, bar_y - 0.37, 0.25), M["oak"])
K.box("foot_rail", (bw, 0.06, 0.06), (bx0, bar_y - 0.45, 0.22), M["brass"])
pumps = []
for i, px in enumerate((-5.0, -4.4, -3.8)):
    K.cyl("pump_base", 0.06, 0.12, (px, bar_y - 0.15, 1.13), M["brass"], verts=10)
    pumps.append(K.cyl("pump_handle", 0.045, 0.5, (px, bar_y - 0.15, 1.25), M["pump"], verts=10))
    pumps.append(K.box("pump_clip", (0.15, 0.03, 0.11), (px, bar_y - 0.2, 1.55),
                       K.mat(f"clip{i}", ((0.1, 0.2, 0.55), (0.6, 0.1, 0.08), (0.75, 0.6, 0.15))[i])))
tag("Pumps", *pumps)
jug = K.cyl("water_jug", 0.08, 0.24, (-3.35, bar_y - 0.12, 1.13), M["water"], verts=12)
K.cyl("jug_handle", 0.02, 0.16, (-3.25, bar_y - 0.12, 1.17), M["water"], verts=6)
for gx in (-3.6, -3.52):
    K.cyl("tumbler", 0.035, 0.09, (gx, bar_y - 0.25, 1.13), M["water"], verts=8)
tag("WaterJug", jug)
K.box("back_bar", (bw + 0.4, 0.5, 1.0), (bx0, BACK - 0.3, 0), M["mahog"])
K.box("bar_mirror", (bw - 0.8, 0.05, 0.7), (bx0, BACK - 0.05, 1.15), K.mat("mirror", (0.30, 0.28, 0.25), rough=0.05))
K.box("bar_mirror_frame", (bw - 0.6, 0.06, 0.08), (bx0, BACK - 0.06, 1.88), M["gilt"])
for sz in (1.95, 2.35):
    K.box("shelf", (bw, 0.28, 0.04), (bx0, BACK - 0.18, sz), M["bar_top"])
    x = bx0 - bw / 2 + 0.25
    while x < bx0 + bw / 2 - 0.25:
        h = rng.uniform(0.18, 0.26)
        K.cyl("bottle", 0.045, h, (x, BACK - 0.18, sz + 0.04), rng.choice(BOTTLES), verts=8)
        x += rng.uniform(0.12, 0.18)
tag("Bar", counter)
K.point_light("bar_light", (bx0, bar_y + 0.4, 2.4), (1.0, 0.70, 0.40), 140, radius=0.5)

# ----------------------------------------------------- front door (exit) ----
ex = -2.2
door = K.box("exit_door", (1.0, 0.12, 2.1), (ex, BACK - 0.05, 0), M["door"])
for pz in (0.2, 1.15):
    for pxo in (-0.23, 0.23):
        K.box("door_panel", (0.34, 0.03, 0.75), (ex + pxo, BACK - 0.12, pz), K.mat("door_panel", (0.06, 0.15, 0.10)))
K.box("door_knob", (0.07, 0.06, 0.07), (ex + 0.38, BACK - 0.14, 1.0), M["brass"])
K.box("fanlight", (1.0, 0.1, 0.32), (ex, BACK - 0.05, 2.14), K.glow_mat("fan", (0.30, 0.40, 0.75), 0.8))
K.box("architrave", (1.3, 0.14, 0.12), (ex, BACK - 0.08, 2.5), M["trim"])
for side in (-0.6, 0.6):
    K.box("door_post", (0.1, 0.14, 2.5), (ex + side, BACK - 0.08, 0), M["trim"])
tag("ExitDoor", door)

# ------------------------------------------------------- the Magic Eye ----
# A random-dot stereogram in a gilt frame. The hidden picture only shows if your eyes go
# out of step... A plain run of wallpaper to its right is where the ghost copy appears (sprite).
mex, mez = -0.6, 1.25
mew, meh = 0.95, 0.72
K.box("me_frame", (mew + 0.14, 0.05, meh + 0.14), (mex, BACK - 0.03, mez - 0.07), M["gilt"])
me = K.box("magic_eye", (mew, 0.04, meh), (mex, BACK - 0.06, mez), magic_eye_mat())
K.box("me_label", (0.36, 0.03, 0.06), (mex, BACK - 0.06, mez - 0.18), M["trim"])
tag("MagicEye", me)
GHOST_DX = 1.25    # metres along the wall; the room script draws the ghost copy this far right
ghost_vol = K.box("ghost_vol", (mew, 0.04, meh), (mex + GHOST_DX, BACK - 0.06, mez), None)
ghost_vol.hide_render = True
tag("GhostPicture", ghost_vol)

# ------------------------------------------------------- long-case clock ----
ckx = 2.0
clock = [K.box("clock_base", (0.55, 0.32, 0.6), (ckx, BACK - 0.2, 0), M["mahog"]),
         K.box("clock_trunk", (0.42, 0.28, 1.05), (ckx, BACK - 0.2, 0.6), M["mahog"]),
         K.box("clock_hood", (0.56, 0.34, 0.55), (ckx, BACK - 0.2, 1.65), M["mahog"])]
K.box("clock_door", (0.26, 0.03, 0.8), (ckx, BACK - 0.36, 0.72), M["oak"])
K.box("clock_pendulum_glass", (0.08, 0.02, 0.12), (ckx, BACK - 0.38, 0.9), M["brass"])
K.box("clock_pediment", (0.6, 0.36, 0.1), (ckx, BACK - 0.2, 2.2), M["gilt"])
face = K.cyl("clock_face", 0.17, 0.02, (0, 0, 0), M["clock_face"], verts=20)
face.location = (ckx, BACK - 0.38, 1.92)
face.rotation_euler = (1.5708, 0, 0)
K.box("clock_hand", (0.02, 0.01, 0.12), (ckx, BACK - 0.4, 1.9), M["iron"])
K.box("clock_hand2", (0.09, 0.01, 0.02), (ckx + 0.04, BACK - 0.4, 1.91), M["iron"])
tag("Clock", *clock)

# --------------------------------------------------------- ship print ----
for (px_, pz, pw, ph) in ((3.35, 1.55, 0.6, 0.45),):
    K.box("print_frame", (pw + 0.1, 0.04, ph + 0.1), (px_, BACK - 0.03, pz - 0.05), M["gilt"])
    K.box("print_sky", (pw, 0.04, ph * 0.55), (px_, BACK - 0.05, pz + ph * 0.45), M["print"])
    K.box("print_sea", (pw, 0.04, ph * 0.45), (px_, BACK - 0.05, pz), M["sea"])
    K.box("print_hull", (0.3, 0.03, 0.06), (px_, BACK - 0.07, pz + 0.18), M["oak"])
    K.box("print_sail", (0.18, 0.03, 0.18), (px_, BACK - 0.07, pz + 0.24), M["trim"])

# ---------------------------------------------------- shove ha'penny ----
# A sturdy table against the wall with the board on it, tipped up towards the camera (and a bit
# over-size) so the brass bed lines read at 320x200. Chalked rules on a slate above.
shx = 4.75
K.box("sh_table_top", (1.3, 0.75, 0.06), (shx, BACK - 0.55, 0.74), M["table"])
for lx in (-0.55, 0.55):
    for ly in (-0.3, 0.3):
        K.box("sh_table_leg", (0.07, 0.07, 0.74), (shx + lx, BACK - 0.55 + ly, 0), M["table"])
bpiv = bpy.data.objects.new("sh_board_pivot", None)
bpy.context.scene.collection.objects.link(bpiv)
bpiv.location = (shx, BACK - 0.6, 0.8)
bpiv.rotation_euler = (0.85, 0, 0)     # tipped up towards the camera
board_parts = [K.box("sh_board", (1.15, 0.7, 0.04), (0, 0, 0), M["slate"])]
for i in range(10):  # the bed lines, near to far
    board_parts.append(K.box("sh_line", (0.86, 0.02, 0.012), (0, -0.24 + i * 0.054, 0.04), M["brass"]))
for side in (-1, 1):  # side lines for the chalk scoring columns
    board_parts.append(K.box("sh_side", (0.02, 0.5, 0.012), (side * 0.43, 0.0, 0.04), M["brass"]))
board_parts.append(K.box("sh_stop", (1.15, 0.04, 0.08), (0, -0.35, 0.0), M["oak"]))  # lip at the near end
for o in board_parts:
    o.parent = bpiv
for i in range(3):  # a couple of ha'pennies on the board
    K.cyl("sh_coin", 0.025, 0.01, (shx - 0.2 + i * 0.17, BACK - 0.55, 0.8 + i * 0.06), M["brass"], verts=10)
tag("ShoveBoard", *board_parts)
rules = K.box("sh_rules", (0.8, 0.05, 0.55), (shx, BACK - 0.05, 1.45), M["chalk"])
K.box("sh_rules_frame", (0.86, 0.04, 0.61), (shx, BACK - 0.03, 1.42), M["oak"])
for i in range(4):
    K.box("sh_rule_line", (rng.uniform(0.35, 0.6), 0.06, 0.03), (shx - 0.05, BACK - 0.09, 1.55 + i * 0.1), M["chalk_text"])
K.point_light("sh_lamp", (shx, BACK - 0.9, 2.0), (1.0, 0.85, 0.6), 35, radius=0.2)

# --------------------------------------------------------------- window ----
wx = 7.55
window = K.box("win_night", (1.0, 0.05, 1.35), (wx, BACK - 0.02, 0.95), M["night"])
for i in (1, 2):
    K.box("win_bar", (0.03, 0.07, 1.35), (wx - 0.5 + i / 3, BACK - 0.06, 0.95), M["trim"])
for j in (1, 2, 3):
    K.box("win_bar", (1.0, 0.07, 0.03), (wx, BACK - 0.06, 0.95 + 1.35 * j / 4), M["trim"])
K.box("win_case", (1.15, 0.1, 1.5), (wx, BACK - 0.01, 0.88), M["trim"])
for side in (-1, 1):
    K.box("curtain", (0.35, 0.12, 1.75), (wx + side * 0.62, BACK - 0.12, 0.65), M["curtain"])
K.box("pelmet", (1.7, 0.16, 0.18), (wx, BACK - 0.12, 2.42), M["curtain"])
tag("Window", window)
# settle under the window
K.box("settle_seat", (1.4, 0.5, 0.08), (wx - 0.2, BACK - 0.45, 0.42), M["mahog"])
K.box("settle_back", (1.4, 0.08, 0.5), (wx - 0.2, BACK - 0.2, 0.42), M["mahog"])

# ------------------------------------------------------------- lighting ----
for lx in (-6.8, 1.45, 4.05, 8.0):
    K.box("wall_lamp", (0.14, 0.1, 0.22), (lx, BACK - 0.1, 2.0), M["lamp_glow"])
    K.point_light("wall_lamp_light", (lx, BACK - 0.5, 2.0), (1.0, 0.68, 0.36), 26, radius=0.2)
for lx in (-4.0, 0.5, 4.5):
    K.point_light("room_light", (lx, 1.2, 2.6), (1.0, 0.72, 0.42), 90, radius=0.5)
for ly in (-0.6, -3.0, -6.0):
    for lx in (-5.5, 0.0, 5.5):
        K.point_light("ceiling_wash", (lx, ly, 1.7), (1.0, 0.68, 0.40), 14, radius=1.2)
# two brass pendant lamps on chains, so the plain Georgian ceiling has something in it
for lx, ly in ((-3.2, 0.6), (3.6, 0.6)):
    K.box("pendant_chain", (0.02, 0.02, 0.5), (lx, ly, CEIL - 0.5), M["iron"])
    K.cyl("pendant_shade", 0.22, 0.14, (lx, ly, CEIL - 0.66), M["brass"], verts=14)
    K.cyl("pendant_bulb", 0.12, 0.08, (lx, ly, CEIL - 0.74), M["lamp_glow"], verts=10)
    K.point_light("pendant_light", (lx, ly, CEIL - 0.85), (1.0, 0.72, 0.42), 40, radius=0.3)
K.point_light("fill", (0, -5, 1.4), (0.40, 0.48, 0.85), 120, radius=3.0)

# --------------------------------------------------------------- camera ----
cam = K.camera((0.0, -11.0, 2.0), (0.0, 0.0, 2.0), lens=35)
cam.data.shift_y = -0.078

scn = bpy.context.scene
scn.render.filepath = os.path.join(OUT, "britannia.png")
bpy.ops.render.render(write_still=True)
bpy.context.view_layer.update()


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
me_px = rect_of([me], pad=0)
data = {
    "hotspots": {k: rect_of(v) for k, v in hot.items()},
    "walk_points": {
        "Bar": to_px((bx0 + 0.6, 1.45, 0)),
        "Pumps": to_px((-4.4, 1.45, 0)),
        "WaterJug": to_px((-3.35, 1.45, 0)),
        "ExitDoor": to_px((ex, 1.6, 0)),
        "MagicEye": to_px((mex, 1.5, 0)),
        "GhostPicture": to_px((mex + 0.4, 1.5, 0)),
        "Clock": to_px((ckx - 0.5, 1.5, 0)),
        "ShoveBoard": to_px((shx - 0.65, 1.45, 0)),
        "Window": to_px((wx - 0.9, 1.5, 0)),
        "Gwen": to_px((bx0 + 0.4, 1.45, 0)),
        "Stan": to_px((4.15, 1.1, 0)),
    },
    "npc": {
        "Gwen": to_px((-6.2, bar_y + 0.9, 0)),
        "Stan": to_px((5.0, 1.0, 0)),
    },
    "spawn": {"from_street": to_px((ex, 1.35, 0))},
    "floor": [list(p) for p in floor],
    # the Magic Eye in game px and how far right its double-vision copy floats
    "magic_eye": me_px,
    "ghost_dx": round(to_px((mex + GHOST_DX, BACK - 0.06, mez))[0] - to_px((mex, BACK - 0.06, mez))[0]),
    "person_px": to_px((0, 1.2, 0))[1] - to_px((0, 1.2, 1.8))[1],
}
with open(os.path.join(OUT, "britannia.json"), "w") as f:
    json.dump(data, f, indent=1)
print("[blender] wrote", scn.render.filepath, json.dumps(data))
