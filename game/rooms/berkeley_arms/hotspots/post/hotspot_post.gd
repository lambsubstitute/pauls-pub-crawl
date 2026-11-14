@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("A huge oak post holding up the main beam. Covered in horse brasses.")
	if not Globals.darts_down:
		await C.player.say("That beam runs right over the dartboard.")


func on_push() -> void:
	await _lean()


func on_use() -> void:
	await _lean()


func on_pull() -> void:
	await C.player.say("It's holding the ceiling up. I'd rather it carried on.")


func on_pick_up() -> void:
	await C.player.say("It's six hundred years old and nailed to the building.")


func _lean() -> void:
	await C.player.walk_to_clicked()
	C.player.face_right()
	if Globals.darts_down:
		await C.player.say("It's done its bit for tonight.")
		return
	if Globals.drunk < Globals.WOBBLY:
		await C.player.say("*push*  Solid oak. Not budging. Not for a steady fella like me, anyway.")
		return
	await R.current.knock_darts_down()


func _on_item_used(_item: PopochiuInventoryItem) -> void:
	await C.player.say("I'm not carving my name in it.")
