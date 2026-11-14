@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("A low oak bar, polished by six hundred years of elbows.")


func on_use() -> void:
	await C.player.say("Best ask Clive. Or help myself to the water jug on the end.")
