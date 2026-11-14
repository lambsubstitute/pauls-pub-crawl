@tool
extends PixelActor
## Dot: seventy-nine, four foot eleven, the Berkeley Arms darts champion. Scores 70.

const Data := preload('character_dot_state.gd')
## Where Paul stands to talk to Dot: left of her, in front of the oche
## (art/renders/berkeley_arms.json).
const TALK_SPOT := Vector2(261, 127)

var state: Data = load("res://game/characters/dot/character_dot.tres")


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
	await C.player.say("Dot. Four foot eleven, glasses on a chain, county darts champion 1983.")
	await C.player.say("And 1984. And most years since.")


func on_talk_to() -> void:
	await _walk_up()
	if Globals.darts_won:
		await C.Dot.say("Beginner's luck, duck. Don't let it go to your head.")
		return
	if Globals.darts_given:
		await R.current.play_darts()
		return
	if I.is_item_in_inventory("Darts"):
		await C.Dot.say("Are those the house darts? Give them here, duck, and we'll have a game.")
		return
	await C.player.say("Evening! Fancy a game of darts?")
	await C.Dot.say("I'd love one, duck, but the house darts are up in that beam.")
	await C.Dot.say("I'd fetch them, but I'm four foot eleven. Clive's got a bad back.")
	if Globals.drunk >= Globals.WOBBLY:
		await C.Dot.say("You're swaying like a hop bine, duck. Mind you don't walk into that post.")


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.Darts:
		await _walk_up()
		await C.player.say("Found the house darts!")
		await C.Dot.say("Clever lad. They've been up there since Easter.")
		I.Darts.remove()
		Globals.darts_given = true
		await R.current.play_darts()
	elif item == I.CrawlCard:
		await _walk_up()
		await C.Dot.say("Clive does the stamping, duck. Beat me first.")
	else:
		await C.Dot.say("No thank you, duck.")
