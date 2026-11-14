@tool
extends PixelActor
## Clive, landlord of the Berkeley Arms. Stamps the card once Paul has beaten Dot at darts.

const Data := preload('character_clive_state.gd')
## Where Paul stands to talk to Clive: in front of the bar, just right of him
## (art/renders/berkeley_arms.json). Explicit, because walking to a character's feet hits their
## navigation obstacle and never finishes.
const TALK_SPOT := Vector2(35, 125)

var state: Data = load("res://game/characters/clive/character_clive.tres")


func _on_room_set() -> void:
	pass


func _on_click() -> void:
	E.command_fallback()


func on_walk_to() -> void:
	await _walk_up()


func _walk_up() -> void:
	await C.player.walk_to(TALK_SPOT)
	C.player.face_left()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("Clive, the landlord. Ginger beard, permanently ducking.")


func on_talk_to() -> void:
	await _walk_up()
	if Globals.stamps >= 3:
		await C.Clive.say("Britannia's next, up High Street from the Cross. Mind the step.")
		return
	if Globals.darts_won:
		if Globals.stamps < 2:
			await C.Clive.say("You beat Dot? Well done! But crawl rules, mate: Cross House and Hop Pole stamps first.")
			await C.Clive.say("Get those and come back. Your win's chalked up, it's not going anywhere.")
			return
		await C.Clive.say("You beat Dot? Our Dot?")
		await C.Clive.say("*STAMP*  Three down, three to go. Have a glass of water on the house.")
		Globals.stamps = 3
		Globals.sober(25)
		return
	await C.player.say("Evening! Stamp for my crawl card?")
	await C.Clive.say("Beat Dot at darts and it's yours. Nobody has since 1983.")
	if Globals.darts_given:
		await C.Clive.say("Steady hand, mind. Water's on the end of the bar if the room's moving.")
		return
	if Globals.darts_down:
		await C.Clive.say("You've got the house darts? Give them to Dot, she'll play you.")
		return
	await C.Clive.say("Trouble is, the house darts are stuck in the beam over the oche.")
	await C.Clive.say("Big Steve threw his arms up for a hundred and eighty. Forgot he was holding them.")
	await C.player.say("Can't you get them down?")
	await C.Clive.say("Not with my back. And nobody stands on my furniture.")
	await C.Clive.say("Last time they came down on their own, a fella'd had a couple and wobbled into that post.")
	await C.Clive.say("Whole ceiling shook. Pumps are on, mind. Crawlers drink on the house.")


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.CrawlCard:
		await on_talk_to()
	elif item == I.Darts:
		await _walk_up()
		await C.Clive.say("Not me, mate. Give them to Dot, she's the one to beat.")
	elif item == I.Pint:
		await _walk_up()
		await C.Clive.say("You hang on to that, mate. Free halves here anyway.")
	else:
		await C.Clive.say("No thanks, mate.")
