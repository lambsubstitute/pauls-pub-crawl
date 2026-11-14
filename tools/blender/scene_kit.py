"""Shared helpers for building Paul's Pub Crawl backgrounds in Blender.

Imported by the per-room scripts (church_st.py, cross_house_tavern.py). Everything is
procedural so a room can be rebuilt from scratch with:

    /Applications/Blender.app/Contents/MacOS/Blender -b -P tools/blender/church_st.py

Look: dusk/night Tewkesbury, cold blue ambient + warm window/lamp glow, lots of surface
texture so the 32-colour dither in tools/pixelate.py has something to chew on.
"""
import math
import random

import bpy
from mathutils import Vector

RNG = random.Random(7)


# ---------------------------------------------------------------- scene ----
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    scn.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in {
        e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items
    } else "BLENDER_EEVEE"
    scn.render.resolution_x = 1280
    scn.render.resolution_y = 800
    scn.render.film_transparent = False
    scn.view_settings.view_transform = "Standard"
    scn.view_settings.look = "None"
    scn.view_settings.exposure = 0.0
    try:
        scn.eevee.taa_render_samples = 32
        scn.eevee.use_shadows = True
    except AttributeError:
        pass
    return scn


def world_sky(top=(0.03, 0.03, 0.10), mid=(0.25, 0.12, 0.28), horizon=(0.95, 0.45, 0.25), strength=1.0):
    """Gradient sky driven by view direction Z, used as both background and ambient."""
    w = bpy.data.worlds.new("Sky")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    geo = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].position = 0.0
    cr.elements[0].color = (*horizon, 1)
    cr.elements[1].position = 0.45
    cr.elements[1].color = (*top, 1)
    e = cr.elements.new(0.12)
    e.color = (*mid, 1)
    nt.links.new(geo.outputs["Window"], sep.inputs[0])
    # use screen-space Y so the gradient is stable regardless of camera tilt
    m = nt.nodes.new("ShaderNodeMapRange")
    m.inputs["From Min"].default_value = 0.35
    m.inputs["From Max"].default_value = 1.0
    nt.links.new(sep.outputs["Y"], m.inputs["Value"])
    nt.links.new(m.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    return w


def camera(loc, look_at, lens=32, ortho_scale=None):
    cam_data = bpy.data.cameras.new("Cam")
    if ortho_scale:
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = ortho_scale
    else:
        cam_data.lens = lens
    cam = bpy.data.objects.new("Cam", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = loc
    d = Vector(look_at) - Vector(loc)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam
    return cam


# ------------------------------------------------------------- materials ----
_mats = {}


def mat(name, color, rough=0.8, noise=0.15, scale=8.0, emission=None, estrength=0.0, bump=0.3):
    """Principled material with a noise-modulated base colour so flat walls get texture."""
    key = (name, color, emission)
    if key in _mats:
        return _mats[key]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = rough
    tex = nt.nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = scale
    tex.inputs["Detail"].default_value = 6.0
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    dark = tuple(max(0, c * (1 - noise)) for c in color)
    light = tuple(min(1, c * (1 + noise)) for c in color)
    mix.inputs["A"].default_value = (*dark, 1)
    mix.inputs["B"].default_value = (*light, 1)
    nt.links.new(tex.outputs["Fac"], mix.inputs["Factor"])
    nt.links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
    if bump:
        b = nt.nodes.new("ShaderNodeBump")
        b.inputs["Strength"].default_value = bump
        nt.links.new(tex.outputs["Fac"], b.inputs["Height"])
        nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1)
        bsdf.inputs["Emission Strength"].default_value = estrength
    _mats[key] = m
    return m


def brick_mat(name, brick=(0.45, 0.16, 0.10), mortar=(0.55, 0.50, 0.45), scale=6.0, vertical=True,
              brick_width=0.5, row_height=0.25):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.9
    tc = nt.nodes.new("ShaderNodeTexCoord")
    bt = nt.nodes.new("ShaderNodeTexBrick")
    bt.inputs["Scale"].default_value = scale
    bt.inputs["Color1"].default_value = (*brick, 1)
    bt.inputs["Color2"].default_value = (brick[0] * 0.75, brick[1] * 0.75, brick[2] * 0.75, 1)
    bt.inputs["Mortar"].default_value = (*mortar, 1)
    bt.inputs["Mortar Size"].default_value = 0.012
    bt.inputs["Brick Width"].default_value = brick_width
    bt.inputs["Row Height"].default_value = row_height
    # Brick texture only uses X/Y; facades face -Y, so feed it (x+y, z) to tile vertical walls.
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    add = nt.nodes.new("ShaderNodeMath")
    add.operation = "ADD"
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    nt.links.new(sep.outputs["X"], add.inputs[0])
    nt.links.new(sep.outputs["Y"], add.inputs[1])
    nt.links.new(add.outputs[0], comb.inputs["X"])
    nt.links.new(sep.outputs["Z"], comb.inputs["Y"])
    if vertical:
        nt.links.new(comb.outputs[0], bt.inputs["Vector"])
    else:
        nt.links.new(tc.outputs["Object"], bt.inputs["Vector"])
    nt.links.new(bt.outputs["Color"], bsdf.inputs["Base Color"])
    b = nt.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value = 0.4
    nt.links.new(bt.outputs["Fac"], b.inputs["Height"])
    nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def glow_mat(name, color, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


# ------------------------------------------------------------ primitives ----
def box(name, size, loc, material, rot=(0, 0, 0)):
    """Axis box: size=(x,y,z) full extents, loc=centre of the bottom face."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0], loc[1], loc[2] + size[2] / 2))
    o = bpy.context.active_object
    o.name = name
    o.scale = size
    o.rotation_euler = rot
    bpy.ops.object.transform_apply(scale=True)
    if material:
        o.data.materials.append(material)
    return o


def cyl(name, r, h, loc, material, verts=16):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=verts, location=(loc[0], loc[1], loc[2] + h / 2))
    o = bpy.context.active_object
    o.name = name
    if material:
        o.data.materials.append(material)
    return o


def gable_roof(name, width, depth, rise, loc, material, overhang=0.25, ridge_along_x=False):
    """Simple pitched roof sitting on top of a box at loc (centre of base)."""
    w, d = width + overhang * 2, depth + overhang * 2
    x0, y0, z0 = loc
    if ridge_along_x:
        verts = [(x0 - w / 2, y0 - d / 2, z0), (x0 + w / 2, y0 - d / 2, z0),
                 (x0 + w / 2, y0 + d / 2, z0), (x0 - w / 2, y0 + d / 2, z0),
                 (x0 - w / 2, y0, z0 + rise), (x0 + w / 2, y0, z0 + rise)]
        faces = [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5)]
    else:
        verts = [(x0 - w / 2, y0 - d / 2, z0), (x0 + w / 2, y0 - d / 2, z0),
                 (x0 + w / 2, y0 + d / 2, z0), (x0 - w / 2, y0 + d / 2, z0),
                 (x0, y0 - d / 2, z0 + rise), (x0, y0 + d / 2, z0 + rise)]
        faces = [(0, 4, 5, 3), (1, 2, 5, 4), (0, 1, 4), (3, 5, 2)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(material)
    return o


def point_light(name, loc, color, energy, radius=0.1):
    ld = bpy.data.lights.new(name, "POINT")
    ld.color = color
    ld.energy = energy
    ld.shadow_soft_size = radius
    o = bpy.data.objects.new(name, ld)
    o.location = loc
    bpy.context.scene.collection.objects.link(o)
    return o


def sun(name, rot, color, energy):
    ld = bpy.data.lights.new(name, "SUN")
    ld.color = color
    ld.energy = energy
    o = bpy.data.objects.new(name, ld)
    o.rotation_euler = rot
    bpy.context.scene.collection.objects.link(o)
    return o


# -------------------------------------------------------------- buildings ----
def window(x, y_face, z, w, h, frame_mat, glass_mat, panes=(2, 3), sill=True):
    """Window on a facade facing -Y at plane y=y_face. x,z = bottom-centre."""
    box("win_frame", (w + 0.12, 0.08, h + 0.12), (x, y_face - 0.02, z - 0.06), frame_mat)
    box("win_glass", (w, 0.06, h), (x, y_face - 0.05, z), glass_mat)
    cols, rows = panes
    for i in range(1, cols):
        box("win_bar", (0.035, 0.07, h), (x - w / 2 + w * i / cols, y_face - 0.09, z), frame_mat)
    for j in range(1, rows):
        box("win_bar", (w, 0.07, 0.035), (x, y_face - 0.09, z + h * j / rows - 0.017), frame_mat)
    if sill:
        box("win_sill", (w + 0.25, 0.18, 0.06), (x, y_face - 0.08, z - 0.08), frame_mat)


def timber_frame(x0, x1, z0, z1, y_face, beam_mat, rng, braces=True, posts_every=0.9):
    """Black-and-white framing on a facade plane between x0..x1, z0..z1."""
    t = 0.11
    box("beam", (x1 - x0, 0.06, t), ((x0 + x1) / 2, y_face - 0.03, z0), beam_mat)
    box("beam", (x1 - x0, 0.06, t), ((x0 + x1) / 2, y_face - 0.03, z1 - t), beam_mat)
    box("beam", (x1 - x0, 0.06, t * 0.8), ((x0 + x1) / 2, y_face - 0.03, (z0 + z1) / 2), beam_mat)
    n = max(2, int((x1 - x0) / posts_every) + 1)
    for i in range(n):
        px = x0 + (x1 - x0) * i / (n - 1)
        box("post", (t, 0.06, z1 - z0), (px, y_face - 0.03, z0), beam_mat)
    if braces:
        for i in range(n - 1):
            if rng.random() < 0.55:
                ax = x0 + (x1 - x0) * i / (n - 1)
                bx = x0 + (x1 - x0) * (i + 1) / (n - 1)
                zm = (z0 + z1) / 2
                L = math.hypot(bx - ax, zm - z0)
                ang = math.atan2(zm - z0, bx - ax) * (1 if rng.random() < 0.5 else -1)
                b = box("brace", (L, 0.05, t * 0.7), ((ax + bx) / 2, y_face - 0.03, z0 + (zm - z0) / 2 - t * 0.35),
                        beam_mat, rot=(0, -ang, 0))


def tudor_house(x, width, depth, storeys, rng, mats, jetty=0.35, gable=True, door=False, y_front=0.0,
                h1=2.6, h2=2.3, roof_rise=2.0):
    """Jettied timber-framed house, front face at y=y_front (facing -Y, towards camera)."""
    plaster, beam, roof, frame, glass_lit, glass_dark = (
        mats["plaster"], mats["beam"], mats["roof"], mats["frame"], mats["glass_lit"], mats["glass_dark"])
    box("ground", (width, depth, h1), (x, y_front + depth / 2, 0), plaster)
    timber_frame(x - width / 2, x + width / 2, 0, h1, y_front, beam, rng, braces=False, posts_every=1.4)
    # upper floors jettied out towards the street
    z = h1
    yf = y_front
    for s in range(storeys - 1):
        yf -= jetty
        box("joist", (width + 0.1, jetty + 0.1, 0.18), (x, yf + jetty / 2, z - 0.05), beam)
        box("upper", (width + 0.1, depth + jetty * (s + 1), h2), (x, yf + (depth + jetty * (s + 1)) / 2, z), plaster)
        timber_frame(x - width / 2, x + width / 2, z, z + h2, yf, beam, rng)
        for wx in (-width / 4, width / 4):
            window(x + wx, yf, z + 0.6, 0.9, 1.0, frame, glass_lit if rng.random() < 0.55 else glass_dark)
        z += h2
    # ground-floor windows / door
    if door:
        box("door", (0.95, 0.1, 2.0), (x - width / 4, y_front - 0.04, 0), mats["door"])
        window(x + width / 4, y_front, 0.8, 1.3, 1.2, frame, glass_lit, panes=(3, 3))
    else:
        window(x, y_front, 0.8, 1.6, 1.2, frame, glass_lit if rng.random() < 0.7 else glass_dark, panes=(4, 3))
    if gable:
        gable_roof("roof", width + 0.1, depth + jetty * (storeys - 1), roof_rise, (x, yf + (depth + jetty) / 2, z), roof,
                   ridge_along_x=False)
    else:
        gable_roof("roof", width + 0.1, depth + jetty * (storeys - 1), roof_rise * 0.75, (x, yf + (depth + jetty) / 2, z), roof,
                   ridge_along_x=True)
    return z


def lamp_post(x, y, mats, light_energy=60):
    cyl("lamp_pole", 0.07, 3.6, (x, y, 0), mats["iron"], verts=8)
    box("lamp_arm", (0.5, 0.06, 0.06), (x + 0.2, y, 3.5), mats["iron"])
    box("lamp_head", (0.32, 0.32, 0.45), (x + 0.42, y, 3.15), mats["lamp"])
    point_light("lamp_light", (x + 0.42, y - 0.3, 3.2), (1.0, 0.72, 0.38), light_energy, radius=0.2)
