@tool
extends PopochiuHotspot
## Ye Olde Black Bear, 68 High St, at the Mythe end (the finale). Coming back out, HighSt spawns
## Paul at from_black_bear (the room sets Globals.last_room = "BlackBear").


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("Ye Olde Black Bear. Thirteen hundred and something, and not a straight line in it.")
	if Globals.stamps < 6:
		await C.player.say("Last orders there, and the champion. Full card first.")
	else:
		await C.player.say("Where I became champion. They'll be talking about it for weeks.")


func on_open() -> void:
	await _go_in()


func on_use() -> void:
	await _go_in()


func on_walk_to() -> void:
	await _go_in()


func _go_in() -> void:
	await C.player.walk_to_clicked()
	if Globals.stamps < 5:
		await C.player.say("Five stamps first, then the champion... but a quick look won't hurt.")
	R.goto_room("BlackBear")
