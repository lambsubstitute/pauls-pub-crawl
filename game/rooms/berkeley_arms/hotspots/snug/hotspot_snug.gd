@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("The Snug: the Berkeley's other bar. About the size of my front room.")


func on_open() -> void:
	await _peek()


func on_use() -> void:
	await _peek()


func on_walk_to() -> void:
	await _peek()


func _peek() -> void:
	await C.player.walk_to_clicked()
	await C.player.say("It's full of a quiz team arguing about the capital of Australia.")
	await C.player.say("I'll leave them to it.")
