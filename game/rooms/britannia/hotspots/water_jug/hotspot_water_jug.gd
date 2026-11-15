@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("A jug of tap water and some glasses. Free, and very sensible.")


func on_use() -> void:
	await _drink()


func on_pick_up() -> void:
	await _drink()


func _drink() -> void:
	await C.player.walk_to_clicked()
	C.player.face_up()
	if Globals.drunk == 0:
		await C.player.say("I'm as sober as a judge. Well, a magistrate.")
		return
	await C.player.say("Glug, glug, glug...")
	Globals.sober(25)
	await C.player.say("Ahh. Clearer already." if Globals.drunk > 0 else "Ahh. Steady as a rock.")
