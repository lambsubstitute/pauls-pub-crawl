@tool
extends PixelActor
## Jackie, landlady of the Nottingham Arms. Pulls the halves, keeps the water jug full and stamps
## the card once Paul has beaten Gaz at pool (5/6).

const Data := preload('character_jackie_state.gd')
## Where Paul stands to talk to Jackie: in front of the bar, just right of her
## (art/renders/nottingham_arms.json). Explicit, because walking to a character's feet hits
## their navigation obstacle and never finishes.
const TALK_SPOT := Vector2(74, 112)

var state: Data = load("res://game/characters/jackie/character_jackie.tres")


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
	await C.player.say("Jackie, the landlady. Auburn bob, gold earrings, misses nothing.")


## Stamp once Gaz is beaten. Crawl rules: the Britannia's stamp (4) must come first; the win is
## remembered and stamped later (the room does it on entry).
func stamp_card() -> void:
	if not Globals.pool_won or Globals.stamps >= 5:
		return
	if Globals.stamps < 4:
		await C.Jackie.say("Crawl rules, love: the Britannia's stamp goes on before mine.")
		await C.Jackie.say("Your win's on the league board. It's not going anywhere.")
		return
	await C.Jackie.say("*STAMP*  Five down, one to go. Have a glass of water on the house.")
	Globals.stamps = 5
	Globals.sober(25)


func on_talk_to() -> void:
	await _walk_up()
	if Globals.stamps >= 5:
		await C.Jackie.say("Black Bear's the last one, love. Back down High Street, the old place by the river.")
		await C.Jackie.say("Their champion plays darts AND pool. Take it steady.")
		return
	if Globals.pool_won:
		await stamp_card()
		return
	await C.player.say("Evening! Stamp for my crawl card?")
	await C.Jackie.say("Beat Gaz at pool and it's yours. That'll take some doing.")
	if Globals.cue_given:
		await C.Jackie.say("Steady hands, love. Water's on the end of the bar.")
		return
	if Globals.cue_made:
		await C.Jackie.say("You've put the house cue back together? Give it to Gaz, then.")
		return
	await C.Jackie.say("Only snag: the house cue's in two halves.")
	if not Globals.butt_taken:
		await C.Jackie.say("Bottom half's in the rack by the door. It unscrews in the middle.")
	if not Globals.shaft_swapped:
		await C.Jackie.say("Top half's Norman's. Uses it to poke the jukebox so he needn't get up.")
		if not Globals.norman_laughed:
			await C.Jackie.say("Laugh at one of his stories and he's yours for life.")
			await C.Jackie.say("Mind, nobody sober has managed it since 1987. Halves are on the house for crawlers.")
		else:
			await C.Jackie.say("He likes you now. He'd swap it for something longer to poke with, I bet.")


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.CrawlCard:
		await on_talk_to()
	elif item == I.HouseCue or item == I.CueButt or item == I.CueShaft:
		await _walk_up()
		await C.Jackie.say("Gaz is the one with the table, love.")
	elif item == I.PoolRest:
		await _walk_up()
		await C.Jackie.say("Norman's always moaning his poker's too short. Just saying.")
	else:
		await C.Jackie.say("You keep that, love.")
