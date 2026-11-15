extends PopochiuInventoryItem
## Butt end of the Nottingham Arms house cue (in the wall rack). Use it with the shaft.

const Data := preload('inventory_item_cue_butt_state.gd')

var state: Data = load("res://game/inventory_items/cue_butt/inventory_item_cue_butt.tres")


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.say("The bottom half of the house cue. Brass thread on the end: something screws in.")


func on_use() -> void:
	await C.player.say("Half a cue. I need the top half to go with it.")


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.CueShaft:
		await assemble()
	else:
		await C.player.say("That does not screw in.")


## Butt + shaft -> the house cue. Shared with the shaft item.
static func assemble() -> void:
	await C.player.say("Righty-tighty...  *twist twist*  One house cue!")
	I.CueButt.remove()
	I.CueShaft.remove()
	I.HouseCue.add()
	Globals.cue_made = true
