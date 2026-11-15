@tool
extends PopochiuHotspot
## Free halves for crawlers, so Paul can always get merry here (Norman only warms to a merry
## Paul). Jackie stops pouring at 60.


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("Three handpumps: Nottingham Gold, High Street Best and Severn Ham Stout.")


func on_use() -> void:
	await _half()


func on_pull() -> void:
	await _half()


func on_pick_up() -> void:
	await _half()


func _half() -> void:
	await C.player.walk_to_clicked()
	C.player.face_up()
	if Globals.drunk >= 60:
		await C.Jackie.say("That's your lot for now, love. Water's on the end of the bar.")
		return
	if Globals.nottingham_halves == 0:
		await C.Jackie.say("Half of Nottingham Gold? Crawlers drink on the house.")
	else:
		await C.Jackie.say("Another half? Go on then, love.")
	Globals.nottingham_halves += 1
	await C.player.say("Cheers!")
	Globals.drink(15)
	if Globals.drunk >= Globals.WOBBLY and not Globals.norman_laughed:
		await C.player.say("Ooh. Everything's a bit funnier than it was.")
