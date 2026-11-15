@tool
extends PopochiuHotspot
## The pool league chalkboard: a hint board for the cue hunt.


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	if Globals.pool_won:
		await C.player.say("'CHAMPION: GAZ' has a line through it. Someone's chalked 'PAUL (once)'.")
		return
	await C.player.say("POOL LEAGUE. Champion: GAZ, eleven seasons running.")
	if not Globals.cue_made and not Globals.cue_given:
		await C.player.say("Underneath: 'HOUSE CUE - top half: ask Norman. Bottom half: rack. DON'T LOSE THEM.'")


func on_use() -> void:
	await C.player.say("I'll put my name up when I've earned it.")


func on_pick_up() -> void:
	await on_use()
