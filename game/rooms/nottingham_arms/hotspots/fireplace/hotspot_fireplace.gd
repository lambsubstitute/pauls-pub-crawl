@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("A little cast-iron fireplace with green tiles. Norman's spot is right beside it.")


func on_use() -> void:
	await C.player.say("Lovely and warm. Norman's got the best seat in the house.")


func on_pick_up() -> void:
	await C.player.say("Ow. No.")
