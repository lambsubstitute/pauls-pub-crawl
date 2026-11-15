@tool
extends PixelActor
## Gwen, landlady of the Britannia. Pulls free halves for crawlers (up to 60), keeps the water
## jug full, and stamps the card once Paul has beaten Stan at shove ha'penny.

const Data := preload('character_gwen_state.gd')
## Where Paul stands to talk to Gwen: in front of the bar, just right of her
## (art/renders/britannia.json). Explicit, because walking to a character's feet hits their
## navigation obstacle and never finishes.
const TALK_SPOT := Vector2(35, 125)

var state: Data = load("res://game/characters/gwen/character_gwen.tres")


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
	await C.player.say("Gwen, the landlady. Neat dark bob, sharp eyes, and a tea towel she can flick at forty paces.")


func on_talk_to() -> void:
	await _walk_up()
	if Globals.stamps >= 4:
		await C.Gwen.say("Nottingham Arms next, love, just up the road. Mind the pool sharks.")
		return
	if Globals.shove_won:
		await R.current.stamp_card()
		return
	await C.player.say("Evening! Stamp for my crawl card?")
	await C.Gwen.say("Beat Stan at shove ha'penny and it's yours, love. That's the Britannia rule.")
	if Globals.halfpenny_given:
		await C.Gwen.say("Steady hands for that board, mind. Water's on the end of the bar.")
		return
	if Globals.halfpenny_found:
		await C.Gwen.say("You found Ernie's ha'penny! Give it to Stan, he's been waiting twenty years.")
		return
	await C.Gwen.say("Only trouble is, the house set's one short. Five ha'pennies a turn, and we've four.")
	await C.Gwen.say("Old Ernie, landlord before me, hid the fifth for a joke when he retired to Weston.")
	await C.Gwen.say("Left a clue in that daft Magic Eye picture by the door. Nobody's ever seen a thing in it.")
	if Globals.magic_eye_seen:
		await C.player.say("I have! A clock with a ha'penny in it.")
		await C.Gwen.say("A clock? There's only one clock in here, love.")
		return
	await C.Gwen.say("The only fella who ever claimed to was Big Mick, four halves in.")
	await C.Gwen.say("Said the picture went double on him, and the spare one had something in it.")
	await C.Gwen.say("Halves are on the house for crawlers, mind. Pumps are just there.")


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.CrawlCard:
		await on_talk_to()
	elif item == I.Halfpenny:
		await _walk_up()
		await C.Gwen.say("Ernie's ha'penny! Don't give it to me, love, give it to Stan.")
	elif item == I.Pint:
		await _walk_up()
		await C.Gwen.say("You hang on to that, love. Halves are free in here anyway.")
	else:
		await C.Gwen.say("No thanks, love.")
