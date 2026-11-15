extends Node
## Berkeley Arms (stop 3): Church St -> the Cross -> Berkeley; every new room can be left with
## nothing in hand; sober Paul can't get the darts, a merry one knocks them out of the beam;
## Dot plays; Clive stamps (3/6). Plus darts maths: good sober aim usually beats Dot's 70,
## drunk or wild aim rarely does.

const Darts := preload("res://game/minigames/darts/darts.gd")

var fails := 0


func _ok(cond: bool, what: String) -> void:
	if not cond:
		fails += 1
	print("[test] %s %s" % ["PASS" if cond else "FAIL", what])


func _room() -> String:
	return R.current.script_name if R.current else ""


## Run a verb on a hotspot the way a click would (E.clicked set, so walk_to_clicked works),
## then wait for the room to be `room` (or just for the action to finish).
func _act(node: Node, method: String, room := "") -> void:
	E.clicked = node
	await node.call(method)
	if room == "":
		return
	for i in 40:
		if _room() == room:
			break
		await get_tree().create_timer(0.25).timeout
	# let a first-visit greeting finish: Popochiu ignores goto_room while a line is playing
	await get_tree().create_timer(4.0).timeout


func _hot(name: String) -> Node:
	return R.current.get_node("Hotspots/%s" % name)


func _finish_darts(score: int) -> void:
	for i in 200:  # dialogue auto-continues first; poll on real time (headless runs uncapped)
		await get_tree().create_timer(0.2).timeout
		for n in get_tree().root.get_children():
			if n.get_script() == Darts:
				n.finished.emit(score)
				return
	_ok(false, "darts overlay appeared")
	get_tree().quit(1)


func _win_rate(aim: Vector2, drunk: int, hand: float, n := 600) -> float:
	var sway: float = 0.0 if drunk < 30 else remap(float(drunk), 30.0, 100.0, 0.5, 6.0)
	var wins := 0
	for s in n:
		if Darts.simulate_match(aim, sway, hand, s * 7 + 1) > 70:
			wins += 1
	return float(wins) / n


func _ready() -> void:
	get_tree().create_timer(900.0).timeout.connect(func():
		print("[test] FAIL berkeley timed out")
		get_tree().quit(1))
	E.settings.auto_continue_text = true
	await get_tree().create_timer(2.0).timeout
	Globals.stamps = 2
	Globals.skittles_won = true

	# --- Church St -> the Cross by walking off the right-hand edge
	_ok(_room() == "ChurchSt", "start on Church St")
	await _act(_hot("ToTheCross"), "on_walk_to", "TheCross")
	_ok(_room() == "TheCross", "Church St right edge leads to the Cross")
	_ok(C.player.position.distance_to(Vector2(23, 130)) < 4, "arrive at the Cross's left edge (%s)" % C.player.position)
	# and back again, with nothing in hand
	await _act(_hot("ToChurchSt"), "on_walk_to", "ChurchSt")
	_ok(_room() == "ChurchSt", "the Cross -> Church St, nothing needed")
	_ok(C.player.position.distance_to(Vector2(307, 130)) < 4, "arrive at Church St's right edge (%s)" % C.player.position)
	await _act(_hot("ToTheCross"), "on_walk_to", "TheCross")
	await _act(_hot("ToHighSt"), "on_walk_to", "HighSt")
	_ok(_room() == "HighSt", "High St exit is open, even before stamp 3")
	await _act(_hot("ToTheCross"), "on_walk_to", "TheCross")
	_ok(_room() == "TheCross", "and back to the Cross from High St")

	# --- into the Berkeley, and straight out again with nothing
	await _act(_hot("BerkeleyDoor"), "on_walk_to", "BerkeleyArms")
	_ok(_room() == "BerkeleyArms", "entered the Berkeley Arms")
	_ok(R.current.get_node("Props/BeamDarts").visible, "house darts visible in the beam")
	await _act(_hot("ExitDoor"), "on_open", "TheCross")
	_ok(_room() == "TheCross", "Berkeley exit works with nothing done")
	_ok(C.player.position.distance_to(Vector2(78, 123)) < 4, "arrive outside the Berkeley door")
	await _act(_hot("BerkeleyDoor"), "on_open", "BerkeleyArms")

	# --- sober: the darts stay put
	Globals.drunk = 0
	await C.Clive.on_talk_to()
	await _act(_hot("BeamDarts"), "on_pick_up")
	_ok(not Globals.darts_down, "sober Paul can't reach the darts")
	await _act(_hot("Post"), "on_push")
	_ok(not Globals.darts_down, "sober push on the post does nothing")
	await C.Dot.on_talk_to()
	_ok(not Globals.darts_given, "Dot can't play without darts")

	# --- free halves get Paul merry (no pint needed, so this can't softlock)
	await _act(_hot("Pumps"), "on_use")
	await _act(_hot("Pumps"), "on_use")
	_ok(Globals.drunk == 30 and Globals.berkeley_halves == 2, "two halves from Clive -> drunk 30 (%d)" % Globals.drunk)
	await _act(_hot("Post"), "on_push")
	_ok(Globals.darts_down, "merry Paul wobbles into the post and the darts fall")
	_ok(I.is_item_in_inventory("Darts"), "Paul picks the darts up")
	_ok(not R.current.get_node("Props/BeamDarts").visible and not _hot("BeamDarts").visible,
			"beam darts sprite and hotspot hidden")

	# --- leave with the darts and come back: state holds
	await _act(_hot("ExitDoor"), "on_walk_to", "TheCross")
	await _act(_hot("BerkeleyDoor"), "on_walk_to", "BerkeleyArms")
	_ok(not R.current.get_node("Props/BeamDarts").visible and I.is_item_in_inventory("Darts"),
			"darts stay down and in inventory after leaving")

	# --- too merry: pumps refuse, water sobers
	Globals.drunk = 70
	await _act(_hot("Pumps"), "on_use")
	_ok(Globals.drunk == 70, "Clive won't pour past 60")
	await _act(_hot("WaterJug"), "on_use")
	_ok(Globals.drunk == 45, "water sobers Paul up (70 -> %d)" % Globals.drunk)

	# --- Dot: lose, then win
	_finish_darts.call_deferred(60)
	await C.Dot._on_item_used(I.Darts)
	_ok(Globals.darts_given and not I.is_item_in_inventory("Darts"), "darts handed to Dot")
	_ok(not Globals.darts_won, "60 doesn't beat Dot's 70")
	_finish_darts.call_deferred(70)
	await C.Dot.on_talk_to()
	_ok(not Globals.darts_won, "a tie (70) doesn't win")
	_finish_darts.call_deferred(81)
	await C.Dot.on_talk_to()
	_ok(Globals.darts_won and Globals.darts_best == 81, "81 beats Dot")
	await C.Clive.on_talk_to()
	_ok(Globals.stamps == 3, "Clive stamps the card (3/6)")
	_ok(Globals.drunk == 20, "and the water on the house sobers Paul a bit (%d)" % Globals.drunk)

	# --- darts maths
	_ok(Darts.score_at(Vector2.ZERO) == 50, "bull is 50")
	_ok(Darts.score_at(Vector2(0, -0.07)) == 25, "outer bull is 25")
	_ok(Darts.score_at(Vector2(0, -0.605)) == 60, "treble 20 is 60")
	_ok(Darts.score_at(Vector2(0, -0.97)) == 40, "double 20 is 40")
	_ok(Darts.score_at(Vector2(0.4, 0)) == 6, "straight right is 6")
	_ok(Darts.score_at(Vector2(0, 0.4)) == 3, "straight down is 3")
	_ok(Darts.score_at(Vector2(0, -1.05)) == 0, "off the board is 0")
	var t20 := Vector2(0, -0.605)
	var sober := _win_rate(t20, 0, Darts.HOLD_STEADY)
	var merry := _win_rate(t20, 45, Darts.HOLD_STEADY)
	var drunk := _win_rate(t20, 80, Darts.HOLD_STEADY)
	var wild := _win_rate(Vector2(0.55, 0.55), 0, Darts.HOLD_STEADY)
	var unsteady := _win_rate(t20, 0, Darts.FREE_HAND)
	print("[test] win rate vs 70: sober %.2f  merry(45) %.2f  drunk(80) %.2f  wild aim %.2f  no steadying %.2f"
			% [sober, merry, drunk, wild, unsteady])
	_ok(sober >= 0.65, "good sober aim beats Dot often")
	_ok(drunk <= 0.2, "drunk aim rarely beats Dot")
	_ok(wild <= 0.1, "bad aim rarely beats Dot")
	_ok(sober > merry and merry > drunk, "every drink makes it harder")
	_ok(unsteady < sober, "holding breath to steady helps")
	_ok(Darts.breath_drain(6.0) > Darts.breath_drain(0.0) * 2.0, "drink empties the breath gauge faster")
	print("[test] %s berkeley (%d failures)" % ["PASS" if fails == 0 else "FAIL", fails])
	get_tree().quit()
