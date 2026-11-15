@tool
extends PopochiuHotspot
## The wall rack. The house cue's butt end stands in it (Props/CueButt) until Paul takes it.


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	if Globals.butt_taken:
		await C.player.say("Six empty slots. Gaz keeps Excalibur in a case, naturally.")
	else:
		await C.player.say("Six slots, one cue. Well, half a cue: the butt end, unscrewed at the brass joint.")


func on_pick_up() -> void:
	await C.player.walk_to_clicked()
	C.player.face_up()
	if Globals.butt_taken:
		await C.player.say("Nothing else in it.")
		return
	await C.player.say("The bottom half of the house cue. Where's the top half got to?")
	Globals.butt_taken = true
	I.CueButt.add()
	R.current.update_props()


func on_use() -> void:
	await on_pick_up()


func on_pull() -> void:
	await on_pick_up()


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.HouseCue or item == I.CueButt or item == I.CueShaft:
		await C.player.say("I'm not putting it back. I need it for Gaz.")
	else:
		await C.player.say("That's not a cue.")
