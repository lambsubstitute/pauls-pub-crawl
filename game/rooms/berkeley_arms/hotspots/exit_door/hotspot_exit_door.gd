@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func _on_double_click() -> void:
	R.goto_room("TheCross")


func on_look_at() -> void:
	await C.player.say("The front door, back out to the Cross. Mind the step. And the beam.")


func on_open() -> void:
	await _leave()


func on_use() -> void:
	await _leave()


func on_walk_to() -> void:
	await _leave()


# Always lets Paul out, whatever he has or hasn't done in here.
func _leave() -> void:
	await C.player.walk_to_clicked()
	R.goto_room("TheCross")
