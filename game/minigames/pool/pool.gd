extends CanvasLayer
## Pool: a short pub-rules race on a top-down table. Seven object balls are scattered on the
## baize; Paul and the opponent take turns, potting a ball lets you go again, and the first to
## pot `race_to` balls wins. Pot the white and the turn passes (it is re-spotted in baulk).
##
## Controls: move the mouse to aim the cue from the white ball. Hold the left button to charge
## the power (it swings up and down), release to strike.
## Drink (Globals.sway_amount()): the aim wobbles round a slow figure-8, the guide line
## shortens, the power bar jitters and the strike picks up random error; from 60 a ghost table
## drifts over the real one (double vision).
##
## API (also used by the finale for the pub-6 rematch):
##
##   const Pool := preload("res://game/minigames/pool/pool.gd")
##   var won: bool = await Pool.play(get_tree(), "Gaz", 0.5)        # Nottingham Arms
##   var won: bool = await Pool.play(get_tree(), "Champion", 0.85, 4)  # harder rematch
##   Pool.last_score  # Vector2i(player balls, opponent balls) of the last match played
##
##   opponent_name  shown on the table ("POOL vs GAZ") and in the result line
##   difficulty     0..1, how straight the opponent cues: opponent_error(d) radians of aim
##                  error (0 -> 0.09 rad, a pub novice; 1 -> 0.012 rad, a county player).
##                  Nottingham's Gaz is NOTTINGHAM_DIFFICULTY.
##   race_to        balls needed to win (default 3; at most 4, there are 7 on the table)
##
## Everything physical is static, node-free maths (Table, plan_shot, ai_velocity,
## simulate_match, aim_wobble, power_jitter...), so tests can play whole matches headless.

signal finished(won: bool)

const FONT := preload("res://addons/popochiu/engine/objects/gui/fonts/minecraftia-regular.ttf")

## Gaz at the Nottingham Arms. The finale passes something harder.
const NOTTINGHAM_DIFFICULTY := 0.5

# Table interior in screen px (top-left of the cushion line) and its size.
const ORIGIN := Vector2(24, 30)
const TW := 240.0
const TH := 120.0
const BALL_R := 3.5
const OBJECT_BALLS := 7
const POCKETS := [Vector2(0, 0), Vector2(TW / 2, -2), Vector2(TW, 0),
		Vector2(0, TH), Vector2(TW / 2, TH + 2), Vector2(TW, TH)]
const CORNER_CAPTURE := 8.5
const MIDDLE_CAPTURE := 7.0
const BAULK_SPOT := Vector2(TW * 0.25, TH / 2)

# Physics (px, seconds).
const FRICTION := 120.0        # rolling deceleration, px/s^2
const MAX_SPEED := 420.0       # a full-power strike
const MIN_POWER := 0.08
const CUSHION := 0.75          # speed kept bouncing off a cushion
const BALL_E := 0.95           # ball-ball restitution
const DT := 1.0 / 120.0
const MAX_TURNS := 60          # headless safety net

## Aim error of a careful sober human lining up with the guide line, radians. Used by the
## headless player model in simulate_match (the real player supplies their own error).
const PLAYER_ERROR := 0.02

enum Phase { AIM, POWER, ROLLING, OPP_THINK, DONE }

static var last_score := Vector2i.ZERO

var opponent := "Gaz"
var difficulty := NOTTINGHAM_DIFFICULTY
var race_to := 3
var table: Table
var scores := [0, 0]           # [player, opponent]
var turn := 0                  # 0 player, 1 opponent
var phase := Phase.AIM
var power := 0.0
var aim_angle := 0.0
var _mouse := ORIGIN + Vector2(TW * 0.6, TH / 2)
var _t := 0.0
var _charge_t := 0.0
var _think_t := 0.0
var _acc := 0.0
var _shot_potted: Array = []
var _turns := 0
var _msg := ""
var _rng := RandomNumberGenerator.new()
var _canvas: Control


static func play(tree: SceneTree, opponent_name := "Gaz", diff := NOTTINGHAM_DIFFICULTY, race := 3) -> bool:
	var s = load("res://game/minigames/pool/pool.gd").new()
	s.opponent = opponent_name
	s.difficulty = clampf(diff, 0.0, 1.0)
	s.race_to = clampi(race, 1, 4)
	tree.root.add_child(s)
	var result: bool = await s.finished
	s.queue_free()
	return result


# =================================================================== maths ====
## Balls on the table. Index 0 is the white (cue ball), 1.. the object balls.
class Table:
	var pos := PackedVector2Array()
	var vel := PackedVector2Array()
	var live: Array[bool] = []

	func moving() -> bool:
		for i in pos.size():
			if live[i] and vel[i].length_squared() > 0.01:
				return true
		return false

	func objects_left() -> int:
		var n := 0
		for i in range(1, pos.size()):
			if live[i]:
				n += 1
		return n

	func copy() -> Table:
		var t := Table.new()
		t.pos = pos.duplicate()
		t.vel = vel.duplicate()
		t.live = live.duplicate()
		return t

	## Advance one fixed step. Returns the indices potted during it.
	func step(dt: float) -> Array:
		var potted := []
		var n := pos.size()
		for i in n:
			if not live[i]:
				continue
			var v := vel[i]
			var sp := v.length()
			if sp > 0.0:
				var ns := maxf(0.0, sp - FRICTION * dt)
				v = v * (ns / sp)
				vel[i] = v
				pos[i] += v * dt
		for i in n:
			if not live[i]:
				continue
			for k in POCKETS.size():
				var cap := MIDDLE_CAPTURE if k == 1 or k == 4 else CORNER_CAPTURE
				if pos[i].distance_to(POCKETS[k]) < cap:
					live[i] = false
					vel[i] = Vector2.ZERO
					potted.append(i)
					break
		for i in n:
			if not live[i]:
				continue
			var p := pos[i]
			var v := vel[i]
			if p.x < BALL_R:
				p.x = BALL_R
				v.x = absf(v.x) * CUSHION
			elif p.x > TW - BALL_R:
				p.x = TW - BALL_R
				v.x = -absf(v.x) * CUSHION
			if p.y < BALL_R:
				p.y = BALL_R
				v.y = absf(v.y) * CUSHION
			elif p.y > TH - BALL_R:
				p.y = TH - BALL_R
				v.y = -absf(v.y) * CUSHION
			pos[i] = p
			vel[i] = v
		for i in n:
			if not live[i]:
				continue
			for j in range(i + 1, n):
				if not live[j]:
					continue
				var d := pos[j] - pos[i]
				var dist := d.length()
				if dist >= BALL_R * 2.0 or dist < 0.0001:
					continue
				var nrm := d / dist
				var push := (BALL_R * 2.0 - dist) * 0.5
				pos[i] -= nrm * push
				pos[j] += nrm * push
				var vrel := (vel[i] - vel[j]).dot(nrm)
				if vrel > 0.0:
					var imp := (1.0 + BALL_E) * 0.5 * vrel
					vel[i] -= nrm * imp
					vel[j] += nrm * imp
		return potted

	## Run until everything stops (or a time cap). Returns every index potted.
	func settle(max_time := 12.0) -> Array:
		var potted := []
		var t := 0.0
		while moving() and t < max_time:
			potted.append_array(step(DT))
			t += DT
		for i in vel.size():
			vel[i] = Vector2.ZERO
		return potted


## A fresh rack: the white on the baulk spot, seven balls scattered over the far two-thirds,
## clear of each other, the cushions and the pockets.
static func new_table(rng: RandomNumberGenerator) -> Table:
	var t := Table.new()
	t.pos.append(BAULK_SPOT)
	t.vel.append(Vector2.ZERO)
	t.live.append(true)
	var tries := 0
	while t.pos.size() < OBJECT_BALLS + 1 and tries < 2000:
		tries += 1
		var p := Vector2(rng.randf_range(TW * 0.38, TW - 14.0), rng.randf_range(12.0, TH - 12.0))
		var ok := true
		for q in t.pos:
			if p.distance_to(q) < BALL_R * 4.0:
				ok = false
		for pk in POCKETS:
			if p.distance_to(pk) < 22.0:
				ok = false
		if ok:
			t.pos.append(p)
			t.vel.append(Vector2.ZERO)
			t.live.append(true)
	return t


## Put the white back on the baulk spot (or the nearest free place up/down the baulk line).
static func respot_cue(t: Table) -> void:
	for k in 40:
		var p := BAULK_SPOT + Vector2(0, (k / 2 + 1) * BALL_R * 2.2 * (1 if k % 2 == 0 else -1)) if k > 0 else BAULK_SPOT
		p.y = clampf(p.y, BALL_R + 1, TH - BALL_R - 1)
		var free := true
		for i in range(1, t.pos.size()):
			if t.live[i] and t.pos[i].distance_to(p) < BALL_R * 2.2:
				free = false
		if free:
			t.pos[0] = p
			break
	t.live[0] = true
	t.vel[0] = Vector2.ZERO


static func _seg_dist(p: Vector2, a: Vector2, b: Vector2) -> float:
	return p.distance_to(Geometry2D.get_closest_point_to_segment(p, a, b))


## The best pot on the table, ghost-ball style: {angle, power (0..1), ok}. ok=false is a
## safety (just roll at the nearest ball) when nothing is on.
static func plan_shot(t: Table) -> Dictionary:
	var c := t.pos[0]
	var best := {}
	var best_cost := INF
	for o in range(1, t.pos.size()):
		if not t.live[o]:
			continue
		var po := t.pos[o]
		for k in POCKETS.size():
			var pk: Vector2 = POCKETS[k]
			var to_pocket := pk - po
			var d2 := to_pocket.length()
			var dir := to_pocket / d2
			if (k == 1 or k == 4) and absf(dir.x) > 0.75:
				continue  # middle pockets only take a ball coming at them fairly square
			var ghost := po - dir * BALL_R * 2.0
			var v1 := ghost - c
			var d1 := v1.length()
			if d1 < 1.0:
				continue
			var cut := v1.angle_to(dir)
			if absf(cut) > deg_to_rad(70.0):
				continue
			var blocked := false
			for q in range(1, t.pos.size()):
				if q == o or not t.live[q]:
					continue
				if _seg_dist(t.pos[q], c, ghost) < BALL_R * 2.0 or _seg_dist(t.pos[q], po, pk) < BALL_R * 2.0:
					blocked = true
					break
			if blocked:
				continue
			var cost := d1 * 0.5 + d2 + rad_to_deg(absf(cut)) * 3.0
			if cost < best_cost:
				best_cost = cost
				var v_obj := sqrt(2.0 * FRICTION * (d2 + 12.0)) * 1.15 + 25.0
				var v_contact := v_obj / maxf(cos(cut) * (1.0 + BALL_E) * 0.5, 0.3)
				var v0 := sqrt(v_contact * v_contact + 2.0 * FRICTION * d1)
				best = {"angle": v1.angle(), "power": clampf(v0 / MAX_SPEED, MIN_POWER, 1.0), "ok": true}
	if best.is_empty():
		var near := -1
		for o in range(1, t.pos.size()):
			if t.live[o] and (near < 0 or c.distance_to(t.pos[o]) < c.distance_to(t.pos[near])):
				near = o
		var ang := 0.0 if near < 0 else (t.pos[near] - c).angle()
		best = {"angle": ang, "power": 0.45, "ok": false}
	return best


## Opponent aim error in radians for a difficulty 0..1.
static func opponent_error(diff: float) -> float:
	return lerpf(0.09, 0.012, clampf(diff, 0.0, 1.0))


## Drunk aim wobble added to the cue angle at time t, radians. sway is Globals.sway_amount().
static func aim_wobble(t: float, sway: float) -> float:
	return (sin(t * 1.7) + 0.5 * sin(t * 4.3 + 1.3)) * sway * 0.03


## Spread (sd, as a fraction of the power) the strike picks up when drunk.
static func power_jitter(sway: float) -> float:
	return sway * 0.05


## How far the guide line reaches from the white, px: shorter the merrier Paul is.
static func guide_length(sway: float) -> float:
	return maxf(30.0, 150.0 - sway * 20.0)


## A planned shot executed with gaussian aim error and power noise -> the white's velocity.
static func ai_velocity(plan: Dictionary, aim_err: float, power_err: float, rng: RandomNumberGenerator) -> Vector2:
	var ang: float = plan.angle + rng.randfn(0.0, aim_err)
	var pw: float = clampf(plan.power * (1.0 + rng.randfn(0.0, power_err)), MIN_POWER, 1.0)
	return Vector2.from_angle(ang) * pw * MAX_SPEED


## Apply a finished shot's pots to the scores. Returns true if the shooter goes again.
static func resolve(t: Table, potted: Array, shooter: int, sc: Array) -> bool:
	var foul := potted.has(0)
	for i in potted:
		if i != 0:
			sc[shooter] += 1
	if foul:
		respot_cue(t)
		return false
	return potted.size() > 0


## A whole match headless. The player is modelled as a careful cueist (player_err, normally
## PLAYER_ERROR) who also suffers the drunk wobble (released at a random moment) and power
## jitter; the opponent cues with opponent_error(diff). Returns true if the player wins.
static func simulate_match(player_err: float, sway: float, diff: float, seed_val: int, race := 3) -> bool:
	var rng := RandomNumberGenerator.new()
	rng.seed = seed_val
	var t := new_table(rng)
	var sc := [0, 0]
	var shooter := 0
	for turn_i in MAX_TURNS:
		var plan := plan_shot(t)
		var v: Vector2
		if shooter == 0:
			var p2 := plan.duplicate()
			p2.angle += aim_wobble(rng.randf_range(0.0, 30.0), sway)
			v = ai_velocity(p2, player_err, 0.05 + power_jitter(sway), rng)
		else:
			v = ai_velocity(plan, opponent_error(diff), 0.05, rng)
		t.vel[0] = v
		var potted := t.settle()
		var again := resolve(t, potted, shooter, sc)
		if sc[shooter] >= race:
			return shooter == 0
		if t.objects_left() == 0:
			break
		if not again:
			shooter = 1 - shooter
	return sc[0] > sc[1]


# ================================================================= runtime ====
func _ready() -> void:
	layer = 20
	_rng.randomize()
	_t = _rng.randf() * 10.0
	table = new_table(_rng)
	var shade := ColorRect.new()  # swallow clicks so the adventure GUI underneath stays put
	shade.color = Color(0, 0, 0, 0.85)  # dark enough to read the score over the verb grid
	shade.size = Vector2(320, 200)
	shade.mouse_filter = Control.MOUSE_FILTER_STOP
	shade.gui_input.connect(_on_input)
	add_child(shade)
	_canvas = Control.new()
	_canvas.size = Vector2(320, 200)
	_canvas.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_canvas.draw.connect(_draw_game)
	add_child(_canvas)
	_msg = "Your break. Pot %d before %s does." % [race_to, opponent]


func _sway() -> float:
	var g = get_node_or_null("/root/Globals")
	return g.sway_amount() if g else 0.0


func _drunk() -> int:
	var g = get_node_or_null("/root/Globals")
	return g.drunk if g else 0


## The cue angle right now: towards the mouse, plus the drunk wobble.
func current_angle() -> float:
	var base := (_mouse - (ORIGIN + table.pos[0])).angle()
	return base + aim_wobble(_t, _sway())


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
				phase = Phase.POWER
				_charge_t = 0.0
		Phase.POWER:
			if not ev.pressed:
				_strike()
		Phase.DONE:
			if ev.pressed:
				_finish()


func _strike() -> void:
	var sw := _sway()
	var pw := clampf(power * (1.0 + _rng.randfn(0.0, power_jitter(sw))), MIN_POWER, 1.0)
	table.vel[0] = Vector2.from_angle(current_angle()) * pw * MAX_SPEED
	_start_roll()


func _start_roll() -> void:
	_shot_potted.clear()
	_acc = 0.0
	phase = Phase.ROLLING


func _finish() -> void:
	last_score = Vector2i(scores[0], scores[1])
	finished.emit(scores[0] >= race_to or (scores[0] > scores[1] and scores[1] < race_to))


func _end_shot() -> void:
	_turns += 1
	var shooter := turn
	var before: int = scores[shooter]
	var again := resolve(table, _shot_potted, shooter, scores)
	var who := "You" if shooter == 0 else opponent
	var pots: int = scores[shooter] - before
	if _shot_potted.has(0):
		_msg = "%s potted the white! Turn over." % who
	elif pots > 0:
		_msg = "%s potted %s! Go again." % [who, "one" if pots == 1 else str(pots)]
	else:
		_msg = "%s missed." % who
	if scores[shooter] >= race_to or table.objects_left() == 0 or _turns >= MAX_TURNS:
		phase = Phase.DONE
		var won: bool = scores[0] > scores[1]
		_msg = "%d-%d. %s" % [scores[0], scores[1], "You beat %s!" % opponent if won else "%s wins." % opponent]
		last_score = Vector2i(scores[0], scores[1])
		return
	if not again:
		turn = 1 - turn
	if turn == 0:
		phase = Phase.AIM
	else:
		phase = Phase.OPP_THINK
		_think_t = 0.0


func _process(delta: float) -> void:
	_t += delta
	match phase:
		Phase.POWER:
			_charge_t += delta
			# swings 0 -> 1 -> 0 every 2 s; drink makes the needle jitter
			var base := 0.5 - 0.5 * cos(_charge_t * PI)
			power = clampf(base + sin(_t * 19.0) * _sway() * 0.02, 0.0, 1.0)
		Phase.ROLLING:
			_acc += delta
			while _acc >= DT:
				_acc -= DT
				_shot_potted.append_array(table.step(DT))
			if not table.moving():
				for i in table.vel.size():
					table.vel[i] = Vector2.ZERO
				_end_shot()
		Phase.OPP_THINK:
			_think_t += delta
			if _think_t >= 1.0:
				var plan := plan_shot(table)
				table.vel[0] = ai_velocity(plan, opponent_error(difficulty), 0.05, _rng)
				_start_roll()
	_canvas.queue_redraw()


# ==================================================================== draw ====
func _draw_table(c: Control, ofs: Vector2, alpha: float) -> void:
	var o := ORIGIN + ofs
	if alpha >= 1.0:
		c.draw_rect(Rect2(o - Vector2(10, 10), Vector2(TW + 20, TH + 20)), Color("4a2410"))
		c.draw_rect(Rect2(o - Vector2(10, 10), Vector2(TW + 20, TH + 20)), Color("1e0e06"), false, 1.0)
		c.draw_rect(Rect2(o - Vector2(4, 4), Vector2(TW + 8, TH + 8)), Color("0d4f22"))
		c.draw_rect(Rect2(o, Vector2(TW, TH)), Color("16803a"))
		c.draw_line(o + Vector2(TW * 0.25, 0), o + Vector2(TW * 0.25, TH), Color(0.85, 0.95, 0.85, 0.35))
		for pk in POCKETS:
			c.draw_circle(o + pk, 6.0, Color("050505"))
		for k in 3:  # diamonds on the rails
			for x in [TW * (k + 1) / 8.0, TW * (k + 5) / 8.0]:
				c.draw_rect(Rect2(o + Vector2(x - 0.5, -8), Vector2(1, 1)), Color("e8d8a0"))
				c.draw_rect(Rect2(o + Vector2(x - 0.5, TH + 7), Vector2(1, 1)), Color("e8d8a0"))
	for i in table.pos.size():
		if not table.live[i]:
			continue
		var col := Color("f2efe4") if i == 0 else (Color("c8261c") if i % 2 == 1 else Color("f0c028"))
		col.a = alpha
		var p := (o + table.pos[i]).round()
		c.draw_circle(p, BALL_R, col)
		if alpha >= 1.0:
			c.draw_rect(Rect2(p + Vector2(-1.5, -1.5), Vector2(1, 1)), Color(1, 1, 1, 0.9))


func _draw_game() -> void:
	var c := _canvas
	var sw := _sway()
	var g = get_node_or_null("/root/Globals")
	var wob: Vector2 = g.sway(0.8).round() if g else Vector2.ZERO
	_draw_table(c, wob, 1.0)
	if _drunk() >= 60:
		_draw_table(c, wob + Vector2(sw * 1.5, sw * 0.6).round(), 0.35)
	var cue := ORIGIN + wob + table.pos[0]
	if (phase == Phase.AIM or phase == Phase.POWER) and table.live[0]:
		var dir := Vector2.from_angle(current_angle())
		# dotted guide, stopping at the first ball it would hit
		var reach := guide_length(sw)
		var hit := -1.0
		for i in range(1, table.pos.size()):
			if not table.live[i]:
				continue
			var rel := table.pos[i] - table.pos[0]
			var along := rel.dot(dir)
			if along <= 0.0:
				continue
			var perp := absf(rel.cross(dir))
			if perp < BALL_R * 2.0:
				var d := along - sqrt(BALL_R * BALL_R * 4.0 - perp * perp)
				if hit < 0.0 or d < hit:
					hit = d
		var len_ := reach if hit < 0.0 else minf(reach, hit)
		var s := 4.0
		while s < len_:
			c.draw_rect(Rect2((cue + dir * s).round(), Vector2(1, 1)), Color(1, 1, 1, 0.75))
			s += 4.0
		if hit >= 0.0 and hit <= reach:
			c.draw_arc((cue + dir * hit).round(), BALL_R, 0.0, TAU, 12, Color(1, 1, 1, 0.6), 1.0)
		# the cue itself, drawn back from the white by the power
		var back := 5.0 + (power if phase == Phase.POWER else 0.0) * 18.0
		c.draw_line(cue - dir * back, cue - dir * (back + 70.0), Color("d8b070"), 2.0)
		c.draw_line(cue - dir * back, cue - dir * (back + 3.0), Color("4060d0"), 2.0)
	if phase == Phase.OPP_THINK and table.live[0]:
		var plan := plan_shot(table)
		var dir2 := Vector2.from_angle(plan.angle)
		var back2 := 5.0 + _think_t * 14.0
		c.draw_line(cue - dir2 * back2, cue - dir2 * (back2 + 70.0), Color("303038"), 2.0)
	# power bar
	c.draw_rect(Rect2(292, 34, 8, 112), Color("0e0906"))
	var ph := 110.0 * (power if phase == Phase.POWER else 0.0)
	c.draw_rect(Rect2(293, 145 - ph, 6, ph), Color.from_hsv(lerpf(0.33, 0.0, power), 0.8, 0.95))
	_text(c, Vector2(284, 156), "POWER", Color("b8e0ff"))
	_text(c, Vector2(66, 12), "POOL vs %s   first to %d" % [opponent.to_upper(), race_to], Color("fad278"))
	_text(c, Vector2(24, 172), "You: %d   %s: %d" % [scores[0], opponent, scores[1]], Color.WHITE)
	var hint := _msg
	match phase:
		Phase.AIM:
			hint = (_msg + "  " if _msg != "" else "") + "Hold to power up"
		Phase.POWER:
			hint = "Release to strike!"
		Phase.ROLLING:
			hint = "..."
		Phase.OPP_THINK:
			hint = "%s lines up a shot..." % opponent
		Phase.DONE:
			hint = _msg + "  Click to finish"
	_text(c, Vector2(24, 185), hint, Color("b8e0ff"))


func _text(c: Control, pos: Vector2, s: String, col: Color) -> void:
	c.draw_string(FONT, pos + Vector2(1, 1), s, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, Color(0, 0, 0, 0.8))
	c.draw_string(FONT, pos, s, HORIZONTAL_ALIGNMENT_LEFT, -1, 8, col)
