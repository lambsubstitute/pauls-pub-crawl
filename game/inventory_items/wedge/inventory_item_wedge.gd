extends PopochiuInventoryItem
## The Black Bear's oak table wedge. It goes under the pool table's short leg (use it on the
## table, or give it to Bernie).

const Data := preload('inventory_item_wedge_state.gd')

var state: Data = load("res://game/inventory_items/wedge/inventory_item_wedge.tres")


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.say("The pool table's wedge. TABLE carved on one side, tooth marks on the other.")


func on_use() -> void:
	await C.player.say("It goes under the short leg of the pool table.")


func _on_item_used(_item: PopochiuInventoryItem) -> void:
	await C.player.say("It's a wedge. It wedges. That's about it.")
