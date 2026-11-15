extends PopochiuInventoryItem
## The table's pool rest. Norman swaps his cue shaft for it (a longer jukebox poker).

const Data := preload('inventory_item_pool_rest_state.gd')

var state: Data = load("res://game/inventory_items/pool_rest/inventory_item_pool_rest.tres")


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.say("A pool rest: a long stick with a brass cross on the end. For shots out of reach.")
	await C.player.say("Or for poking things from your chair, I suppose.")


func on_use() -> void:
	await C.player.say("No shot to reach yet.")


func _on_item_used(_item: PopochiuInventoryItem) -> void:
	await C.player.say("That doesn't go with the rest.")
