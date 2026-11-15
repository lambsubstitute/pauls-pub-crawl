@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("High Street in the drizzle. Up towards the Mythe, the Black Bear's lights are on.")


func on_open() -> void:
	await C.player.say("It's November. Gwen's got the heating on. Best not.")
