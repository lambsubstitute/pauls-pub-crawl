@tool
extends PopochiuRoom

const Data := preload('room_hop_pole_state.gd')
const Skittles := preload("res://game/minigames/skittles/skittles.gd")
const REG_SCORE := 6

var state: Data = load("res://game/rooms/hop_pole/room_hop_pole.tres")


func _on_room_entered() -> void:
	# Spawn and figure height come from art/renders/hop_pole.json.
	# A walk started in the previous room (e.g. click then double-click a door) must not
	# carry on here towards that room's coordinates.
	C.player.stop_walking()
	C.player.set_height(46)
	C.Barmaid.set_height(46)
	C.Reg.set_height(46)
	C.Reg.face_left()  # watching the room, not the alley
	# Popochiu re-instances characters on room entry and keeps only their position, so the
	# per-room talk spots (from art/renders/hop_pole.json) are applied here.
	C.Barmaid.walk_to_point = Vector2(-11, 13)
	C.Reg.walk_to_point = Vector2(-24, 5)
	C.player.position = Vector2(128, 126)
	C.player.face_right()


func _on_room_transition_finished() -> void:
	if state.visited_first_time:
		await C.Barmaid.say("Evening, love. Welcome to the Hop Pole.")


func _on_room_exited() -> void:
	Globals.last_room = "HopPole"


func _on_restore_from_savegame() -> void:
	pass


## Reg vs Paul at skittles. Called from Reg, the alley and handing the pin back.
func play_skittles() -> void:
	if not Globals.pin_returned:
		await C.Reg.say("Can't play with eight pins, son.")
		return
	if Globals.skittles_won:
		await C.Reg.say("You've had your fun. I'm nursing my pride.")
		return
	await C.Reg.say("Three balls, all nine pins. I knocked down %d. Beat that." % REG_SCORE)
	if Globals.drunk >= 60:
		await C.player.say("Why are there two alleys?")
	var score: int = await Skittles.play(get_tree(), REG_SCORE)
	Globals.skittles_best = maxi(Globals.skittles_best, score)
	if score > REG_SCORE:
		Globals.skittles_won = true
		await C.player.say("%d! Get in!" % score)
		await C.Reg.say("Well I never. First time since nineteen eighty-seven.")
		await C.Reg.say("Go on, tell Bev at the bar. She'll stamp you.")
	elif score == REG_SCORE:
		await C.Reg.say("A tie's no good, son. Go again when you're ready.")
	else:
		await C.player.say("%d. The alley's wonky." % score)
		await C.Reg.say("Bad workman blames his alley. Go again whenever.")
