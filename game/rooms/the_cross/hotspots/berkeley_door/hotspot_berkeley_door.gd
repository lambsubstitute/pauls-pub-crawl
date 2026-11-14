@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func _on_double_click() -> void:
	R.goto_room("BerkeleyArms")


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("The Berkeley Arms. Fifteenth century, and leaning a bit. Like me, later.")
	if Globals.stamps == 2:
		await C.player.say("Stop number three.")


func on_open() -> void:
	await _go_in()


func on_use() -> void:
	await _go_in()


func on_walk_to() -> void:
	await _go_in()


func _go_in() -> void:
	await C.player.walk_to_clicked()
	if Globals.stamps < 2:
		await C.player.say("Hop Pole's stamp should come first... but a quick look won't hurt.")
	R.goto_room("BerkeleyArms")
