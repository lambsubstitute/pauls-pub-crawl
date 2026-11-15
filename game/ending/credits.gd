extends CanvasLayer
## THE END: the closing card and credits, over the Mythe bridge. Two buttons: keep exploring
## (closes the card, Paul is back on the riverside path) or start again (reloads the game).
##
##   const Credits := preload("res://game/ending/credits.gd")
##   var choice: String = await Credits.play(get_tree())   # "explore" or "restart"
##   if choice == "restart": Credits.restart(get_tree())

signal finished(choice: String)

const FONT := preload("res://addons/popochiu/engine/objects/gui/fonts/minecraftia-regular.ttf")
const GOLD := Color(1.0, 0.82, 0.35)
const CREAM := Color(0.94, 0.91, 0.82)
const DIM := Color(0.62, 0.66, 0.80)
## Seconds for the text to fade in, line by line.
const LINE_DELAY := 0.25

const LINES := [
	["THE END", GOLD, 16],
	["PAUL'S PUB CRAWL", CREAM, 8],
	["Made for Paul", GOLD, 8],
	["", CREAM, 8],
	["Six pubs, six stamps, one champion of Tewkesbury.", CREAM, 8],
	["", CREAM, 8],
	["Cross House Tavern - Bev and the quiz machine", DIM, 8],
	["Royal Hop Pole - Reg and the skittle alley", DIM, 8],
	["Berkeley Arms - Clive and Dot at the oche", DIM, 8],
	["Britannia Inn - Gwen and Stan at shove ha'penny", DIM, 8],
	["Nottingham Arms - Jackie, Gaz and Norman", DIM, 8],
	["Ye Olde Black Bear - Rosie, Bernie and Ursula", DIM, 8],
	["", CREAM, 8],
	["Paul always has a glass of water between halves.", CREAM, 8],
]

var _box: VBoxContainer
var _buttons: HBoxContainer
var _labels: Array[Label] = []
var _t := 0.0


static func play(tree: SceneTree) -> String:
	var s = load("res://game/ending/credits.gd").new()
	tree.root.add_child(s)
	var choice: String = await s.finished
	s.queue_free()
	return choice


## Start the whole game again from Church Street with nothing on the card: reload the page on the
## web build, relaunch the executable on desktop.
static func restart(tree: SceneTree) -> void:
	if OS.has_feature("web"):
		JavaScriptBridge.eval("window.location.reload()")
		return
	OS.create_process(OS.get_executable_path(), OS.get_cmdline_args())
	tree.quit()


func _ready() -> void:
	layer = 25
	var shade := ColorRect.new()  # swallow clicks so the adventure GUI underneath stays put
	shade.color = Color(0.01, 0.015, 0.05, 0.88)
	shade.size = Vector2(320, 200)
	shade.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(shade)
	_box = VBoxContainer.new()
	_box.position = Vector2(8, 4)
	_box.size = Vector2(304, 160)
	_box.alignment = BoxContainer.ALIGNMENT_BEGIN
	_box.add_theme_constant_override("separation", -4)
	add_child(_box)
	for l in LINES:
		var lab := Label.new()
		lab.text = l[0]
		lab.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		lab.add_theme_font_override("font", FONT)
		lab.add_theme_font_size_override("font_size", l[2])
		lab.add_theme_color_override("font_color", l[1])
		lab.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.8))
		lab.add_theme_constant_override("shadow_offset_x", 1)
		lab.add_theme_constant_override("shadow_offset_y", 1)
		lab.modulate.a = 0.0
		lab.custom_minimum_size = Vector2(304, 0)
		_box.add_child(lab)
		_labels.append(lab)
	_buttons = HBoxContainer.new()
	_buttons.position = Vector2(40, 178)
	_buttons.size = Vector2(240, 18)
	_buttons.alignment = BoxContainer.ALIGNMENT_CENTER
	_buttons.add_theme_constant_override("separation", 16)
	_buttons.modulate.a = 0.0
	add_child(_buttons)
	_buttons.add_child(_button("Keep exploring", "explore"))
	_buttons.add_child(_button("Start again", "restart"))


func _button(text: String, choice: String) -> Button:
	var b := Button.new()
	b.text = text
	b.name = choice.capitalize()
	b.add_theme_font_override("font", FONT)
	b.add_theme_font_size_override("font_size", 8)
	b.add_theme_color_override("font_color", CREAM)
	b.add_theme_color_override("font_hover_color", GOLD)
	b.focus_mode = Control.FOCUS_NONE
	b.pressed.connect(func(): finished.emit(choice))
	return b


func _process(delta: float) -> void:
	_t += delta
	for i in _labels.size():
		_labels[i].modulate.a = clampf((_t - i * LINE_DELAY) / 0.6, 0.0, 1.0)
	_buttons.modulate.a = clampf((_t - _labels.size() * LINE_DELAY) / 0.6, 0.0, 1.0)
