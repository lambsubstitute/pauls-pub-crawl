extends Node
## Britannia Inn (stop 4): the Cross -> High St -> Britannia; every new room and stub door can be
## used with nothing in hand; sober Paul sees only dots in the Magic Eye, seeing double (60+) the
## ghost picture appears and shows the clock; the ha'penny comes out of the clock (sober too,
## once seen) and survives leaving; Stan plays (lose, tie, win); a win before the Berkeley stamp
## is remembered and stamped when Paul comes back with it (4/6). Plus shove ha'penny maths:
## good sober play usually beats Stan's 20, drunk play rarely does.

const Shove := preload("res://game/minigames/shove/shove.gd")

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


func _finish_shove(score: int) -> void:
	for i in 200:  # dialogue auto-continues first; poll on real time (headless runs uncapped)
		await get_tree().create_timer(0.2).timeout
		for n in get_tree().root.get_children():
			if n.get_script() == Shove:
				n.finished.emit(score)
				return
	_ok(false, "shove ha'penny overlay appeared")
	get_tree().quit(1)


func _overlay_open() -> bool:
	for n in get_tree().root.get_children():
		if n.get_script() == Shove:
			return true
	return false


func _sway(drunk: int) -> float:
	return 0.0 if drunk < 30 else remap(float(drunk), 30.0, 100.0, 0.5, 6.0)


func _win_rate(drunk: int, bed := 7, n := 600) -> float:
	var wins := 0
	for s in n:
		if Shove.simulate_match(bed, _sway(drunk), s * 7 + 1) > 20:
			wins += 1
	return float(wins) / n


func _ready() -> void:
	get_tree().create_timer(900.0).timeout.connect(func():
		print("[test] FAIL britannia timed out")
		get_tree().quit(1))
	E.settings.auto_continue_text = true
	await get_tree().create_timer(2.0).timeout
	Globals.stamps = 2   # Berkeley not done yet: the Britannia win must wait for its stamp

	# --- the Cross -> High St, and back, with nothing in hand
	R.goto_room("TheCross")
	await get_tree().create_timer(5.0).timeout
	await _act(_hot("ToHighSt"), "on_walk_to", "HighSt")
	_ok(_room() == "HighSt", "the Cross's High St exit leads to High St (even before stamp 3)")
	_ok(C.player.position.distance_to(Vector2(23, 130)) < 4, "arrive at High St's left edge (%s)" % C.player.position)
	await _act(_hot("ToTheCross"), "on_walk_to", "TheCross")
	_ok(_room() == "TheCross", "High St -> the Cross, nothing needed")
	_ok(C.player.position.distance_to(Vector2(310, 125)) < 4, "arrive at the Cross's right edge (%s)" % C.player.position)
	await _act(_hot("ToHighSt"), "on_use", "HighSt")

	# --- the Nottingham Arms door goes in; its exit brings Paul back out by that door
	await _act(_hot("NottinghamDoor"), "on_open", "NottinghamArms")
	_ok(_room() == "NottinghamArms", "Nottingham Arms door leads inside")
	await _act(_hot("ExitDoor"), "on_open", "HighSt")
	_ok(_room() == "HighSt", "Nottingham Arms exit leads back to High St")
	_ok(C.player.position.distance_to(Vector2(159, 123)) < 4, "arrive outside the Nottingham door (%s)" % C.player.position)
	# --- the Black Bear door is still a stub and leaves Paul on High St
	await _act(_hot("BlackBearDoor"), "on_walk_to")
	_ok(_room() == "HighSt", "Black Bear door is a polite stub")
	_ok(_hot("BlackBearDoor").get_node("InteractionPolygon").polygon[0].x > 200, "Black Bear is at the far right")

	# --- into the Britannia and straight out again
	await _act(_hot("BritanniaDoor"), "on_walk_to", "Britannia")
	_ok(_room() == "Britannia", "entered the Britannia")
	await _act(_hot("ExitDoor"), "on_open", "HighSt")
	_ok(_room() == "HighSt", "Britannia exit works with nothing done")
	_ok(C.player.position.distance_to(Vector2(64, 123)) < 4, "arrive outside the Britannia door (%s)" % C.player.position)
	await _act(_hot("BritanniaDoor"), "on_open", "Britannia")

	# --- sober: just dots, nothing in the clock, Stan won't play
	Globals.drunk = 0
	await get_tree().create_timer(0.3).timeout
	_ok(not R.current.get_node("Props/GhostPicture").visible and not _hot("GhostPicture").visible,
			"sober: no ghost picture")
	await C.Gwen.on_talk_to()
	await _act(_hot("MagicEye"), "on_look_at")
	_ok(not Globals.magic_eye_seen, "sober Paul sees only dots")
	await _act(_hot("Clock"), "on_open")
	_ok(not Globals.halfpenny_found, "the clock looks empty before the Magic Eye clue")
	await C.Stan.on_talk_to()
	await _act(_hot("ShoveBoard"), "on_use")
	_ok(not Globals.halfpenny_given and not _overlay_open(), "no game with four ha'pennies")

	# --- free halves up to seeing double (no pint needed, so this can't softlock)
	for i in 4:
		await _act(_hot("Pumps"), "on_use")
	_ok(Globals.drunk == 60 and Globals.britannia_halves == 4, "four halves from Gwen -> drunk 60 (%d)" % Globals.drunk)
	await _act(_hot("Pumps"), "on_use")
	_ok(Globals.drunk == 60, "Gwen won't pour past 60")
	await get_tree().create_timer(0.3).timeout
	_ok(R.current.get_node("Props/GhostPicture").visible and _hot("GhostPicture").visible
			and _hot("GhostPicture").clickable and R.current.get_node("DoubleVision").visible,
			"seeing double: ghost room, ghost picture sprite and hotspot appear")
	await _act(_hot("MagicEye"), "on_look_at")
	await _act(_hot("GhostPicture"), "on_look_at")
	_ok(Globals.magic_eye_seen, "the ghost picture shows the clock")

	# --- water sobers; the clue is remembered, the ghost goes
	await _act(_hot("WaterJug"), "on_use")
	_ok(Globals.drunk == 35, "water sobers Paul up (60 -> %d)" % Globals.drunk)
	await get_tree().create_timer(0.3).timeout
	_ok(not _hot("GhostPicture").visible, "ghost picture gone once below 60")
	await _act(_hot("Clock"), "on_open")
	_ok(Globals.halfpenny_found and I.is_item_in_inventory("Halfpenny"), "the ha'penny comes out of the clock")
	await _act(_hot("WaterJug"), "on_use")
	await _act(_hot("WaterJug"), "on_use")
	_ok(Globals.drunk == 0, "water down to sober (%d)" % Globals.drunk)

	# --- leave with the ha'penny and come back: state holds
	await _act(_hot("ExitDoor"), "on_walk_to", "HighSt")
	await _act(_hot("BritanniaDoor"), "on_walk_to", "Britannia")
	_ok(I.is_item_in_inventory("Halfpenny") and Globals.magic_eye_seen, "ha'penny and clue survive leaving")
	await _act(_hot("Clock"), "on_open")
	_ok(I.is_item_in_inventory("Halfpenny") and Globals.halfpenny_found, "opening the clock again is harmless")

	# --- Stan: lose, tie, win (before the Berkeley stamp)
	_finish_shove.call_deferred(15)
	await C.Stan._on_item_used(I.Halfpenny)
	_ok(Globals.halfpenny_given and not I.is_item_in_inventory("Halfpenny"), "ha'penny handed to Stan")
	_ok(not Globals.shove_won and Globals.shove_best == 15, "15 doesn't beat Stan's 20")
	_finish_shove.call_deferred(20)
	await C.Stan.on_talk_to()
	_ok(not Globals.shove_won, "a tie (20) doesn't win")
	_finish_shove.call_deferred(24)
	await _act(_hot("ShoveBoard"), "on_use")
	_ok(Globals.shove_won and Globals.shove_best == 24, "24 beats Stan (replayable from the board)")
	await C.Gwen.on_talk_to()
	_ok(Globals.stamps == 2, "crawl rules: no stamp before the Berkeley's (still %d)" % Globals.stamps)

	# --- come back with the Berkeley stamp: the remembered win is stamped
	await _act(_hot("ExitDoor"), "on_use", "HighSt")
	Globals.stamps = 3
	await _act(_hot("BritanniaDoor"), "on_walk_to", "Britannia")
	for i in 240:  # Gwen's lines run first (slow with auto-continue), so allow up to a minute
		if Globals.stamps == 4:
			break
		await get_tree().create_timer(0.25).timeout
	_ok(Globals.stamps == 4, "Gwen stamps the remembered win on return (4/6)")
	await C.Gwen.on_talk_to()
	_ok(Globals.stamps == 4, "and only once")
	_finish_shove.call_deferred(10)
	await C.Stan.on_talk_to()
	_ok(Globals.shove_won and Globals.stamps == 4, "a lost rematch changes nothing")
	await _act(_hot("ExitDoor"), "on_walk_to", "HighSt")
	_ok(_room() == "HighSt", "out on High St after the stamp")

	# --- shove ha'penny maths
	var mid := Shove.BED_START + Shove.BED_H * 2.5   # middle of bed 3
	_ok(Shove.bed_of(Vector2(0, mid)) == 3, "coin in the middle of bed 3 scores 3")
	_ok(Shove.bed_of(Vector2(0, Shove.line_y(3))) == 0, "coin on a line scores 0")
	_ok(Shove.bed_of(Vector2(0, Shove.line_y(3) + Shove.COIN_R * 0.5)) == 0, "coin touching a line scores 0")
	_ok(Shove.bed_of(Vector2(0, 0.5)) == 0, "short of the first line scores 0")
	_ok(Shove.bed_of(Vector2(0, Shove.line_y(9) + 0.1)) == 0, "past the last line scores 0")
	_ok(Shove.bed_of(Vector2(0.99, mid)) == 0, "half in the gutter scores 0")
	_ok(Shove.score_coins([Vector2(0, mid), Vector2(0.4, Shove.BED_START + Shove.BED_H * 8.5)]) == 12,
			"scores add up (3 + 9)")
	var rng := RandomNumberGenerator.new()
	rng.seed = 3
	var r := Shove.simulate_shove([], 0.0, 1.2, Vector2.ZERO, rng)
	_ok(r.coins.is_empty(), "a full-blooded shove goes off the far end")
	r = Shove.simulate_shove([], 0.0, Shove.power_for_bed(5, 0.0), Vector2.ZERO, rng)
	_ok(r.coins.size() == 1 and Shove.bed_of(r.coins[0]) == 5, "a perfect shove lands in its bed (%s)" % [r.coins])
	var resting := [Vector2(0, Shove.BED_START + Shove.BED_H * 1.5)]
	r = Shove.simulate_shove(resting, 0.0, Shove.power_for_bed(6, 0.0), Vector2.ZERO, rng)
	_ok(r.moves.size() >= 2 and r.all[0].y > resting[0].y + 0.3, "a coin in the way gets knocked up the board")
	var sober := _win_rate(0)
	var merry := _win_rate(45)
	var double := _win_rate(60)
	var drunk := _win_rate(80)
	var timid := _win_rate(0, 3)
	print("[test] win rate vs 20: sober %.2f  merry(45) %.2f  double(60) %.2f  drunk(80) %.2f  timid aim %.2f"
			% [sober, merry, double, drunk, timid])
	_ok(sober >= 0.65, "good sober play beats Stan often")
	_ok(drunk <= 0.2, "drunk play rarely beats Stan")
	_ok(timid <= 0.1, "playing safe in the low beds doesn't beat Stan")
	_ok(sober > merry and merry > drunk, "drink makes it harder")
	_ok(Shove.random_tilt(0.0, rng) == Vector2.ZERO, "a sober table doesn't tilt")
	print("[test] %s britannia (%d failures)" % ["PASS" if fails == 0 else "FAIL", fails])
	get_tree().quit()
