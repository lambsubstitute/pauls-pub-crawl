@tool
extends PixelActor

const Data := preload('character_barmaid_state.gd')

var state: Data = load("res://game/characters/barmaid/character_barmaid.tres")


func _on_room_set() -> void:
	pass


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("The barmaid. Her badge says BEV.")


func on_talk_to() -> void:
	await C.player.walk_to(Vector2(47, 124))
	await C.player.face_left()
	if Globals.stamps == 0:
		await C.player.say("Evening! Can I get a stamp on my crawl card?")
		await C.Barmaid.say("Cross House first, love. Crawl rules. They're just down the road.")
		return
	if Globals.stamps >= 2:
		await C.Barmaid.say("Berkeley Arms next, love. Down by the Cross.")
		return
	if Globals.skittles_won:
		await C.Barmaid.say("You beat Reg? Our Reg?")
		await C.Barmaid.say("*STAMP*  Two down. And this one's on the house.")
		Globals.stamps = 2
		if not Globals.hop_pole_pint:
			Globals.hop_pole_pint = true
			I.Pint.add()
		return
	await C.player.say("Evening! Stamp for my crawl card?")
	await C.Barmaid.say("Beat Reg at skittles and it's yours. Nobody's beaten him since 1987.")
	await C.player.say("How hard can it be?")
	if not Globals.pin_returned:
		await C.Barmaid.say("Mind, the alley's been a pin short for years.")


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.CrawlCard:
		await on_talk_to()
	elif item == I.SkittlePin:
		await C.Barmaid.say("That's Reg's business, love, not mine.")
	else:
		await C.Barmaid.say("No thanks, love.")
