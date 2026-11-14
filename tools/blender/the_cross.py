"""The Cross, Tewkesbury at night — where Church St meets High St and Barton St.

    /Applications/Blender.app/Contents/MacOS/Blender -b -P tools/blender/the_cross.py

Same camera as church_st.py (level at 6 m, lens shift so the pavement is rows ~118-148 and a
1.8 m figure is ~30 px). Left: Church St carries on, with the Berkeley Arms (8 Church St), a low
15th-century black-and-white timber-framed pub. Right: the street opens into the Cross with the
war memorial and High Street running away north; that side is left free for later pubs.

Writes art/renders/the_cross.png + .json (hotspots, walk points, spawns in 320x200 game px).
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
rng = random.Random(23)

K.reset_scene()
K.world_sky(top=(0.01, 0.015, 0.06), mid=(0.10, 0.06, 0.20), horizon=(0.75, 0.30, 0.18), strength=0.45)

M = {
    "plaster": K.mat("plaster", (0.82, 0.78, 0.66), noise=0.16, scale=4),
    "plaster_old": K.mat("plaster_old", (0.80, 0.74, 0.58), noise=0.22, scale=5),
    "beam": K.mat("beam", (0.04, 0.03, 0.025), noise=0.3, scale=20),
    "roof": K.mat("roof", (0.22, 0.10, 0.08), noise=0.35, scale=30, bump=0.8),
    "roof_old": K.mat("roof_old", (0.17, 0.09, 0.07), noise=0.4, scale=34, bump=0.9),
    "slate": K.mat("slate", (0.12, 0.12, 0.16), noise=0.3, scale=30, bump=0.8),
    "frame": K.mat("frame", (0.85, 0.83, 0.78), noise=0.05),
    "lead": K.mat("lead", (0.10, 0.10, 0.12), noise=0.05),
    "glass_lit": K.glow_mat("glass_lit", (1.0, 0.50, 0.15), 2.2),
    "glass_warm": K.glow_mat("glass_warm", (1.0, 0.42, 0.12), 1.8),
    "glass_dark": K.mat("glass_dark", (0.05, 0.06, 0.10), rough=0.15, noise=0.1),
    "door": K.mat("door", (0.10, 0.07, 0.05), noise=0.2, scale=12),
    "iron": K.mat("iron", (0.03, 0.03, 0.035), rough=0.5),
    "lamp": K.glow_mat("lamp", (1.0, 0.75, 0.40), 5.0),
    "stone": K.mat("stone", (0.62, 0.57, 0.48), noise=0.25, scale=3, bump=0.6),
    "stone_dark": K.mat("stone_dark", (0.42, 0.38, 0.34), noise=0.25, scale=3, bump=0.6),
    "asphalt": K.mat("asphalt", (0.07, 0.07, 0.08), noise=0.4, scale=40, bump=0.3),
    "kerb": K.mat("kerb", (0.45, 0.43, 0.40), noise=0.2, scale=10),
    "line_white": K.mat("line_white", (0.85, 0.85, 0.80), noise=0.1),
    "line_yellow": K.mat("line_yellow", (0.85, 0.65, 0.10), noise=0.1),
    "sign_red": K.mat("sign_red", (0.55, 0.06, 0.05), noise=0.1, emission=(0.5, 0.05, 0.03), estrength=0.4),
    "sign_white": K.mat("sign_white", (0.92, 0.90, 0.84), noise=0.05, emission=(0.8, 0.78, 0.7), estrength=0.5),
    "board": K.mat("board", (0.04, 0.04, 0.04), noise=0.1),
    "board_text": K.mat("board_text", (0.88, 0.80, 0.55), emission=(0.9, 0.8, 0.5), estrength=0.7),
    "shop": K.mat("shop", (0.08, 0.14, 0.22), noise=0.1),
    "poppy": K.mat("poppy", (0.75, 0.06, 0.05), noise=0.1),
}
BRICK = K.brick_mat("brick", brick=(0.48, 0.17, 0.10), mortar=(0.62, 0.58, 0.52), scale=2.2)
FLAGS = K.brick_mat("flags", brick=(0.36, 0.34, 0.31), mortar=(0.16, 0.15, 0.14), scale=1.0, vertical=False)

hot = {}


def tag(name, *objs):
    hot.setdefault(name, []).extend(objs)


def tri_panel(name, x0, x1, z0, rise, y, mat):
    """Flat triangle (a gable end) on the plane y, base x0..x1 at z0."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([(x0, y, z0), (x1, y, z0), ((x0 + x1) / 2, y, z0 + rise)], [], [(0, 1, 2)])
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


def leaded_window(x, y_face, z, w, h, glass, cols=4, rows=4):
    """Small-paned leaded casement in a heavy oak frame."""
    K.box("lw_frame", (w + 0.16, 0.1, h + 0.16), (x, y_face - 0.03, z - 0.08), M["beam"])
    K.box("lw_glass", (w, 0.06, h), (x, y_face - 0.07, z), glass)
    for i in range(1, cols):
        K.box("lw_lead", (0.02, 0.07, h), (x - w / 2 + w * i / cols, y_face - 0.1, z), M["lead"])
    for j in range(1, rows):
        K.box("lw_lead", (w, 0.07, 0.02), (x, y_face - 0.1, z + h * j / rows), M["lead"])
    K.box("lw_mullion", (0.06, 0.08, h), (x, y_face - 0.11, z), M["beam"])


def close_stud(x0, x1, z0, z1, y, every=0.42, t=0.12):
    """Close studding: tall oak posts at tight centres, the West Midlands look."""
    K.box("rail", (x1 - x0, 0.07, t), ((x0 + x1) / 2, y - 0.035, z0), M["beam"])
    K.box("rail", (x1 - x0, 0.07, t), ((x0 + x1) / 2, y - 0.035, z1 - t), M["beam"])
    n = max(2, int(round((x1 - x0) / every)) + 1)
    for i in range(n):
        K.box("stud", (t, 0.07, z1 - z0), (x0 + (x1 - x0) * i / (n - 1), y - 0.035, z0), M["beam"])


# --------------------------------------------------------------- ground ----
K.box("road", (70, 16, 0.02), (0, -10, -0.02), M["asphalt"])
K.box("pavement", (21, 3.2, 0.14), (-3.5, -1.6, 0), FLAGS)          # Church St side
K.box("pavement_r", (8, 3.2, 0.14), (16.5, -1.6, 0), FLAGS)        # beyond the High St mouth
K.box("crossing", (5.0, 3.2, 0.02), (10.5, -1.6, 0), M["asphalt"])  # dropped kerb across the mouth
K.box("kerb", (21, 0.25, 0.16), (-3.5, -3.25, 0), M["kerb"])
K.box("kerb_r", (8, 0.25, 0.16), (16.5, -3.25, 0), M["kerb"])
for side_y in (-3.55, -3.7):
    K.box("dyl", (21, 0.08, 0.005), (-3.5, side_y, 0.0), M["line_yellow"])
for i in range(-5, 3):
    K.box("centre_line", (2.2, 0.12, 0.005), (i * 4.5, -9.5, 0.0), M["line_white"])
for i in range(6):  # give-way / zebra stripes across the junction mouth
    K.box("zebra", (0.5, 3.0, 0.006), (8.6 + i * 0.8, -1.6, 0.0), M["line_white"])
# High Street running away north through the mouth of the junction
K.box("high_st_road", (6.0, 50, 0.02), (10.5, 25, -0.02), M["asphalt"])
K.box("high_st_pav_l", (1.6, 50, 0.12), (6.8, 25, 0), FLAGS)
K.box("high_st_pav_r", (1.6, 50, 0.12), (14.2, 25, 0), FLAGS)
for i in range(10):
    K.box("high_st_line", (0.12, 2.0, 0.005), (10.5, 3 + i * 4.5, 0.0), M["line_white"])

# ----------------------------------------------- Church St, left end ----
tudor = {"plaster": M["plaster"], "beam": M["beam"], "roof": M["roof"], "frame": M["frame"],
         "glass_lit": M["glass_lit"], "glass_dark": M["glass_dark"], "door": M["door"]}
K.tudor_house(-11.2, 4.2, 6, 2, rng, tudor, door=True)
K.box("brick_house", (3.0, 7, 6.6), (-7.6, 3.5, 0), BRICK)
K.gable_roof("brick_house_roof", 3.0, 7, 1.6, (-7.6, 3.5, 6.6), M["slate"], ridge_along_x=True)
for wz in (0.9, 3.6):
    K.window(-7.6, 0, wz, 1.0, 1.6, M["frame"], M["glass_lit"] if rng.random() < 0.5 else M["glass_dark"], panes=(2, 3))

# ------------------------------------------------- the Berkeley Arms ----
# Low, two jettied storeys under two street-facing gables; close-studded oak, limewashed panels,
# leaded windows, a low oak door and the Berkeley shield (red, white chevron) on a bracket.
bx0, bx1 = -6.1, 0.9
bw = bx1 - bx0
bcx = (bx0 + bx1) / 2
H1, H2, JET = 2.35, 2.05, 0.4
K.box("bk_ground", (bw, 8, H1), (bcx, 4.0, 0), M["plaster_old"])
close_stud(bx0, bx1, 0.0, H1, 0.0, every=0.45)
K.box("bk_sill_beam", (bw + 0.1, 0.2, 0.22), (bcx, -0.06, 0.0), M["beam"])
K.box("bk_jetty", (bw + 0.15, JET + 0.12, 0.2), (bcx, -JET / 2, H1 - 0.06), M["beam"])
yf = -JET
K.box("bk_upper", (bw + 0.1, 8 + JET, H2), (bcx, yf + (8 + JET) / 2, H1), M["plaster_old"])
close_stud(bx0, bx1, H1, H1 + H2, yf, every=0.5)
K.box("bk_bressumer", (bw + 0.15, 0.14, 0.2), (bcx, yf - 0.05, H1), M["beam"])
# a middle rail with herringbone braces under each upper window
K.box("bk_midrail", (bw, 0.08, 0.1), (bcx, yf - 0.06, H1 + 0.8), M["beam"])
z_top = H1 + H2
gw = bw / 2
for gi, gx in enumerate((bx0 + gw / 2, bx0 + gw * 1.5)):
    K.gable_roof("bk_gable_roof", gw - 0.05, 8 + JET, 2.0, (gx, yf + (8 + JET) / 2, z_top), M["roof_old"],
                 overhang=0.22, ridge_along_x=False)
    tri_panel("bk_gable_face", gx - gw / 2, gx + gw / 2, z_top, 2.0, yf - 0.24, M["plaster_old"])
    K.box("bk_tie", (gw, 0.09, 0.14), (gx, yf - 0.29, z_top), M["beam"])
    K.box("bk_collar", (gw * 0.5, 0.09, 0.12), (gx, yf - 0.29, z_top + 1.0), M["beam"])
    K.box("bk_kingpost", (0.12, 0.09, 1.9), (gx, yf - 0.29, z_top), M["beam"])
    for side in (-1, 1):  # raking bargeboards
        L = math.hypot(gw / 2, 2.0)
        K.box("bk_barge", (L + 0.2, 0.1, 0.14), (gx + side * gw / 4, yf - 0.31, z_top + 0.93), M["beam"],
              rot=(0, side * math.atan2(2.0, gw / 2), 0))
    leaded_window(gx, yf - 0.24, z_top + 0.35, 0.55, 0.55, M["glass_warm"] if gi == 0 else M["glass_dark"], 2, 2)
    leaded_window(gx, yf, H1 + 0.95, 1.35, 0.8, M["glass_lit"] if gi == 1 else M["glass_warm"], 5, 3)
K.box("bk_chimney", (0.8, 0.8, 1.6), (bx0 + gw, 3.5, z_top + 1.2), BRICK)
# ground floor: low door left of centre, two wide leaded bar windows
door_x = bx0 + 1.6
bdoor = K.box("bk_door", (0.95, 0.16, 1.85), (door_x, -0.04, 0.0), M["door"])
for i in range(4):
    K.box("bk_door_plank", (0.03, 0.18, 1.8), (door_x - 0.36 + i * 0.24, -0.06, 0.02), M["beam"])
K.box("bk_door_head", (1.25, 0.2, 0.18), (door_x, -0.08, 1.85), M["beam"])
K.box("bk_door_latch", (0.12, 0.06, 0.05), (door_x + 0.32, -0.15, 0.95), M["iron"])
K.box("bk_step", (1.3, 0.45, 0.1), (door_x, -0.3, 0.0), M["stone"])
leaded_window(door_x - 1.0, 0.0, 0.85, 0.7, 0.8, M["glass_lit"], 2, 3)
leaded_window(bx0 + 3.7, 0.0, 0.8, 1.9, 0.95, M["glass_lit"], 6, 3)
leaded_window(bx0 + 5.95, 0.0, 0.8, 1.2, 0.95, M["glass_warm"], 4, 3)
# name board along the jetty
K.box("bk_nameboard", (3.6, 0.08, 0.3), (bcx + 0.4, -0.13, 1.98), M["board"])
K.box("bk_name_text", (3.0, 0.06, 0.12), (bcx + 0.4, -0.18, 2.07), M["board_text"])
# lantern over the door
K.box("bk_lantern", (0.22, 0.22, 0.3), (door_x, -0.45, 2.0), M["lamp"])
K.point_light("bk_door_light", (door_x, -1.3, 2.2), (1.0, 0.65, 0.3), 45, radius=0.3)
tag("BerkeleyDoor", bdoor)
# hanging sign: the Berkeley shield. Built round an empty and turned to face the street a little,
# otherwise a square-on camera sees a projecting sign edge-on.
sgx = bx1 - 0.5
K.box("bk_sign_arm", (0.07, 1.5, 0.07), (sgx, -0.95, 3.25), M["iron"])
K.box("bk_sign_strut", (0.05, 1.05, 0.05), (sgx, -0.6, 2.9), M["iron"], rot=(-0.6, 0, 0))
piv = bpy.data.objects.new("bk_sign_pivot", None)
bpy.context.scene.collection.objects.link(piv)
piv.location = (sgx, -1.3, 2.1)
piv.rotation_euler = (0, 0, 1.15)
parts = [K.box("bk_sign", (0.08, 0.95, 1.05), (0, 0, 0), M["board"]),
         K.box("bk_shield", (0.1, 0.75, 0.82), (0, 0, 0.1), M["sign_red"])]
for side in (-1, 1):
    parts.append(K.box("bk_chevron", (0.12, 0.42, 0.11), (0, side * 0.15, 0.36), M["sign_white"], rot=(-side * 0.75, 0, 0)))
for (cy, cz) in ((-0.22, 0.7), (0.22, 0.7), (0.0, 0.22), (-0.24, 0.42), (0.24, 0.42)):
    parts.append(K.box("bk_cross", (0.12, 0.09, 0.09), (0, cy, cz), M["sign_white"]))
for o in parts:
    o.parent = piv
K.box("bk_sign_chain", (0.03, 0.03, 0.12), (sgx, -1.3, 3.13), M["iron"])
bpy.context.view_layer.update()
sign = parts[0]
tag("BerkeleySign", sign)

# ------------------------------------------ corner building at the Cross ----
cx0, cx1 = 1.0, 6.0
K.box("corner", (cx1 - cx0, 8, 7.2), ((cx0 + cx1) / 2, 4.0, 0), BRICK)
K.box("corner_cornice", (cx1 - cx0 + 0.3, 0.4, 0.3), ((cx0 + cx1) / 2, -0.1, 6.9), M["stone"])
K.gable_roof("corner_roof", cx1 - cx0, 8, 1.6, ((cx0 + cx1) / 2, 4.0, 7.2), M["slate"], ridge_along_x=True)
K.box("corner_side", (0.2, 8, 7.2), (cx1, 4.0, 0), BRICK)  # flank facing the High St mouth
for wx in (1.9, 3.5, 5.1):
    for wz in (3.1, 5.2):
        K.window(wx, 0, wz, 0.85, 1.35, M["frame"], M["glass_lit"] if rng.random() < 0.35 else M["glass_dark"],
                 panes=(2, 3))
K.box("shopfront", (cx1 - cx0 - 0.4, 0.12, 2.2), ((cx0 + cx1) / 2, -0.05, 0.3), M["shop"])
K.box("shop_fascia", (cx1 - cx0 - 0.2, 0.15, 0.45), ((cx0 + cx1) / 2, -0.1, 2.55), M["board"])
K.window(3.5, 0, 0.6, 2.8, 1.6, M["frame"], M["glass_dark"], panes=(4, 2))

# ----------------------------------------------------- High St receding ----
for i in range(7):
    y0 = 6 + i * 6.5
    for side, x in ((-1, 5.2), (1, 15.8)):
        h = rng.uniform(6.0, 8.5)
        mat = rng.choice([BRICK, M["plaster"], M["stone"]])
        K.box("hs_bldg", (3.0, 6.3, h), (x, y0 + 3.2, 0), mat)
        K.gable_roof("hs_roof", 3.0, 6.3, 1.4, (x, y0 + 3.2, h), M["slate"], ridge_along_x=False)
        for wz in (1.0, 3.6, 5.6):
            if wz + 1.2 < h:
                wx = x - side * 1.52
                gm = M["glass_lit"] if rng.random() < 0.45 else M["glass_dark"]
                K.box("hs_win", (0.08, 0.8, 1.1), (wx, y0 + 2.0, wz), gm)
                K.box("hs_win", (0.08, 0.8, 1.1), (wx, y0 + 4.4, wz), gm)
for i in range(4):
    K.point_light("hs_lamp", (10.5 + (-2.8 if i % 2 else 2.8), 8 + i * 9, 4.5), (1.0, 0.7, 0.4), 300, radius=0.3)
    K.lamp_post(10.5 + (-3.0 if i % 2 else 2.6), 8 + i * 9, {"iron": M["iron"], "lamp": M["lamp"]}, light_energy=0)

# right-hand corner: a timber-framed building on the far side of the High St mouth
K.tudor_house(15.5, 3.6, 6, 2, rng, tudor, door=False)

# ---------------------------------------------------- the war memorial ----
mx, my = 9.4, 6.5
mem = []
for k, (w, h) in enumerate(((3.2, 0.3), (2.5, 0.3), (1.8, 0.3))):
    mem.append(K.box("mem_step", (w, w, h), (mx, my, 0.3 * k), M["stone_dark"]))
mem.append(K.box("mem_plinth", (1.0, 1.0, 1.6), (mx, my, 0.9), M["stone"]))
mem.append(K.box("mem_cap", (1.2, 1.2, 0.2), (mx, my, 2.5), M["stone"]))
mem.append(K.box("mem_shaft", (0.38, 0.38, 3.6), (mx, my, 2.7), M["stone"]))
mem.append(K.box("mem_arm", (1.3, 0.3, 0.3), (mx, my, 5.3), M["stone"]))
K.box("mem_plaque", (0.6, 0.05, 0.7), (mx, my - 0.53, 1.3), M["stone_dark"])
for i in range(5):  # a ring of poppy wreaths on the steps
    a = i / 5 * math.pi + math.pi
    K.cyl("wreath", 0.16, 0.06, (mx + math.cos(a) * 0.8, my + math.sin(a) * 0.8 - 0.4, 0.9), M["poppy"], verts=10)
K.point_light("mem_light", (mx, my - 2.5, 1.0), (0.9, 0.85, 0.75), 90, radius=0.5)
tag("Memorial", *mem)

# ----------------------------------------------------------- street props ----
K.lamp_post(-3.6, -2.75, {"iron": M["iron"], "lamp": M["lamp"]}, light_energy=420)
K.lamp_post(6.6, -2.75, {"iron": M["iron"], "lamp": M["lamp"]}, light_energy=380)
for bxp in (7.6, 13.4):
    K.cyl("bollard", 0.12, 0.9, (bxp, -2.9, 0.14), M["iron"], verts=10)
# fingerpost at the junction: High St (north), Barton St (east), Church St (back the way we came)
fpx, fpy = 7.9, -1.0
K.cyl("fingerpost", 0.05, 2.8, (fpx, fpy, 0.14), M["iron"], verts=8)
FP = K.mat("fp_board", (0.86, 0.84, 0.78), noise=0.05)
for z, ang in ((2.55, 0.35), (2.22, -0.6), (1.9, 2.9)):
    K.box("fp_arm", (0.85, 0.05, 0.19), (fpx + math.cos(ang) * 0.4, fpy + math.sin(ang) * 0.4, z), FP, rot=(0, 0, ang))

# exits: unrendered volumes over the pavement at each edge
to_church = K.box("exit_church", (1.6, 3.0, 2.6), (-8.9, -1.9, 0.14), None)
to_church.hide_render = True
tag("ToChurchSt", to_church)
to_high = K.box("exit_high", (2.4, 3.6, 2.6), (13.2, 1.3, 0.0), None)
to_high.hide_render = True
tag("ToHighSt", to_high)

# ---------------------------------------------------------------- lights ----
K.sun("moon", (0.9, -0.25, 0.5), (0.50, 0.62, 1.0), 0.9)
K.sun("dusk_fill", (1.35, 0.0, 2.6), (1.0, 0.50, 0.30), 0.12)

# ---------------------------------------------------------------- camera ----
cam = K.camera((0.8, -15.0, 6.0), (0.8, 0.0, 6.0), lens=24)
cam.data.shift_y = -0.21

scn = bpy.context.scene
scn.render.filepath = os.path.join(OUT, "the_cross.png")
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
            min(320, int(max(xs)) + pad), min(152, int(max(ys)) + pad)]


GUI_TOP = 150
floor = [to_px((-14, -0.5, 0.14)), to_px((14, -0.5, 0.14)), to_px((14, -6.5, 0)), to_px((-14, -6.5, 0))]
floor = [(min(316, max(4, x)), min(GUI_TOP - 2, y)) for x, y in floor]
data = {
    "hotspots": {k: rect_of(v) for k, v in hot.items()},
    "walk_points": {
        "BerkeleyDoor": to_px((door_x, -1.0, 0.14)),
        "BerkeleySign": to_px((sgx, -2.0, 0.14)),
        "Memorial": to_px((mx, -0.9, 0.14)),
        "ToChurchSt": to_px((-8.3, -2.2, 0.14)),
        "ToHighSt": to_px((11.0, -1.0, 0.14)),
    },
    "spawn": {"from_church_st": to_px((-7.4, -2.2, 0.14)), "from_berkeley": to_px((door_x, -1.2, 0.14))},
    "floor": [list(p) for p in floor],
    "person_px": to_px((0, -2.2, 0.14))[1] - to_px((0, -2.2, 1.94))[1],
}
with open(os.path.join(OUT, "the_cross.json"), "w") as f:
    json.dump(data, f, indent=1)
print("[blender] wrote", scn.render.filepath, json.dumps(data))
