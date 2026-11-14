@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	if Globals.darts_won:
		await C.player.say("Someone's rubbed out DOT and chalked PAUL. It was me.")
	else:
		await C.player.say("A chalk scoreboard. 'DOT 70', and underlined twice.")


func on_use() -> void:
	await C.player.say("I'll write my name on it when I've earned it.")


func on_pick_up() -> void:
	await on_use()
