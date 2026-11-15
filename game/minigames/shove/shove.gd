extends CanvasLayer
## Shove ha'penny: five ha'pennies up a polished board ruled into nine beds, seen from above.
## A coin that comes to rest wholly inside a bed (not touching a line) scores that bed's number,
## 1 nearest to 9 farthest. On a line, in the gutter or off the far end: nothing. Coins left on
## the board can be knocked on by later ones, for better or worse. Beat the opponent's score.
##
## Move the mouse left/right to angle the shove. Hold the button: the power bar fills (and
## empties again if you hang on). Let go to shove.
## Drink makes it harder: the aim line wanders, the power bar jitters, the table "tilts" so the
## coin drifts, and from 60 a ghost board swims over the real one.
##
##   var score: int = await Shove.play(get_tree(), stan_score)
##
## The board maths is static and node-free (bed_of, score_coins, simulate_shove, simulate_match)
## so tests can drive it headless.

signal finished(score: int)

const FONT := preload("res://addons/popochiu/engine/objects/gui/fonts/minecraftia-regular.ttf")
const COINS := 5

# Board units: x -1..1 across, y 0 at the near edge growing away from the player.
const COIN_R := 0.08
const BED_START := 0.9      # first line
const BED_H := 0.34         # bed depth (a coin is 0.16 across, so ~0.18 of play each bed)
const BEDS := 9
const BOARD_END := 4.3      # past this the coin drops off the far end
const D_MAX := 4.8          # how far a full-power shove travels
const MAX_ANGLE := 0.3      # radians either side of straight up

# Difficulty: all drink effects scale with Globals.sway_amount() (0 sober, 0.5 at 30 .. 6 at 100).
const FRICTION_SD := 0.012  # board friction varies a little shove to shove (fraction of distance)
const JITTER := 0.035       # power bar jitter, power units per point of sway
const TILT := 0.06          # sideways/along drift per point of sway (board units over a full shove)
const AIM_WOBBLE := 0.04    # aim line wander, radians per point of sway
const CHARGE_RATE := 0.45   # power per second while holding (ping-pongs 0..1..0)

enum Phase { AIM, CHARGE, SLIDING, DONE }

var target := 16
var score := 0
var coin := 0
var phase := Phase.AIM
var coins: Array = []        # Vector2 board positions of coins at rest on the board
var power := 0.0
var _charge_t := 0.0
var _mouse := Vector2(160, 150)
var _t := 0.0
var _moves: Array = []       # [{idx, from, to}] from simulate_shove, animated in order
var _move_i := 0
var _move_t := 0.0
var _anim_coins: Array = []
var _msg := ""
var _rng := RandomNumberGenerator.new()
var _canvas: Control

# Screen layout (320x200): board drawn 40 px per unit, near edge at the bottom.
const PX := 37.0
const ORIGIN := Vector2(160, 176)   # board (0, 0)


static func play(tree: SceneTree, to_beat := 16) -> int:
	var s = load("res://game/minigames/shove/shove.gd").new()
	s.target = to_beat
	tree.root.add_child(s)
	var result: int = await s.finished
	s.queue_free()
	return result


# ------------------------------------------------------------------ maths ----
## Line i (0..BEDS) across the board.
static func line_y(i: int) -> float:
	return BED_START + i * BED_H


## Bed number 1..9 if the coin at p lies wholly inside a bed and on the board, else 0.
static func bed_of(p: Vector2) -> int:
	if absf(p.x) > 1.0 - COIN_R:
		return 0
	var k := int(floor((p.y - BED_START) / BED_H))
	if k < 0 or k >= BEDS:
		return 0
	if p.y - COIN_R < line_y(k) or p.y + COIN_R > line_y(k + 1):
		return 0  # touching a line
	return k + 1


static func score_coins(cs: Array) -> int:
	var total := 0
	for p in cs:
		total += bed_of(p)
	return total


static func on_board(p: Vector2) -> bool:
	return absf(p.x) <= 1.0 and p.y <= BOARD_END and p.y >= 0.0


## Power needed (no drink, no friction luck) to stop a coin shoved at `angle` in the middle of
## bed k.
static func power_for_bed(k: int, angle: float) -> float:
	var y := BED_START + (k - 0.5) * BED_H
	return y / cos(angle) / D_MAX


## Random "table tilt" for one shove: drink makes the coin drift.
static func random_tilt(sway: float, rng: RandomNumberGenerator) -> Vector2:
	return Vector2(rng.randfn(0.0, TILT * sway), rng.randfn(0.0, TILT * sway * 0.6))


## Slide one coin from `from` along `angle` for distance `dist`, curving with `tilt`, knocking
## on any resting coin it meets (the struck coin carries most of what's left; the striker stops).
## Mutates `cs` (positions of resting coins) and appends {idx, from, to} to `moves`.
static func _slide(cs: Array, idx: int, from: Vector2, angle: float, dist: float, tilt: Vector2,
		moves: Array, depth: int) -> void:
	var dir := Vector2(sin(angle), cos(angle))
	var step := 0.02
	var s := 0.0
	var pos := from
	var hit := -1
	while s < dist:
		s = minf(dist, s + step)
		var k := s / D_MAX
		pos = from + dir * s + Vector2(tilt.x * k * k * 6.0, tilt.y * k * 4.0)
		if not on_board(pos):
			break
		if depth < 6:
			for j in cs.size():
				if j != idx and cs[j] != null and pos.distance_to(cs[j]) < COIN_R * 2.0:
					hit = j
					break
		if hit >= 0:
			break
	cs[idx] = pos
	moves.append({"idx": idx, "from": from, "to": pos})
	if hit >= 0:
		var rem := (dist - s) * 0.8
		var push_angle := angle + clampf((cs[hit].x - pos.x) * 2.0, -0.6, 0.6)
		_slide(cs, hit, cs[hit], push_angle, rem, tilt * 0.5, moves, depth + 1)


## One shove. resting: coins already on the board. Returns {"coins": positions still on the
## board afterwards (the new coin included if it stayed on), "moves": [{idx, from, to}]}.
static func simulate_shove(resting: Array, angle: float, pwr: float, tilt: Vector2,
		rng: RandomNumberGenerator) -> Dictionary:
	var cs: Array = resting.duplicate()
	cs.append(Vector2.ZERO)
	var dist := maxf(0.0, pwr) * D_MAX * (1.0 + rng.randfn(0.0, FRICTION_SD))
	var moves: Array = []
	_slide(cs, cs.size() - 1, Vector2.ZERO, angle, dist, tilt, moves, 0)
	var kept: Array = []
	for p in cs:
		if on_board(p) and p.y > COIN_R:   # a dribble that never left the edge doesn't count
			kept.append(p)
	return {"coins": kept, "moves": moves, "all": cs}


## A whole turn of five ha'pennies by a "player" aiming the middle of bed `bed` in five lanes,
## with human timing/aim error (`human_pwr_sd`, `human_ang_sd`) plus the game's own drink effects
## for `sway`. Returns the score.
static func simulate_match(bed: int, sway: float, seed_val: int, human_pwr_sd := 0.016,
		human_ang_sd := 0.02) -> int:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_val
	var lanes := [0.0, -0.2, 0.2, -0.1, 0.1]
	var cs: Array = []
	for i in COINS:
		var a: float = lanes[i] + rng.randfn(0.0, human_ang_sd) + sin(rng.randf() * TAU) * AIM_WOBBLE * sway
		var p := power_for_bed(bed, lanes[i]) + rng.randfn(0.0, human_pwr_sd) \
				+ sin(rng.randf() * TAU) * JITTER * sway
		cs = simulate_shove(cs, a, p, random_tilt(sway, rng), rng).coins
	return score_coins(cs)


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


## Current aim angle: the mouse sets it, drink makes it wander.
func aim_angle() -> float:
	var a := clampf((_mouse.x - ORIGIN.x) / 120.0, -MAX_ANGLE, MAX_ANGLE)
	return a + sin(_t * 1.9) * AIM_WOBBLE * _sway()


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
				phase = Phase.CHARGE
				_charge_t = 0.0
				power = 0.0
		Phase.CHARGE:
			if not ev.pressed:
				_shove()
		Phase.DONE:
			if ev.pressed:
				finished.emit(score)


func _shove() -> void:
	var res := simulate_shove(coins, aim_angle(), power, random_tilt(_sway(), _rng), _rng)
	_moves = res.moves
	_anim_coins = coins.duplicate()
	_anim_coins.append(Vector2.ZERO)
	coins = res.coins
	_move_i = 0
	_move_t = 0.0
	phase = Phase.SLIDING


func _process(delta: float) -> void:
	_t += delta
	match phase:
		Phase.CHARGE:
			_charge_t += delta
			var c := fmod(_charge_t * CHARGE_RATE, 2.0)
			power = c if c <= 1.0 else 2.0 - c
			power = clampf(power + sin(_t * 19.0) * JITTER * _sway(), 0.0, 1.0)
		Phase.SLIDING:
			if _move_i >= _moves.size():
				_end_coin()
			else:
				var m: Dictionary = _moves[_move_i]
				var length: float = maxf(0.05, m.from.distance_to(m.to))
				_move_t += delta * 3.5 / length
				_anim_coins[m.idx] = m.from.lerp(m.to, minf(1.0, _move_t))
				if _move_t >= 1.0:
					_move_i += 1
					_move_t = 0.0
	_canvas.queue_redraw()


func _end_coin() -> void:
	coin += 1
	score = score_coins(coins)
	var last: Vector2 = _moves[0].to if not _moves.is_empty() else Vector2.ZERO
	var b := bed_of(last)
	if not on_board(last):
		_msg = "Off the end!" if last.y > BOARD_END else "In the gutter!"
	elif b == 0:
		_msg = "On the line."
	else:
		_msg = "Bed %d!" % b
	if coin >= COINS:
		phase = Phase.DONE
		_msg = "%d. %s" % [score, "You beat Stan!" if score > target else "A tie!" if score == target else "Stan wins."]
	else:
		phase = Phase.AIM


# ------------------------------------------------------------------- draw ----
func _to_px(p: Vector2, ofs := Vector2.ZERO) -> Vector2:
	return ORIGIN + Vector2(p.x * PX, -p.y * PX) + ofs


func _draw_board(c: Control, ofs: Vector2, alpha: float) -> void:
	var tl := _to_px(Vector2(-1, BOARD_END), ofs)
	var br := _to_px(Vector2(1, 0), ofs)
	if alpha >= 1.0:
		c.draw_rect(Rect2(tl - Vector2(6, 2), br - tl + Vector2(12, 4)), Color("3a1c0c"))   # frame
		c.draw_rect(Rect2(tl, br - tl), Color("7a3a18"))
		for i in 9:  # grain
			var x := tl.x + 6 + i * 8.5
			c.draw_line(Vector2(x, tl.y), Vector2(x + 2, br.y), Color("6c3214"))
	var brass := Color(0.95, 0.75, 0.32, alpha)
	for i in BEDS + 1:
		var y := _to_px(Vector2(0, line_y(i)), ofs).y
		c.draw_line(Vector2(tl.x, y), Vector2(br.x, y), brass)
	for side in [-1.0, 1.0]:  # chalk-column side lines
		var x := _to_px(Vector2(side * (1.0 - COIN_R * 2.2), 0), ofs).x
		c.draw_line(Vector2(x, _to_px(Vector2(0, line_y(0)), ofs).y), Vector2(x, _to_px(Vector2(0, line_y(BEDS)), ofs).y),
				Color(0.95, 0.75, 0.32, alpha * 0.6))
	if alpha >= 1.0:
		for i in BEDS:
			var y := _to_px(Vector2(0, line_y(i) + BED_H * 0.5), ofs).y
			c.draw_string(FONT, Vector2(br.x + 3, y + 3), str(i + 1), HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color("e8d8a8"))


func _draw_coin(c: Control, p: Vector2, ofs: Vector2, alpha: float) -> void:
	var cp := _to_px(p, ofs)
	c.draw_circle(cp, COIN_R * PX + 0.6, Color(0.2, 0.1, 0.04, alpha))
	c.draw_circle(cp, COIN_R * PX - 0.4, Color(0.80, 0.52, 0.24, alpha))
	c.draw_circle(cp + Vector2(-1, -1), 1.0, Color(0.95, 0.75, 0.45, alpha))


func _draw_game() -> void:
	var c := _canvas
	var sw := _sway()
	var g = get_node_or_null("/root/Globals")
	var wob: Vector2 = g.sway(0.7).round() if g else Vector2.ZERO
	c.draw_rect(Rect2(4, 2, 312, 186), Color("1c120c"))
	c.draw_rect(Rect2(4, 2, 312, 186), Color("6b3a18"), false, 1.0)
	_draw_board(c, wob, 1.0)
	var shown: Array = _anim_coins if phase == Phase.SLIDING else coins
	for p in shown:
		_draw_coin(c, p, wob, 1.0)
	if phase in [Phase.AIM, Phase.CHARGE]:
		_draw_coin(c, Vector2.ZERO, wob, 1.0)
		var a := aim_angle()
		var reach := minf(BOARD_END, 0.6 + (power * D_MAX if phase == Phase.CHARGE else 0.6))
		var tip := _to_px(Vector2(sin(a), cos(a)) * reach, wob)
		c.draw_line(_to_px(Vector2.ZERO, wob), tip, Color(1, 1, 1, 0.35), 1.0)
	# seeing double from 60: a see-through ghost board (and coins) swims over the real one
	if _drunk() >= 60:
		var gofs := wob + Vector2(sw * 1.4, -sw * 0.6).round()
		_draw_board(c, gofs, 0.35)
		for p in shown:
			_draw_coin(c, p, gofs, 0.35)
	# power bar
	c.draw_rect(Rect2(246, 40, 8, 104), Color("0e0906"))
	var ph := 102.0 * power
	c.draw_rect(Rect2(247, 143 - ph, 6, ph), Color.from_hsv(lerpf(0.33, 0.0, power), 0.85, 0.95))
	_text(c, Vector2(236, 154), "POWER", Color("b8e0ff"))
	# text
	_text(c, Vector2(10, 14), "SHOVE HA'PENNY", Color("fad278"))
	_text(c, Vector2(10, 26), "vs STAN", Color("fad278"))
	_text(c, Vector2(10, 44), "Coin %d/%d" % [mini(coin + 1, COINS), COINS], Color.WHITE)
	_text(c, Vector2(10, 56), "You:  %d" % score_coins(coins), Color.WHITE)
	_text(c, Vector2(10, 68), "Stan: %d" % target, Color.WHITE)
	_text(c, Vector2(10, 92), "Clean in a bed", Color("c8b890"))
	_text(c, Vector2(10, 102), "scores its number.", Color("c8b890"))
	_text(c, Vector2(10, 112), "Lines score 0.", Color("c8b890"))
	# instructions and the last result live in the left column, clear of the board's near end
	var lines: Array = []
	match phase:
		Phase.AIM: lines = ["Mouse: aim", "Hold: power up", "Let go: shove"]
		Phase.CHARGE: lines = ["Let go to shove!"]
		Phase.SLIDING: lines = ["..."]
		Phase.DONE: lines = ["Click to finish"]
	for i in lines.size():
		_text(c, Vector2(10, 136 + i * 11), lines[i], Color("b8e0ff"))
	if _msg != "" and phase != Phase.SLIDING:
		_text(c, Vector2(10, 178), _msg, Color("fad278"))


func _text(c: Control, pos: Vector2, s: String, col: Color) -> void:
	c.draw_string(FONT, pos + Vector2(1, 1), s, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0, 0, 0, 0.8))
	c.draw_string(FONT, pos, s, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, col)
