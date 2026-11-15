@tool
extends PixelActor
## Rosie, landlady of Ye Olde Black Bear and owner of Ursula the Newfoundland. Pulls the free
## halves, keeps the water jug full, gives the hints and stamps the card when Bernie is beaten
## (6/6).

const Data := preload('character_rosie_state.gd')
## Where Paul stands to talk to Rosie: in front of the bar, just right of her
## (art/renders/black_bear.json). Explicit, because walking to a character's feet hits their
## navigation obstacle and never finishes.
const TALK_SPOT := Vector2(46, 126)

var state: Data = load("res://game/characters/rosie/character_rosie.tres")


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
	await C.player.say("Rosie, the landlady. Silver bun, reading glasses on a chain, a laugh like a foghorn.")


## The last stamp, once Bernie is beaten. He only plays a full card, so stamp 5 is always on.
func stamp_card() -> void:
	if not Globals.finale_won or Globals.stamps >= 6 or Globals.stamps < 5:
		return
	await C.Rosie.say("Give that card here, love. *STAMP*  Six out of six!")
	Globals.stamps = 6
	await C.Rosie.say("And a big glass of water on the house. It's a long walk home.")
	Globals.sober(25)


func on_talk_to() -> void:
	await _walk_up()
	if Globals.finale_won:
		await stamp_card()
		await C.Rosie.say("Our champion! Go and get some fresh air by the river, love. You've earned it.")
		return
	await C.player.say("Evening! I'm on the last stop of a pub crawl.")
	if Globals.stamps < 5:
		await C.Rosie.say("Then you're early, love. Bernie only plays for the last stamp with a full card.")
		await C.Rosie.say("Have a look round, mind. We've been here since 1308, we're not going anywhere.")
	else:
		await C.Rosie.say("Five stamps! Beat Bernie and the sixth is yours. Darts AND pool, mind.")
	if Globals.table_level:
		await C.Rosie.say("Table's level, so Bernie's got no excuses. Steady hands, love.")
		return
	if Globals.wedge_taken:
		await C.Rosie.say("You've got the wedge? Under the short leg of the pool table with it.")
		return
	await C.Rosie.say("Only, the pool table's wedge has gone missing again. Without it the balls all roll to the river end.")
	if Globals.ursula_moved:
		await C.Rosie.say("Ursula's moved! Was she lying on it? Have a look by the fire.")
		return
	await C.Rosie.say("I bet Ursula's got it. She sleeps on it, the daft thing. That's her by the fire.")
	await C.Rosie.say("Nothing wakes her. Not thunder, not the fire alarm, not the Severn Bore.")
	await C.Rosie.say("Only a hiccup. Her old master had terrible hiccups, and she always jumps up to check on you.")
	if not Globals.has_hiccups():
		await C.player.say("I haven't got the hiccups. I only get them after a couple of halves.")
		await C.Rosie.say("Halves are on the house for crawlers, love. Water's on the end of the bar for after.")


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.CrawlCard:
		await on_talk_to()
	elif item == I.Wedge:
		await _walk_up()
		await C.Rosie.say("That's our wedge! Under the short leg of the pool table, love. Or give it to Bernie.")
	else:
		await _walk_up()
		await C.Rosie.say("You hang on to that, love.")
