@tool
extends PopochiuHotspot
## Only exists in Paul's double vision (drunk 60+): the room script shows this hotspot and the
## Props/GhostPicture sprite together. In the ghost copy of the Magic Eye, the hidden picture
## shows: a long-case clock with a ha'penny in its trunk.


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.walk_to_clicked()
	C.player.face_up()
	await C.player.say("The ghost picture! With my eyes out of step the dots slide apart and...")
	await C.player.say("It's a grandfather clock! And in its trunk, a little round coin. A ha'penny!")
	if not Globals.magic_eye_seen:
		Globals.magic_eye_seen = true
		await C.player.say("Ernie hid the fifth ha'penny in the clock! I must remember that. Clock. Ha'penny. Clock.")


func on_use() -> void:
	await on_look_at()


func on_pick_up() -> void:
	await C.player.say("My hand went straight through it. It's only in my eyes.")


func _on_item_used(_item: PopochiuInventoryItem) -> void:
	await C.player.say("It's not really there, you know.")
