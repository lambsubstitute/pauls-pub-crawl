@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("Britannia, with her shield and her trident. Ruling the waves, two hundred miles from the sea.")


func on_pick_up() -> void:
	await C.player.say("It's bolted to the wall, and Britannia looks like she'd fight back.")


func _on_item_used(_item: PopochiuInventoryItem) -> void:
	await C.player.say("Can't reach it. And why would I?")
