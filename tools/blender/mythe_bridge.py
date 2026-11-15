"""The Mythe Bridge at night — Paul's Pub Crawl ending scene.

    /Applications/Blender.app/Contents/MacOS/Blender -b -P tools/blender/mythe_bridge.py

Telford's Mythe Bridge (1826): a single 170 ft cast-iron arch over the Severn just north of
Tewkesbury, with open lattice spandrels and stone approaches pierced by little flood arches, and
a toll house at the Tewkesbury end. Paul stands on the riverside path on the Tewkesbury bank;
the bridge springs from this bank on the right and crosses to the far bank away to the left, so
its downstream face is seen in perspective over the moonlit river.

Same street camera as church_st.py / high_st.py (6 m up, lens shift, path rows ~118-148, a
1.8 m figure ~30 px). Writes art/renders/mythe_bridge.png + .json (hotspots, walk points,
spawns, and the deck line the ending's car drives along, in 320x200 game px).
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
rng = random.Random(1826)
NO_RENDER = os.environ.get("NO_RENDER") == "1"

K.reset_scene()
K.world_sky(top=(0.005, 0.01, 0.045), mid=(0.04, 0.05, 0.14), horizon=(0.16, 0.14, 0.26), strength=0.5)

M = {
    "iron": K.mat("iron", (0.10, 0.11, 0.13), rough=0.45, noise=0.15, scale=20),
    "iron_lit": K.mat("iron_lit", (0.30, 0.32, 0.38), rough=0.35, noise=0.1, scale=20),
    "stone": K.mat("stone", (0.44, 0.40, 0.34), noise=0.3, scale=3, bump=0.7),
    "stone_dark": K.mat("stone_dark", (0.03, 0.03, 0.04), noise=0.1),
    "deck": K.mat("deck", (0.12, 0.12, 0.13), noise=0.3, scale=20),
    "water": K.mat("water", (0.02, 0.05, 0.12), rough=0.08, noise=0.25, scale=3, bump=0.2,
                   emission=(0.01, 0.025, 0.07), estrength=0.6),
    "glint": K.glow_mat("glint", (0.75, 0.80, 0.95), 1.4),
    "glint_warm": K.glow_mat("glint_warm", (1.0, 0.65, 0.3), 1.0),
    "grass": K.mat("grass", (0.05, 0.10, 0.05), noise=0.4, scale=12, bump=0.5),
    "grass_far": K.mat("grass_far", (0.03, 0.06, 0.05), noise=0.3, scale=6),
    "trees": K.mat("trees", (0.02, 0.04, 0.04), noise=0.4, scale=4, bump=0.6),
    "path": K.brick_mat("path", brick=(0.30, 0.28, 0.25), mortar=(0.20, 0.19, 0.17), scale=1.4, vertical=False,
                        brick_width=0.9, row_height=0.6),
    "brick": K.brick_mat("brick", brick=(0.42, 0.18, 0.12), mortar=(0.55, 0.52, 0.46), scale=2.2),
    "roof": K.mat("roof", (0.10, 0.10, 0.13), noise=0.3, scale=30, bump=0.8),
    "wood": K.mat("wood", (0.20, 0.11, 0.05), noise=0.3, scale=14),
    "glass_lit": K.glow_mat("glass_lit", (1.0, 0.55, 0.18), 2.2),
    "lamp": K.glow_mat("lamp", (1.0, 0.75, 0.40), 5.0),
    "sign": K.mat("sign", (0.85, 0.82, 0.72), noise=0.05, emission=(0.4, 0.38, 0.32), estrength=0.3),
    "white": K.mat("white", (0.85, 0.85, 0.82), noise=0.05),
}
hot = {}


def tag(name, *objs):
    hot.setdefault(name, []).extend(objs)


def mesh(name, verts, faces, mat):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    if mat:
        o.data.materials.append(mat)
    return o


RIVER_Z = -3.2
DECK_Z = 4.4
# the bridge axis: from the near (Tewkesbury) bank on the right to the far bank, back and left
A = Vector((11.5, 8.0))
B = Vector((-34.0, 36.0))
AX = (B - A).normalized()
NRM = Vector((-AX.y, AX.x))        # horizontal, pointing at the camera side (downstream face)
SPAN = (B - A).length
YAW = math.atan2(AX.y, AX.x)


def on_axis(t, off=0.0):
    p = A + (B - A) * t + NRM * off
    return p


def arch_z(t, rise_top):
    """Segmental arch: springs at the river at t=0/1, crown at rise_top."""
    return RIVER_Z + 0.4 + (rise_top - RIVER_Z - 0.4) * math.sin(math.pi * t) ** 0.8


def band(name, z_lo, z_hi, off, thick, mat, n=40, t0=0.0, t1=1.0):
    """A curved vertical strip along the bridge axis between z_lo(t) and z_hi(t), offset `off`
    towards the camera, `thick` deep."""
    verts, faces = [], []
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        for o in (off, off - thick):
            p = on_axis(t, o)
            verts.append((p.x, p.y, z_lo(t)))
            verts.append((p.x, p.y, z_hi(t)))
    for i in range(n):
        a = i * 4
        b = a + 4
        faces += [(a, b, b + 1, a + 1), (a + 2, a + 3, b + 3, b + 2), (a + 1, b + 1, b + 3, a + 3), (a, a + 2, b + 2, b)]
    return mesh(name, verts, faces, mat)


def strut(name, p0, p1, w, mat):
    """Thin square bar between two 3-D points."""
    v = Vector(p1) - Vector(p0)
    L = v.length
    o = K.box(name, (L, w, w), (0, 0, 0), mat)
    o.location = (Vector(p0) + Vector(p1)) / 2
    o.rotation_euler = (0, -math.asin(max(-1.0, min(1.0, v.z / L))), math.atan2(v.y, v.x))
    return o


# ------------------------------------------------------------- the river ----
river = K.box("river", (220, 140, 0.05), (0, 70.0, RIVER_Z - 0.05), M["water"])
tag("River", river)
# moonlight on the water: broken glints in a column under the moon (upper left of frame)
for i in range(26):
    gy = rng.uniform(14, 70)
    gx = -9.0 - gy * 0.32 + rng.uniform(-1.5, 1.5)
    K.box("glint", (rng.uniform(0.6, 2.4), 0.12, 0.01), (gx, gy, RIVER_Z + 0.01), M["glint"])
for i in range(8):  # the lamp post reflected
    K.box("glint_w", (rng.uniform(0.3, 0.9), 0.1, 0.01), (6.2 + rng.uniform(-0.5, 0.5), 5.0 + i * 0.9, RIVER_Z + 0.01),
          M["glint_warm"])

# ------------------------------------------------------------- the banks ----
# near bank: grass falling from the path to the water's edge
mesh("near_bank", [(-60, 0.2, 0.0), (60, 0.2, 0.0), (60, 4.2, RIVER_Z), (-60, 4.2, RIVER_Z)], [(0, 1, 2, 3)], M["grass"])
K.box("path", (80, 6.8, 0.1), (0, -3.2, -0.1), M["path"])
K.box("path_edge", (80, 0.25, 0.12), (0, 0.15, -0.06), M["stone"])
# far bank: a low line of meadow and black trees, rising to the Mythe on the right
mesh("far_bank", [(-140, 62, RIVER_Z), (140, 62, RIVER_Z), (140, 66, RIVER_Z + 2.0), (-140, 66, RIVER_Z + 2.0)],
     [(0, 1, 2, 3)], M["grass_far"])
for i in range(70):
    tx = rng.uniform(-110, 110)
    r = rng.uniform(2.5, 6.0)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=r, subdivisions=2,
                                          location=(tx, rng.uniform(66, 76), RIVER_Z + 2.0 + r * 0.6))
    o = bpy.context.active_object
    o.scale = (1.0, 0.6, rng.uniform(0.8, 1.3))
    o.data.materials.append(M["trees"])
# willows on the near bank, upstream of the bridge
for wx_ in (24.0, 28.0, 33.0):
    bpy.ops.mesh.primitive_ico_sphere_add(radius=3.2, subdivisions=2, location=(wx_, 7.0, 1.5))
    o = bpy.context.active_object
    o.scale = (1.0, 0.8, 1.2)
    o.data.materials.append(M["trees"])

# ------------------------------------------------------------ the bridge ----
deck_lo = lambda t: DECK_Z - 0.55
deck_hi = lambda t: DECK_Z
crown = DECK_Z - 0.7
parts = []
# the arch: four cast-iron ribs, we see the downstream pair; each is a deep curved band
for off in (1.6, 0.55, -0.55, -1.6):
    parts.append(band("rib", lambda t: arch_z(t, crown - 0.75), lambda t: arch_z(t, crown), off, 0.18,
                      M["iron_lit"] if off > 1 else M["iron"]))
# deck fascia and parapet rail
parts.append(band("deck_fascia", deck_lo, deck_hi, 1.75, 0.15, M["iron_lit"], n=24, t0=-0.05, t1=1.05))
K.box("deck_road", (SPAN * 1.1, 3.6, 0.12), (0, 0, 0), M["deck"])
road = bpy.context.active_object
road.location = ((A + B) / 2).to_3d() + Vector((0, 0, DECK_Z - 0.06))
road.rotation_euler = (0, 0, YAW)
parts.append(band("parapet_rail", lambda t: DECK_Z + 1.05, lambda t: DECK_Z + 1.15, 1.8, 0.08, M["iron_lit"], n=24,
                  t0=-0.05, t1=1.05))
parts.append(band("parapet_rail_far", lambda t: DECK_Z + 1.05, lambda t: DECK_Z + 1.15, -1.8, 0.08, M["iron"], n=24,
                  t0=-0.05, t1=1.05))
# open lattice spandrels: diagonal iron bars crossing between the ribs and the deck
N_PANEL = 16
for i in range(N_PANEL):
    t0, t1 = i / N_PANEL, (i + 1) / N_PANEL
    for off in (1.62, -1.6):
        p0, p1 = on_axis(t0, off), on_axis(t1, off)
        z0, z1 = arch_z(t0, crown), arch_z(t1, crown)
        m = M["iron_lit"] if off > 0 else M["iron"]
        if z0 < DECK_Z - 0.6:
            parts.append(strut("lattice", (p0.x, p0.y, z0), (p1.x, p1.y, DECK_Z - 0.5), 0.09, m))
        if z1 < DECK_Z - 0.6:
            parts.append(strut("lattice", (p1.x, p1.y, z1), (p0.x, p0.y, DECK_Z - 0.5), 0.09, m))
        if 0 < i and z0 < DECK_Z - 0.6:
            parts.append(strut("post", (p0.x, p0.y, z0), (p0.x, p0.y, DECK_Z - 0.5), 0.1, m))
# parapet balusters
for i in range(60):
    t = -0.04 + 1.08 * i / 59
    p = on_axis(t, 1.8)
    parts.append(K.box("baluster", (0.05, 0.05, 1.1), (p.x, p.y, DECK_Z), M["iron_lit"]))
tag("Bridge", *parts)

# stone approaches with little flood arches, both banks
def approach(t_from, t_to, name):
    p0, p1 = on_axis(t_from), on_axis(t_to)
    mid = (p0 + p1) / 2
    L = (p1 - p0).length
    o = K.box(name, (L, 4.2, DECK_Z - RIVER_Z + 0.6), (mid.x, mid.y, RIVER_Z - 0.6), M["stone"], rot=(0, 0, YAW))
    K.box(name + "_cope", (L, 4.4, 0.25), (mid.x, mid.y, DECK_Z), M["stone"], rot=(0, 0, YAW))
    K.box(name + "_parapet", (L, 0.45, 1.0), (0, 0, 0), M["stone"])
    par = bpy.context.active_object
    pp = mid + NRM * 1.95
    par.location = (pp.x, pp.y, DECK_Z + 0.75)
    par.rotation_euler = (0, 0, YAW)
    # flood arches: dark openings on the downstream face
    n = max(1, int(L / 4.5))
    for k in range(n):
        tt = (k + 0.5) / n
        c = p0 + (p1 - p0) * tt + NRM * 2.12
        K.box("flood_arch", (2.0, 0.1, 2.6), (c.x, c.y, RIVER_Z + 0.4), M["stone_dark"], rot=(0, 0, YAW))
        cap = K.cyl("flood_arch_top", 1.0, 0.1, (0, 0, 0), M["stone_dark"], verts=16)
        cap.rotation_euler = (math.pi / 2, 0, YAW)
        cap.location = (c.x, c.y, RIVER_Z + 3.0)
    return o


near = approach(-0.38, -0.02, "near_approach")
far = approach(1.02, 1.5, "far_approach")
tag("Bridge", near)

# -------------------------------------------------------- the path props ----
bench_x = -3.0
bench = [K.box("bench_seat", (1.8, 0.45, 0.07), (bench_x, -0.55, 0.45), M["wood"]),
         K.box("bench_back", (1.8, 0.06, 0.45), (bench_x, -0.32, 0.6), M["wood"])]
for lx in (-0.8, 0.8):
    bench.append(K.box("bench_leg", (0.08, 0.45, 0.45), (bench_x + lx, -0.55, 0.0), M["iron"]))
tag("Bench", *bench)
K.lamp_post(5.5, -0.4, {"iron": M["iron"], "lamp": M["lamp"]}, light_energy=220)
# fingerpost: Severn Way, Tewkesbury
sp_x = -7.6
post = K.box("fingerpost", (0.1, 0.1, 2.3), (sp_x, -0.5, 0.0), M["white"])
K.box("finger_a", (0.9, 0.04, 0.18), (sp_x - 0.4, -0.5, 1.9), M["sign"], rot=(0, 0.0, 0.0))
K.box("finger_b", (0.8, 0.04, 0.18), (sp_x + 0.35, -0.5, 1.6), M["sign"], rot=(0, 0.0, 0.25))
tag("Signpost", post)
# exit: unrendered volume over the path at the left edge, back into town
to_town = K.box("exit_town", (1.2, 3.0, 2.6), (-10.0, -1.9, 0.0), None)
to_town.hide_render = True
tag("ToHighSt", to_town)

# ---------------------------------------------------------------- lights ----
K.sun("moon", (0.75, 0.25, -0.6), (0.55, 0.65, 1.0), 0.8)
K.sun("sky_fill", (1.2, 0.0, 2.6), (0.35, 0.40, 0.75), 0.15)
for t in (0.1, 0.5, 0.9):   # moonlight catching the face of the arch
    p = on_axis(t, 6.0)
    wash = K.point_light("arch_wash", (p.x, p.y, 1.5), (0.55, 0.65, 1.0), 900, radius=2.0)
    wash.data.specular_factor = 0.0   # no hot spots on the water

# ---------------------------------------------------------------- camera ----
cam = K.camera((0.8, -15.0, 6.0), (0.8, 0.0, 6.0), lens=24)
cam.data.shift_y = -0.21

scn = bpy.context.scene
bpy.context.view_layer.update()
if not NO_RENDER:
    scn.render.filepath = os.path.join(OUT, "mythe_bridge.png")
    bpy.ops.render.render(write_still=True)


def to_px(world):
    co = world_to_camera_view(scn, cam, Vector(world))
    return (co.x * 320.0, (1.0 - co.y) * 200.0)


def rect_of(objs, pad=1, ymax=152):
    xs, ys = [], []
    for o in objs:
        for c in o.bound_box:
            x, y = to_px(o.matrix_world @ Vector(c))
            xs.append(x)
            ys.append(y)
    return [max(0, int(min(xs)) - pad), max(0, int(min(ys)) - pad),
            min(320, int(max(xs)) + pad), min(ymax, int(max(ys)) + pad)]


GUI_TOP = 150
floor = [to_px((-16, -0.4, 0.0)), to_px((16, -0.4, 0.0)), to_px((16, -6.5, 0)), to_px((-16, -6.5, 0))]
floor = [(min(316, max(4, x)), min(GUI_TOP - 2, y)) for x, y in floor]
hs = {k: rect_of(v) for k, v in hot.items()}
# the river is everything between the bridge and the near bank: keep it to the open water
rx0, ry0, rx1, ry1 = hs["River"]
hs["River"] = [0, max(ry0, to_px((0, 60, RIVER_Z))[1]), 320, int(to_px((0, 4.2, RIVER_Z))[1])]
PATH_TOP = 118
arch_lo = [to_px((on_axis(t / 10).x, on_axis(t / 10).y, arch_z(t / 10, crown - 0.75))) for t in range(10, -1, -1)]
bridge_poly = ([to_px((on_axis(t / 10).x, on_axis(t / 10).y, DECK_Z + 1.2)) for t in range(-6, 12)] + arch_lo
               + [to_px((on_axis(-0.02).x, on_axis(-0.02).y, RIVER_Z)), to_px((on_axis(-0.4).x, on_axis(-0.4).y, RIVER_Z))])
bridge_poly = [(x, min(PATH_TOP, y)) for x, y in bridge_poly]
river_poly = ([(0.0, arch_lo[0][1] + 2)] + [(x, y + 2) for x, y in arch_lo]
              + [(arch_lo[-1][0] + 4, PATH_TOP), (0.0, PATH_TOP)])
data = {
    "hotspots": hs,
    "walk_points": {
        "Bench": to_px((bench_x, -1.3, 0.0)),
        "Signpost": to_px((sp_x + 0.6, -1.3, 0.0)),
        "Bridge": to_px((4.0, -1.3, 0.0)),
        "River": to_px((0.0, -1.2, 0.0)),
        "ToHighSt": to_px((-9.6, -2.2, 0.0)),
    },
    "spawn": {
        "from_high_st": to_px((-8.6, -2.2, 0.0)),
        "ending_spot": to_px((0.5, -1.6, 0.0)),
        "walk_off_left": to_px((-9.9, -2.4, 0.0)),
        "walk_off_right": to_px((11.0, -1.4, 0.0)),
    },
    # where the lift home drives along the bridge deck, far end -> near end (game px)
    "deck_far": to_px((on_axis(0.92).x, on_axis(0.92).y, DECK_Z)),
    "deck_near": to_px((on_axis(0.12).x, on_axis(0.12).y, DECK_Z)),
    # outlines in place of rectangles: the bridge from the parapet top down to the arch and the
    # near abutment, and the open river under the arch down to the path's edge
    "polys": {"Bridge": bridge_poly, "River": river_poly},
    "floor": [list(p) for p in floor],
    "person_px": to_px((0, -2.2, 0.0))[1] - to_px((0, -2.2, 1.8))[1],
}
with open(os.path.join(OUT, "mythe_bridge.json"), "w") as f:
    json.dump(data, f, indent=1)
print("[blender] wrote", json.dumps(data))
