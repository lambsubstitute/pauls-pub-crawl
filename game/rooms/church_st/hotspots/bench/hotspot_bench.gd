@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	if Globals.found_coin:
		await C.player.say("A bench. Not sitting down yet - the night is young.")
	else:
		await C.player.say("A bench. Something's glinting underneath it...")


func on_pick_up() -> void:
	if Globals.found_coin:
		await C.player.say("It's bolted down. Probably for the best.")
		return
	await C.player.walk_to_clicked()
	await C.player.face_clicked()
	await C.player.say("A pound coin! Somebody's loss is Paul's gain.")
	Globals.found_coin = true
	I.Coin.add()


func on_use() -> void:
	await C.player.say("Not sitting down yet. The night is young.")


func _on_item_used(_item: PopochiuInventoryItem) -> void:
	await C.player.say("The bench doesn't need that.")
