@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func _on_double_click() -> void:
	R.goto_room("CrossHouseTavern")


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("The Cross House Tavern. Stop number one.")


func on_open() -> void:
	await _go_in()


func on_use() -> void:
	await _go_in()


func on_walk_to() -> void:
	await _go_in()


func _go_in() -> void:
	await C.player.walk_to_clicked()
	R.goto_room("CrossHouseTavern")
