@tool
class_name PixelActor
extends PopochiuCharacter
## Sprite-sheet character: 10 frames in one row (0 idle, 1-8 walk, 9 talk), facing right.
## Sheets come in per-room heights (see tools/sprites.py); rooms call set_height() on entry so
## the character is redrawn at the right pixel size instead of being scaled.

const WALK_FRAMES := 8
const TALK_FRAME := WALK_FRAMES + 1
const SHEET_FRAMES := WALK_FRAMES + 2
const TALK_FPS := 6.0
## Walking pace in px/s per px of figure height (~0.67 body-heights per second, an easy stroll).
const SPEED_PER_HEIGHT := 1.2
## How far a foot travels over one full walk cycle, as a fraction of figure height. Matches the
## leg swing in tools/sprites.py; frame rate is derived from it so feet plant instead of skating.
const STRIDE_PER_HEIGHT := 0.56

## Folder + basename of the sheets, e.g. "res://game/characters/paul/paul" -> paul_30.png
@export var sheet_base := ""

var _anim_t := 0.0
var _height := 46
var _was_moving := false


func set_height(px: int) -> void:
	var path := "%s_%d.png" % [sheet_base, px]
	if sheet_base.is_empty() or not ResourceLoader.exists(path):
		return
	_height = px
	var spr: Sprite2D = $Sprite2D
	spr.texture = load(path)
	spr.hframes = SHEET_FRAMES
	var fh := spr.texture.get_height()
	spr.offset = Vector2(0, -fh / 2.0 + 1)
	var hw := px * 0.22
	interaction_polygon = PackedVector2Array([
		Vector2(-hw, -px), Vector2(hw, -px), Vector2(hw, 0), Vector2(-hw, 0)])
	dialog_pos = Vector2(0, -px - 4)
	walk_speed = px * SPEED_PER_HEIGHT


func walk_fps() -> float:
	return walk_speed / (STRIDE_PER_HEIGHT * _height) * WALK_FRAMES


# Animation runs in _physics_process because PopochiuCharacter calls set_process(false) in
# _ready() and only re-enables _process while facing/following another character.
func _physics_process(delta: float) -> void:
	super(delta)
	if Engine.is_editor_hint():
		return
	_anim_t += delta
	var spr: Sprite2D = get_node_or_null("Sprite2D")
	if not spr or spr.hframes < SHEET_FRAMES:
		return
	if is_moving and not _was_moving:
		_anim_t = 0.0  # start each walk on the first stride frame
	_was_moving = is_moving
	if is_moving:
		spr.frame = 1 + int(_anim_t * walk_fps()) % WALK_FRAMES
	elif is_talking:
		spr.frame = TALK_FRAME if int(_anim_t * TALK_FPS) % 2 == 0 else 0
	else:
		spr.frame = 0


# No AnimationPlayer clips: frames are driven above, so silence Popochiu's animation lookups.
func play_animation(_animation_label: String, _animation_fallback := "") -> void:
	pass
