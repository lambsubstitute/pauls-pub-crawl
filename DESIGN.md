# Paul's Pub Crawl — Design Doc

Classic verb-grid point-and-click adventure, early-90s Amiga/VGA look, set in
Tewkesbury. Original art, story, music and UI — genre homage, no borrowed assets.

## Pillars
- **Family friendly.** No swearing, no flirting, no dares. Comedy from daft locals,
  slapstick and Paul's wobbly self-belief.
- **Real Tewkesbury.** Real streets and real pubs, recognisable to locals.
- **Drink changes the controls.** Mini-games get harder as Paul gets merrier, but
  some puzzles only open up when he's tipsy.
- **Browser first.** Runs from a link (GitHub Pages).

## Hero
**Paul** — brother-in-law of the dev. Sprite drawn from family photos. Cheerful,
over-confident at darts, terrible at remembering where he left things.

## Goal
Finish the crawl card: one stamp per pub, six pubs, before last orders at the
Black Bear. The champion there won't play anyone without a full card.

## Route (verified open via CAMRA listings, Nov 2026 — recheck before release)
Walks from the Abbey end of Church Street, through the Cross, up High Street to
the Mythe end.

| # | Pub | Address | Main game | Role |
|---|-----|---------|-----------|------|
| 1 | Cross House Tavern | 108 Church St | Quiz machine | Tutorial: verbs, inventory, first stamp |
| 2 | Royal Hop Pole | 94 Church St | Skittles | Pin chain: Cross House doorstop pin -> Reg -> skittles -> Bev stamps |
| 3 | Berkeley Arms | 8 Church St | Darts | Darts intro, drunk meter matters |
| 4 | Britannia Inn | 30 High St | Shove ha'penny | Double-vision puzzle |
| 5 | Nottingham Arms | 129 High St | Pool | Hardest mid-game puzzle |
| 6 | Ye Olde Black Bear | 68 High St | Darts + pool rematch | Finale vs the pub champion |

Fallbacks if any close: Anchor 1774 (42 High St), New Plough (85 Barton St).

Street scenes between pubs: Abbey gates, Church St, the Cross, High St,
riverside / Mill Avon, Mythe bridge (ending).

## Controls / UI
- 320×200 game area, integer-scaled. Bottom panel: verb grid + inventory.
- Verbs: Look at, Pick up, Use, Open, Close, Talk to, Give, Push, Pull.
- Sentence line ("Use pint glass with tap"). Right-click = default verb.
- Dialogue trees with numbered options.

## Drunk meter (0–100)
| Level | Effect |
|-------|--------|
| 0–30 | Clean controls |
| 30–60 | Cursor drift, slight screen sway |
| 60–80 | Double vision on targets, input lag, hiccups interrupt |
| 80–95 | Heavy wobble, slurred lines, odd dialogue options |
| 95+ | "Paul has a sit down" — wakes on a bench, lost time, meter reset to 60 |

Each pint +15ish. Down: chips, water, walking a street scene, time.
No hard fail state — family friendly; overdoing it costs time, not the game.

### Puzzles where tipsy helps
- **Double vision:** some hotspots only exist in the ghost image (60+).
- **Wobble physics:** Paul sways into a shelf, knocks down an item out of reach.
- **Tipsy logic:** certain locals only chat to a merry Paul; extra dialogue options.
- **Sobering up:** chips shop, water at the bar, a riverside walk.

## Mini-games
- **Darts** — 501 / round-the-clock. Aim reticle drifts in a figure-8 that widens
  with the meter; hold to steady (limited breath).
- **Pool** — top-down 8-ball. Cue guide shortens and wobbles; power bar jitters.
- **Skittles** — West Country alley; ball line sways, timing window shrinks.
- **Shove ha'penny** — flick power + angle; table "tilts" when drunk.
- **Quiz machine** — Tewkesbury/general trivia; letters swim when drunk.

## Art pipeline
Quality bar: 320x200, ~32-colour backgrounds with ordered dithering, strong night mood
(cold blue ambient vs warm windows), characters ~16 colours with dark outlines. All art original.

1. `tools/blender/<room>.py` builds the room procedurally in Blender (shared kit in
   `tools/blender/scene_kit.py`) and renders 1280x800. It also projects hotspots, walk points,
   floor and NPC spots into game pixels -> `art/renders/<room>.json`.
   `/Applications/Blender.app/Contents/MacOS/Blender -b -P tools/blender/church_st.py`
2. `python3 tools/pixelate.py <room>` -> stars/moon, area downscale, median-cut palette
   (+ reserved accent colours), 4x4 Bayer dither -> `game/rooms/<room>/props/bg_<room>.png`.
3. `python3 tools/layout_slice.py` writes hotspots/floor/NPC positions from the JSON into the
   room scenes and cuts foreground pieces (e.g. the bar counter) as y-sorted sprites.
4. `python3 tools/sprites.py` draws character sheets (idle, 6-frame walk, talk) at each room's
   figure height (street 30px, pub 46px). `PixelActor` swaps sheets per room.
5. Hand touch-up in Aseprite/LibreSprite is optional on top of step 2.

## Tech
- **Godot 4** + **Popochiu** (adventure framework: rooms, hotspots, inventory,
  dialogue, walkable areas, verb GUI template).
- Web export (HTML5) → GitHub Pages.
- Mini-games as normal Godot scenes, read the drunk meter from a global.

## Milestones
1. **Vertical slice:** Church St scene, Cross House Tavern interior, 2–3 NPCs,
   one inventory puzzle, quiz machine, drunk meter, verb grid, save/load, web build.
2. Darts + Berkeley Arms.
3. Remaining pubs and mini-games.
4. Finale, endings, music/SFX, polish.
