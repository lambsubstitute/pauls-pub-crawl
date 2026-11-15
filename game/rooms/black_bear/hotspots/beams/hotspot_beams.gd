@tool
extends PopochiuHotspot
## The low, crooked beams, with a "mind your head" board by the door.


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("A board on the beam: 'MIND YOUR HEAD. DUCK OR GROUSE.'")
	await C.player.say("Every beam in here is crooked. They've had seven hundred years to settle.")


func on_push() -> void:
	await C.player.say("If I push it, the whole pub might fall down. It's probably only the beams holding it up.")


func on_pull() -> void:
	await on_push()


func on_use() -> void:
	await C.player.walk_to_clicked()
	C.player.face_up()
	await C.player.say("*BONK*  Ow. Right. Duck.")


func on_pick_up() -> void:
	await C.player.say("It's a load-bearing beam. I'd rather it kept bearing.")
