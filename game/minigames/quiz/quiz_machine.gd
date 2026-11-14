extends CanvasLayer
## Pub quiz machine mini-game. Three questions, need 2 right.
## Answers wobble with Globals.sway() so it gets harder to click the right one.
##
##   var won: bool = await QuizMachine.play(get_tree())

signal finished(won: bool)

const FONT := preload("res://addons/popochiu/engine/objects/gui/fonts/minecraftia-regular.ttf")
const QUESTIONS := [
	["Which river meets the Severn at Tewkesbury?", ["Avon", "Thames", "Wye"], 0],
	["Tewkesbury Abbey's tower is in which style?", ["Gothic", "Norman", "Modern"], 1],
	["Which battle was fought here in 1471?", ["Hastings", "Bosworth", "Tewkesbury"], 2],
	["Mustard was once famous in which town?", ["Tewkesbury", "Dijon only", "Leeds"], 0],
	["How many pubs on Paul's crawl?", ["Three", "Six", "Eleven"], 1],
]

var _round := 0
var _score := 0
var _picked: Array = []
var _q_label: Label
var _buttons: Array[Button] = []
var _base: Array[Vector2] = []
var _t := 0.0


static func play(tree: SceneTree) -> bool:
	var q = load("res://game/minigames/quiz/quiz_machine.gd").new()
	tree.root.add_child(q)
	var won: bool = await q.finished
	q.queue_free()
	return won


func _ready() -> void:
	layer = 20
	var qs := QUESTIONS.duplicate()
	qs.shuffle()
	_picked = qs.slice(0, 3)

	var panel := ColorRect.new()
	panel.color = Color("181430")
	panel.position = Vector2(30, 14)
	panel.size = Vector2(260, 116)
	add_child(panel)
	var title := _label("QUIZ-O-MATIC  -  WIN A STAMP!", Vector2(38, 18), Color("fad278"))
	add_child(title)
	_q_label = _label("", Vector2(38, 34), Color.WHITE)
	_q_label.size = Vector2(244, 30)
	_q_label.autowrap_mode = TextServer.AUTOWRAP_WORD
	add_child(_q_label)
	for i in 3:
		var b := Button.new()
		b.add_theme_font_override("font", FONT)
		b.add_theme_font_size_override("font_size", 8)
		b.size = Vector2(110, 16)
		b.position = Vector2(105, 70 + i * 19)
		b.focus_mode = Control.FOCUS_NONE
		b.pressed.connect(_answer.bind(i))
		add_child(b)
		_buttons.append(b)
		_base.append(b.position)
	_show()


func _label(text: String, pos: Vector2, col: Color) -> Label:
	var l := Label.new()
	l.text = text
	l.position = pos
	l.add_theme_font_override("font", FONT)
	l.add_theme_font_size_override("font_size", 8)
	l.add_theme_color_override("font_color", col)
	return l


func _show() -> void:
	var q = _picked[_round]
	_q_label.text = "Q%d. %s" % [_round + 1, q[0]]
	for i in 3:
		_buttons[i].text = q[1][i]


func _answer(i: int) -> void:
	if i == _picked[_round][2]:
		_score += 1
	_round += 1
	if _round >= _picked.size():
		finished.emit(_score >= 2)
	else:
		_show()


func _process(delta: float) -> void:
	_t += delta
	var g = get_node_or_null("/root/Globals")
	if not g:
		return
	for i in _buttons.size():
		# Each answer wobbles out of phase so they drift over each other when drunk.
		var a: float = g.sway_amount() * 1.5
		_buttons[i].position = _base[i] + Vector2(sin(_t * 2.0 + i * 2.1) * a, cos(_t * 1.7 + i) * a * 0.6)
