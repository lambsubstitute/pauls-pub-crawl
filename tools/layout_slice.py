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
}
BAR_ROOMS = {"cross_house_tavern", "hop_pole"}

import json

DESC = {
    "TavernDoor": "Cross House Tavern door", "Abbey": "Tewkesbury Abbey", "Bench": "Bench",
    "Bar": "Bar", "QuizMachine": "Quiz machine", "ExitDoor": "Door to Church Street",
    "HopPoleDoor": "Royal Hop Pole door", "SkittleAlley": "Skittle alley", "Portrait": "Portrait",
}


def from_render(room, fallback):
    j = ROOT / "art" / "renders" / f"{room}.json"
    if not j.exists():
        return fallback
    d = json.loads(j.read_text())
    spec = {"Floor": {"poly": [(round(x), round(y)) for x, y in d["floor"]]}, "npcs": {}}
    for name in fallback:
        if name in ("Floor", "npcs"):
            continue
        if name not in d["hotspots"]:
            if fallback[name].get("manual"):
                spec[name] = fallback[name]
            continue
        x0, y0, x1, y1 = d["hotspots"][name]
        wx, wy = d["walk_points"].get(name, ((x0 + x1) / 2, y1 + 4))
        wx = min(x1, max(x0, wx))  # perspective can push floor points past the object's own width
        if name == "Bar":
            y0 = max(y0, y1 - 18)  # counter front only, so the landlord behind it stays clickable
        wy = min(146, max(spec["Floor"]["poly"][0][1] + 2, wy))
        spec[name] = {"poly": rect(x0, y0, x1, y1), "walk": (round(wx), round(wy)), "desc": DESC.get(name, name),
                      "baseline": y1 if name != "Abbey" else 0}
    if "landlord_pos" in d:
        spec["npcs"]["Landlord"] = tuple(round(v) for v in d["landlord_pos"])
    for npc, pos in d.get("npc", {}).items():
        spec["npcs"][npc] = tuple(round(v) for v in pos)
    # where Paul stands to talk to each NPC, stored relative to the NPC (Popochiu walk_to_point)
    spec["npc_walk"] = {n: (round(d["walk_points"][n][0] - p[0]), round(d["walk_points"][n][1] - p[1]))
                        for n, p in spec["npcs"].items() if n in d.get("walk_points", {})}
    spec["_meta"] = d
    return spec


CHAR_SCENES = {c: f"res://game/characters/{c.lower()}/character_{c.lower()}.tscn"
               for c in ("Landlord", "Barmaid", "Reg")}


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
            text = set_node_props(text, "Floor", "WalkableAreas", {
                "interaction_polygon": f"Array[PackedVector2Array]([{vec_array(s['poly'])}])",
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


def bake_floor(room, poly):
    """Write the floor polygon into the walkable area's own scene, pre-baked.

    Popochiu rebakes navigation at runtime from the room's interaction_polygon, but the web
    export still paths on the NavigationPolygon saved in this scene (the factory's 20px default
    square), so Paul walked to its corner at (10, 10). Saving the real shape fixes that.
    """
    p = ROOT / f"game/rooms/{room}/walkable_areas/floor/walkable_area_floor.tscn"
    t = p.read_text()
    arr = vec_array(poly)
    idx = ", ".join(str(i) for i in range(len(poly)))
    t = re.sub(r"outlines = Array\[PackedVector2Array\]\(\[.*?\]\)\n(?:vertices = .*\n)?(?:polygons = .*\n)?",
               f"outlines = Array[PackedVector2Array]([{arr}])\nvertices = {arr}\npolygons = [PackedInt32Array({idx})]\n", t)
    t = re.sub(r"(\[node name=\"Floor\" type=\"Node2D\"[^\]]*\]\n)position = Vector2\([^)]*\)\n", r"\1position = Vector2(0, 0)\n", t)
    t = re.sub(r"^interaction_polygon = .*$", f"interaction_polygon = Array[PackedVector2Array]([{arr}])", t, flags=re.M)
    p.write_text(t)
    print("baked floor", room)


def sprite_chars():
    """Point each character at its 46px sprite sheet (10 frames). PixelActor swaps sizes per room."""
    for c in ("paul", "landlord", "barmaid", "reg"):
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
    path.write_text(text)
    print("bar front", (x0, y0, x1, y1))


def item_icons():
    for k in ("coin", "pint", "crawl_card", "skittle_pin"):
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
        bake_floor(r, s["Floor"]["poly"])
        bar_front(r, s)
        doorstop_sprite(r)
    sprite_chars()
    item_icons()
