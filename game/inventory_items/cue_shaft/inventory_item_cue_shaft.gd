extends PopochiuInventoryItem
## Top half of the house cue: Norman's jukebox poker until he swaps it for the rest.

const Data := preload('inventory_item_cue_shaft_state.gd')
const CueButt := preload("res://game/inventory_items/cue_butt/inventory_item_cue_butt.gd")

var state: Data = load("res://game/inventory_items/cue_shaft/inventory_item_cue_shaft.tres")


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.say("The top half of the house cue. Smells faintly of jukebox.")


func on_use() -> void:
	await C.player.say("On its own it's a very good stick for poking jukeboxes.")


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.CueButt:
		await CueButt.assemble()
	else:
		await C.player.say("That does not screw in.")
