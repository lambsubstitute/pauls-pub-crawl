@tool
extends PopochiuHotspot
## The pool table's wedge, on the hearth rug where Ursula was lying (Props/WedgeProp). Only
## shown once she's moved.


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("A chunky oak wedge. Someone's carved TABLE on it. Someone else has chewed it.")


func on_pick_up() -> void:
	await C.player.walk_to_clicked()
	C.player.face_up()
	await C.player.say("A bit warm and a bit doggy. That'll level a pool table.")
	Globals.wedge_taken = true
	I.Wedge.add()
	R.current.update_props()


func on_use() -> void:
	await on_pick_up()
