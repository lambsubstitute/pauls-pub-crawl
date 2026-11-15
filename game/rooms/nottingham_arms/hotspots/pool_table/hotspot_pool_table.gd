@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("A proper pub pool table. Green baize, worn pale round the pockets.")
	if not Globals.cue_given:
		await C.player.say("Balls are all out, but there's no house cue to play with.")


func on_use() -> void:
	await C.player.walk_to_clicked()
	if Globals.cue_given:
		await R.current.play_pool()
	elif I.is_item_in_inventory("HouseCue"):
		await C.player.say("I'll give the cue to Gaz. It's his table, really.")
	elif I.is_item_in_inventory("CueButt") or I.is_item_in_inventory("CueShaft"):
		await C.player.say("With half a cue? Gaz would laugh me out of the pub.")
	else:
		await C.player.say("With what? My finger?")


func on_push() -> void:
	await C.player.say("Weighs about as much as a car. And Gaz is watching.")


func on_pick_up() -> void:
	await on_push()


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.HouseCue:
		await C.Gaz._on_item_used(item)
	else:
		await on_use()
