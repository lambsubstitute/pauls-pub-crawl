extends PopochiuInventoryItem

const Data := preload('inventory_item_skittle_pin_state.gd')

var state: Data = load("res://game/inventory_items/skittle_pin/inventory_item_skittle_pin.tres")


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.say("Skittle pin, number nine. Belongs to the Hop Pole.")


func _on_item_used(_item: PopochiuInventoryItem) -> void:
	await C.player.say("That doesn't go with that.")
