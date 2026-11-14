@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("An inglenook. You could park a Mini in there.")


func on_use() -> void:
	await C.player.say("I'm warm enough, ta. That's the beer.")


func on_pick_up() -> void:
	await C.player.say("Ow. No.")
