@tool
extends PixelActor

const Data := preload('character_reg_state.gd')

var state: Data = load("res://game/characters/reg/character_reg.tres")


func _on_room_set() -> void:
	pass


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("A man in a flat cap who has clearly been here since about 1974.")


## Where Paul stands to talk to Reg (left of him, from art/renders/hop_pole.json). Explicit,
## because walk_to_clicked() on a character can target its feet, which its obstacle blocks.
const TALK_SPOT := Vector2(254, 129)


func _walk_up() -> void:
	await C.player.walk_to(TALK_SPOT)
	C.player.face_right()


func on_talk_to() -> void:
	await _walk_up()
	if Globals.skittles_won:
		await C.Reg.say("Beginner's luck, that's all.")
		return
	if not Globals.pin_returned:
		await C.Reg.say("Fancy a game? Can't. Alley's a pin short.")
		await C.Reg.say("Number nine walked off years ago. Last I heard, the Cross House had it.")
		if I.is_item_in_inventory("SkittlePin"):
			await C.player.say("Funny you should say that...")
		return
	await R.current.play_skittles()


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.SkittlePin:
		await _walk_up()
		await C.player.say("Lose one of these?")
		await C.Reg.say("Number nine! Where'd you find her?")
		await C.player.say("Holding a door open at the Cross House.")
		await C.Reg.say("The cheeky beggars. Right, she's back where she belongs.")
		I.SkittlePin.remove()
		Globals.pin_returned = true
		await R.current.play_skittles()
	else:
		await C.Reg.say("Ta, but no.")
