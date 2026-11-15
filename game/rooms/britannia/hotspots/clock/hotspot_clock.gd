@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("A long-case clock. Mahogany, brass face, and a tick like a slow heartbeat.")
	if Globals.magic_eye_seen and not Globals.halfpenny_found:
		await C.player.say("The clock from the Magic Eye! The ha'penny was in its trunk.")


func on_open() -> void:
	await _search()


func on_use() -> void:
	await _search()


func on_pick_up() -> void:
	await _search()


func on_pull() -> void:
	await C.player.say("Pulling the weights would stop it. Gwen would give me a look.")


func _search() -> void:
	await C.player.walk_to_clicked()
	C.player.face_up()
	await R.current.search_clock()


func _on_item_used(_item: PopochiuInventoryItem) -> void:
	await C.player.say("It doesn't need winding with that.")
