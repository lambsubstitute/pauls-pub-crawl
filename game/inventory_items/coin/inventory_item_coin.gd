extends PopochiuInventoryItem

const Data := preload('inventory_item_coin_state.gd')

var state: Data = load("res://game/inventory_items/coin/inventory_item_coin.tres")


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.say("A pound coin. Slightly sticky.")



func _on_item_used(_item: PopochiuInventoryItem) -> void:
	await C.player.say("That doesn't do anything.")
