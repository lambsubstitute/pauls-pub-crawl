@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("Tewkesbury Abbey. Nine hundred years old.")
	await C.player.say("Older than the carpet in the Black Bear. Just.")


func on_pick_up() -> void:
	await C.player.say("I'd need a much bigger pocket.")


func on_talk_to() -> void:
	await C.player.say("Evening, Abbey.")
	await C.player.say("...It's the strong silent type.")
