@tool
extends PopochiuHotspot
## The pool table, leaning with the floor until the wedge goes under its short leg.


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	if Globals.table_level:
		await C.player.say("Level at last, with the wedge under its short leg. The balls stay where you put them.")
		return
	await C.player.say("It leans like the rest of the pub. Every ball has rolled down to the river end.")
	await C.player.say("The right-hand leg is short. It needs something wedged under it.")


func on_use() -> void:
	await C.player.walk_to_clicked()
	if not Globals.table_level and I.is_item_in_inventory("Wedge"):
		await R.current.level_table()
		return
	await R.current.play_match()


func on_push() -> void:
	await C.player.say("Weighs about as much as a car. And it'd only roll downhill.")


func on_pick_up() -> void:
	await on_push()


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.Wedge:
		await R.current.level_table()
	else:
		await C.player.say("That won't help it stand straight.")
