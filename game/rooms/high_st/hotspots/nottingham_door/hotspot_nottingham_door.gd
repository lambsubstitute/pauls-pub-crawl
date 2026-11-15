@tool
extends PopochiuHotspot
## Nottingham Arms, 129 High St (stop 5). Coming back out, HighSt spawns Paul at from_nottingham
## (the room sets Globals.last_room = "NottinghamArms").


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
	if Globals.stamps < 4:
		await C.player.say("Britannia's stamp should come first... but a quick look won't hurt.")
	R.goto_room("NottinghamArms")
