@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func _on_double_click() -> void:
	R.goto_room("ChurchSt")


func on_look_at() -> void:
	await C.player.say("Back out to Church Street.")


func on_open() -> void:
	await _leave()


func on_use() -> void:
	await _leave()


func on_walk_to() -> void:
	await _leave()


func _leave() -> void:
	await C.player.walk_to_clicked()
	# Never block the exit: the coin for the quiz machine is outside, so blocking here softlocks.
	if Globals.stamps == 0 and not Globals.quiz_won:
		await C.player.say("I'll be back for that stamp.")
	R.goto_room("ChurchSt")
