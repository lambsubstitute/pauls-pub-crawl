@tool
extends PixelActor
## Stan: retired maths teacher, bow tie, the Britannia's shove ha'penny man. Scores 20.

const Data := preload('character_stan_state.gd')
## Where Paul stands to talk to Stan: left of him, in front of the board
## (art/renders/britannia.json).
const TALK_SPOT := Vector2(267, 126)

var state: Data = load("res://game/characters/stan/character_stan.tres")


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
	await C.player.say("Stan. Bow tie, cardigan, glasses. Taught maths at the school for forty years.")
	await C.player.say("Calculates the angle of every shove. Out loud.")


func on_talk_to() -> void:
	await _walk_up()
	if Globals.halfpenny_given:
		if Globals.shove_won:
			await C.Stan.say("Well played, lad. Gwen's got your stamp.")
		await R.current.play_shove()
		return
	if I.is_item_in_inventory("Halfpenny"):
		await C.Stan.say("Is that a ha'penny? A proper old one? Give it here, lad!")
		return
	await C.player.say("Evening! Fancy a game of shove ha'penny?")
	await C.Stan.say("I'd love one, lad, but Ernie's set is one short. Four's no good.")
	await C.Stan.say("Five coins a turn. Always has been, always will be. It's practically maths.")
	if Globals.drunk >= Globals.SEEING_DOUBLE:
		await C.Stan.say("And you're squinting at me like there's two of me. Glass of water before we play, eh?")


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.Halfpenny:
		await _walk_up()
		await C.player.say("Ernie's fifth ha'penny! It was in the clock.")
		await C.Stan.say("In the clock! The old rascal. Five at last.")
		I.Halfpenny.remove()
		Globals.halfpenny_given = true
		await R.current.play_shove()
	elif item == I.Coin:
		await _walk_up()
		await C.Stan.say("That's a pound, lad. Wrong size, wrong century.")
	elif item == I.CrawlCard:
		await _walk_up()
		await C.Stan.say("Gwen does the stamping. Beat me first.")
	else:
		await C.Stan.say("No thank you, lad.")
