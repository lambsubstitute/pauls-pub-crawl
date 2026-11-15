@tool
extends PopochiuHotspot
## A riverside bench. Sitting down watches the river (and, after the ending, rolls the credits
## again).


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("A bench with a little brass plaque: 'For everyone who loves this river.'")


func on_use() -> void:
	await C.player.walk_to_clicked()
	C.player.face_up()
	await C.player.say("I'll sit for a minute and watch the river go by.")
	if Globals.ending_seen:
		await R.current.roll_credits()
	else:
		await C.player.say("...Lovely. Right, onwards.")
