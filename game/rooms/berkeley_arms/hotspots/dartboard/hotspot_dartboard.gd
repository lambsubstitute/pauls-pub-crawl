@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("A proper bristle board in an oak cabinet. The treble twenty's worn shiny.")
	if not Globals.darts_down:
		await C.player.say("No darts anywhere, though. Odd, for a darts pub.")


func on_use() -> void:
	await C.player.walk_to_clicked()
	if Globals.darts_given:
		await R.current.play_darts()
	elif I.is_item_in_inventory("Darts"):
		await C.player.say("Dot's the one to play. I'll give her the darts.")
	else:
		await C.player.say("With what? My fingers?")


func on_pick_up() -> void:
	await C.player.say("Dot would have my hands off.")


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.Darts:
		await C.player.say("Better give them to Dot. It's her board, really.")
	else:
		await C.player.say("That won't stick.")
