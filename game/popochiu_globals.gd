extends Node
## Game-wide state. Every script var here is saved/loaded by Popochiu automatically.

signal drunk_changed(value: int)

const PUBS := [
	"Cross House Tavern", "Royal Hop Pole", "Berkeley Arms",
	"Britannia Inn", "Nottingham Arms", "Ye Olde Black Bear",
]

## Merry enough to sway into things (DESIGN.md: 30+ is cursor drift and screen sway). The
## Berkeley Arms darts only come down when Paul leans on the post this wobbly.
const WOBBLY := 30
## Seeing double (DESIGN.md: 60+). Mini-games draw a ghost copy; in the Britannia a hidden
## picture only exists in Paul's double vision.
const SEEING_DOUBLE := 60

## 0 sober .. 100 "has a sit down". See DESIGN.md drunk table.
var drunk := 0: set = set_drunk
var stamps := 0: set = set_stamps
var found_coin := false
var quiz_won := false
var had_free_pint := false
var last_room := ""
# Royal Hop Pole
var pin_taken := false        # picked the skittle pin up off the Cross House door
var pin_returned := false     # gave it back to Reg, so the alley has nine pins again
var skittles_won := false
var skittles_best := 0
var hop_pole_pint := false
# Berkeley Arms
var darts_down := false       # knocked the house darts out of the beam over the oche
var darts_given := false      # handed them to Dot, so she'll play
var darts_won := false
var darts_best := 0
var berkeley_halves := 0      # halves Clive has pulled for Paul
# Britannia Inn
var magic_eye_seen := false   # saw the hidden clock + ha'penny in the Magic Eye, seeing double
var halfpenny_found := false  # took Ernie's fifth ha'penny out of the long-case clock
var halfpenny_given := false  # gave it to Stan: a full set of five, so he'll play
var shove_won := false
var shove_best := 0
var britannia_halves := 0     # halves Gwen has pulled for Paul

var _t := 0.0
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


## Water, chips, fresh air: the other way down the drunk table.
func sober(amount := 25) -> void:
	drunk -= amount


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
