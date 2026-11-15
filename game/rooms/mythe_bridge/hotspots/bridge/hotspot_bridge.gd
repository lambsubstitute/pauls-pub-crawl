@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("The Mythe bridge. Thomas Telford built it in 1826: one cast-iron arch, a hundred and seventy feet.")
	await C.player.say("All that lacy ironwork, and it's still carrying lorries to Ledbury two hundred years later.")


func on_use() -> void:
	await C.player.say("I'll admire it from down here. It's prettier from the side.")


func on_walk_to() -> void:
	await C.player.walk_to_clicked()
