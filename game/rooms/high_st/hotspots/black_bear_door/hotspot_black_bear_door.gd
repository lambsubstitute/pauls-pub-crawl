@tool
extends PopochiuHotspot
## Ye Olde Black Bear, 68 High St, at the Mythe end (the finale). Stub until its room is built;
## HighSt already has its spawn (last_room "BlackBear").


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("Ye Olde Black Bear. Thirteen hundred and something, and not a straight line in it.")
	await C.player.say("Last orders there, and the champion. Full card first.")


func on_open() -> void:
	await _go_in()


func on_use() -> void:
	await _go_in()


func on_walk_to() -> void:
	await _go_in()


func _go_in() -> void:
	await C.player.walk_to_clicked()
	await C.player.say("Not yet - one pub at a time.")
