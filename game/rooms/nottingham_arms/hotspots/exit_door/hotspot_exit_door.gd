@tool
extends PopochiuHotspot
## Out to High Street. Always works, whatever Paul has or hasn't done in here. Falls back to the
## Cross while the HighSt room (pub-4 branch) isn't in the project.

const Room := preload("res://game/rooms/nottingham_arms/room_nottingham_arms.gd")


func _on_click() -> void:
	E.command_fallback()


func _on_double_click() -> void:
	R.goto_room(Room.street_room())


func on_look_at() -> void:
	await C.player.say("The front door, back out to High Street.")


func on_open() -> void:
	await _leave()


func on_use() -> void:
	await _leave()


func on_walk_to() -> void:
	await _leave()


func _leave() -> void:
	await C.player.walk_to_clicked()
	R.goto_room(Room.street_room())
