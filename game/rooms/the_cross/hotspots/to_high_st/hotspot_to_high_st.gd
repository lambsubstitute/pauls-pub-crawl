@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("High Street, running up to the Mythe. The Britannia's up there, and the Black Bear.")


func on_walk_to() -> void:
	await _go()


func on_use() -> void:
	await _go()


func _go() -> void:
	await C.player.walk_to_clicked()
	if Globals.stamps < 3:
		await C.player.say("Berkeley Arms first. Crawl rules.")
		return
	await C.player.say("Up High Street to the Britannia...")
	await C.player.say("...is a walk for another night. (The rest of the crawl is still being built!)")
