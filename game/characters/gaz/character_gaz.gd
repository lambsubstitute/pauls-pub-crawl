@tool
extends PixelActor
## Gaz: pool league champion eleven seasons running, waistcoat, tache, a cue called Excalibur
## that nobody else touches. Plays anyone who brings a proper cue.

const Data := preload('character_gaz_state.gd')
## Where Paul stands to talk to Gaz: in front of the table's right-hand end, left of him.
const TALK_SPOT := Vector2(216, 126)

var state: Data = load("res://game/characters/gaz/character_gaz.tres")


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
	await C.player.say("Gaz. Waistcoat, tache, chalking a cue like it owes him money.")


func on_talk_to() -> void:
	await _walk_up()
	if Globals.pool_won:
		await C.Gaz.say("Good game, mate. The Black Bear's champion is better than me, mind. Just.")
		return
	if Globals.cue_given:
		await R.current.play_pool()
		return
	if I.is_item_in_inventory("HouseCue"):
		await C.Gaz.say("That the house cue? All in one piece? Give it here and we'll play.")
		return
	await C.player.say("Evening! Fancy a game? I need a stamp off Jackie.")
	await C.Gaz.say("Jackie stamps anyone who beats me. Nobody has. Eleven seasons.")
	await C.Gaz.say("Bring a cue and I'll play you. Not borrowing mine: this is Excalibur.")
	if I.is_item_in_inventory("CueButt") or I.is_item_in_inventory("CueShaft"):
		await C.Gaz.say("Half a cue's no good. The house cue screws together in the middle.")
	else:
		await C.Gaz.say("House cue's in bits. Ask Jackie where the halves have got to.")


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.HouseCue:
		await _walk_up()
		await C.player.say("One house cue, all in one piece!")
		await C.Gaz.say("Now that's a cue. Rack 'em up.")
		I.HouseCue.remove()
		Globals.cue_given = true
		await R.current.play_pool()
	elif item == I.CueButt or item == I.CueShaft:
		await _walk_up()
		await C.Gaz.say("That's half a cue, mate. Screw the two halves together first.")
	elif item == I.PoolRest:
		await _walk_up()
		await C.Gaz.say("You don't break with the rest, mate. You need a cue.")
	elif item == I.CrawlCard:
		await _walk_up()
		await C.Gaz.say("Jackie does the stamping. Beat me first.")
	else:
		await C.Gaz.say("No ta, mate.")
