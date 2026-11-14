@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("A skittle pin, propping the door open. Number nine, it says on the bottom.")


func on_pick_up() -> void:
	await C.player.walk_to_clicked()
	await C.player.face_clicked()
	await C.Landlord.say("Oi! That's my doorstop!")
	await C.player.say("It's a skittle pin.")
	await C.Landlord.say("...Fair enough. Borrowed it off the Hop Pole years back. Reg'll want it home.")
	Globals.pin_taken = true
	I.SkittlePin.add()
	R.current._update_doorstop()


func on_push() -> void:
	await C.player.say("It's doing a fine job. For now.")


func on_pull() -> void:
	await on_pick_up()
