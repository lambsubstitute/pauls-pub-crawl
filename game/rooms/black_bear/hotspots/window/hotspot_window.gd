@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("A little leaded window. The River Avon slides past right underneath, black and shiny.")
	await C.player.say("Up the road, the Mythe bridge crosses the Severn. Lovely walk on a clear night.")


func on_open() -> void:
	await C.player.say("Painted shut. Some time around 1700, by the look of it.")


func on_use() -> void:
	await on_open()
