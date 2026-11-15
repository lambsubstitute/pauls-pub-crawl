@tool
extends PopochiuHotspot
## Ursula, Rosie's Newfoundland (Props/Ursula). Asleep on the table wedge by the fire until a
## hiccup wakes her; only a merry Paul has the hiccups. The room moves this hotspot with her.


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	if Globals.ursula_moved:
		await C.player.say("Ursula, flat out under the window. One eye open, keeping an eye on me.")
		return
	await C.player.say("Is that... a bear? No. A dog. A huge, black, shaggy, very asleep dog.")
	await C.player.say("She's lying on something wooden. A chunk of it is sticking out from under her.")


func on_talk_to() -> void:
	await _rouse("Ursula? Here, girl!")


func on_push() -> void:
	await _rouse("She's the size of a sofa, and about as keen to move.")


func on_pull() -> void:
	await on_push()


func on_pick_up() -> void:
	await _rouse("I'd need a forklift. And a bigger forklift.")


func on_use() -> void:
	await on_talk_to()


func _rouse(sober_line: String) -> void:
	await C.player.walk_to_clicked()
	C.player.face_up()
	if Globals.ursula_moved:
		await C.player.say("Good girl, Ursula. *pat pat*")
		return
	if Globals.has_hiccups():
		await R.current.wake_ursula()
		return
	await C.player.say(sober_line)
	await C.player.say("...")
	await C.player.say("Not so much as a twitch. Just snoring.")


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.Wedge:
		await C.player.say("She's had enough of that wedge for one night.")
	else:
		await C.Rosie.say("No feeding the dog, love. She's on a diet. Allegedly.")
