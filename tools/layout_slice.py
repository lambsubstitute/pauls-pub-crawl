"""Lay out the vertical-slice rooms to match the room art.

Hotspots, walk points, floors and NPC spots come from art/renders/<room>.json, which the
Blender scripts (tools/blender/*.py) write by projecting the 3D props into 320x200 game pixels,
so click areas always line up with the rendered background. Falls back to the hand-placed
rects below if a room has no render yet.

Popochiu's factories drop every new hotspot / walkable area at the screen centre with a
24 px square. This rewrites those node overrides in the room .tscn files with real
polygons (absolute coords, node at 0,0), adds the background sprite and places NPCs.
Idempotent: safe to re-run after regenerating rooms.

    python3 tools/layout_slice.py
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


ROOMS = {
    "church_st": {
        "Floor": {"poly": rect(4, 102, 316, 146)},
        "TavernDoor": {"poly": rect(198, 70, 220, 100), "walk": (209, 106), "desc": "Cross House Tavern door", "baseline": 100},
        "Abbey": {"poly": rect(18, 14, 66, 86), "walk": (60, 108), "desc": "Tewkesbury Abbey", "baseline": 0},
        "Bench": {"poly": rect(270, 84, 306, 102), "walk": (288, 108), "desc": "Bench", "baseline": 101},
        "HopPoleDoor": {"poly": rect(259, 81, 280, 118), "walk": (270, 126), "desc": "Royal Hop Pole door", "baseline": 118},
        "ToTheCross": {},
        "npcs": {},
    },
    "cross_house_tavern": {
        "Floor": {"poly": rect(4, 106, 316, 146)},
        "Bar": {"poly": rect(90, 76, 240, 104), "walk": (200, 112), "desc": "Bar", "baseline": 104},
        "QuizMachine": {"poly": rect(20, 44, 54, 104), "walk": (44, 112), "desc": "Quiz machine", "baseline": 104},
        "ExitDoor": {"poly": rect(272, 34, 304, 104), "walk": (288, 110), "desc": "Door to Church Street", "baseline": 104},
        # Doorstop pin is a sprite drawn by tools/sprites.py, not part of the render.
        "Doorstop": {"poly": rect(278, 89, 289, 105), "walk": (284, 123), "desc": "Skittle pin", "baseline": 104, "manual": True},
        "npcs": {"Landlord": (165, 74)},
    },
    "hop_pole": {
        "Floor": {"poly": rect(4, 122, 316, 148)},
        "Bar": {}, "SkittleAlley": {}, "ExitDoor": {}, "Portrait": {},
        "npcs": {},
    },
    # the_cross / berkeley_arms only exist as renders: everything comes from their JSON
    "the_cross": {
        "Floor": {"poly": rect(4, 119, 316, 148)},
        "BerkeleyDoor": {}, "BerkeleySign": {}, "Memorial": {}, "ToChurchSt": {}, "ToHighSt": {},
        "npcs": {},
    },
    "berkeley_arms": {
        "Floor": {"poly": rect(4, 124, 316, 147)},
        "Bar": {}, "Pumps": {}, "WaterJug": {}, "Snug": {}, "ExitDoor": {}, "Fireplace": {}, "Post": {},
        "Dartboard": {}, "Scoreboard": {}, "BeamDarts": {},
        "npcs": {},
    },
    "high_st": {
        "Floor": {"poly": rect(4, 119, 316, 148)},
        "ToTheCross": {}, "BritanniaDoor": {}, "BritanniaSign": {}, "NottinghamDoor": {}, "BlackBearDoor": {},
        "npcs": {},
    },
    "britannia": {
        "Floor": {"poly": rect(4, 124, 316, 147)},
        "Bar": {}, "Pumps": {}, "WaterJug": {}, "ExitDoor": {"desc_override": "Door to High Street"}, "MagicEye": {}, "GhostPicture": {}, "Clock": {},
        "ShoveBoard": {}, "Window": {},
        "npcs": {},
    },
    # the pool table stands in the middle of the floor: a hole in the walkable area plus a
    # y-sorted cut-out sprite (see table_cutout)
    "nottingham_arms": {
        "Floor": {"poly": rect(4, 110, 316, 147)},
        "Bar": {}, "Pumps": {}, "WaterJug": {}, "ExitDoor": {"desc_override": "Door to High Street"}, "Fireplace": {"desc_override": "Fireplace"},
        "CueRack": {}, "PoolTable": {}, "PoolRest": {}, "Jukebox": {}, "CueShaft": {},
        "LeagueBoard": {},
        "npcs": {},
    },
    # the finale: Ursula the dog and the table wedge are sprites over the background (see
    # black_bear_props); the pool table is behind the walk band, so no hole
    "black_bear": {
        "Floor": {"poly": rect(4, 124, 316, 147)},
        "Bar": {}, "Pumps": {}, "WaterJug": {}, "ExitDoor": {"desc_override": "Door to High Street"},
        "Beams": {}, "Window": {}, "Fireplace": {}, "Ursula": {}, "Wedge": {}, "HonoursBoard": {},
        "Dartboard": {}, "PoolTable": {},
        "npcs": {},
    },
    # the ending: the bridge and river are polygons from the render (JSON "polys")
    "mythe_bridge": {
        "Floor": {"poly": rect(4, 121, 316, 148)},
        "Bridge": {}, "River": {}, "Bench": {}, "Signpost": {}, "ToHighSt": {"desc_override": "Back to town"},
        "npcs": {},
    },
}
BAR_ROOMS = {"cross_house_tavern", "hop_pole", "berkeley_arms", "britannia", "nottingham_arms", "black_bear"}

import json

DESC = {
    "TavernDoor": "Cross House Tavern door", "Abbey": "Tewkesbury Abbey", "Bench": "Bench",
    "Bar": "Bar", "QuizMachine": "Quiz machine", "ExitDoor": "Door to Church Street",
    "HopPoleDoor": "Royal Hop Pole door", "SkittleAlley": "Skittle alley", "Portrait": "Portrait",
    "ToTheCross": "Way to the Cross", "BerkeleyDoor": "Berkeley Arms door", "BerkeleySign": "Pub sign",
    "Memorial": "War memorial", "ToChurchSt": "Church Street", "ToHighSt": "High Street",
    "Pumps": "Beer pumps", "WaterJug": "Water jug", "Snug": "Snug", "Fireplace": "Inglenook",
    "Post": "Oak post", "Dartboard": "Dartboard", "Scoreboard": "Chalk scoreboard", "BeamDarts": "Darts",
    "BritanniaDoor": "Britannia Inn door", "BritanniaSign": "Pub sign", "NottinghamDoor": "Nottingham Arms door",
    "BlackBearDoor": "Ye Olde Black Bear door", "MagicEye": "Magic Eye picture", "GhostPicture": "Hidden picture",
    "Clock": "Grandfather clock", "ShoveBoard": "Shove ha'penny board", "Window": "Window",
    "CueRack": "Cue rack", "PoolTable": "Pool table", "PoolRest": "Pool rest", "Jukebox": "Jukebox",
    "CueShaft": "Cue shaft", "LeagueBoard": "League board",
    "Beams": "Low beam", "Ursula": "Big black dog", "Wedge": "Wooden wedge", "HonoursBoard": "Honours board",
    "Bridge": "Mythe Bridge", "River": "River Severn", "Signpost": "Fingerpost",
}


def from_render(room, fallback):
    j = ROOT / "art" / "renders" / f"{room}.json"
    if not j.exists():
        return fallback
    d = json.loads(j.read_text())
    spec = {"Floor": {"poly": [(round(x), round(y)) for x, y in d["floor"]],
                      # holes wound the other way round (TL, BL, BR, TR): Godot's bake unions
                      # same-winding outlines, so only a reversed one is cut out
                      "holes": [[(round(x), round(y)) for x, y in (h[0], h[3], h[2], h[1])]
                                for h in d.get("floor_holes", [])]},
            "npcs": {}}
    for name in fallback:
        if name in ("Floor", "npcs"):
            continue
        if name not in d["hotspots"]:
            if fallback[name].get("manual"):
                spec[name] = fallback[name]
            continue
        x0, y0, x1, y1 = d["hotspots"][name]
        poly = d.get("polys", {}).get(name)
        if poly:  # a real outline (the Mythe bridge's arch), clamped to the game area
            poly = [(round(min(320, max(0, x))), round(min(150, max(0, y)))) for x, y in poly]
            x0, x1 = min(p[0] for p in poly), max(p[0] for p in poly)
            y0, y1 = min(p[1] for p in poly), max(p[1] for p in poly)
        wx, wy = d["walk_points"].get(name, ((x0 + x1) / 2, y1 + 4))
        wx = min(x1, max(x0, wx))  # perspective can push floor points past the object's own width
        if name == "Bar":
            y0 = max(y0, y1 - 18)  # counter front only, so the landlord behind it stays clickable
        wy = min(146, max(spec["Floor"]["poly"][0][1] + 2, wy))
        desc = fallback[name].get("desc_override") or DESC.get(name, name)
        spec[name] = {"poly": poly or rect(x0, y0, x1, y1), "walk": (round(wx), round(wy)), "desc": desc,
                      "baseline": y1 if name != "Abbey" else 0}
    if "landlord_pos" in d:
        spec["npcs"]["Landlord"] = tuple(round(v) for v in d["landlord_pos"])
    for npc, pos in d.get("npc", {}).items():
        spec["npcs"][npc] = tuple(round(v) for v in pos)
    # NPCs win over scenery: trim any hotspot that overlaps an NPC's body (~22x46 px) back to the
    # side away from them, otherwise clicking the NPC hits the hotspot (Reg vs the skittle alley).
    for npc, (nx, ny) in spec["npcs"].items():
        bx0, bx1, by0 = nx - 12, nx + 12, ny - 48
        for name, h in spec.items():
            if name in ("Floor", "npcs", "_meta", "Bar") or not isinstance(h, dict) or "poly" not in h:
                continue
            if len(h["poly"]) != 4:
                continue
            (x0, y0), _, (x1, y1), _ = h["poly"]
            if x0 < bx1 and x1 > bx0 and y1 > by0:
                if (nx - x0) > (x1 - nx):
                    x1 = bx0
                else:
                    x0 = bx1
                h["poly"] = rect(x0, y0, x1, y1)
                h["walk"] = (min(x1, max(x0, h["walk"][0])), h["walk"][1])
    # where Paul stands to talk to each NPC, stored relative to the NPC (Popochiu walk_to_point)
    spec["npc_walk"] = {n: (round(d["walk_points"][n][0] - p[0]), round(d["walk_points"][n][1] - p[1]))
                        for n, p in spec["npcs"].items() if n in d.get("walk_points", {})}
    spec["_meta"] = d
    return spec


CHAR_SCENES = {c: f"res://game/characters/{c.lower()}/character_{c.lower()}.tscn"
               for c in ("Landlord", "Barmaid", "Reg", "Clive", "Dot", "Gwen", "Stan", "Jackie", "Gaz", "Norman",
                         "Bernie", "Rosie")}


def vec_array(pts):
    return "PackedVector2Array(" + ", ".join(f"{x}, {y}" for x, y in pts) + ")"


def set_node_props(text, node_name, parent, props):
    """Replace the property block of [node name=X parent=Y ...] with `props`."""
    pat = re.compile(
        r'(\[node name="%s" parent="%s"[^\]]*\]\n)(.*?)(?=\n\[|\Z)' % (node_name, parent), re.S
    )
    m = pat.search(text)
    if not m:
        raise SystemExit(f"node {parent}/{node_name} not found")
    body = "\n".join(f"{k} = {v}" for k, v in props.items())
    return text[: m.start()] + m.group(1) + body + "\n" + text[m.end():]


def next_ext_id(text):
    ids = [int(i.split("_")[0]) for i in re.findall(r'id="(\d+_\w+)"', text)]
    return max(ids, default=0) + 1


def add_ext(text, line):
    last = list(re.finditer(r"^\[ext_resource .*\]$", text, re.M))[-1]
    return text[: last.end()] + "\n" + line + text[last.end():]


def layout(room, spec):
    path = ROOT / f"game/rooms/{room}/room_{room}.tscn"
    text = path.read_text()

    for name, s in spec.items():
        if name in ("npcs", "npc_walk", "_meta"):
            continue
        if name == "Floor":
            outlines = ", ".join(vec_array(o) for o in [s["poly"]] + s.get("holes", []))
            text = set_node_props(text, "Floor", "WalkableAreas", {
                "interaction_polygon": f"Array[PackedVector2Array]([{outlines}])",
            })
            continue
        wx, wy = s["walk"]
        text = set_node_props(text, name, "Hotspots", {
            "description": f'"{s["desc"]}"',
            "baseline": s["baseline"],
            "walk_to_point": f"Vector2({wx}, {wy})",
            "interaction_polygon": vec_array(s["poly"]),
        })

    if 'name="Background"' not in text:
        bg = f"res://game/rooms/{room}/props/bg_{room}.png"
        eid = f"{next_ext_id(text)}_bg"
        text = add_ext(text, f'[ext_resource type="Texture2D" path="{bg}" id="{eid}"]')
        text = text.replace(
            '[node name="WalkableAreas"',
            f'[node name="Background" type="Sprite2D" parent="."]\n'
            f"z_index = -10\ntexture_filter = 1\ntexture = ExtResource(\"{eid}\")\ncentered = false\n\n"
            '[node name="WalkableAreas"',
            1,
        )

    for npc, (x, y) in spec["npcs"].items():
        if f'name="Character{npc}"' in text:
            text = re.sub(r'(\[node name="Character%s"[^\]]*\]\n)position = Vector2\([^)]*\)' % npc,
                          r"\1position = Vector2(%d, %d)" % (x, y), text)
            if npc in spec.get("npc_walk", {}):
                wx, wy = spec["npc_walk"][npc]
                text = re.sub(r'(\[node name="Character%s"[^\]]*\]\nposition = Vector2\([^)]*\)\n)(?:walk_to_point = Vector2\([^)]*\)\n)?' % npc,
                              r"\1walk_to_point = Vector2(%d, %d)\n" % (wx, wy), text)
            continue
        eid = f"{next_ext_id(text)}_{npc.lower()}"
        text = add_ext(text, f'[ext_resource type="PackedScene" path="{CHAR_SCENES[npc]}" id="{eid}"]')
        text = text.rstrip("\n") + (
            f'\n\n[node name="Character{npc}" parent="Characters" instance=ExtResource("{eid}")]\n'
            f"position = Vector2({x}, {y})\n"
        )

    # Hotspot nodes' own scenes keep position (160,100) from the factory; zero it in the room.
    text = re.sub(r'(\[node name="\w+" parent="(?:Hotspots|WalkableAreas)"[^\]]*\]\n)',
                  r"\1position = Vector2(0, 0)\n", text)
    text = re.sub(r"(position = Vector2\(0, 0\)\n)+", r"\1", text)
    path.write_text(text)
    print("laid out", room)


def bake_floor(room, poly, holes=()):
    """Write the floor polygon into the walkable area's own scene, pre-baked.

    Popochiu rebakes navigation at runtime from the room's interaction_polygon, but the web
    export still paths on the NavigationPolygon saved in this scene (the factory's 20px default
    square), so Paul walked to its corner at (10, 10). Saving the real shape fixes that.
    """
    p = ROOT / f"game/rooms/{room}/walkable_areas/floor/walkable_area_floor.tscn"
    t = p.read_text()
    arr = vec_array(poly)
    idx = ", ".join(str(i) for i in range(len(poly)))
    outlines, verts, polys = arr, arr, f"PackedInt32Array({idx})"
    if holes:
        # One quad hole in a quad floor (the pool table): outer 0-3 (TL, TR, BR, BL), hole 4-7
        # reversed (TL, BL, BR, TR), split into four convex quads round the hole.
        (h,) = holes
        outlines = ", ".join(vec_array(o) for o in [poly, h])
        verts = vec_array(list(poly) + list(h))
        polys = ", ".join(f"PackedInt32Array({q})" for q in
                          ("0, 1, 7, 4", "7, 1, 2, 6", "5, 6, 2, 3", "0, 4, 5, 3"))
    t = re.sub(r"outlines = Array\[PackedVector2Array\]\(\[.*?\]\)\n(?:vertices = .*\n)?(?:polygons = .*\n)?",
               f"outlines = Array[PackedVector2Array]([{outlines}])\nvertices = {verts}\npolygons = [{polys}]\n", t)
    t = re.sub(r"(\[node name=\"Floor\" type=\"Node2D\"[^\]]*\]\n)position = Vector2\([^)]*\)\n", r"\1position = Vector2(0, 0)\n", t)
    t = re.sub(r"^interaction_polygon = .*$", f"interaction_polygon = Array[PackedVector2Array]([{outlines}])", t, flags=re.M)
    p.write_text(t)
    print("baked floor", room)


def sprite_chars():
    """Point each character at its 46px sprite sheet (10 frames). PixelActor swaps sizes per room."""
    for c in ("paul", "landlord", "barmaid", "reg", "clive", "dot", "gwen", "stan", "jackie", "gaz", "norman",
              "bernie", "rosie"):
        p = ROOT / f"game/characters/{c}/character_{c}.tscn"
        t = p.read_text()
        if f'id="9_{c}tex"' not in t:
            t = add_ext(t, f'[ext_resource type="Texture2D" path="res://game/characters/{c}/{c}_46.png" id="9_{c}tex"]')
        t = re.sub(r'path="res://game/characters/%s/%s(?:_\d+)?\.png"' % (c, c),
                   f'path="res://game/characters/{c}/{c}_46.png"', t)
        if "sheet_base" not in t:
            t = t.replace('cursor = 8\n', f'cursor = 8\nsheet_base = "res://game/characters/{c}/{c}"\n', 1)
        t = re.sub(r"^interaction_polygon = PackedVector2Array\(\)$",
                   "interaction_polygon = PackedVector2Array(-10, -46, 10, -46, 10, 0, -10, 0)", t, flags=re.M)
        # the collision shape itself (what Popochiu actually hit-tests for characters)
        t = re.sub(r'(\[node name="InteractionPolygon"[^\]]*\]\n(?:visible = false\n)?)polygon = PackedVector2Array\([^)]*\)',
                   r"\1polygon = PackedVector2Array(-10, -46, 10, -46, 10, 0, -10, 0)", t)
        g = ROOT / f"game/characters/{c}/character_{c}.gd"
        gs = g.read_text()
        if "extends PopochiuCharacter" in gs:
            g.write_text(gs.replace("extends PopochiuCharacter", "extends PixelActor", 1))
        t = re.sub(r'(\[node name="Sprite2D" type="Sprite2D" parent="\."[^\]]*\]\n)(?:texture = [^\n]*\n)?(?:hframes = \d+\n)?(?:offset = [^\n]*\n)?',
                   lambda m: m.group(1) + 'texture = ExtResource("9_%stex")\nhframes = 10\noffset = Vector2(0, -23)\n' % c, t)
        t = re.sub(r"^flips_when = \d+\n", "", t, flags=re.M)
        t = t.replace('cursor = 8\n', 'cursor = 8\nflips_when = 2\n', 1)
        p.write_text(t)
        print("sprite", c)


def doorstop_sprite(room):
    """Skittle pin propping the Cross House exit door open. A separate sprite so it can vanish
    when Paul picks it up (room script hides Props/DoorstopPin)."""
    if room != "cross_house_tavern":
        return
    path = ROOT / f"game/rooms/{room}/room_{room}.tscn"
    text = path.read_text()
    if 'name="DoorstopPin"' in text:
        return
    res = f"res://game/rooms/{room}/props/doorstop_pin.png"
    eid = f"{next_ext_id(text)}_doorstop"
    text = add_ext(text, f'[ext_resource type="Texture2D" path="{res}" id="{eid}"]')
    node = (f'[node name="DoorstopPin" type="Sprite2D" parent="Props"]\n'
            f'position = Vector2(283, 104)\ntexture_filter = 1\ntexture = ExtResource("{eid}")\n'
            f'centered = false\noffset = Vector2(-4, -14)\n\n')
    text = text.replace('[node name="Hotspots"', node + '[node name="Hotspots"', 1)
    path.write_text(text)
    print("doorstop sprite")


def beam_darts_sprite(room, spec):
    """House darts stuck in the beam over the oche. A sprite, not part of the background, because
    they fall out when Paul thumps the oak post (the room script hides Props/BeamDarts)."""
    if room != "berkeley_arms" or "beam_darts" not in spec.get("_meta", {}):
        return
    x, y = (round(v) for v in spec["_meta"]["beam_darts"])
    path = ROOT / f"game/rooms/{room}/room_{room}.tscn"
    text = path.read_text()
    text = re.sub(r'\n\[node name="BeamDarts" type="Sprite2D"[^\]]*\]\n(?:[^\[\n][^\n]*\n)*', "\n", text)
    res = f"res://game/rooms/{room}/props/beam_darts.png"
    if f'path="{res}"' not in text:
        text = add_ext(text, f'[ext_resource type="Texture2D" path="{res}" id="{next_ext_id(text)}_beamdarts"]')
    eid = re.search(r'path="%s" id="([^"]+)"' % re.escape(res), text).group(1)
    node = (f'[node name="BeamDarts" type="Sprite2D" parent="Props"]\n'
            f'position = Vector2({x}, {y})\ntexture_filter = 1\ntexture = ExtResource("{eid}")\n'
            f'centered = false\noffset = Vector2(-4, 0)\n\n')
    text = text.replace('[node name="Hotspots"', node + '[node name="Hotspots"', 1)
    path.write_text(text)
    print("beam darts sprite", (x, y))


def _sprite_node(room, name, png, pos, offset):
    """(Re)place a Props/<name> Sprite2D showing props/<png>, idempotently."""
    path = ROOT / f"game/rooms/{room}/room_{room}.tscn"
    text = path.read_text()
    text = re.sub(r'\n\[node name="%s" type="Sprite2D"[^\]]*\]\n(?:[^\[\n][^\n]*\n)*' % name, "\n", text)
    res = f"res://game/rooms/{room}/props/{png}"
    if f'path="{res}"' not in text:
        text = add_ext(text, f'[ext_resource type="Texture2D" path="{res}" id="{next_ext_id(text)}_{name.lower()}"]')
    eid = re.search(r'path="%s" id="([^"]+)"' % re.escape(res), text).group(1)
    node = (f'[node name="{name}" type="Sprite2D" parent="Props"]\n'
            f'position = Vector2({pos[0]}, {pos[1]})\ntexture_filter = 1\ntexture = ExtResource("{eid}")\n'
            f'centered = false\noffset = Vector2({offset[0]}, {offset[1]})\n\n')
    text = text.replace('[node name="Hotspots"', node + '[node name="Hotspots"', 1)
    text = re.sub(r"\n{3,}", "\n\n", text)
    path.write_text(text)


def magic_eye_sprites(room, spec):
    """Britannia: the Magic Eye's dots (drawn by tools/sprites.py, crisper than the render) and
    its double-vision copy, which floats ghost_dx px to the right and only shows from drunk 60
    (the room script toggles Props/GhostPicture with the GhostPicture hotspot)."""
    if room != "britannia" or "magic_eye" not in spec.get("_meta", {}):
        return
    x0, y0, x1, y1 = spec["_meta"]["magic_eye"]
    dx = spec["_meta"]["ghost_dx"]
    # sort them just behind everything else on the wall: position at the picture's bottom edge
    _sprite_node(room, "MagicEyeDots", "magic_eye.png", (x0, y1), (0, y0 - y1))
    _sprite_node(room, "GhostPicture", "ghost_picture.png", (x0 + dx, y1), (0, y0 - y1))
    print("magic eye sprites", (x0, y0, x1, y1), dx)
def _prop_sprite(text, room, node, png, pos, offset):
    """(Re)place a Sprite2D under Props, before the Hotspots node."""
    text = re.sub(r'\n\[node name="%s" type="Sprite2D"[^\]]*\]\n(?:[^\[\n][^\n]*\n)*' % node, "\n", text)
    res = f"res://game/rooms/{room}/props/{png}"
    if f'path="{res}"' not in text:
        text = add_ext(text, f'[ext_resource type="Texture2D" path="{res}" id="{next_ext_id(text)}_{node.lower()}"]')
    eid = re.search(r'path="%s" id="([^"]+)"' % re.escape(res), text).group(1)
    node_txt = (f'[node name="{node}" type="Sprite2D" parent="Props"]\n'
                f'position = Vector2({pos[0]}, {pos[1]})\ntexture_filter = 1\ntexture = ExtResource("{eid}")\n'
                f'centered = false\noffset = Vector2({offset[0]}, {offset[1]})\n\n')
    text = text.replace('[node name="Hotspots"', node_txt + '[node name="Hotspots"', 1)
    return re.sub(r"\n{3,}", "\n\n", text)


def table_cutout(room, spec):
    """Cut the pool table out of the background as a y-sorted sprite, using the table-only alpha
    mask Blender rendered (art/renders/<room>_table.png), so Paul is hidden behind it from the
    back and drawn over it from the front. Without the mask a rectangle would hide him behind
    plain wall too."""
    meta = spec.get("_meta", {})
    mask_png = ROOT / "art" / "renders" / f"{room}_table.png"
    if "table_baseline" not in meta:
        return
    from PIL import Image
    out = ROOT / f"game/rooms/{room}/props/pool_table_front.png"
    if mask_png.exists():
        bg = Image.open(ROOT / f"game/rooms/{room}/props/bg_{room}.png").convert("RGBA")
        a = Image.open(mask_png).getchannel("A").resize((320, 200), Image.Resampling.BOX)
        a = a.point(lambda v: 255 if v >= 110 else 0)
        x0, y0, x1, y1 = a.getbbox()
        crop = bg.crop((x0, y0, x1, y1))
        crop.putalpha(a.crop((x0, y0, x1, y1)))
        crop.save(out)
        meta["_table_box"] = (x0, y0, x1, y1)
        (ROOT / "art" / "renders" / f"{room}_table_box.json").write_text(json.dumps([x0, y0, x1, y1]))
    else:  # renders are not committed: keep the box the last cut used
        box = ROOT / "art" / "renders" / f"{room}_table_box.json"
        if not box.exists() or not out.exists():
            return
        x0, y0, x1, y1 = json.loads(box.read_text())
    base = round(meta["table_baseline"])
    path = ROOT / f"game/rooms/{room}/room_{room}.tscn"
    text = _prop_sprite(path.read_text(), room, "PoolTableFront", "pool_table_front.png", (0, base), (x0, y0 - base))
    path.write_text(text)
    print("table cut-out", (x0, y0, x1, y1), "baseline", base)


def pickup_sprites(room, spec):
    """Things Paul picks up in the Nottingham Arms (drawn by tools/sprites.py): the cue butt in
    the rack, the pool rest leaning on the wall and Norman's cue shaft by the fireplace. Each
    anchor is the bottom of the object; the room script hides them once taken."""
    meta = spec.get("_meta", {})
    if room != "nottingham_arms" or "cue_butt" not in meta:
        return
    from PIL import Image
    path = ROOT / f"game/rooms/{room}/room_{room}.tscn"
    text = path.read_text()
    for node, key, png in (("CueButt", "cue_butt", "cue_butt.png"), ("PoolRestProp", "pool_rest", "pool_rest.png"),
                           ("CueShaftProp", "cue_shaft", "cue_shaft.png")):
        im = Image.open(ROOT / f"game/rooms/{room}/props/{png}")
        x, y = (round(v) for v in meta[key])
        text = _prop_sprite(text, room, node, png, (x, y), (-(im.width // 2), -im.height))
    path.write_text(text)
    print("pickup sprites")


def black_bear_props(room, spec):
    """Ye Olde Black Bear: Ursula asleep on the hearth (the room script swaps her texture and
    moves her to the window once a hiccup wakes her) and the table wedge she was lying on (moved
    under the pool table's short leg once levelled). Anchors are bottom-centre."""
    meta = spec.get("_meta", {})
    if room != "black_bear" or "ursula" not in meta:
        return
    from PIL import Image
    path = ROOT / f"game/rooms/{room}/room_{room}.tscn"
    text = path.read_text()
    for node, key, png in (("Ursula", "ursula", "ursula_asleep.png"), ("WedgeProp", "wedge", "wedge.png")):
        im = Image.open(ROOT / f"game/rooms/{room}/props/{png}")
        x, y = (round(v) for v in meta[key])
        text = _prop_sprite(text, room, node, png, (x, y), (-(im.width // 2), -im.height))
    path.write_text(text)
    print("black bear props")


def mythe_props(room, spec):
    """The Mythe bridge ending: Paul's lift home and its headlights, hidden until the ending
    drives them along the deck (the room script tweens them from deck_far to deck_near)."""
    meta = spec.get("_meta", {})
    if room != "mythe_bridge" or "deck_far" not in meta:
        return
    path = ROOT / f"game/rooms/{room}/room_{room}.tscn"
    text = path.read_text()
    x, y = (round(v) for v in meta["deck_far"])
    text = _prop_sprite(text, room, "Headlights", "headlights.png", (x, y), (16, -6))
    text = _prop_sprite(text, room, "Car", "car.png", (x, y), (0, -7))
    for node in ("Car", "Headlights"):
        text = text.replace('[node name="%s" type="Sprite2D" parent="Props"]\n' % node,
                            '[node name="%s" type="Sprite2D" parent="Props"]\nvisible = false\n' % node)
    path.write_text(text)
    print("mythe props")


def bar_front(room, spec):
    """Cut the bar counter out of the background as a y-sorted sprite, so the landlord stands
    behind it and Paul in front of it."""
    if room not in BAR_ROOMS or "Bar" not in spec:
        return
    from PIL import Image
    x0, y0, x1, y1 = spec["_meta"]["hotspots"]["Bar"] if "_meta" in spec else (
        spec["Bar"]["poly"][0][0], spec["Bar"]["poly"][0][1], spec["Bar"]["poly"][2][0], spec["Bar"]["poly"][2][1])
    bg = Image.open(ROOT / f"game/rooms/{room}/props/bg_{room}.png").convert("RGBA")
    crop = bg.crop((x0, y0, x1, y1))
    out = ROOT / f"game/rooms/{room}/props/bar_front.png"
    crop.save(out)
    path = ROOT / f"game/rooms/{room}/room_{room}.tscn"
    text = path.read_text()
    text = re.sub(r'\n\[node name="BarFront"[^\]]*\]\n(?:[^\[\n][^\n]*\n)*', "\n", text)
    if 'path="res://game/rooms/%s/props/bar_front.png"' % room not in text:
        text = add_ext(text, f'[ext_resource type="Texture2D" path="res://game/rooms/{room}/props/bar_front.png" id="{next_ext_id(text)}_barfront"]')
    eid = re.search(r'path="res://game/rooms/%s/props/bar_front.png" id="([^"]+)"' % room, text).group(1)
    node = (f'[node name="BarFront" type="Sprite2D" parent="Props"]\n'
            f'position = Vector2(0, {y1})\ntexture_filter = 1\ntexture = ExtResource("{eid}")\n'
            f'centered = false\noffset = Vector2({x0}, {y0 - y1})\n\n')
    text = text.replace('[node name="Hotspots"', node + '[node name="Hotspots"', 1)
    text = re.sub(r"\n{3,}", "\n\n", text)  # removing/re-adding nodes each run used to pile up blank lines
    path.write_text(text)
    print("bar front", (x0, y0, x1, y1))


def item_icons():
    for k in ("coin", "pint", "crawl_card", "skittle_pin", "darts", "halfpenny", "cue_butt", "cue_shaft", "house_cue", "pool_rest",
              "wedge"):
        p = ROOT / f"game/inventory_items/{k}/inventory_item_{k}.tscn"
        t = p.read_text()
        if "texture = " in t:
            continue
        eid = f"9_{k}"
        t = add_ext(t, f'[ext_resource type="Texture2D" path="res://game/inventory_items/{k}/{k}.png" id="{eid}"]') \
            if "[ext_resource" in t else t
        t = re.sub(r'(\[node name="Item\w+" type="TextureRect"[^\]]*\]\n)',
                   r'\1texture = ExtResource("%s")\n' % eid, t)
        p.write_text(t)
        print("icon", k)


if __name__ == "__main__":
    for r, s in ROOMS.items():
        s = from_render(r, s)
        layout(r, s)
        bake_floor(r, s["Floor"]["poly"], s["Floor"].get("holes", ()))
        bar_front(r, s)
        doorstop_sprite(r)
        beam_darts_sprite(r, s)
        magic_eye_sprites(r, s)
        table_cutout(r, s)
        pickup_sprites(r, s)
        black_bear_props(r, s)
        mythe_props(r, s)
    sprite_chars()
    item_icons()
