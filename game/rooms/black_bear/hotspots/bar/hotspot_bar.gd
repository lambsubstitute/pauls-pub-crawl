@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("A black oak bar, worn smooth by seven hundred years of elbows. It slopes, like everything else.")


func on_use() -> void:
	await C.player.say("Rosie pulls the halves. Water jug's on the end, help yourself.")


func _on_item_used(_item: PopochiuInventoryItem) -> void:
	await C.player.say("I'll hang on to it.")
