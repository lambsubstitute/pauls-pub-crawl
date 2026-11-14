extends Node
## Game-wide state. Every script var here is saved/loaded by Popochiu automatically.

signal drunk_changed(value: int)

const PUBS := [
	"Cross House Tavern", "Royal Hop Pole", "Berkeley Arms",
	"Britannia Inn", "Nottingham Arms", "Ye Olde Black Bear",
]

## 0 sober .. 100 "has a sit down". See DESIGN.md drunk table.
var drunk := 0: set = set_drunk
var stamps := 0: set = set_stamps
var found_coin := false
var quiz_won := false
var had_free_pint := false
var last_room := ""

var _t := 0.0
var _dbg_t := 0.0
var _hud: CanvasLayer
var _bar: ColorRect
var _label: Label


func _ready() -> void:
	_build_hud()
	var test := OS.get_environment("PPC_TEST")
	if test != "" and ResourceLoader.exists("res://tests/%s_test.gd" % test):
		add_child(load("res://tests/%s_test.gd" % test).new())


func set_drunk(v: int) -> void:
	drunk = clampi(v, 0, 100)
	drunk_changed.emit(drunk)
	_update_hud()


func set_stamps(v: int) -> void:
	stamps = clampi(v, 0, PUBS.size())
	_update_hud()


func drink(amount := 15) -> void:
	drunk += amount


## How far things wobble right now, in pixels. Mini-games use this too.
func sway_amount() -> float:
	if drunk < 30:
		return 0.0
	return remap(float(drunk), 30.0, 100.0, 0.5, 6.0)


## Figure-8 wobble vector; `speed` lets mini-games use a different rhythm.
func sway(speed := 1.0) -> Vector2:
	var a := sway_amount()
	return Vector2(sin(_t * 1.3 * speed) * a, sin(_t * 2.6 * speed) * a * 0.5)


func mood() -> String:
	if drunk < 30: return "Sober"
	if drunk < 60: return "Merry"
	if drunk < 80: return "Tipsy"
	if drunk < 95: return "Wobbly"
	return "Sit down!"


func _process(delta: float) -> void:
	_t += delta
	_dbg_t += delta
	if OS.is_debug_build() and _dbg_t > 1.0:
		_dbg_t = 0.0
		var cc = get_node_or_null("/root/C")
		if cc and cc.player:
			var pl = cc.player
			print("[dbg] player pos ", pl.position, " gpos ", pl.global_position, " vis ", pl.visible, " scale ", pl.scale, " parent ", pl.get_parent().name if pl.get_parent() else "none", " cam ", get_node("/root/E").camera.offset if get_node_or_null("/root/E") else "")
	var cam = get_node_or_null("/root/E")
	if cam and cam.get("camera"):
		cam.camera.offset = sway(0.6).round()


func _build_hud() -> void:
	_hud = CanvasLayer.new()
	_hud.layer = 5
	add_child(_hud)
	var bg := ColorRect.new()
	bg.color = Color(0, 0, 0, 0.55)
	bg.position = Vector2(2, 2)
	bg.size = Vector2(54, 10)
	_hud.add_child(bg)
	_bar = ColorRect.new()
	_bar.position = Vector2(3, 3)
	_bar.size = Vector2(0, 2)
	_hud.add_child(_bar)
	_label = Label.new()
	_label.position = Vector2(3, 3)
	_label.add_theme_font_size_override("font_size", 8)
	_label.add_theme_font_override("font", load("res://addons/popochiu/engine/objects/gui/fonts/minecraftia-regular.ttf"))
	_hud.add_child(_label)
	_update_hud()


func _update_hud() -> void:
	if not _bar:
		return
	_bar.size.x = 52.0 * drunk / 100.0
	_bar.color = Color.from_hsv(lerp(0.33, 0.0, drunk / 100.0), 0.8, 0.9)
	_label.position.y = -1
	_label.text = "%s  %d/6" % [mood(), stamps]
