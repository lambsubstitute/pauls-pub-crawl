@tool
extends PopochiuRoom
## The Berkeley Arms, 8 Church St: stop 3, the darts pub.
## Chain: the house darts are stuck in the beam over the oche -> a merry (wobbly) Paul thumps the
## oak post and they drop -> give them to Dot -> beat her 70 at darts -> Clive stamps the card.
## Drink is needed to wobble (pint, or a free half at the pumps) and hurts at the oche (water helps).

const Data := preload('room_berkeley_arms_state.gd')
const Darts := preload("res://game/minigames/darts/darts.gd")
const DOT_SCORE := 70

var state: Data = load("res://game/rooms/berkeley_arms/room_berkeley_arms.tres")


func _on_room_entered() -> void:
	# Spawn, figure height and talk spots come from art/renders/berkeley_arms.json.
	# A walk started in the previous room must not carry on here.
	C.player.stop_walking()
	C.player.set_height(46)
	C.Clive.set_height(46)
	C.Dot.set_height(46)
	C.Dot.face_left()  # watching the room from beside the oche
	# Popochiu re-instances characters on room entry and keeps only their position.
	C.Clive.walk_to_point = Vector2(10, 6)
	C.Dot.walk_to_point = Vector2(-30, 0)
	C.player.position = Vector2(121, 125)
	C.player.face_right()
	_update_darts()


func _update_darts() -> void:
	# The darts are a sprite over the background; once they've fallen, hide it and its hotspot.
	var up := not Globals.darts_down
	$Props/BeamDarts.visible = up
	$Hotspots/BeamDarts.visible = up
	$Hotspots/BeamDarts.clickable = up


func _on_room_transition_finished() -> void:
	# face_left() in _on_room_entered can't flip her sprite yet (she isn't in the tree), so again here
	C.Dot.face_left()
	if state.visited_first_time:
		await C.Clive.say("Evening! Mind your head on the beams. Welcome to the Berkeley.")


func _on_room_exited() -> void:
	Globals.last_room = "BerkeleyArms"


func _on_restore_from_savegame() -> void:
	_update_darts()


## Paul sways into the oak post; the ceiling shudders and the house darts drop out of the beam.
func knock_darts_down() -> void:
	await C.player.say("Whoa... just steadying myself on this post...")
	await C.player.say("*THUMP*")
	if E.camera:
		E.camera.shake(1.5, 0.5)
	var spr: Sprite2D = $Props/BeamDarts
	var tw := create_tween()
	tw.tween_property(spr, "position:y", 121.0, 0.45).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	await tw.finished
	Globals.darts_down = true
	_update_darts()
	await C.Clive.say("Well I never! The house darts!")
	await C.player.walk_to(Vector2(246, 126))
	await C.player.say("Got them. Three darts, slightly dusty.")
	I.Darts.add()
	await C.Dot.say("Bring them here, duck, and we'll have a game.")


## Dot vs Paul. Called from Dot, the dartboard and handing her the darts.
func play_darts() -> void:
	if not Globals.darts_given:
		await C.Dot.say("No darts, no game, duck.")
		return
	if Globals.darts_won:
		await C.Dot.say("Once was enough for my nerves, duck.")
		return
	await C.Dot.say("Three darts each, most points wins. Ladies first.")
	await C.Dot.say("...Treble twenty, five, five. Seventy. Your go, duck.")
	if Globals.drunk >= 60:
		await C.player.say("Which of the two boards is the real one?")
		await C.Dot.say("Aim between them and hope.")
	var score: int = await Darts.play(get_tree(), DOT_SCORE)
	Globals.darts_best = maxi(Globals.darts_best, score)
	if score > DOT_SCORE:
		Globals.darts_won = true
		await C.player.say("%d! I've beaten the champion!" % score)
		await C.Dot.say("Well, I'll go to the foot of our stairs.")
		await C.Dot.say("Go on, tell Clive. He'll stamp your card.")
	elif score == DOT_SCORE:
		await C.Dot.say("A tie? We'll call that a warm-up. Again whenever you like.")
	else:
		await C.player.say("%d. The board moved." % score)
		if Globals.drunk >= Globals.WOBBLY:
			await C.Dot.say("The board didn't, duck, you did. Glass of water off the bar and try again.")
		else:
			await C.Dot.say("Hold your breath to steady up, let go to throw. Again whenever you like.")
