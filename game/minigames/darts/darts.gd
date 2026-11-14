extends CanvasLayer
## Darts: three darts at a full-size board, most points wins, against a fixed score.
## Move the mouse to aim. The reticle drifts round a figure-8 that widens as Paul gets merrier.
## Hold the left button to steady your hand (limited breath; drink empties it faster), release
## to throw. Run out of breath and the hand shakes worse than before.
##
##   var score: int = await Darts.play(get_tree(), dot_score)
##
## Scoring and the throw itself are static, node-free maths (score_at, drift, simulate_dart,
## simulate_match), so tests can drive them headless.

signal finished(score: int)

const FONT := preload("res://addons/popochiu/engine/objects/gui/fonts/minecraftia-regular.ttf")
const DARTS := 3
const CENTRE := Vector2(150, 88)
const R := 52.0   # board radius in px: the outer edge of the double ring

# Board in "board units": radius 1 = outer edge of the doubles, y points down (screen space).
const SEGMENTS := [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
const BULL_R := 0.037
const OUTER_BULL_R := 0.094
const TREBLE_IN := 0.582
const TREBLE_OUT := 0.629
const DOUBLE_IN := 0.953

# Hand steadiness, as a multiplier on the drift.
const HOLD_STEADY := 0.3    # holding the button with breath left
const FREE_HAND := 1.0      # not holding
const OUT_OF_BREATH := 1.6  # held too long: the arm starts to shake

enum Phase { AIM, FLYING, DONE }

var target := 70
var score := 0
var dart := 0
var phase := Phase.AIM
var breath := 1.0
var holding := false
var landed: Array = []      # [{pos: Vector2 (board units), pts: int}]
var _mouse := CENTRE
var _t := 0.0
var _fly_t := 0.0
var _fly_to := Vector2.ZERO
var _msg := ""
var _rng := RandomNumberGenerator.new()
var _canvas: Control


static func play(tree: SceneTree, to_beat := 70) -> int:
	var s = load("res://game/minigames/darts/darts.gd").new()
	s.target = to_beat
	tree.root.add_child(s)
	var result: int = await s.finished
	s.queue_free()
	return result


# ------------------------------------------------------------------ maths ----
## Points for a dart landing at p (board units, y down). 0 off the board.
static func score_at(p: Vector2) -> int:
	var r := p.length()
	if r <= BULL_R:
		return 50
	if r <= OUTER_BULL_R:
		return 25
	if r > 1.0:
		return 0
	var ang := fposmod(rad_to_deg(atan2(p.x, -p.y)) + 9.0, 360.0)  # 0 = straight up, clockwise
	var seg: int = SEGMENTS[int(ang / 18.0) % 20]
	if r >= TREBLE_IN and r <= TREBLE_OUT:
		return seg * 3
	if r >= DOUBLE_IN:
		return seg * 2
	return seg


## Name of a hit for the score line: "T20", "D16", "Bull", "Miss"...
static func describe(p: Vector2) -> String:
	var pts := score_at(p)
	var r := p.length()
	if pts == 0:
		return "Miss"
	if r <= BULL_R:
		return "Bull!"
	if r <= OUTER_BULL_R:
		return "25"
	if r >= TREBLE_IN and r <= TREBLE_OUT:
		return "T%d" % (pts / 3)
	if r >= DOUBLE_IN:
		return "D%d" % (pts / 2)
	return str(pts)


## Size of the figure-8 wander, in board units. sway is Globals.sway_amount() (0 sober .. 6).
static func amplitude(sway: float, hand: float) -> float:
	return (0.10 + sway * 0.05) * hand


## Figure-8 offset of the reticle from where the player is pointing, at time t.
static func drift(t: float, sway: float, hand: float) -> Vector2:
	return Vector2(sin(t * 1.7), sin(t * 3.4) * 0.5) * amplitude(sway, hand)


## Release wobble: random spread of the dart around the reticle, wider with drink.
static func scatter(sway: float) -> float:
	return 0.035 + sway * 0.025


## Where one dart lands when aimed at `aim` and released at time t.
static func simulate_dart(aim: Vector2, t: float, sway: float, hand: float, rng: RandomNumberGenerator) -> Vector2:
	var s := scatter(sway)
	return aim + drift(t, sway, hand) + Vector2(rng.randfn(0.0, s), rng.randfn(0.0, s))


## Three darts at `aim`, released at random moments. Returns the total.
static func simulate_match(aim: Vector2, sway: float, hand: float, seed_val: int) -> int:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_val
	var total := 0
	for i in DARTS:
		total += score_at(simulate_dart(aim, rng.randf_range(0.0, 20.0), sway, hand, rng))
	return total


## Breath used per second while holding; drink empties the lungs faster (~2.2 s sober, <1 s at 100).
static func breath_drain(sway: float) -> float:
	return 0.45 + sway * 0.12


# ---------------------------------------------------------------- runtime ----
func _ready() -> void:
	layer = 20
	_rng.randomize()
	_t = _rng.randf() * 10.0
	var shade := ColorRect.new()  # swallow clicks so the adventure GUI underneath stays put
	shade.color = Color(0, 0, 0, 0.6)
	shade.size = Vector2(320, 200)
	shade.mouse_filter = Control.MOUSE_FILTER_STOP
	shade.gui_input.connect(_on_input)
	add_child(shade)
	_canvas = Control.new()
	_canvas.size = Vector2(320, 200)
	_canvas.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_canvas.draw.connect(_draw_game)
	add_child(_canvas)


func _sway() -> float:
	var g = get_node_or_null("/root/Globals")
	return g.sway_amount() if g else 0.0


func _drunk() -> int:
	var g = get_node_or_null("/root/Globals")
	return g.drunk if g else 0


func _hand() -> float:
	if not holding:
		return FREE_HAND
	return HOLD_STEADY if breath > 0.0 else OUT_OF_BREATH


func _aim() -> Vector2:
	return (_mouse - CENTRE) / R


func reticle() -> Vector2:
	return _aim() + drift(_t, _sway(), _hand())


func _on_input(ev: InputEvent) -> void:
	if ev is InputEventMouseMotion:
		_mouse = ev.position
		return
	if not (ev is InputEventMouseButton and ev.button_index == MOUSE_BUTTON_LEFT):
		return
	_mouse = ev.position
	match phase:
		Phase.AIM:
			if ev.pressed:
				holding = true
			elif holding:
				_throw()
		Phase.DONE:
			if ev.pressed:
				finished.emit(score)


func _throw() -> void:
	var s := scatter(_sway())
	_fly_to = reticle() + Vector2(_rng.randfn(0.0, s), _rng.randfn(0.0, s))
	holding = false
	_fly_t = 0.0
	phase = Phase.FLYING


func _process(delta: float) -> void:
	_t += delta
	var sw := _sway()
	if holding and phase == Phase.AIM:
		breath = maxf(0.0, breath - delta * breath_drain(sw))
	else:
		breath = minf(1.0, breath + delta * 0.4)
	if phase == Phase.FLYING:
		_fly_t += delta
		if _fly_t >= 0.3:
			var pts := score_at(_fly_to)
			landed.append({"pos": _fly_to, "pts": pts})
			score += pts
			dart += 1
			_msg = describe(_fly_to) + ("" if pts == 0 or describe(_fly_to).is_valid_int() else "  (%d)" % pts)
			if dart >= DARTS:
				phase = Phase.DONE
				_msg = "%d. %s" % [score, "You beat Dot!" if score > target else "A tie!" if score == target else "Dot wins."]
			else:
				phase = Phase.AIM
	_canvas.queue_redraw()


# ------------------------------------------------------------------- draw ----
func _to_px(p: Vector2, ofs := Vector2.ZERO) -> Vector2:
	return CENTRE + p * R + ofs


func _ring(c: Control, centre: Vector2, r0: float, r1: float, a0: float, a1: float, col: Color) -> void:
	var pts := PackedVector2Array()
	var steps := 4
	for i in steps + 1:
		var a := lerpf(a0, a1, float(i) / steps)
		pts.append(centre + Vector2(sin(a), -cos(a)) * r1 * R)
	for i in range(steps, -1, -1):
		var a := lerpf(a0, a1, float(i) / steps)
		pts.append(centre + Vector2(sin(a), -cos(a)) * r0 * R)
	c.draw_colored_polygon(pts, col)


func _draw_board(c: Control, ofs: Vector2, alpha: float) -> void:
	var ctr := CENTRE + ofs
	var black := Color(0.08, 0.07, 0.07, alpha)
	var cream := Color(0.90, 0.84, 0.66, alpha)
	var red := Color(0.78, 0.12, 0.10, alpha)
	var green := Color(0.10, 0.52, 0.22, alpha)
	c.draw_circle(ctr, R * 1.24, Color(0.06, 0.05, 0.05, alpha))   # surround with the numbers
	for i in 20:
		var a0 := deg_to_rad(i * 18.0 - 9.0)
		var a1 := deg_to_rad(i * 18.0 + 9.0)
		var single := black if i % 2 == 0 else cream
		var band := red if i % 2 == 0 else green
		_ring(c, ctr, OUTER_BULL_R, TREBLE_IN, a0, a1, single)
		_ring(c, ctr, TREBLE_IN, TREBLE_OUT, a0, a1, band)
		_ring(c, ctr, TREBLE_OUT, DOUBLE_IN, a0, a1, single)
		_ring(c, ctr, DOUBLE_IN, 1.0, a0, a1, band)
	c.draw_circle(ctr, OUTER_BULL_R * R, green)
	c.draw_circle(ctr, BULL_R * R + 0.5, red)
	if alpha < 1.0:
		return
	for i in 20:
		var a := deg_to_rad(i * 18.0)
		var np := ctr + Vector2(sin(a), -cos(a)) * R * 1.13
		var s := str(SEGMENTS[i])
		c.draw_string(FONT, np + Vector2(-2.5 * s.length(), 3), s, HORIZONTAL_ALIGNMENT_LEFT, -1, 8,
				Color(0.92, 0.90, 0.84))


func _draw_dart(c: Control, tip: Vector2, scale_f: float, alpha: float) -> void:
	var tail := tip + Vector2(5, 7) * scale_f
	c.draw_line(tip, tail, Color(0.82, 0.80, 0.76, alpha), 1.0)
	c.draw_colored_polygon(PackedVector2Array([tail, tail + Vector2(4, 1) * scale_f, tail + Vector2(1, 4) * scale_f]),
			Color(0.80, 0.14, 0.10, alpha))


func _draw_game() -> void:
	var c := _canvas
	var sw := _sway()
	var g = get_node_or_null("/root/Globals")
	var wob: Vector2 = g.sway(0.8).round() if g else Vector2.ZERO
	c.draw_rect(Rect2(70, 2, 180, 184), Color("1c120c"))
	c.draw_rect(Rect2(70, 2, 180, 184), Color("6b3a18"), false, 1.0)
	_draw_board(c, wob, 1.0)
	# seeing double from 60: a see-through ghost board drifts over the real one
	if _drunk() >= 60:
		_draw_board(c, wob + Vector2(sw * 1.6, sw * 0.5).round(), 0.3)
	for d in landed:
		_draw_dart(c, _to_px(d.pos, wob), 1.0, 1.0)
	if phase == Phase.FLYING:
		var k := clampf(_fly_t / 0.3, 0.0, 1.0)
		var start := Vector2(160, 200)
		_draw_dart(c, start.lerp(_to_px(_fly_to, wob), k), lerpf(2.5, 1.0, k), 1.0)
	if phase == Phase.AIM:
		var rp := _to_px(reticle(), wob)
		var col := Color(1, 1, 1, 0.9)
		if holding:
			col = Color(0.5, 1.0, 0.5, 0.95) if breath > 0.0 else Color(1.0, 0.35, 0.3, 0.95)
		c.draw_arc(rp, 4.0, 0.0, TAU, 16, col, 1.0)
		c.draw_line(rp + Vector2(-7, 0), rp + Vector2(-2, 0), col)
		c.draw_line(rp + Vector2(2, 0), rp + Vector2(7, 0), col)
		c.draw_line(rp + Vector2(0, -7), rp + Vector2(0, -2), col)
		c.draw_line(rp + Vector2(0, 2), rp + Vector2(0, 7), col)
	# breath gauge
	c.draw_rect(Rect2(232, 36, 8, 104), Color("0e0906"))
	var bh := 102.0 * breath
	c.draw_rect(Rect2(233, 139 - bh, 6, bh), Color.from_hsv(lerpf(0.0, 0.55, breath), 0.7, 0.95))
	_text(c, Vector2(226, 150), "BREATH", Color("b8e0ff"))
	# score lines
	_text(c, Vector2(78, 14), "DARTS  vs  DOT", Color("fad278"))
	_text(c, Vector2(78, 162), "Dart %d/%d   You: %d   Dot: %d" % [mini(dart + 1, DARTS), DARTS, score, target], Color.WHITE)
	var hint := ""
	match phase:
		Phase.AIM:
			hint = (_msg + "   " if _msg != "" else "") + ("Release to throw!" if holding else "Hold to steady, let go to throw")
		Phase.FLYING:
			hint = "..."
		Phase.DONE:
			hint = _msg + "  Click to finish"
	_text(c, Vector2(78, 175), hint, Color("b8e0ff"))


func _text(c: Control, pos: Vector2, s: String, col: Color) -> void:
	c.draw_string(FONT, pos + Vector2(1, 1), s, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0, 0, 0, 0.8))
	c.draw_string(FONT, pos, s, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, col)
