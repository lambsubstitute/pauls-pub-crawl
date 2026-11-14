@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("Four hand pumps. A thing of beauty.")


func on_use() -> void:
	await C.player.say("Better ask the landlord, not help myself.")


func on_pick_up() -> void:
	await C.player.say("It's a bar. It's staying where it is.")
