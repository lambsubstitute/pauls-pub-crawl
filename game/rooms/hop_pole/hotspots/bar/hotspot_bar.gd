@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("Five brass pumps and a mirror you could do your hair in.")


func on_use() -> void:
	await C.player.say("Best ask Bev.")
