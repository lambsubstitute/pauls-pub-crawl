@tool
extends PopochiuHotspot
## Back into town, off the left-hand edge. Always open. HighSt spawns Paul at its Mythe end (the
## room sets Globals.last_room = "MytheBridge").

const EDGE := Vector2(8, 133)


func _on_click() -> void:
	E.command_fallback()


func _on_double_click() -> void:
	R.goto_room("HighSt")


func on_look_at() -> void:
	await C.player.say("The path back into town, past the Black Bear to High Street.")


func on_walk_to() -> void:
	await _leave()


func on_use() -> void:
	await _leave()


func _leave() -> void:
	await C.player.walk_to(EDGE)
	R.goto_room("HighSt")
