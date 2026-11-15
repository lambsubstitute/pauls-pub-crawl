@tool
extends PopochiuRoom
## Ye Olde Black Bear, 68 High St: stop 6, the finale. Reputedly Gloucestershire's oldest inn
## (1308); crooked low beams, dark panelling, and a floor that runs downhill towards the Avon.
## Chain:
##   1. Bernie "the Bear", the pub champion, only plays someone holding a full crawl card (5
##      stamps) - and never on a table that leans. The pool table's wedge has gone missing.
##   2. Ursula, Rosie's enormous Newfoundland, is asleep on the wedge by the fire. Nothing wakes
##      her except a hiccup (her old master had terrible hiccups), and only a merry Paul (30+,
##      Rosie's free halves) has the hiccups: drunk helps.
##   3. Hiccup at Ursula: she gets up to check on Paul and flops down under the window instead.
##      Take the wedge and put it under the table's short leg (or give it to Bernie).
##   4. The Black Bear double: a leg of darts, a leg of pool and, at one leg all, a darts decider.
##      Drink widens the darts wobble and wobbles the cue (drunk hinders); the water jug sobers.
## Win: Rosie stamps the card (6/6), the pub cheers, and Paul walks out to the Mythe bridge for the
## ending (MytheBridge). Losing costs nothing: Bernie plays again whenever Paul likes. The exit
## always works and every flag survives leaving, so the steps can be done in any order.

const Data := preload('room_black_bear_state.gd')
const Darts := preload("res://game/minigames/darts/darts.gd")
const Pool := preload("res://game/minigames/pool/pool.gd")
const URSULA_AWAKE := preload("res://game/rooms/black_bear/props/ursula_awake.png")
const URSULA_ASLEEP := preload("res://game/rooms/black_bear/props/ursula_asleep.png")

## Where Paul appears coming in from High Street (art/renders/black_bear.json from_high_st).
const SPAWN := Vector2(96, 125)
## Ursula's sprite anchors: asleep on the hearth rug, and under the window once she's moved
## (black_bear.json ursula / ursula_moved). Her hotspot moves with her.
const URSULA_HEARTH := Vector2(174, 119)
const URSULA_WINDOW := Vector2(129, 118)
## The wedge: on the rug where Ursula was lying, then under the table's short leg.
const WEDGE_HEARTH := Vector2(182, 118)
const WEDGE_TABLE := Vector2(304, 121)
## Where Paul stands to put the wedge under the short leg.
const TABLE_SPOT := Vector2(292, 126)

## Bernie's darts: three at treble twenty with a hand twice as shaky as Paul's steadied one
## (Darts.HOLD_STEADY 0.3). Averages ~104; a sober Paul who steadies up beats him ~60% of the
## time, a merry one (45) ~18%, a drunk one (80) ~6% (tests/blackbear_test.gd).
const T20 := Vector2(0, -0.605)
const BERNIE_HAND := 0.6
## Pool leg: a race to 3 against a stronger cueist than Gaz (Pool.NOTTINGHAM_DIFFICULTY 0.5).
## Sober ~57%, merry ~34%, drunk ~6%.
const POOL_DIFFICULTY := 0.8
const POOL_RACE := 3

var state: Data = load("res://game/rooms/black_bear/room_black_bear.tres")
## Tests: force Bernie's next darts total (-1 = throw for real).
var next_bernie_total := -1
var _rng := RandomNumberGenerator.new()


func _on_room_entered() -> void:
	# A walk started in the previous room must not carry on here.
	C.player.stop_walking()
	C.player.set_height(46)
	for npc in [C.Rosie, C.Bernie]:
		npc.set_height(46)
	# Popochiu re-instances characters on room entry and keeps only their position, so the
	# talk spots live in each character's TALK_SPOT.
	C.player.position = SPAWN
	C.player.face_right()
	_rng.randomize()
	update_props()


## Ursula, the wedge and their hotspots, from the flags.
func update_props() -> void:
	var ursula: Sprite2D = $Props/Ursula
	ursula.position = URSULA_WINDOW if Globals.ursula_moved else URSULA_HEARTH
	ursula.texture = URSULA_AWAKE if Globals.ursula_moved else URSULA_ASLEEP
	($Hotspots/Ursula as Node2D).position = (URSULA_WINDOW - URSULA_HEARTH) if Globals.ursula_moved else Vector2.ZERO
	var wedge: Sprite2D = $Props/WedgeProp
	if Globals.table_level:
		wedge.visible = true
		wedge.position = WEDGE_TABLE
	else:
		wedge.position = WEDGE_HEARTH
		wedge.visible = Globals.ursula_moved and not Globals.wedge_taken
	_show_hotspot("Wedge", Globals.ursula_moved and not Globals.wedge_taken and not Globals.table_level)


func _show_hotspot(name: String, on: bool) -> void:
	var h: PopochiuHotspot = get_node("Hotspots/%s" % name)
	h.visible = on
	h.clickable = on


func _on_room_transition_finished() -> void:
	C.Bernie.face_left()
	if state.visited_first_time:
		await C.Rosie.say("Evening, love! Mind your head on the beams, and mind the dog.")
		if Globals.stamps >= 5:
			await C.Rosie.say("Ooh, a full crawl card! Bernie, you've got a challenger.")


func _on_room_exited() -> void:
	Globals.last_room = "BlackBear"


func _on_restore_from_savegame() -> void:
	update_props()


# ------------------------------------------------------------------ puzzle ----
## Paul hiccups at Ursula: she gets up to check on him, pads over to the window and flops down
## there, leaving the wedge she was lying on.
func wake_ursula() -> void:
	await C.player.say("Ursula? Wakey wak- *HIC!*")
	var ursula: Sprite2D = $Props/Ursula
	ursula.texture = URSULA_AWAKE
	if E.camera:
		E.camera.shake(0.8, 0.3)
	await C.Rosie.say("There she goes! Up to check you're all right, love.")
	await C.player.say("I'm fine, Ursula. Just the *HIC* hiccups.")
	var tw := create_tween()
	tw.tween_property(ursula, "position", URSULA_WINDOW, 1.2).set_trans(Tween.TRANS_SINE)
	await tw.finished
	Globals.ursula_moved = true
	update_props()
	await C.player.say("She's flopped down under the window. And she was lying on... a wooden wedge!")


## The wedge goes under the pool table's short leg.
func level_table() -> void:
	await C.player.walk_to(TABLE_SPOT)
	C.player.face_up()
	await C.player.say("Short leg's at the river end... in it goes.")
	I.Wedge.remove()
	Globals.table_level = true
	update_props()
	await C.Bernie.say("Now that's level. Well, level for the Black Bear.")
	if Globals.stamps >= 5 and not Globals.finale_won:
		await C.Bernie.say("Darts and pool, lad. Say when.")


# ------------------------------------------------------------------- match ----
## Bernie's three darts at treble twenty. Returns {total, names}.
static func bernie_throw(rng: RandomNumberGenerator) -> Dictionary:
	var names: Array[String] = []
	var total := 0
	for i in Darts.DARTS:
		var p := Darts.simulate_dart(T20, rng.randf_range(0.0, 20.0), 0.0, BERNIE_HAND, rng)
		total += Darts.score_at(p)
		names.append(Darts.describe(p))
	return {"total": total, "names": names}


## Why Bernie won't play yet, or "" if he will.
func match_blocker() -> String:
	if Globals.finale_won:
		return "won"
	if Globals.stamps < 5:
		return "card"
	if not Globals.table_level:
		return "table"
	return ""


## The Black Bear double vs Bernie. Called from Bernie, the dartboard and the pool table.
func play_match() -> void:
	match match_blocker():
		"won":
			await C.Bernie.say("You're the champion now, lad. I'll have my rematch next year.")
			return
		"card":
			await C.Bernie.say("Full card first, lad. Five stamps and I'll play you for the sixth.")
			return
		"table":
			await C.Bernie.say("Not on a table that leans like that. Find the wedge for the short leg.")
			return
	Globals.finale_matches += 1
	await C.Bernie.say("The Black Bear double: a leg of darts, a leg of pool. Win both and you're champion.")
	await C.Bernie.say("One each, and we settle it on the dartboard.")
	if Globals.drunk >= Globals.SEEING_DOUBLE:
		await C.Bernie.say("You're swaying more than my floor, lad. There's water on the bar, mind.")
	var legs := [0, 0]
	# leg 1: darts
	if await _darts_leg():
		legs[0] += 1
	else:
		legs[1] += 1
	await _score(legs)
	# leg 2: pool
	await C.Bernie.say("Pool, then. Race to %d. You break." % POOL_RACE)
	if Globals.drunk >= Globals.SEEING_DOUBLE:
		await C.player.say("Why has the table got two white balls?")
	var pool_won: bool = await Pool.play(get_tree(), "Bernie", POOL_DIFFICULTY, POOL_RACE)
	Globals.pool_best = maxi(Globals.pool_best, Pool.last_score.x)
	if pool_won:
		legs[0] += 1
	else:
		legs[1] += 1
	await _score(legs)
	# decider at one leg all: darts again
	if legs[0] == 1 and legs[1] == 1:
		await C.Bernie.say("One leg all. Decider on the dartboard. Three darts, highest wins.")
		if await _darts_leg():
			legs[0] += 1
		else:
			legs[1] += 1
	if legs[0] >= 2:
		await _win()
	else:
		await _lose()


func _score(legs: Array) -> void:
	if legs[0] + legs[1] >= 2 and legs[0] != legs[1]:
		return
	await C.Rosie.say("That's Paul %d, Bernie %d!" % [legs[0], legs[1]])


## One leg of darts: Bernie throws first, Paul has to beat his total. Level scores throw again.
func _darts_leg() -> bool:
	while true:
		var total := next_bernie_total
		next_bernie_total = -1
		if total < 0:
			var t := bernie_throw(_rng)
			total = t.total
			await C.Bernie.say("%s, %s, %s..." % t.names)
		await C.Bernie.say("%d. Beat that, lad." % total)
		if Globals.drunk >= Globals.SEEING_DOUBLE:
			await C.player.say("Which of the two boards is the real one?")
		var score: int = await Darts.play(get_tree(), total, "Bernie")
		Globals.darts_best = maxi(Globals.darts_best, score)
		if score > total:
			await C.player.say("%d! That's my leg!" % score)
			return true
		if score < total:
			await C.player.say("%d. The board's on a slope, I'm sure of it." % score)
			return false
		await C.Bernie.say("Level! We'll both throw that again.")
	return false


func _win() -> void:
	Globals.finale_won = true
	await C.player.say("I've done it! I've beaten the Bear!")
	await C.Bernie.say("Well, I'll be... Nobody's beaten me since 1999. Put it there, champion.")
	if E.camera:
		E.camera.shake(1.0, 0.6)
	await C.Rosie.say("Hip hip... HOORAY! A new champion of the Black Bear!")
	await C.Rosie.stamp_card()
	await C.Bernie.say("Your name goes up on the honours board tomorrow. Gold leaf, the works.")
	await C.Rosie.say("*DING DING* Time, ladies and gentlemen, please!")
	await C.player.say("Six pubs. Six stamps. What a night.")
	await C.player.say("I think I'll get some fresh air. Down to the river and the Mythe bridge.")
	R.goto_room("MytheBridge")


func _lose() -> void:
	await C.Bernie.say("Hard luck, lad. Good game, though. Again whenever you like.")
	if Globals.drunk >= Globals.WOBBLY:
		await C.Rosie.say("A glass of water and a steady hand, love. That's how Bernie does it.")
	else:
		await C.Rosie.say("Hold your breath on the darts and nice smooth strokes on the pool.")
