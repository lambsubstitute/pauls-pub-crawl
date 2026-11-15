@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func _on_double_click() -> void:
	R.goto_room("Britannia")


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("The Britannia Inn. Georgian, red brick, very proper. Number 30.")
	if Globals.stamps == 3:
		await C.player.say("Stop number four.")


func on_open() -> void:
	await _go_in()


func on_use() -> void:
	await _go_in()


func on_walk_to() -> void:
	await _go_in()


func _go_in() -> void:
	await C.player.walk_to_clicked()
	if Globals.stamps < 3:
		await C.player.say("Berkeley's stamp should come first... but a quick look won't hurt.")
	R.goto_room("Britannia")
