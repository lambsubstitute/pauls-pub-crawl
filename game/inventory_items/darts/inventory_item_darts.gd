extends PopochiuInventoryItem

const Data := preload('inventory_item_darts_state.gd')

var state: Data = load("res://game/inventory_items/darts/inventory_item_darts.tres")


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.say("The Berkeley's house darts. Brass barrels, red and green flights.")


func on_use() -> void:
	await C.player.say("Not in here. Dot's got the board.")


func _on_item_used(_item: PopochiuInventoryItem) -> void:
	await C.player.say("That doesn't go with darts.")
