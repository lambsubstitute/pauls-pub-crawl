extends PopochiuInventoryItem

const Data := preload('inventory_item_halfpenny_state.gd')

var state: Data = load("res://game/inventory_items/halfpenny/inventory_item_halfpenny.tres")


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.say("An old ha'penny, worn smooth, with a little sailing ship on it. Ernie's fifth.")


func on_use() -> void:
	await C.player.say("It belongs on Stan's board.")


func _on_item_used(_item: PopochiuInventoryItem) -> void:
	await C.player.say("That doesn't go with a ha'penny.")
