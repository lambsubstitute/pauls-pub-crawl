extends PopochiuInventoryItem

const Data := preload('inventory_item_pint_state.gd')

var state: Data = load("res://game/inventory_items/pint/inventory_item_pint.tres")


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.say("A pint of local ale. Lovely head on it.")


func on_use() -> void:
	await C.player.say("Cheers!")
	remove()
	Globals.drink(35)
	await C.player.say("Ahh. Everything's gone a bit wobbly.")


func _on_item_used(_item: PopochiuInventoryItem) -> void:
	await C.player.say("Not mixing my drinks.")
