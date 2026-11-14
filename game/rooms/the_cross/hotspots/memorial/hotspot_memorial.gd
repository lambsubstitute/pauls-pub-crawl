@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("Tewkesbury's war memorial, right where the three streets meet.")
	await C.player.say("Somebody's laid fresh poppies on the steps.")


func on_pick_up() -> void:
	await C.player.say("Certainly not.")


func on_talk_to() -> void:
	await C.player.face_clicked()
	await C.player.say("...")
	await C.player.say("Some things you just stand quietly by for a moment.")
