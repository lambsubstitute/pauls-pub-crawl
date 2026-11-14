@tool
class_name PixelActor
extends PopochiuCharacter
## Sprite-sheet character: 8 frames in one row (0 idle, 1-6 walk, 7 talk), facing right.
## Sheets come in per-room heights (see tools/sprites.py); rooms call set_height() on entry so
## the character is redrawn at the right pixel size instead of being scaled.

const WALK_FPS := 10.0
const TALK_FPS := 6.0

## Folder + basename of the sheets, e.g. "res://game/characters/paul/paul" -> paul_30.png
@export var sheet_base := ""

var _anim_t := 0.0
var _height := 46


func set_height(px: int) -> void:
	var path := "%s_%d.png" % [sheet_base, px]
	if sheet_base.is_empty() or not ResourceLoader.exists(path):
		return
	_height = px
	var spr: Sprite2D = $Sprite2D
	spr.texture = load(path)
	spr.hframes = 8
	var fh := spr.texture.get_height()
	spr.offset = Vector2(0, -fh / 2.0 + 1)
	var hw := px * 0.22
	interaction_polygon = PackedVector2Array([
		Vector2(-hw, -px), Vector2(hw, -px), Vector2(hw, 0), Vector2(-hw, 0)])
	dialog_pos = Vector2(0, -px - 4)


func _process(delta: float) -> void:
	super(delta)
	if Engine.is_editor_hint():
		return
	_anim_t += delta
	var spr: Sprite2D = get_node_or_null("Sprite2D")
	if not spr or spr.hframes < 8:
		return
	if is_moving:
		spr.frame = 1 + int(_anim_t * WALK_FPS) % 6
	elif is_talking:
		spr.frame = 7 if int(_anim_t * TALK_FPS) % 2 == 0 else 0
	else:
		spr.frame = 0


# No AnimationPlayer clips: frames are driven above, so silence Popochiu's animation lookups.
func play_animation(_animation_label: String, _animation_fallback := "") -> void:
	pass
