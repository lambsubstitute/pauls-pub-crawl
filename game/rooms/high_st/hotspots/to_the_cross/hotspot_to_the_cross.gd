@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func _on_double_click() -> void:
	R.goto_room("TheCross")


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("Back down to the Cross, the war memorial and the Berkeley Arms.")


func on_walk_to() -> void:
	await _go()


func on_use() -> void:
	await _go()


# Always lets Paul back to the Cross, whatever he has or hasn't done.
func _go() -> void:
	await C.player.walk_to_clicked()
	R.goto_room("TheCross")
