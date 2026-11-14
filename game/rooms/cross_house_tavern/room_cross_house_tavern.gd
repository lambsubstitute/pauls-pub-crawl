@tool
extends PopochiuRoom

const Data := preload('room_cross_house_tavern_state.gd')

var state: Data = load("res://game/rooms/cross_house_tavern/room_cross_house_tavern.tres")


func _on_room_entered() -> void:
	# Pub is a closer cutaway than the street, so figures are drawn at 46px here.
	# A walk started in the previous room (e.g. click then double-click a door) must not
	# carry on here towards that room's coordinates.
	C.player.stop_walking()
	C.player.set_height(46)
	C.Landlord.set_height(46)
	C.Landlord.walk_to_point = Vector2(8, 13)  # see HopPole: room overrides don't survive
	C.player.position = Vector2(288, 126)
	C.player.face_left()
	_update_doorstop()


func _update_doorstop() -> void:
	# The pin is a sprite over the background; once Paul has it, hide it and its hotspot.
	var taken := Globals.pin_taken
	$Props/DoorstopPin.visible = not taken
	$Hotspots/Doorstop.visible = not taken
	$Hotspots/Doorstop.clickable = not taken


func _on_room_transition_finished() -> void:
	if state.visited_first_time:
		await C.Landlord.say("Evening! Welcome to the Cross House.")


func _on_room_exited() -> void:
	Globals.last_room = "CrossHouseTavern"


func _on_restore_from_savegame() -> void:
	_update_doorstop()
