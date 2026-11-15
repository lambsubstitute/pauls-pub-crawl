extends Node
## Ye Olde Black Bear (stop 6, the finale) and the Mythe bridge ending. Checks: the High St door
## goes in and the exit comes back out by it, with nothing in hand; sober Paul can't wake Ursula
## and Bernie won't play a part-filled card; merry Paul's hiccups wake her, the wedge comes out
## from under her and survives leaving; the table is levelled before the card is full and that is
## remembered; Rosie stops pouring at 60, water sobers and cures the hiccups; a drunk match lost
## 0-2, then a sober rematch won 2-1 (a tied decider thrown again) -> stamp 6 -> the Mythe bridge
## ending (walking home) -> credits -> keep exploring -> back to High St and into the pub again.
## The very merry ending (the lift home) is played too. Plus darts/pool win rates vs Bernie.

const Darts := preload("res://game/minigames/darts/darts.gd")
const Pool := preload("res://game/minigames/pool/pool.gd")
const Credits := preload("res://game/ending/credits.gd")
const Room := preload("res://game/rooms/black_bear/room_black_bear.gd")
const Bridge := preload("res://game/rooms/mythe_bridge/room_mythe_bridge.gd")

var fails := 0
## What the driver saw when the credits came up: Paul's position and drink.
var credits_seen: Array = []
var _driving := false


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


func _overlay(script: Script) -> Node:
	for n in get_tree().root.get_children():
		if n.get_script() == script:
			return n
	return null


## Plays the mini-games and the credits for the match: each step waits (real time, headless
## lines auto-continue) for its overlay and finishes it.
##   ["darts", paul_score]  ["pool", won]  ["credits", choice]  ["bernie", next_total]
func _drive(steps: Array) -> void:
	_driving = true
	for st in steps:
		if st[0] == "bernie":
			R.current.next_bernie_total = st[1]
			continue
		var script: Script = {"darts": Darts, "pool": Pool, "credits": Credits}[st[0]]
		var node: Node = null
		for i in 900:
			await get_tree().create_timer(0.2).timeout
			node = _overlay(script)
			if node:
				break
		if not node:
			_ok(false, "%s overlay appeared" % st[0])
			break
		await get_tree().create_timer(0.3).timeout
		match st[0]:
			"darts":
				node.finished.emit(st[1])
			"pool":
				node.scores = [3 if st[1] else 1, 1 if st[1] else 3]
				Pool.last_score = Vector2i(node.scores[0], node.scores[1])
				node.finished.emit(st[1])
			"credits":
				credits_seen.append({"pos": C.player.position, "drunk": Globals.drunk, "room": _room()})
				node.finished.emit(st[1])
	_driving = false


func _until(cond: Callable, secs := 90.0) -> void:
	var t := 0.0
	while t < secs and not cond.call():
		await get_tree().create_timer(0.25).timeout
		t += 0.25


func _sway(drunk: int) -> float:
	return 0.0 if drunk < 30 else remap(float(drunk), 30.0, 100.0, 0.5, 6.0)


## Darts leg vs Bernie, ties thrown again: P(Paul's three darts beat Bernie's).
func _darts_rate(drunk: int, n := 2000) -> float:
	var w := 0
	var l := 0
	var rng := RandomNumberGenerator.new()
	for s in n:
		rng.seed = s * 31 + 9
		var b: int = Room.bernie_throw(rng).total
		var p := Darts.simulate_match(Room.T20, _sway(drunk), Darts.HOLD_STEADY, s * 7 + 1)
		if p > b:
			w += 1
		elif p < b:
			l += 1
	return float(w) / maxi(1, w + l)


func _pool_rate(drunk: int, n := 300) -> float:
	var w := 0
	for s in n:
		if Pool.simulate_match(Pool.PLAYER_ERROR, _sway(drunk), Room.POOL_DIFFICULTY, s * 13 + 5, Room.POOL_RACE):
			w += 1
	return float(w) / n


## The whole match: darts, pool, darts decider at one all. Win two.
static func match_rate(d: float, p: float) -> float:
	return d * p + (d * (1.0 - p) + (1.0 - d) * p) * d


func _ready() -> void:
	get_tree().create_timer(1500.0).timeout.connect(func():
		print("[test] FAIL blackbear timed out")
		get_tree().quit(1))
	E.settings.auto_continue_text = true
	await get_tree().create_timer(2.0).timeout
	# four stamps: a quick look before the full card, and the table levelled early
	Globals.stamps = 4
	Globals.drunk = 0
	Globals.last_room = "TheCross"
	I.CrawlCard.add()  # Church St hands it out; this test starts on High St

	# --- High St door round trip, nothing in hand
	R.goto_room("HighSt")
	await _wait_room("HighSt")
	await _act(_hot("BlackBearDoor"), "on_walk_to", "BlackBear")
	_ok(_room() == "BlackBear", "High St's Black Bear door leads inside (4 stamps: a quick look)")
	_ok(C.player.position.distance_to(Room.SPAWN) < 4, "Paul at the door spawn (%s)" % C.player.position)
	_ok(R.current.get_node("Props/Ursula").position == Room.URSULA_HEARTH and not R.current.get_node("Props/WedgeProp").visible
			and not _hot("Wedge").visible, "Ursula asleep on the hearth, wedge hidden under her")
	await _act(_hot("ExitDoor"), "on_open", "HighSt")
	_ok(_room() == "HighSt", "exit works with nothing done")
	_ok(C.player.position.distance_to(Vector2(274, 123)) < 4, "back out by the Black Bear door (%s)" % C.player.position)
	await _act(_hot("BlackBearDoor"), "on_open", "BlackBear")

	# --- sober and four stamps: no game, no waking Ursula
	await C.Bernie.on_talk_to()
	_ok(Globals.bernie_met and Globals.finale_matches == 0, "Bernie explains but won't play four stamps")
	await C.Rosie.on_talk_to()
	await _act(_hot("Ursula"), "on_talk_to")
	await _act(_hot("Ursula"), "on_push")
	_ok(not Globals.ursula_moved, "sober Paul can't wake Ursula")
	await _act(_hot("PoolTable"), "on_use")
	_ok(Globals.finale_matches == 0 and not Globals.table_level, "no wedge, no level table, no game")

	# --- merry: two free halves -> hiccups -> Ursula moves off the wedge
	await _act(_hot("Pumps"), "on_use")
	_ok(not Globals.has_hiccups(), "one half: no hiccups yet (%d)" % Globals.drunk)
	await _act(_hot("Pumps"), "on_use")
	_ok(Globals.drunk == 30 and Globals.has_hiccups() and Globals.black_bear_halves == 2, "two halves -> 30, hiccups")
	await _act(_hot("Ursula"), "on_talk_to")
	_ok(Globals.ursula_moved, "a hiccup wakes Ursula")
	_ok(R.current.get_node("Props/Ursula").position == Room.URSULA_WINDOW
			and (_hot("Ursula") as Node2D).position == Room.URSULA_WINDOW - Room.URSULA_HEARTH,
			"Ursula and her hotspot are under the window now")
	_ok(R.current.get_node("Props/WedgeProp").visible and _hot("Wedge").visible, "the wedge shows on the rug")
	await _act(_hot("Wedge"), "on_pick_up")
	_ok(I.is_item_in_inventory("Wedge") and Globals.wedge_taken and not _hot("Wedge").visible
			and not R.current.get_node("Props/WedgeProp").visible, "wedge taken")

	# --- leave and come back: state holds
	await _act(_hot("ExitDoor"), "on_walk_to", "HighSt")
	await _act(_hot("BlackBearDoor"), "on_use", "BlackBear")
	_ok(I.is_item_in_inventory("Wedge") and R.current.get_node("Props/Ursula").position == Room.URSULA_WINDOW
			and not _hot("Wedge").visible, "wedge and Ursula's new spot survive leaving")

	# --- level the table before the card is full: remembered, still no game
	E.clicked = _hot("PoolTable")
	await _hot("PoolTable")._on_item_used(I.Wedge)
	_ok(Globals.table_level and not I.is_item_in_inventory("Wedge"), "wedge under the short leg")
	_ok(R.current.get_node("Props/WedgeProp").visible and R.current.get_node("Props/WedgeProp").position == Room.WEDGE_TABLE,
			"wedge sprite now under the table")
	await C.Bernie.on_talk_to()
	_ok(Globals.finale_matches == 0, "level table, but still four stamps: no game")

	# --- Rosie stops at 60; water sobers and cures the hiccups
	Globals.drunk = 70
	await _act(_hot("Pumps"), "on_use")
	_ok(Globals.drunk == 70, "Rosie won't pour past 60")
	await _act(_hot("WaterJug"), "on_use")
	_ok(Globals.drunk == 45, "water sobers (70 -> %d)" % Globals.drunk)

	# --- the fifth stamp arrives; a drunk match is lost 0-2
	await _act(_hot("ExitDoor"), "on_open", "HighSt")
	Globals.stamps = 5
	Globals.drunk = 75
	await _act(_hot("BlackBearDoor"), "on_open", "BlackBear")
	_drive.call_deferred([["bernie", 100], ["darts", 41], ["pool", false]])
	await C.Bernie.on_talk_to()
	await _until(func(): return not _driving, 10.0)
	_ok(Globals.finale_matches == 1 and not Globals.finale_won and Globals.stamps == 5, "drunk match lost 0-2, no stamp")
	_ok(Globals.darts_best >= 41, "darts best recorded (%d)" % Globals.darts_best)
	_ok(_room() == "BlackBear", "losing leaves Paul in the pub")
	await _act(_hot("ExitDoor"), "on_walk_to", "HighSt")
	_ok(_room() == "HighSt", "exit still works after a loss")
	await _act(_hot("BlackBearDoor"), "on_open", "BlackBear")

	# --- sober rematch: darts won, pool lost, decider tied then won -> 6/6 -> the ending
	await _act(_hot("WaterJug"), "on_use")
	await _act(_hot("WaterJug"), "on_use")
	await _act(_hot("WaterJug"), "on_use")
	_ok(Globals.drunk == 0 and not Globals.has_hiccups(), "water all the way down: sober, no hiccups")
	_drive.call_deferred([["bernie", 80], ["darts", 81], ["pool", false], ["bernie", 90], ["darts", 90],
			["bernie", 70], ["darts", 71], ["credits", "explore"]])
	await _act(_hot("Dartboard"), "on_use")
	_ok(Globals.finale_won and Globals.finale_matches == 2, "beat Bernie 2-1 in the rematch")
	_ok(Globals.stamps == 6, "Rosie stamps the card: 6/6")
	await _until(func(): return _room() == "MytheBridge", 60.0)
	_ok(_room() == "MytheBridge", "walked out to the Mythe bridge")
	await _until(func(): return not _driving, 180.0)
	_ok(Globals.ending_seen, "the ending played")
	_ok(credits_seen.size() == 1 and credits_seen[0].room == "MytheBridge" and credits_seen[0].pos.x < 40,
			"sober ending: Paul walks home along the river, then THE END (%s)" % [credits_seen])
	await get_tree().create_timer(3.0).timeout
	_ok(C.player.position.distance_to(Bridge.ENDING_SPOT) < 4, "keep exploring: Paul back on the path")
	_ok(I.is_item_in_inventory("CrawlCard"), "the crawl card is still in hand")

	# --- the very merry ending: the lift home over the bridge
	Globals.drunk = 75
	_drive.call_deferred([["credits", "explore"]])
	await R.current.play_ending()
	await _until(func(): return not _driving, 30.0)
	_ok(credits_seen.size() == 2 and credits_seen[1].pos.x > 280 and credits_seen[1].drunk >= 60,
			"very merry ending: Paul walks off to his lift (%s)" % [credits_seen.back()])
	_ok(not R.current.get_node("Props/Car").visible, "car gone again after the ending")
	await get_tree().create_timer(3.0).timeout
	Globals.drunk = 0

	# --- back to town and into the pub again: no replay, no extra stamp
	await _act(_hot("ToHighSt"), "on_walk_to", "HighSt")
	_ok(_room() == "HighSt", "bridge path leads back to High St")
	_ok(C.player.position.distance_to(Vector2(306, 130)) < 4, "arrive at High St's Mythe end (%s)" % C.player.position)
	await _act(_hot("BlackBearDoor"), "on_open", "BlackBear")
	await C.Bernie.on_talk_to()
	await C.Rosie.on_talk_to()
	_ok(Globals.stamps == 6 and Globals.finale_matches == 2, "champion: nothing to replay, still 6/6")
	await _act(_hot("ExitDoor"), "on_open", "HighSt")
	_ok(_room() == "HighSt", "exit works at the very end")

	# --- maths: Bernie's darts and the pool leg, sober vs drunk
	var t := Room.bernie_throw(RandomNumberGenerator.new())
	_ok(t.names.size() == 3 and t.total >= 0 and t.total <= 180, "Bernie throws three darts (%s = %d)" % [t.names, t.total])
	var d0 := _darts_rate(0)
	var d45 := _darts_rate(45)
	var d80 := _darts_rate(80)
	var p0 := _pool_rate(0)
	var p45 := _pool_rate(45)
	var p80 := _pool_rate(80)
	print("[test] darts leg vs Bernie: sober %.2f  merry(45) %.2f  drunk(80) %.2f" % [d0, d45, d80])
	print("[test] pool leg vs Bernie (d%.2f, race %d): sober %.2f  merry(45) %.2f  drunk(80) %.2f"
			% [Room.POOL_DIFFICULTY, Room.POOL_RACE, p0, p45, p80])
	print("[test] whole match: sober %.2f  merry(45) %.2f  drunk(80) %.2f"
			% [match_rate(d0, p0), match_rate(d45, p45), match_rate(d80, p80)])
	_ok(d0 >= 0.52 and d0 <= 0.7, "sober darts leg is winnable but not a gimme")
	_ok(p0 >= 0.5 and p0 <= 0.7, "sober pool leg is winnable but not a gimme")
	_ok(d80 <= 0.15 and p80 <= 0.15, "drunk legs are hard")
	_ok(d0 > d45 and d45 > d80 and p0 > p45 and p45 > p80, "every drink makes it harder")
	_ok(match_rate(d0, p0) >= 0.55 and match_rate(d80, p80) <= 0.05, "sober match ~60%, drunk match rare")
	print("[test] %s blackbear (%d failures)" % ["PASS" if fails == 0 else "FAIL", fails])
	get_tree().quit()
