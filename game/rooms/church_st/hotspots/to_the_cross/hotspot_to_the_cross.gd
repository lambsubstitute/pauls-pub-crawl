@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func _on_double_click() -> void:
	R.goto_room("TheCross")


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("The fingerpost says 'The Cross'. Church Street runs on to it, past the Hop Pole.")


func on_walk_to() -> void:
	await _go()


func on_use() -> void:
	await _go()


func _go() -> void:
	await C.player.walk_to_clicked()
	R.goto_room("TheCross")
