@tool
extends PopochiuRoom
## The Cross: the top of Church St where it meets High St and Barton St. The Berkeley Arms is
## on the left; High Street (the Britannia and the later pubs) runs away north on the right.

const Data := preload('room_the_cross_state.gd')

var state: Data = load("res://game/rooms/the_cross/room_the_cross.tres")


func _on_room_entered() -> void:
	# Spawns from art/renders/the_cross.json. Same street camera as Church St: 30px figures.
	C.player.stop_walking()
	C.player.set_height(30)
	if Globals.last_room == "BerkeleyArms":
		C.player.position = Vector2(78, 123)   # from_berkeley
	elif Globals.last_room == "HighSt":
		C.player.position = Vector2(310, 125)  # from_high_st: just in from the right-hand edge
		C.player.face_left()
		return
	else:
		C.player.position = Vector2(23, 130)   # from_church_st: in from the left-hand edge
	C.player.face_right()


func _on_room_transition_finished() -> void:
	if state.visited_first_time:
		await C.player.say("The Cross. Church Street, High Street and Barton Street, all meeting for a pint.")


func _on_room_exited() -> void:
	Globals.last_room = "TheCross"


func _on_restore_from_savegame() -> void:
	pass
