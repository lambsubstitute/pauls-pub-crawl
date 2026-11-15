@tool
extends PopochiuHotspot
## The cue's top half, leaning by Norman's chair (Props/CueShaftProp) until he swaps it.


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("The top half of a pool cue! Brass joint on the bottom, chalky blue tip.")
	await C.player.say("Norman pokes the jukebox buttons with it.")


func on_pick_up() -> void:
	await C.player.walk_to_clicked()
	if Globals.norman_laughed:
		await C.Norman.say("Steady, lad! That's my poker. Find me something longer and we'll swap.")
	else:
		await C.Norman.say("Oi! Hands off my jukebox poker.")


func on_use() -> void:
	await on_pick_up()


func on_pull() -> void:
	await on_pick_up()


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.PoolRest:
		await C.Norman._on_item_used(item)
	elif item == I.CueButt:
		await C.player.say("They'd screw together, but Norman would have my hands off. Better ask him.")
	else:
		await C.player.say("Better leave Norman's things alone.")
