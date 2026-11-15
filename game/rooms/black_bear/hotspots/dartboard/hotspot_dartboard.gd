@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("A dartboard in an old oak cabinet. It hangs a bit low: the floor's come up to meet it.")


func on_use() -> void:
	await C.player.walk_to_clicked()
	C.player.face_up()
	await R.current.play_match()


func on_pick_up() -> void:
	await C.player.say("Bernie would have something to say about that.")


func _on_item_used(_item: PopochiuInventoryItem) -> void:
	await C.player.say("You throw darts at it. Not that.")
