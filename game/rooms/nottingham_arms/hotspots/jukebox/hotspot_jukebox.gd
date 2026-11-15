@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("A glowing old jukebox. Set to free play since the coin slot jammed.")
	if not Globals.shaft_swapped:
		await C.player.say("The buttons are dented. Norman pokes them from his spot with half a pool cue.")


func on_use() -> void:
	await C.player.walk_to_clicked()
	C.player.face_up()
	await C.player.say("Ooh, what's on...")
	await C.Norman.say("Oi! Number seven or nothing, lad. I'm in charge of the jukebox.")


func on_push() -> void:
	await on_use()


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.PoolRest or item == I.CueShaft:
		await C.Norman.say("Leave my jukebox be, lad.")
	else:
		await C.player.say("It's on free play anyway.")
