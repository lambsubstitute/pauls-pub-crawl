@tool
extends PopochiuRoom

const Data := preload('room_cross_house_tavern_state.gd')

var state: Data = load("res://game/rooms/cross_house_tavern/room_cross_house_tavern.tres")


func _on_room_entered() -> void:
	# Pub is a closer cutaway than the street, so figures are drawn at 46px here.
	C.player.set_height(46)
	C.Landlord.set_height(46)
	C.player.position = Vector2(288, 126)
	C.player.face_left()


func _on_room_transition_finished() -> void:
	if state.visited_first_time:
		await C.Landlord.say("Evening! Welcome to the Cross House.")


func _on_room_exited() -> void:
	Globals.last_room = "CrossHouseTavern"


func _on_restore_from_savegame() -> void:
	pass
