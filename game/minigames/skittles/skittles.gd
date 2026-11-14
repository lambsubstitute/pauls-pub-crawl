extends CanvasLayer
## West Country skittles: three balls at nine pins set in a diamond, seen from above.
## Click once to lock the aim (marker sweeps across the lane), click again to lock the power
## (bar pumps up and down). Drink makes the marker wobble and the bar jitter.
##
##   var score: int = await Skittles.play(get_tree(), reg_score)
##
## The roll itself is plain maths in simulate_roll(), so tests can drive it headless.

signal finished(score: int)

const FONT := preload("res://addons/popochiu/engine/objects/gui/fonts/minecraftia-regular.ttf")
const BALLS := 3

# Lane geometry in screen px (320x200 viewport). Pins in "lane units": x -1..1 across, y 0..1 up.
const LANE := Rect2(124, 18, 72, 128)
const PIN_R := 0.075
const BALL_R := 0.11
const PIN_LAYOUT := [  # diamond, front pin first
	Vector2(0.0, 0.70),
	Vector2(-0.22, 0.76), Vector2(0.22, 0.76),
	Vector2(-0.44, 0.82), Vector2(0.0, 0.82), Vector2(0.44, 0.82),
	Vector2(-0.22, 0.88), Vector2(0.22, 0.88),
	Vector2(0.0, 0.94),
]

enum Phase { AIM, POWER, ROLLING, BETWEEN, DONE }

var reg_score := 6
var score := 0
var ball := 0
var standing: Array[bool] = []
var phase := Phase.AIM
var aim := 0.0         # lane x where the ball is released, -1..1
var power := 0.0       # 0..1
var _t := 0.0
var _roll_path: Array = []   # [{pos, knocked:[idx...]}] keyframes from simulate_roll
var _roll_t := 0.0
var _msg := ""
var _rng := RandomNumberGenerator.new()
var _canvas: Control


static func play(tree: SceneTree, reg := 6) -> int:
	var s = load("res://game/minigames/skittles/skittles.gd").new()
	s.reg_score = reg
	tree.root.add_child(s)
	var result: int = await s.finished
	s.queue_free()
	return result


func _ready() -> void:
	layer = 20
	_rng.randomize()
	_reset_pins()
	var shade := ColorRect.new()  # swallow clicks so the adventure GUI underneath stays put
	shade.color = Color(0, 0, 0, 0.55)
	shade.size = Vector2(320, 200)
	shade.mouse_filter = Control.MOUSE_FILTER_STOP
	shade.gui_input.connect(_on_input)
	add_child(shade)
	_canvas = Control.new()
	_canvas.size = Vector2(320, 200)
	_canvas.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_canvas.draw.connect(_draw_game)
	add_child(_canvas)


func _reset_pins() -> void:
	standing.clear()
	for i in PIN_LAYOUT.size():
		standing.append(true)


func _drunk() -> float:
	var g = get_node_or_null("/root/Globals")
	return g.sway_amount() if g else 0.0


func _on_input(ev: InputEvent) -> void:
	if not (ev is InputEventMouseButton and ev.pressed and ev.button_index == MOUSE_BUTTON_LEFT):
		return
	match phase:
		Phase.AIM:
			phase = Phase.POWER
			_t = 0.0
		Phase.POWER:
			_bowl()
		Phase.BETWEEN:
			_next_ball()
		Phase.DONE:
			finished.emit(score)


func _process(delta: float) -> void:
	_t += delta
	var wob := _drunk()
	match phase:
		Phase.AIM:
			# steady sweep, plus a figure-8 wobble that grows with drink
			aim = sin(_t * 1.6) * 0.85 + sin(_t * 5.3) * wob * 0.05
			aim = clampf(aim, -0.95, 0.95)
		Phase.POWER:
			power = 0.5 - 0.5 * cos(_t * 3.2) + (sin(_t * 17.0) * wob * 0.02)
			power = clampf(power, 0.0, 1.0)
		Phase.ROLLING:
			_roll_t += delta * 1.6
			for k in _roll_path:
				if k.t <= _roll_t:
					for idx in k.knocked:
						standing[idx] = false
			if _roll_t >= _roll_path[-1].t:
				_end_ball()
	_canvas.queue_redraw()


func _bowl() -> void:
	# Drink also nudges the release: a tipsy hand drifts the line a little.
	var drift := _rng.randf_range(-1.0, 1.0) * _drunk() * 0.04
	_roll_path = simulate_roll(aim, power, drift, standing, _rng.randi())
	_roll_t = 0.0
	phase = Phase.ROLLING


func _end_ball() -> void:
	var before := 0
	for k in _roll_path:
		before += k.knocked.size()
	score += before
	ball += 1
	if standing.count(true) == 0 and ball < BALLS:
		_msg = "ALL NINE! Pins up again."
		_reset_pins()
	else:
		_msg = "Gutter!" if before == 0 else "One down." if before == 1 else "%d down!" % before
	phase = Phase.DONE if ball >= BALLS else Phase.BETWEEN
	if phase == Phase.DONE:
		_msg = "%d pins. %s" % [score, "You beat Reg!" if score > reg_score else "Reg wins." if score < reg_score else "A tie."]


func _next_ball() -> void:
	phase = Phase.AIM
	_t = _rng.randf() * 3.0
	_msg = ""


## Pure roll maths (no nodes): returns keyframes [{t, pos, knocked}] for the ball's run.
## aim: lane x at release (-1..1). pwr: 0..1. drift: sideways curve. Pins that are already down
## are ignored. Knocked pins can topple neighbours, more often with a harder ball.
static func simulate_roll(aim_x: float, pwr: float, drift: float, up: Array, seed_val: int) -> Array:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_val
	var reach := lerpf(0.45, 1.05, pwr)       # weak balls stop short of the back pins
	var still_up := up.duplicate()
	var frames: Array = []
	var pos := Vector2(aim_x, 0.0)
	var steps := 60
	for s in steps + 1:
		var y := reach * float(s) / steps
		pos = Vector2(aim_x + drift * y * y * 6.0, y)
		if absf(pos.x) > 1.0:  # into the cushion: ball dies
			frames.append({"t": float(s) / steps, "pos": pos, "knocked": []})
			break
		var hit: Array = []
		for i in PIN_LAYOUT.size():
			if still_up[i] and pos.distance_to(PIN_LAYOUT[i]) < PIN_R + BALL_R:
				hit.append(i)
				still_up[i] = false
		# each toppled pin may take out neighbours behind/beside it
		var queue := hit.duplicate()
		while not queue.is_empty():
			var i: int = queue.pop_front()
			for j in PIN_LAYOUT.size():
				if still_up[j] and PIN_LAYOUT[i].distance_to(PIN_LAYOUT[j]) < 0.27 \
						and PIN_LAYOUT[j].y >= PIN_LAYOUT[i].y - 0.01 \
						and rng.randf() < lerpf(0.35, 0.8, pwr):
					still_up[j] = false
					hit.append(j)
					queue.append(j)
		frames.append({"t": float(s) / steps, "pos": pos, "knocked": hit})
	return frames


# ------------------------------------------------------------------ draw ----
func _lane_to_px(p: Vector2) -> Vector2:
	return Vector2(LANE.position.x + (p.x + 1.0) * 0.5 * LANE.size.x,
				   LANE.position.y + (1.0 - p.y) * LANE.size.y)


func _draw_game() -> void:
	var c := _canvas
	var wob := _drunk()
	var sway := Vector2(sin(_t * 1.3) * wob, sin(_t * 2.6) * wob * 0.5).round()
	# panel + title
	c.draw_rect(Rect2(94, 4, 132, 174), Color("2a170c"))
	c.draw_rect(Rect2(94, 4, 132, 174), Color("6b3a18"), false, 1.0)
	c.draw_rect(Rect2(LANE.position + sway, LANE.size), Color("b07a3a"))
	for i in 7:  # boards
		var x := LANE.position.x + 4 + i * 10 + sway.x
		c.draw_line(Vector2(x, LANE.position.y + sway.y), Vector2(x, LANE.end.y + sway.y), Color("9a6630"))
	c.draw_rect(Rect2(LANE.position.x - 6 + sway.x, LANE.position.y + sway.y, 6, LANE.size.y), Color("4a2410"))
	c.draw_rect(Rect2(LANE.end.x + sway.x, LANE.position.y + sway.y, 6, LANE.size.y), Color("4a2410"))
	# pins (drawn twice, offset, when Paul is seeing double)
	var ghosts: Array[Vector2] = [Vector2.ZERO]
	if wob > 2.0:
		ghosts.append(Vector2(wob * 0.8, 0).round())
	for gofs: Vector2 in ghosts:
		var alpha := 1.0 if gofs == Vector2.ZERO else 0.4
		for i in PIN_LAYOUT.size():
			var p: Vector2 = _lane_to_px(PIN_LAYOUT[i]) + sway + gofs
			if standing[i]:
				c.draw_circle(p, 3.2, Color(0.1, 0.06, 0.05, alpha))
				c.draw_circle(p, 2.4, Color(0.93, 0.89, 0.80, alpha))
				c.draw_circle(p, 1.0, Color(0.72, 0.12, 0.10, alpha))
			elif gofs == Vector2.ZERO:
				c.draw_line(p + Vector2(-3, 1), p + Vector2(3, -1), Color("6b5a40"), 2.0)
	# ball
	var ball_lane: Vector2 = Vector2(aim, 0.0)
	if phase == Phase.ROLLING:
		for k in _roll_path:
			if k.t <= _roll_t:
				ball_lane = k.pos
	if phase in [Phase.AIM, Phase.POWER, Phase.ROLLING]:
		var bp := _lane_to_px(ball_lane) + sway
		c.draw_circle(bp, 4.5, Color("1a0e08"))
		c.draw_circle(bp, 3.5, Color("5a3418"))
		c.draw_circle(bp + Vector2(-1, -1), 1.0, Color("8a5a30"))
	if phase == Phase.AIM:
		var ap := _lane_to_px(Vector2(aim, 0.0)) + sway
		c.draw_line(ap + Vector2(0, -8), ap + Vector2(0, -LANE.size.y + 10), Color(1, 1, 1, 0.25), 1.0)
	# power bar
	c.draw_rect(Rect2(204, 30, 8, 100), Color("1a0e08"))
	if phase in [Phase.POWER, Phase.ROLLING, Phase.BETWEEN]:
		var hgt := 98.0 * power
		c.draw_rect(Rect2(205, 129 - hgt, 6, hgt), Color.from_hsv(lerpf(0.33, 0.0, power), 0.85, 0.95))
	# text
	_text(c, Vector2(100, 14), "SKITTLES  vs  REG", Color("fad278"))
	_text(c, Vector2(100, 160), "Ball %d/%d   You: %d   Reg: %d" % [mini(ball + 1, BALLS), BALLS, score, reg_score], Color.WHITE)
	var hint := ""
	match phase:
		Phase.AIM: hint = "Click to aim"
		Phase.POWER: hint = "Click to bowl!"
		Phase.BETWEEN: hint = _msg + "  Click for next ball"
		Phase.DONE: hint = _msg + "  Click to finish"
	_text(c, Vector2(100, 172), hint, Color("b8e0ff"))


func _text(c: Control, pos: Vector2, s: String, col: Color) -> void:
	c.draw_string(FONT, pos + Vector2(1, 1), s, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0, 0, 0, 0.8))
	c.draw_string(FONT, pos, s, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, col)
