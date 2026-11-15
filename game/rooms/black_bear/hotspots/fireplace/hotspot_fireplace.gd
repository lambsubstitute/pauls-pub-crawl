@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("An inglenook you could park a car in, with a beam over it like a ship's keel.")
	if not Globals.ursula_moved:
		await C.player.say("There's a big black rug in front of it. The rug is snoring.")


func on_use() -> void:
	await C.player.say("Lovely and warm. Ursula's got the best spot in the house.")


func on_pick_up() -> void:
	await C.player.say("Ow. No.")


func _on_item_used(_item: PopochiuInventoryItem) -> void:
	await C.player.say("I'm not burning that.")
