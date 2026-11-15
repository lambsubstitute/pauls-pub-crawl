@tool
extends PixelActor
## Bernie "the Bear": champion of Ye Olde Black Bear at darts and pool since 1999. A big, gentle
## man in a black darts shirt. Only plays someone holding a full crawl card (5 stamps), and only
## on a level table.

const Data := preload('character_bernie_state.gd')
## Where Paul stands to talk to Bernie: just left of him, in front of the dartboard.
const TALK_SPOT := Vector2(252, 127)

var state: Data = load("res://game/characters/bernie/character_bernie.tres")


func _on_room_set() -> void:
	pass


func _on_click() -> void:
	E.command_fallback()


func on_walk_to() -> void:
	await _walk_up()


func _walk_up() -> void:
	await C.player.walk_to(TALK_SPOT)
	C.player.face_right()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("Bernie 'the Bear'. Built like a wardrobe, beard like a hedge, gentle as a lamb.")
	await C.player.say("Darts AND pool champion of the Black Bear since 1999.")


func on_talk_to() -> void:
	await _walk_up()
	if Globals.finale_won:
		await C.Bernie.say("Champion! Mind how you go on the way home, lad.")
		return
	if not Globals.bernie_met:
		Globals.bernie_met = true
		await C.player.say("Evening! I'm doing the Tewkesbury pub crawl. Fancy a game?")
		await C.Bernie.say("A crawler, eh? Black Bear rules: I play anyone with a full card, for the last stamp.")
		await C.Bernie.say("The Black Bear double. A leg of darts, a leg of pool, and a decider if we need one.")
	if Globals.stamps < 5:
		await C.Bernie.say("You've got %d stamp%s, lad. Come back with five." % [Globals.stamps, "" if Globals.stamps == 1 else "s"])
		if not Globals.table_level:
			await C.Bernie.say("And find the table wedge while you're at it. That table leans worse than me.")
		return
	if not Globals.table_level:
		await C.Bernie.say("A full card! Right then. Only, I'm not playing pool on a table that leans.")
		await C.Bernie.say("The wedge for the short leg's gone walkabout. Rosie'll know where.")
		return
	await R.current.play_match()


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.Wedge:
		await _walk_up()
		await C.Bernie.say("The table wedge! Good lad. Short leg, river end.")
		await R.current.level_table()
	elif item == I.CrawlCard:
		await _walk_up()
		if Globals.stamps >= 5:
			await C.Bernie.say("Five stamps, all present and correct. Fair enough, lad.")
			await on_talk_to()
		else:
			await C.Bernie.say("%d of 6. Full card first, lad." % Globals.stamps)
	elif item == I.Pint:
		await _walk_up()
		await C.Bernie.say("Not while I'm playing, ta. Lemonade man on match nights.")
	else:
		await _walk_up()
		await C.Bernie.say("No ta, lad.")
