@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("Three handpumps: Britannia Best, Trident and Ruler of the Waves.")


func on_use() -> void:
	await _half()


func on_pull() -> void:
	await _half()


func on_pick_up() -> void:
	await _half()


# Free halves, so getting merry never needs a pint Paul might not have; Gwen stops at 60
# (seeing double), and the water jug is always beside the pumps.
func _half() -> void:
	await C.player.walk_to_clicked()
	C.player.face_up()
	if Globals.drunk >= Globals.SEEING_DOUBLE:
		await C.Gwen.say("That's your lot for now, love. There's water on the end of the bar.")
		return
	if Globals.britannia_halves == 0:
		await C.Gwen.say("Half of Britannia Best? Crawlers drink on the house, love.")
	else:
		await C.Gwen.say("Another half? Go on then.")
	Globals.britannia_halves += 1
	await C.player.say("Cheers!")
	Globals.drink(15)
	if Globals.drunk >= Globals.SEEING_DOUBLE:
		await C.player.say("Whoa. There are two Gwens. And two of everything else.")
