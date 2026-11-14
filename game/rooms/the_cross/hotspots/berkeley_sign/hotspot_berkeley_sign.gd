@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("The Berkeley family arms. Red shield, white chevron, ten little crosses.")
	await C.player.say("I can count six. The rest must be in the Snug.")


func on_pick_up() -> void:
	await C.player.say("It's bolted on. They've met people like me before.")


func on_talk_to() -> void:
	await C.player.say("Evening, sign. ...Swinging, not talking.")
