@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("A long mahogany bar with a brass foot rail. You could see your face in it. I'd rather not.")


func on_use() -> void:
	await C.player.say("Best ask Gwen. Or help myself to the water jug on the end.")
