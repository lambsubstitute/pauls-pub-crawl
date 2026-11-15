@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("A fingerpost. 'SEVERN WAY'. And pointing back: 'TEWKESBURY, HIGH STREET'.")


func on_use() -> void:
	await C.player.say("It says the town's back that way. Off to the left.")
