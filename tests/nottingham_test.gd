extends Node
## Nottingham Arms (stop 5). Teleports in (HighSt lives on the pub-4 branch). Checks: the exit
## works with nothing in hand (falls back to the Cross without HighSt); sober Paul can't win
## Norman over; the halves get him merry, he laughs, swaps the shaft for the rest; the halves
## screw together; Gaz plays; lose then win; a win before stamp 4 is remembered and stamped on
## the next visit; water sobers, Jackie stops pouring at 60. Plus the pool maths and win rates.

const Pool := preload("res://game/minigames/pool/pool.gd")
const Room := preload("res://game/rooms/nottingham_arms/room_nottingham_arms.gd")

var fails := 0


func _ok(cond: bool, what: String) -> void:
	if not cond:
		fails += 1
	print("[test] %s %s" % ["PASS" if cond else "FAIL", what])


func _room() -> String:
	return R.current.script_name if R.current else ""


func _act(node: Node, method: String, room := "") -> void:
	E.clicked = node
	await node.call(method)
	if room == "":
		return
	await _wait_room(room)


func _wait_room(room: String) -> void:
	for i in 40:
		if _room() == room:
			break
		await get_tree().create_timer(0.25).timeout
	await get_tree().create_timer(4.0).timeout


func _hot(name: String) -> Node:
	return R.current.get_node("Hotspots/%s" % name)


func _finish_pool(won: bool, potted: int) -> void:
	for i in 200:
		await get_tree().create_timer(0.2).timeout
		for n in get_tree().root.get_children():
			if n.get_script() == Pool:
				n.scores = [potted, 3 if not won else 1]
				Pool.last_score = Vector2i(potted, n.scores[1])
				n.finished.emit(won)
				return
	_ok(false, "pool overlay appeared")
	get_tree().quit(1)


func _rate(drunk: int, diff: float, n := 300) -> float:
	var sway: float = 0.0 if drunk < 30 else remap(float(drunk), 30.0, 100.0, 0.5, 6.0)
	var w := 0
	for s in n:
		if Pool.simulate_match(Pool.PLAYER_ERROR, sway, diff, s * 13 + 5):
			w += 1
	return float(w) / n


func _ready() -> void:
	get_tree().create_timer(900.0).timeout.connect(func():
		print("[test] FAIL nottingham timed out")
		get_tree().quit(1))
	E.settings.auto_continue_text = true
	await get_tree().create_timer(2.0).timeout
	# a win here before the Britannia's stamp must wait for it: start at 3 stamps
	Globals.stamps = 3
	Globals.drunk = 0

	R.goto_room("NottinghamArms")
	await _wait_room("NottinghamArms")
	_ok(_room() == "NottinghamArms", "teleported into the Nottingham Arms")
	_ok(C.player.position.distance_to(Room.SPAWN) < 4, "Paul at the door spawn (%s)" % C.player.position)
	_ok(R.current.get_node("Props/CueButt").visible and R.current.get_node("Props/CueShaftProp").visible
			and R.current.get_node("Props/PoolRestProp").visible, "butt, shaft and rest sprites visible")
	var nav := R.current.get_node("WalkableAreas/Floor") as PopochiuWalkableArea
	_ok(nav.interaction_polygon.size() == 2, "pool table is a hole in the floor")

	# --- straight out with nothing (no HighSt on this branch -> the Cross)
	_ok(Room.street_room() == ("HighSt" if PopochiuResources.has_data_value("rooms", "HighSt") else "TheCross"),
			"street room is HighSt if present, else the Cross")
	await _act(_hot("ExitDoor"), "on_open", Room.street_room())
	_ok(_room() == Room.street_room(), "exit works with nothing done (-> %s)" % _room())
	R.goto_room("NottinghamArms")
	await _wait_room("NottinghamArms")

	# --- sober: Gaz won't play without a cue, Norman sulks, no swap
	await C.Gaz.on_talk_to()
	_ok(not Globals.cue_given, "no cue, no game")
	await C.Jackie.on_talk_to()
	await _act(_hot("CueRack"), "on_pick_up")
	_ok(Globals.butt_taken and I.is_item_in_inventory("CueButt") and not R.current.get_node("Props/CueButt").visible,
			"cue butt taken from the rack")
	await C.Gaz._on_item_used(I.CueButt)
	_ok(not Globals.cue_given, "half a cue isn't enough for Gaz")
	await _act(_hot("PoolRest"), "on_pick_up")
	_ok(I.is_item_in_inventory("PoolRest") and not _hot("PoolRest").visible, "pool rest taken")
	await C.Norman.on_talk_to()
	_ok(not Globals.norman_laughed, "sober Paul doesn't laugh at Norman's story")
	await C.Norman._on_item_used(I.PoolRest)
	_ok(not Globals.shaft_swapped and I.is_item_in_inventory("PoolRest"), "Norman won't swap with a sober stranger")
	await _act(_hot("CueShaft"), "on_pick_up")
	_ok(not I.is_item_in_inventory("CueShaft"), "can't just take Norman's poker")

	# --- leave with half the kit and come back: state holds
	await _act(_hot("ExitDoor"), "on_walk_to", Room.street_room())
	R.goto_room("NottinghamArms")
	await _wait_room("NottinghamArms")
	_ok(not R.current.get_node("Props/CueButt").visible and not R.current.get_node("Props/PoolRestProp").visible
			and I.is_item_in_inventory("CueButt") and I.is_item_in_inventory("PoolRest"), "items and props survive leaving")

	# --- merry: two free halves, Norman laughs, swaps
	await _act(_hot("Pumps"), "on_use")
	await _act(_hot("Pumps"), "on_use")
	_ok(Globals.drunk == 30 and Globals.nottingham_halves == 2, "two halves from Jackie -> drunk 30 (%d)" % Globals.drunk)
	await C.Norman.on_talk_to()
	_ok(Globals.norman_laughed, "merry Paul laughs; Norman warms to him")
	await C.Norman._on_item_used(I.PoolRest)
	_ok(Globals.shaft_swapped and I.is_item_in_inventory("CueShaft") and not I.is_item_in_inventory("PoolRest"),
			"Norman swaps the shaft for the rest")
	_ok(not R.current.get_node("Props/CueShaftProp").visible and R.current.get_node("Props/PoolRestProp").visible
			and not _hot("CueShaft").visible, "shaft sprite gone, rest now leans by Norman")

	# --- combine
	await I.CueShaft._on_item_used(I.CueButt)
	_ok(I.is_item_in_inventory("HouseCue") and not I.is_item_in_inventory("CueButt")
			and not I.is_item_in_inventory("CueShaft") and Globals.cue_made, "butt + shaft = house cue")

	# --- too merry: no more halves, water sobers
	Globals.drunk = 70
	await _act(_hot("Pumps"), "on_use")
	_ok(Globals.drunk == 70, "Jackie won't pour past 60")
	await _act(_hot("WaterJug"), "on_use")
	_ok(Globals.drunk == 45, "water sobers Paul up (70 -> %d)" % Globals.drunk)

	# --- Gaz: lose, then win (before the Britannia's stamp)
	_finish_pool.call_deferred(false, 1)
	await C.Gaz._on_item_used(I.HouseCue)
	_ok(Globals.cue_given and not I.is_item_in_inventory("HouseCue"), "house cue handed to Gaz")
	_ok(not Globals.pool_won, "losing doesn't win")
	_finish_pool.call_deferred(true, 3)
	await C.Gaz.on_talk_to()
	_ok(Globals.pool_won and Globals.pool_best == 3, "beat Gaz (best %d)" % Globals.pool_best)
	_ok(Globals.stamps == 3, "no stamp 5 before stamp 4 (%d)" % Globals.stamps)
	await C.Jackie.on_talk_to()
	_ok(Globals.stamps == 3, "Jackie holds the stamp until the Britannia's is on")

	# --- the Britannia's stamp arrives; coming back in, Jackie stamps straight away
	await _act(_hot("ExitDoor"), "on_walk_to", Room.street_room())
	Globals.stamps = 4
	var before := Globals.drunk
	R.goto_room("NottinghamArms")
	await _wait_room("NottinghamArms")
	for i in 120:  # Jackie calls Paul over on entry; headless lines auto-continue slowly
		if Globals.stamps == 5:
			break
		await get_tree().create_timer(0.25).timeout
	await get_tree().create_timer(1.0).timeout
	_ok(Globals.stamps == 5, "remembered win stamped on return (5/6)")
	_ok(Globals.drunk == maxi(0, before - 25), "water on the house (%d -> %d)" % [before, Globals.drunk])
	await C.Gaz.on_talk_to()
	_ok(Globals.stamps == 5, "talking again changes nothing")
	await _act(_hot("ExitDoor"), "on_open", Room.street_room())
	_ok(_room() == Room.street_room(), "exit still works at the end")

	# --- pool maths
	var t := Pool.Table.new()
	t.pos = PackedVector2Array([Vector2(100, 60), Vector2(150, 60)])
	t.vel = PackedVector2Array([Vector2(300, 0), Vector2.ZERO])
	t.live = [true, true]
	t.settle()
	_ok(t.pos[1].x > 150 and t.pos[0].x < 150, "straight hit passes the speed to the object ball")
	t = Pool.Table.new()
	t.pos = PackedVector2Array([Vector2(200, 100), Vector2(225, 110)])
	t.vel = PackedVector2Array([Vector2.ZERO, Vector2.ZERO])
	t.live = [true, true]
	var plan := Pool.plan_shot(t)
	t.vel[0] = Vector2.from_angle(plan.angle) * plan.power * Pool.MAX_SPEED
	var potted := t.settle()
	_ok(plan.ok and potted.has(1) and not potted.has(0), "a perfect planned shot pots into the corner")
	var sc := [0, 0]
	_ok(Pool.resolve(t, [1], 0, sc) and sc[0] == 1, "potting a ball scores and goes again")
	t.live[0] = false
	_ok(not Pool.resolve(t, [0], 0, sc) and t.live[0] and t.pos[0].distance_to(Pool.BAULK_SPOT) < 20,
			"potting the white ends the turn and re-spots it")
	t = Pool.Table.new()
	t.pos = PackedVector2Array([Vector2(50, 50)])
	t.vel = PackedVector2Array([Vector2(-200, 0)])
	t.live = [true]
	t.step(0.5)
	_ok(t.pos[0].x >= Pool.BALL_R and t.vel[0].x > 0, "cushion bounces the ball back")
	_ok(Pool.aim_wobble(1.3, 0.0) == 0.0 and absf(Pool.aim_wobble(1.3, 6.0)) > 0.0, "sober aim doesn't wobble, drunk does")
	_ok(Pool.guide_length(6.0) < Pool.guide_length(0.0), "drink shortens the guide line")
	_ok(Pool.power_jitter(0.0) == 0.0 and Pool.power_jitter(6.0) > 0.2, "drink jitters the power")
	_ok(Pool.opponent_error(0.85) < Pool.opponent_error(Pool.NOTTINGHAM_DIFFICULTY), "higher difficulty cues straighter")
	var sober := _rate(0, Pool.NOTTINGHAM_DIFFICULTY)
	var merry := _rate(45, Pool.NOTTINGHAM_DIFFICULTY)
	var drunk := _rate(80, Pool.NOTTINGHAM_DIFFICULTY)
	var finale := _rate(0, 0.85)
	print("[test] win rate vs Gaz: sober %.2f  merry(45) %.2f  drunk(80) %.2f   sober vs difficulty 0.85: %.2f"
			% [sober, merry, drunk, finale])
	_ok(sober >= 0.65, "sober Paul usually beats Gaz")
	_ok(drunk <= 0.2, "drunk Paul rarely beats Gaz")
	_ok(sober > merry and merry > drunk, "every drink makes it harder")
	_ok(finale < sober, "a harder opponent (finale rematch) wins more")
	print("[test] %s nottingham (%d failures)" % ["PASS" if fails == 0 else "FAIL", fails])
	get_tree().quit()
