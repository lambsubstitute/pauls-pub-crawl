@tool
extends PixelActor

const Data := preload('character_landlord_state.gd')

var state: Data = load("res://game/characters/landlord/character_landlord.tres")


func _on_room_set() -> void:
	pass


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("The landlord. Beard you could lose a darts flight in.")


func on_talk_to() -> void:
	await C.player.walk_to(Vector2(226, 124))
	await C.player.face_up()
	if Globals.stamps > 0:
		await C.Landlord.say("Royal Hop Pole's next, just up Church Street.")
		return
	if not Globals.had_free_pint:
		await C.player.say("Evening! I'm on a pub crawl.")
		await C.Landlord.say("Crawl card, is it? First pint's on the house.")
		Globals.had_free_pint = true
		I.Pint.add()
	if Globals.quiz_won:
		await C.Landlord.say("Quiz champion! Give us that card.")
		await C.Landlord.say("*STAMP*  One down, five to go.")
		Globals.stamps = 1
	else:
		await C.Landlord.say("Beat the quiz machine and I'll stamp your card.")
		await C.player.say("How hard can it be?")
		if not I.is_item_in_inventory("Coin") and not Globals.found_coin:
			await C.player.say("...Don't suppose you'd lend me a pound for it?")
			await C.Landlord.say("Ha! Have a look outside. Folk drop change by that bench all night.")


func on_give() -> void:
	await C.player.say("Give him what?")


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.CrawlCard:
		await on_talk_to()
	elif item == I.Coin:
		await C.Landlord.say("Keep it for the quiz machine, mate.")
	else:
		await C.Landlord.say("No thanks.")
