@tool
extends PopochiuHotspot
## Free halves for crawlers, so Paul can always get merry here (only a merry Paul has the
## hiccups that wake Ursula). Rosie stops pouring at 60.


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("Three handpumps: Black Bear Bitter, Mythe Mild and Old Ursula, a very dark stout.")


func on_use() -> void:
	await _half()


func on_pull() -> void:
	await _half()


func on_pick_up() -> void:
	await _half()


func _half() -> void:
	await C.player.walk_to_clicked()
	C.player.face_up()
	if Globals.drunk >= Globals.SEEING_DOUBLE:
		await C.Rosie.say("That's your lot for now, love. Water's on the end of the bar.")
		return
	if Globals.black_bear_halves == 0:
		await C.Rosie.say("Half of Black Bear Bitter? Crawlers drink on the house.")
	else:
		await C.Rosie.say("Another half? Go on then, love.")
	Globals.black_bear_halves += 1
	var had := Globals.has_hiccups()
	await C.player.say("Cheers!")
	Globals.drink(15)
	if Globals.has_hiccups() and not had:
		await C.player.say("*HIC!* Oh no. Hiccups. I always get them after a couple of halves.")
