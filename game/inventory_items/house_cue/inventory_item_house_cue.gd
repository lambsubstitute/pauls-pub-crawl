extends PopochiuInventoryItem
## The house cue, screwed back together. Give it to Gaz for a game.

const Data := preload('inventory_item_house_cue_state.gd')

var state: Data = load("res://game/inventory_items/house_cue/inventory_item_house_cue.tres")


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.say("The Nottingham's house cue, back in one piece. Slightly bendy.")


func on_use() -> void:
	await C.player.say("Gaz is the one to play. I'll give it to him.")


func _on_item_used(_item: PopochiuInventoryItem) -> void:
	await C.player.say("It's a cue, not a Swiss army knife.")
