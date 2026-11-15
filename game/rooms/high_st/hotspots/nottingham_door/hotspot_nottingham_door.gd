@tool
extends PopochiuHotspot
## Nottingham Arms, 129 High St (stop 5). Stub until its room is built: then send Paul in with
## R.goto_room("NottinghamArms"); HighSt already has its spawn (last_room "NottinghamArms").


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("The Nottingham Arms. Black and white, leaning on its neighbours. There's a pool table in there, I'm told.")


func on_open() -> void:
	await _go_in()


func on_use() -> void:
	await _go_in()


func on_walk_to() -> void:
	await _go_in()


func _go_in() -> void:
	await C.player.walk_to_clicked()
	await C.player.say("Not yet - one pub at a time.")
