@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("A shove ha'penny board: polished mahogany, nine beds between brass lines.")
	await C.player.say("Shove a coin with the heel of your hand. Clean in a bed scores the bed's number.")
	if not Globals.halfpenny_given:
		await C.player.say("Only four ha'pennies on it, though.")


func on_use() -> void:
	await _play()


func on_push() -> void:
	await _play()


func on_pick_up() -> void:
	await C.player.say("Stan would have my hand off. It's his board in all but name.")


func _play() -> void:
	await C.player.walk_to_clicked()
	C.player.face_up()
	await R.current.play_shove()


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.Halfpenny:
		await C.Stan._on_item_used(item)
	elif item == I.Coin:
		await C.player.say("A pound coin's too big and too modern. It has to be a ha'penny.")
	else:
		await C.player.say("That's not a ha'penny.")
