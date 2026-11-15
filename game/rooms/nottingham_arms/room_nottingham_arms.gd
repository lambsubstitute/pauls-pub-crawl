@tool
extends PopochiuRoom
## The Nottingham Arms, 129 High St: stop 5, the pool pub, and the crawl's hardest puzzle so far.
## Chain: Gaz plays anyone with a proper cue, but the house cue is in two halves ->
##   1. the butt end is in the cue rack (pick it up)
##   2. the top half is Norman's "jukebox poker"; he only warms to someone who laughs at his
##      stories, and only a merry Paul (30+) finds them funny (drunk helps)
##   3. take the pool rest off the wall and give it to Norman: a longer poker, so he swaps
##   4. use the shaft with the butt to screw the house cue together (item combination)
##   5. give the cue to Gaz and beat him at pool (drink makes the cue wobble: drunk hinders)
## Jackie stamps the card (5/6). A win before the Britannia's stamp is remembered and stamped
## as soon as Paul has 4. Halves at the pumps (up to 60) and the water jug are always there.

const Data := preload('room_nottingham_arms_state.gd')
const Pool := preload("res://game/minigames/pool/pool.gd")
## Where Paul appears coming in from High Street (art/renders/nottingham_arms.json from_high_st).
const SPAWN := Vector2(101, 112)
## The finale reuses Pool with a higher difficulty; Gaz is the mid-game version.
const GAZ_DIFFICULTY := Pool.NOTTINGHAM_DIFFICULTY
const RACE_TO := 3

var state: Data = load("res://game/rooms/nottingham_arms/room_nottingham_arms.tres")


func _on_room_entered() -> void:
	# A walk started in the previous room must not carry on here.
	C.player.stop_walking()
	C.player.set_height(46)
	for npc in [C.Jackie, C.Gaz, C.Norman]:
		npc.set_height(46)
	# Popochiu re-instances characters on room entry and keeps only their position, so the
	# talk spots live in each character's TALK_SPOT and these are just for completeness.
	C.Jackie.walk_to_point = Vector2(16, 7)
	C.Gaz.walk_to_point = Vector2(-18, 2)
	C.Norman.walk_to_point = Vector2(-17, 1)
	C.player.position = SPAWN
	C.player.face_right()
	update_props()


## Sprites and hotspots for the things that get picked up or swapped.
func update_props() -> void:
	var butt_here := not Globals.butt_taken
	$Props/CueButt.visible = butt_here
	var rest_on_wall := not Globals.rest_taken
	var rest: Sprite2D = $Props/PoolRestProp
	var shaft: Sprite2D = $Props/CueShaftProp
	_show_hotspot("PoolRest", rest_on_wall)
	_show_hotspot("CueShaft", not Globals.shaft_swapped)
	shaft.visible = not Globals.shaft_swapped
	if Globals.shaft_swapped:
		# Norman's new jukebox poker leans where the shaft used to
		rest.visible = true
		rest.position = shaft.position
	else:
		rest.visible = rest_on_wall


func _show_hotspot(name: String, on: bool) -> void:
	var h: PopochiuHotspot = get_node("Hotspots/%s" % name)
	h.visible = on
	h.clickable = on


func _on_room_transition_finished() -> void:
	C.Gaz.face_left()
	C.Norman.face_left()
	if state.visited_first_time:
		await C.Jackie.say("Evening, love! Welcome to the Nottingham. Mind Gaz's elbows by the table.")
	# a win from earlier in the night, now the Britannia's stamp is on the card
	if Globals.pool_won and Globals.stamps == 4:
		await C.Jackie.say("There's our pool champion! Card here, love.")
		await C.Jackie.stamp_card()


func _on_room_exited() -> void:
	Globals.last_room = "NottinghamArms"


func _on_restore_from_savegame() -> void:
	update_props()


## Leave to High Street. HighSt is built on the pub-4 branch; until it is merged in, fall back to
## the Cross so the door always works.
static func street_room() -> String:
	if PopochiuResources.has_data_value("rooms", "HighSt"):
		var path: String = PopochiuResources.get_data_value("rooms", "HighSt", "")
		if path != "" and ResourceLoader.exists(path):
			return "HighSt"
	return "TheCross"


## Norman's story. Sober Paul asks sensible questions and Norman sulks; merry Paul laughs.
func norman_story() -> void:
	await C.Norman.say("Did I ever tell you about the night the Severn Bore came up the Avon...")
	await C.Norman.say("...and carried off my bicycle, my sandwiches and the vicar's hat?")
	await C.Norman.say("Found the bike in Gloucester. Still had the sandwiches in the basket.")
	if Globals.drunk < Globals.WOBBLY:
		await C.player.say("Hang on. How did the bike float? And whose hat was it, really?")
		await C.Norman.say("If you're going to be sensible about it, I'll not bother.")
		await C.Norman.say("Nobody laughs at my stories any more. Too sober, the lot of you.")
		return
	await C.player.say("Ha! HA HA! The sandwiches! In GLOUCESTER!")
	await C.Norman.say("Ha! Finally, a lad with a sense of humour!")
	await C.Norman.say("You're all right, you are. Anything you need, you ask Norman.")
	Globals.norman_laughed = true


## Paul vs Gaz. Called from Gaz, the table and handing over the cue.
func play_pool() -> void:
	if not Globals.cue_given:
		await C.Gaz.say("No cue, no game, mate. And nobody touches Excalibur.")
		return
	if Globals.pool_won:
		await C.Gaz.say("Once is plenty for my reputation, mate.")
		return
	await C.Gaz.say("Pub rules: first to pot %d. You break." % RACE_TO)
	if Globals.drunk >= 60:
		await C.player.say("Why has the table got two white balls?")
		await C.Gaz.say("It hasn't, mate.")
	var won: bool = await Pool.play(get_tree(), "Gaz", GAZ_DIFFICULTY, RACE_TO)
	Globals.pool_best = maxi(Globals.pool_best, Pool.last_score.x)
	if won:
		Globals.pool_won = true
		await C.player.say("Yes! I've beaten Gaz on his own table!")
		await C.Gaz.say("Eleven seasons... Fair play, mate. Fair play.")
		await C.Jackie.say("Well, I never! Bring that card over, love.")
		await C.Jackie.stamp_card()
	else:
		await C.player.say("The pockets kept moving.")
		if Globals.drunk >= Globals.WOBBLY:
			await C.Gaz.say("That's the beer, mate. Glass of water off the bar and go again.")
		else:
			await C.Gaz.say("Line up on the dotted line, nice smooth stroke. Again whenever you like.")
