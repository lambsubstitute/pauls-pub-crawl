@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("Three handpumps. Berkeley Bitter, Old Abbey and something called Mythe Mild.")


func on_use() -> void:
	await _half()


func on_pull() -> void:
	await _half()


func on_pick_up() -> void:
	await _half()


func _half() -> void:
	await C.player.walk_to_clicked()
	C.player.face_up()
	if Globals.drunk >= 60:
		await C.Clive.say("I think you've had plenty, mate. There's water on the end of the bar.")
		return
	if Globals.berkeley_halves == 0:
		await C.Clive.say("Half of Berkeley Bitter? Crawlers drink on the house here.")
	else:
		await C.Clive.say("Another half? Go on then.")
	Globals.berkeley_halves += 1
	await C.player.say("Cheers!")
	Globals.drink(15)
	if Globals.drunk >= 30 and not Globals.darts_down:
		await C.player.say("Ooh. The room's gone a bit swimmy.")
