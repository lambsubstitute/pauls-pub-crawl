@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	if Globals.pin_returned:
		await C.player.say("Skittle alley. Nine pins in a diamond, and a ball the size of a cheese.")
	else:
		await C.player.say("Skittle alley. One, two... eight pins. There's a gap where number nine should be.")


func on_use() -> void:
	await C.player.walk_to_clicked()
	await R.current.play_skittles()


func on_pick_up() -> void:
	await C.player.say("Reg would have my hands off.")


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.SkittlePin:
		await C.Reg.say("Oi, give that here. That's mine to put back.")
	else:
		await C.player.say("That won't help my game.")
