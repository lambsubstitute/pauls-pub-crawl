@tool
extends PixelActor
## Norman: the Nottingham's oldest regular. Never leaves his spot by the window; changes the
## jukebox record by poking the buttons with the house cue's top half. Only warms to someone who
## laughs at his stories, and only a merry Paul does (the "tipsy logic" puzzle).

const Data := preload('character_norman_state.gd')
## Where Paul stands to talk to Norman: left of him, in front of the jukebox.
const TALK_SPOT := Vector2(233, 112)

var state: Data = load("res://game/characters/norman/character_norman.tres")


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
	await C.player.say("Norman. A walrus moustache with a man attached. He's been here since 1962.")
	if not Globals.shaft_swapped:
		await C.player.say("That's the top half of a pool cue leaning by his chair.")


func on_talk_to() -> void:
	await _walk_up()
	if Globals.shaft_swapped:
		await C.Norman.say("Grand poker, this. Got a fork on the end and everything.")
		return
	if not Globals.norman_laughed:
		await C.player.say("Evening!")
		await R.current.norman_story()
		return
	await C.player.say("Norman, could I borrow that half a cue?")
	await C.Norman.say("My jukebox poker? Then how would I change the record without getting up?")
	await C.Norman.say("My knees, lad. Find me something longer to poke with and we'll swap.")


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.PoolRest:
		await _walk_up()
		if Globals.shaft_swapped:
			await C.Norman.say("I've got one, lad.")
			return
		if not Globals.norman_laughed:
			await C.Norman.say("Swaps? With a stranger? I've not had so much as a chuckle out of you.")
			await C.Norman.say("Sit down and I'll tell you about my bicycle.")
			await R.current.norman_story()
			if not Globals.norman_laughed:
				return
		await C.player.say("How about this? It's longer, and it's got a fork for the buttons.")
		await C.Norman.say("Ooh, now that's a poker. Go on then, lad, take the old one.")
		I.PoolRest.remove()
		I.CueShaft.add()
		Globals.shaft_swapped = true
		R.current.update_props()
		await C.Norman.say("*poke*  There. Number seven. Lovely.")
	elif item == I.CueButt or item == I.HouseCue:
		await _walk_up()
		await C.Norman.say("Heavy end of a cue? Can't poke with that, lad. Too short and too heavy.")
	elif item == I.Pint:
		await _walk_up()
		await C.Norman.say("Kind of you, lad, but I'm on my halves.")
	else:
		await C.Norman.say("No ta, lad.")
