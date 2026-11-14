@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func _on_double_click() -> void:
	R.goto_room("HopPole")


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("The Royal Hop Pole. Very posh. Stop number two.")


func on_open() -> void:
	await _go_in()


func on_use() -> void:
	await _go_in()


func on_walk_to() -> void:
	await _go_in()


func _go_in() -> void:
	await C.player.walk_to_clicked()
	if Globals.stamps == 0:
		await C.player.say("Should really start at the Cross House... but a quick look won't hurt.")
	R.goto_room("HopPole")
