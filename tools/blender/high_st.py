"""High Street, Tewkesbury at night — from the Cross up towards the Mythe.

    /Applications/Blender.app/Contents/MacOS/Blender -b -P tools/blender/high_st.py

Same camera as church_st.py / the_cross.py (level at 6 m, lens shift so the pavement is rows
~118-148 and a 1.8 m figure is ~30 px). The street is squeezed into one frontage so the next
three pubs share a screen, left to right in the order of the crawl:
  - the Britannia Inn (30 High St): a three-storey Georgian red-brick front, sash windows,
    stone cornice and parapet, a painted pub front with the Britannia sign on a bracket
  - the Nottingham Arms (129 High St): jettied black-and-white timber framing with a gable to
    the street and a painted fascia
  - Ye Olde Black Bear (68 High St) at the far (Mythe) end, on the right: very old, crooked
    close-studded timber framing, sagging roofs, leaning posts and the black bear on a gold sign
Georgian brick and timber-framed fronts fill the gaps. The Cross is off the left-hand edge.

Writes art/renders/high_st.png + .json (hotspots, walk points, spawns in 320x200 game px).
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
rng = random.Random(41)

K.reset_scene()
K.world_sky(top=(0.01, 0.015, 0.06), mid=(0.10, 0.06, 0.20), horizon=(0.75, 0.30, 0.18), strength=0.45)

M = {
    "plaster": K.mat("plaster", (0.82, 0.78, 0.66), noise=0.16, scale=4),
    "plaster_old": K.mat("plaster_old", (0.80, 0.74, 0.58), noise=0.22, scale=5),
    "stucco": K.mat("stucco", (0.78, 0.74, 0.64), noise=0.1, scale=3),
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
    "door_green": K.mat("door_green", (0.04, 0.16, 0.10), noise=0.15, scale=12),
    "iron": K.mat("iron", (0.03, 0.03, 0.035), rough=0.5),
    "lamp": K.glow_mat("lamp", (1.0, 0.75, 0.40), 5.0),
    "stone": K.mat("stone", (0.62, 0.57, 0.48), noise=0.25, scale=3, bump=0.6),
    "asphalt": K.mat("asphalt", (0.07, 0.07, 0.08), noise=0.4, scale=40, bump=0.3),
    "kerb": K.mat("kerb", (0.45, 0.43, 0.40), noise=0.2, scale=10),
    "line_white": K.mat("line_white", (0.85, 0.85, 0.80), noise=0.1),
    "line_yellow": K.mat("line_yellow", (0.85, 0.65, 0.10), noise=0.1),
    "pubfront": K.mat("pubfront", (0.05, 0.09, 0.22), noise=0.1, scale=10),      # Britannia navy
    "pubfront_red": K.mat("pubfront_red", (0.30, 0.05, 0.05), noise=0.1, scale=10),  # Nottingham
    "board": K.mat("board", (0.04, 0.04, 0.04), noise=0.1),
    "board_text": K.mat("board_text", (0.88, 0.80, 0.55), emission=(0.9, 0.8, 0.5), estrength=0.7),
    "sign_navy": K.mat("sign_navy", (0.06, 0.12, 0.40), noise=0.1, emission=(0.04, 0.08, 0.3), estrength=0.4),
    "sign_red": K.mat("sign_red", (0.55, 0.06, 0.05), noise=0.1, emission=(0.5, 0.05, 0.03), estrength=0.4),
    "sign_white": K.mat("sign_white", (0.92, 0.90, 0.84), noise=0.05, emission=(0.8, 0.78, 0.7), estrength=0.5),
    "sign_gold": K.mat("sign_gold", (0.85, 0.62, 0.18), noise=0.1, emission=(0.7, 0.5, 0.12), estrength=0.5),
    "bear": K.mat("bear", (0.02, 0.02, 0.02), noise=0.05),
    "shop": K.mat("shop", (0.08, 0.14, 0.22), noise=0.1),
}
BRICK = K.brick_mat("brick", brick=(0.48, 0.17, 0.10), mortar=(0.62, 0.58, 0.52), scale=2.2)
BRICK2 = K.brick_mat("brick2", brick=(0.40, 0.15, 0.10), mortar=(0.55, 0.52, 0.46), scale=2.2)
FLAGS = K.brick_mat("flags", brick=(0.36, 0.34, 0.31), mortar=(0.16, 0.15, 0.14), scale=1.0, vertical=False)

hot = {}


def tag(name, *objs):
    hot.setdefault(name, []).extend(objs)


def tri_panel(name, x0, x1, z0, rise, y, mat, lean=0.0):
    """Flat triangle (a gable end) on the plane y, base x0..x1 at z0; lean shifts the apex."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([(x0, y, z0), (x1, y, z0), ((x0 + x1) / 2 + lean, y, z0 + rise)], [], [(0, 1, 2)])
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


def leaded_window(x, y_face, z, w, h, glass, cols=4, rows=4, tilt=0.0):
    """Small-paned leaded casement in a heavy oak frame (tilt: radians off true, for the Bear)."""
    r = (0, tilt, 0)
    K.box("lw_frame", (w + 0.16, 0.1, h + 0.16), (x, y_face - 0.03, z - 0.08), M["beam"], rot=r)
    K.box("lw_glass", (w, 0.06, h), (x, y_face - 0.07, z), glass, rot=r)
    for i in range(1, cols):
        K.box("lw_lead", (0.02, 0.07, h), (x - w / 2 + w * i / cols, y_face - 0.1, z), M["lead"], rot=r)
    for j in range(1, rows):
        K.box("lw_lead", (w, 0.07, 0.02), (x, y_face - 0.1, z + h * j / rows), M["lead"], rot=r)


def sash(x, y_face, z, w, h, glass):
    """Georgian six-over-six sash with a stone lintel and sill."""
    K.box("sash_frame", (w + 0.1, 0.08, h + 0.1), (x, y_face - 0.02, z - 0.05), M["frame"])
    K.box("sash_glass", (w, 0.06, h), (x, y_face - 0.05, z), glass)
    for i in (1, 2):
        K.box("sash_bar", (0.03, 0.07, h), (x - w / 2 + w * i / 3, y_face - 0.08, z), M["frame"])
    for j in (1, 2, 3):
        K.box("sash_bar", (w, 0.07, 0.03), (x, y_face - 0.08, z + h * j / 4 - 0.015), M["frame"])
    K.box("sash_meet", (w, 0.08, 0.05), (x, y_face - 0.09, z + h / 2 - 0.025), M["frame"])
    K.box("lintel", (w + 0.3, 0.1, 0.18), (x, y_face - 0.04, z + h + 0.05), M["stone"])
    K.box("sill", (w + 0.25, 0.16, 0.07), (x, y_face - 0.07, z - 0.12), M["stone"])


def close_stud(x0, x1, z0, z1, y, every=0.42, t=0.12, lean=0.0, jit=0.0):
    """Close studding; lean tips every stud the same way, jit adds a little crookedness each."""
    K.box("rail", (x1 - x0, 0.07, t), ((x0 + x1) / 2, y - 0.035, z0), M["beam"], rot=(0, lean * 0.3, 0))
    K.box("rail", (x1 - x0, 0.07, t), ((x0 + x1) / 2, y - 0.035, z1 - t), M["beam"], rot=(0, -lean * 0.4, 0))
    n = max(2, int(round((x1 - x0) / every)) + 1)
    for i in range(n):
        a = lean + rng.uniform(-jit, jit)
        K.box("stud", (t, 0.07, z1 - z0), (x0 + (x1 - x0) * i / (n - 1), y - 0.035, z0), M["beam"], rot=(0, a, 0))


def hanging_sign(sx, arm_z, board_mat, face_mats, turn=1.15):
    """Sign on an iron bracket, turned towards the street so the camera doesn't see it edge-on.
    face_mats: list of (size, local loc, material, rot) boxes on the board face."""
    K.box("sign_arm", (0.07, 1.5, 0.07), (sx, -0.95, arm_z), M["iron"])
    K.box("sign_strut", (0.05, 1.05, 0.05), (sx, -0.6, arm_z - 0.35), M["iron"], rot=(-0.6, 0, 0))
    piv = bpy.data.objects.new("sign_pivot", None)
    bpy.context.scene.collection.objects.link(piv)
    piv.location = (sx, -1.3, arm_z - 1.15)
    piv.rotation_euler = (0, 0, turn)
    parts = [K.box("sign_board", (0.08, 0.95, 1.05), (0, 0, 0), M["board"]),
             K.box("sign_face", (0.1, 0.8, 0.9), (0, 0, 0.075), board_mat)]
    for size, loc, m, rot in face_mats:
        parts.append(K.box("sign_bit", size, loc, m, rot=rot))
    for o in parts:
        o.parent = piv
    K.box("sign_chain", (0.03, 0.03, 0.12), (sx, -1.3, arm_z - 0.12), M["iron"])
    return parts


# --------------------------------------------------------------- ground ----
K.box("road", (70, 16, 0.02), (0, -10, -0.02), M["asphalt"])
K.box("pavement", (40, 3.2, 0.14), (1.0, -1.6, 0), FLAGS)
K.box("kerb", (40, 0.25, 0.16), (1.0, -3.25, 0), M["kerb"])
for side_y in (-3.55, -3.7):
    K.box("dyl", (40, 0.08, 0.005), (1.0, side_y, 0.0), M["line_yellow"])
for i in range(-5, 5):
    K.box("centre_line", (2.2, 0.12, 0.005), (i * 4.5, -9.5, 0.0), M["line_white"])

tudor = {"plaster": M["plaster"], "beam": M["beam"], "roof": M["roof"], "frame": M["frame"],
         "glass_lit": M["glass_lit"], "glass_dark": M["glass_dark"], "door": M["door"]}

# ------------------------------------------- left: back towards the Cross ----
K.box("brick_l", (3.6, 7, 7.4), (-10.4, 3.5, 0), BRICK2)
K.gable_roof("brick_l_roof", 3.6, 7, 1.5, (-10.4, 3.5, 7.4), M["slate"], ridge_along_x=True)
for wz in (3.0, 5.2):
    sash(-9.6, 0, wz, 0.8, 1.35, M["glass_dark"] if rng.random() < 0.6 else M["glass_lit"])
K.box("shop_l", (2.8, 0.12, 2.2), (-10.2, -0.05, 0.3), M["shop"])
K.box("shop_l_fascia", (3.2, 0.15, 0.45), (-10.2, -0.1, 2.55), M["board"])

# ------------------------------------------------- the Britannia Inn ----
# 30 High St: three-storey Georgian brick, three bays, a stone cornice and parapet; the ground
# floor is a painted pub front with a central door under a fanlight and two lit bar windows.
bx0, bx1 = -8.2, -2.6
bcx, bw = (bx0 + bx1) / 2, bx1 - bx0
K.box("br_body", (bw, 8, 8.4), (bcx, 4.0, 0), BRICK)
K.box("br_band", (bw + 0.1, 0.12, 0.16), (bcx, -0.04, 2.95), M["stone"])
K.box("br_cornice", (bw + 0.3, 0.45, 0.28), (bcx, -0.12, 7.9), M["stone"])
K.box("br_parapet", (bw, 0.3, 0.6), (bcx, 0.1, 8.15), BRICK)
K.box("br_coping", (bw + 0.1, 0.4, 0.1), (bcx, 0.1, 8.75), M["stone"])
K.gable_roof("br_roof", bw - 0.4, 7.5, 1.3, (bcx, 4.3, 8.4), M["slate"], ridge_along_x=True)
for cxo in (bx0 + 0.4, bx1 - 0.4):
    K.box("br_chimney", (0.7, 0.7, 1.6), (cxo, 2.5, 8.6), BRICK)
for wx in (bcx - 1.75, bcx, bcx + 1.75):
    sash(wx, 0, 3.55, 0.95, 1.6, M["glass_lit"] if wx != bcx + 1.75 else M["glass_dark"])
    sash(wx, 0, 5.95, 0.85, 1.25, M["glass_dark"] if wx != bcx else M["glass_warm"])
# painted pub front: pilasters, fascia, two bar windows and a panelled door with a fanlight
K.box("br_front", (bw - 0.1, 0.14, 2.75), (bcx, -0.07, 0.0), M["pubfront"])
for px in (bx0 + 0.15, bcx - 0.7, bcx + 0.7, bx1 - 0.15):
    K.box("br_pilaster", (0.22, 0.24, 2.75), (px, -0.16, 0.0), M["frame"])
K.box("br_fascia", (bw, 0.3, 0.5), (bcx, -0.2, 2.25), M["pubfront"])
K.box("br_fascia_cap", (bw + 0.2, 0.4, 0.1), (bcx, -0.22, 2.75), M["frame"])
K.box("br_name", (bw - 1.2, 0.06, 0.16), (bcx, -0.37, 2.42), M["board_text"])
for wx in (bcx - 1.75, bcx + 1.75):
    K.window(wx, -0.15, 0.75, 1.6, 1.25, M["frame"], M["glass_lit"], panes=(4, 3))
door_br = bcx
brdoor = K.box("br_door", (0.95, 0.12, 1.95), (door_br, -0.14, 0.0), M["door_green"])
for pz in (0.25, 1.05):
    for pxo in (-0.22, 0.22):
        K.box("br_door_panel", (0.32, 0.03, 0.6), (door_br + pxo, -0.21, pz), M["pubfront"])
K.box("br_fanlight", (0.95, 0.08, 0.32), (door_br, -0.16, 1.98), M["glass_warm"])
K.box("br_step", (1.3, 0.45, 0.12), (door_br, -0.35, 0.0), M["stone"])
K.box("br_lantern", (0.22, 0.22, 0.3), (door_br, -0.5, 2.0), M["lamp"])
K.point_light("br_door_light", (door_br, -1.3, 2.2), (1.0, 0.65, 0.3), 45, radius=0.3)
tag("BritanniaDoor", brdoor)
# the sign: Britannia's shield (white with a red cross) and her gold trident, on navy
sign = hanging_sign(bx1 - 0.5, 3.55, M["sign_navy"], [
    ((0.12, 0.4, 0.48), (0, 0.12, 0.0), M["sign_white"], (0, 0, 0)),
    ((0.14, 0.08, 0.48), (0, 0.12, 0.0), M["sign_red"], (0, 0, 0)),
    ((0.14, 0.4, 0.08), (0, 0.12, 0.05), M["sign_red"], (0, 0, 0)),
    ((0.12, 0.04, 0.8), (0, -0.22, 0.05), M["sign_gold"], (0, 0, 0)),
    ((0.12, 0.2, 0.04), (0, -0.22, 0.34), M["sign_gold"], (0, 0, 0)),
    ((0.12, 0.035, 0.14), (0, -0.31, 0.4), M["sign_gold"], (0, 0, 0)),
    ((0.12, 0.035, 0.14), (0, -0.13, 0.4), M["sign_gold"], (0, 0, 0)),
])
tag("BritanniaSign", sign[0])

# ------------------------------------------------- timber-framed filler ----
K.tudor_house(-1.35, 2.3, 6, 2, rng, tudor, door=False, h1=2.5, h2=2.2, roof_rise=1.8)

# ------------------------------------------------- the Nottingham Arms ----
# 129 High St: two jettied storeys of black-and-white framing under one street gable, with a
# painted fascia and a door on the left. The pool table lives inside.
nx0, nx1 = -0.15, 4.25
ncx, nw = (nx0 + nx1) / 2, nx1 - nx0
NH1, NH2, NJET = 2.6, 2.35, 0.35
K.box("nt_ground", (nw, 8, NH1), (ncx, 4.0, 0), M["plaster"])
close_stud(nx0, nx1, 0.0, NH1, 0.0, every=0.7)
K.box("nt_jetty", (nw + 0.15, NJET + 0.1, 0.2), (ncx, -NJET / 2, NH1 - 0.06), M["beam"])
nyf = -NJET
K.box("nt_upper", (nw + 0.1, 8 + NJET, NH2), (ncx, nyf + (8 + NJET) / 2, NH1), M["plaster"])
K.timber_frame(nx0, nx1, NH1, NH1 + NH2, nyf, M["beam"], rng, braces=True, posts_every=1.1)
K.gable_roof("nt_roof", nw, 8 + NJET, 2.3, (ncx, nyf + (8 + NJET) / 2, NH1 + NH2), M["roof"], overhang=0.25)
tri_panel("nt_gable", nx0, nx1, NH1 + NH2, 2.3, nyf - 0.26, M["plaster"])
K.box("nt_tie", (nw, 0.09, 0.14), (ncx, nyf - 0.3, NH1 + NH2), M["beam"])
K.box("nt_king", (0.12, 0.09, 2.2), (ncx, nyf - 0.3, NH1 + NH2), M["beam"])
for side in (-1, 1):
    L = math.hypot(nw / 2, 2.3)
    K.box("nt_barge", (L + 0.2, 0.1, 0.14), (ncx + side * nw / 4, nyf - 0.32, NH1 + NH2 + 1.07), M["beam"],
          rot=(0, side * math.atan2(2.3, nw / 2), 0))
leaded_window(ncx, nyf - 0.26, NH1 + NH2 + 0.35, 0.7, 0.6, M["glass_warm"], 3, 2)
for wx in (ncx - 1.1, ncx + 1.1):
    leaded_window(wx, nyf, NH1 + 0.75, 1.1, 1.0, M["glass_lit"] if wx < ncx else M["glass_dark"], 4, 3)
K.box("nt_fascia", (nw - 0.2, 0.12, 0.42), (ncx, -0.12, 2.0), M["pubfront_red"])
K.box("nt_name", (nw - 1.0, 0.06, 0.13), (ncx, -0.19, 2.14), M["board_text"])
door_nt = nx0 + 0.9
ntdoor = K.box("nt_door", (0.9, 0.12, 1.85), (door_nt, -0.05, 0.0), M["door"])
for i in range(4):
    K.box("nt_door_plank", (0.03, 0.14, 1.8), (door_nt - 0.33 + i * 0.22, -0.07, 0.02), M["beam"])
K.box("nt_step", (1.2, 0.45, 0.1), (door_nt, -0.3, 0.0), M["stone"])
K.window(ncx + 0.75, 0, 0.75, 2.0, 1.1, M["beam"], M["glass_lit"], panes=(5, 3))
K.point_light("nt_door_light", (door_nt, -1.3, 2.2), (1.0, 0.65, 0.3), 35, radius=0.3)
tag("NottinghamDoor", ntdoor)

# ----------------------------------------------------- Georgian stucco ----
K.box("stucco", (2.6, 7, 6.8), (5.55, 3.5, 0), M["stucco"])
K.box("stucco_cornice", (2.8, 0.35, 0.22), (5.55, -0.08, 6.6), M["stone"])
K.gable_roof("stucco_roof", 2.6, 7, 1.3, (5.55, 3.5, 6.8), M["slate"], ridge_along_x=True)
for wz in (3.0, 5.0):
    sash(5.55, 0, wz, 0.85, 1.35, M["glass_dark"] if wz > 4 else M["glass_lit"])
K.box("stucco_shop", (2.3, 0.12, 2.1), (5.55, -0.05, 0.3), M["shop"])
K.box("stucco_fascia", (2.5, 0.15, 0.4), (5.55, -0.1, 2.45), M["board"])

# ------------------------------------------------ Ye Olde Black Bear ----
# 68 High St, out at the Mythe end: the oldest inn in the county and it looks it. Close-studded
# oak that leans, a jetty that sags, two street gables of different heights, small leaded
# windows set at odd angles, and the black bear on a gold board.
kx0, kx1 = 6.95, 14.5
kcx, kw = (kx0 + kx1) / 2, kx1 - kx0
KH1, KH2, KJET = 2.4, 2.1, 0.45
K.box("bb_ground", (kw, 8, KH1), (kcx, 4.0, 0), M["plaster_old"], rot=(0, 0.012, 0))
close_stud(kx0, kx1, 0.0, KH1, 0.0, every=0.4, lean=0.05, jit=0.05)
K.box("bb_sill", (kw + 0.1, 0.2, 0.22), (kcx, -0.06, 0.0), M["beam"])
K.box("bb_jetty", (kw + 0.2, KJET + 0.12, 0.22), (kcx, -KJET / 2, KH1 - 0.08), M["beam"], rot=(0, -0.02, 0))
kyf = -KJET
K.box("bb_upper", (kw + 0.1, 8 + KJET, KH2), (kcx, kyf + (8 + KJET) / 2, KH1), M["plaster_old"], rot=(0, -0.015, 0))
close_stud(kx0, kx1, KH1, KH1 + KH2, kyf, every=0.45, lean=-0.06, jit=0.06)
K.box("bb_bressumer", (kw + 0.2, 0.14, 0.2), (kcx, kyf - 0.05, KH1), M["beam"], rot=(0, -0.025, 0))
kz = KH1 + KH2
for gi, (gx, gw, rise, lean) in enumerate(((kx0 + 1.7, 3.3, 2.4, 0.25), (kx0 + 5.0, 3.1, 1.9, -0.3))):
    K.gable_roof("bb_gable_roof", gw, 8 + KJET, rise, (gx, kyf + (8 + KJET) / 2, kz - 0.05 * gi), M["roof_old"],
                 overhang=0.25).rotation_euler = (0, 0.03 * (1 if gi else -1), 0)
    tri_panel("bb_gable_face", gx - gw / 2, gx + gw / 2, kz - 0.05 * gi, rise, kyf - 0.27, M["plaster_old"], lean=lean)
    K.box("bb_tie", (gw, 0.09, 0.14), (gx, kyf - 0.31, kz - 0.05 * gi), M["beam"], rot=(0, 0.03, 0))
    K.box("bb_king", (0.12, 0.09, rise - 0.1), (gx + lean * 0.4, kyf - 0.31, kz - 0.05 * gi), M["beam"],
          rot=(0, math.atan2(lean, rise) * 0.8, 0))
    for side in (-1, 1):
        L = math.hypot(gw / 2, rise)
        K.box("bb_barge", (L + 0.2, 0.1, 0.14), (gx + side * gw / 4 + lean * 0.5, kyf - 0.33, kz + rise / 2 - 0.1),
              M["beam"], rot=(0, side * math.atan2(rise, gw / 2), 0))
    leaded_window(gx + lean * 0.3, kyf - 0.27, kz + 0.35, 0.55, 0.5, M["glass_warm"] if gi == 0 else M["glass_dark"],
                  2, 2, tilt=0.06 * (1 if gi else -1))
    leaded_window(gx, kyf, KH1 + 0.6, 1.25, 0.85, M["glass_lit"], 5, 3, tilt=-0.04 if gi == 0 else 0.05)
K.box("bb_chimney", (0.8, 0.8, 1.8), (kx0 + 3.45, 3.0, kz + 1.0), BRICK, rot=(0, 0.06, 0))
door_bb = kx0 + 1.2
bbdoor = K.box("bb_door", (0.9, 0.16, 1.75), (door_bb, -0.04, 0.0), M["door"], rot=(0, 0.03, 0))
for i in range(4):
    K.box("bb_door_plank", (0.03, 0.18, 1.7), (door_bb - 0.33 + i * 0.22, -0.06, 0.02), M["beam"])
K.box("bb_door_head", (1.2, 0.2, 0.18), (door_bb, -0.08, 1.75), M["beam"], rot=(0, -0.05, 0))
K.box("bb_step", (1.2, 0.45, 0.1), (door_bb, -0.3, 0.0), M["stone"])
K.box("bb_lantern", (0.22, 0.22, 0.3), (door_bb, -0.45, 1.9), M["lamp"])
K.point_light("bb_door_light", (door_bb, -1.3, 2.1), (1.0, 0.65, 0.3), 45, radius=0.3)
leaded_window(kx0 + 2.7, 0.0, 0.8, 1.6, 0.9, M["glass_lit"], 6, 3, tilt=0.03)
leaded_window(kx0 + 4.6, 0.0, 0.75, 1.1, 0.95, M["glass_warm"], 4, 3, tilt=-0.05)
K.box("bb_nameboard", (3.4, 0.08, 0.3), (kx0 + 3.6, -0.13, 1.98), M["board"], rot=(0, -0.025, 0))
K.box("bb_name_text", (2.9, 0.06, 0.12), (kx0 + 3.6, -0.18, 2.07), M["board_text"], rot=(0, -0.025, 0))
tag("BlackBearDoor", bbdoor)
# the black bear, standing on its hind legs, on a gold board
hanging_sign(kx0 + 3.0, 3.35, M["sign_gold"], [
    ((0.12, 0.34, 0.42), (0, 0.0, -0.08), M["bear"], (0.15, 0, 0)),     # body
    ((0.12, 0.22, 0.2), (0, 0.06, 0.32), M["bear"], (0, 0, 0)),         # head
    ((0.12, 0.08, 0.08), (0, 0.2, 0.34), M["bear"], (0, 0, 0)),         # snout
    ((0.12, 0.06, 0.07), (0, 0.0, 0.5), M["bear"], (0, 0, 0)),          # ear
    ((0.12, 0.08, 0.3), (0, 0.2, 0.08), M["bear"], (0.9, 0, 0)),        # paw up
    ((0.12, 0.09, 0.22), (0, -0.1, -0.36), M["bear"], (0, 0, 0)),       # legs
    ((0.12, 0.09, 0.22), (0, 0.1, -0.36), M["bear"], (0, 0, 0)),
])

# ----------------------------------------------------------- street props ----
for lx in (-0.9, 5.2, 11.4):
    K.lamp_post(lx, -2.75, {"iron": M["iron"], "lamp": M["lamp"]}, light_energy=380)
for bxp in (-3.3, 8.6):
    K.cyl("bollard", 0.12, 0.9, (bxp, -2.9, 0.14), M["iron"], verts=10)

# exit: unrendered volume over the pavement at the left edge, back to the Cross
to_cross = K.box("exit_cross", (1.6, 3.0, 2.6), (-8.9, -1.9, 0.14), None)
to_cross.hide_render = True
tag("ToTheCross", to_cross)

# ---------------------------------------------------------------- lights ----
K.sun("moon", (0.9, -0.25, 0.5), (0.50, 0.62, 1.0), 0.9)
K.sun("dusk_fill", (1.35, 0.0, 2.6), (1.0, 0.50, 0.30), 0.12)

# ---------------------------------------------------------------- camera ----
cam = K.camera((0.8, -15.0, 6.0), (0.8, 0.0, 6.0), lens=24)
cam.data.shift_y = -0.21

scn = bpy.context.scene
scn.render.filepath = os.path.join(OUT, "high_st.png")
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


bpy.context.view_layer.update()
GUI_TOP = 150
floor = [to_px((-14, -0.5, 0.14)), to_px((14, -0.5, 0.14)), to_px((14, -6.5, 0)), to_px((-14, -6.5, 0))]
floor = [(min(316, max(4, x)), min(GUI_TOP - 2, y)) for x, y in floor]
data = {
    "hotspots": {k: rect_of(v) for k, v in hot.items()},
    "walk_points": {
        "BritanniaDoor": to_px((door_br, -1.0, 0.14)),
        "BritanniaSign": to_px((bx1 - 0.5, -2.0, 0.14)),
        "NottinghamDoor": to_px((door_nt, -1.0, 0.14)),
        "BlackBearDoor": to_px((door_bb, -1.0, 0.14)),
        "ToTheCross": to_px((-8.3, -2.2, 0.14)),
    },
    "spawn": {
        "from_the_cross": to_px((-7.4, -2.2, 0.14)),
        "from_britannia": to_px((door_br, -1.2, 0.14)),
        "from_nottingham": to_px((door_nt, -1.2, 0.14)),
        "from_black_bear": to_px((door_bb, -1.2, 0.14)),
    },
    "floor": [list(p) for p in floor],
    "person_px": to_px((0, -2.2, 0.14))[1] - to_px((0, -2.2, 1.94))[1],
}
with open(os.path.join(OUT, "high_st.json"), "w") as f:
    json.dump(data, f, indent=1)
print("[blender] wrote", scn.render.filepath, json.dumps(data))
