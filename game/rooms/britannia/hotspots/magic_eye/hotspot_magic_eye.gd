@tool
extends PopochiuHotspot
## Old Ernie's Magic Eye. Sober it's just dots; seeing double, a ghost copy floats to the right
## (the GhostPicture hotspot) and that's where the hidden picture shows.


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.walk_to_clicked()
	C.player.face_up()
	if R.current.seeing_double():
		await C.player.say("Whoa, the picture's gone double. There's a see-through copy of it floating to the right.")
		await C.player.say("And the copy's... different. Something's standing out of the dots in that one.")
		return
	await C.player.say("A Magic Eye picture. Thousands of coloured dots. 'Old Ernie's Puzzle', says the label.")
	await C.player.say("You're meant to let your eyes go out of step till a hidden picture pops out.")
	await C.player.say("Nnnngh... Nope. My eyes are far too well-behaved.")
	if Globals.drunk >= Globals.WOBBLY:
		await C.player.say("Although the dots are starting to swim a bit...")


func on_pick_up() -> void:
	await C.player.say("Gwen would notice. It's the only picture in here that isn't a ship.")


func on_use() -> void:
	await on_look_at()


func _on_item_used(_item: PopochiuInventoryItem) -> void:
	await C.player.say("I don't think the dots need any help.")
