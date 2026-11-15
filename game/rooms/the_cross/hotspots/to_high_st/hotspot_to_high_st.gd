@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func _on_double_click() -> void:
	R.goto_room("HighSt")


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("High Street, running up to the Mythe. The Britannia's up there, and the Black Bear.")


func on_walk_to() -> void:
	await _go()


func on_use() -> void:
	await _go()


# Always open: a pub done out of order is remembered and stamped when its turn comes.
func _go() -> void:
	await C.player.walk_to_clicked()
	if Globals.stamps < 3:
		await C.player.say("Berkeley Arms should come first... but a stroll up High Street won't hurt.")
	R.goto_room("HighSt")
