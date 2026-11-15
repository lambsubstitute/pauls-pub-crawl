@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("The Severn, wide and black, with the moon broken up in it.")
	await C.player.say("The Avon joins it just downstream, past the Black Bear. Then it's all the way to the sea.")


func on_use() -> void:
	await C.player.say("I'm not going in. It's November, and I'm the champion.")


func on_pick_up() -> void:
	await C.player.say("You can't pick up a river. I've tried. Well, I haven't, but I can tell.")


func _on_item_used(_item: PopochiuInventoryItem) -> void:
	await C.player.say("I'm not throwing anything in the river. Mum would have words.")
