@tool
extends PopochiuHotspot
## Out to High Street. Always works, whatever Paul has or hasn't done in here; HighSt spawns him
## at from_black_bear (the room sets Globals.last_room = "BlackBear").


func _on_click() -> void:
	E.command_fallback()


func _on_double_click() -> void:
	R.goto_room("HighSt")


func on_look_at() -> void:
	await C.player.say("The front door, back out to High Street. It's about four foot six.")


func on_open() -> void:
	await _leave()


func on_use() -> void:
	await _leave()


func on_walk_to() -> void:
	await _leave()


func _leave() -> void:
	await C.player.walk_to_clicked()
	R.goto_room("HighSt")
