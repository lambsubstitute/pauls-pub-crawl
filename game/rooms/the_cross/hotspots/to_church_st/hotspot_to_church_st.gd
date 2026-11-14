@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func _on_double_click() -> void:
	R.goto_room("ChurchSt")


func on_look_at() -> void:
	await C.player.say("Back down Church Street to the Hop Pole and the Cross House.")


func on_walk_to() -> void:
	await _go()


func on_use() -> void:
	await _go()


func _go() -> void:
	await C.player.walk_to_clicked()
	R.goto_room("ChurchSt")
