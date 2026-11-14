@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("'Sir Humphrey Hopwood, founder.' He looks like he's smelt something.")


func on_talk_to() -> void:
	await C.player.say("Evening, Sir Humphrey.")
	await C.player.say("...Tough crowd.")


func on_pick_up() -> void:
	await C.player.say("Bev's watching. And he's heavier than he looks.")
