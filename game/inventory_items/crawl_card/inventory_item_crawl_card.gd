extends PopochiuInventoryItem

const Data := preload('inventory_item_crawl_card_state.gd')

var state: Data = load("res://game/inventory_items/crawl_card/inventory_item_crawl_card.tres")


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.say("Paul's Pub Crawl card. %d of 6 stamped." % Globals.stamps)
	if Globals.stamps < 6:
		await C.player.say("Next up: %s." % Globals.PUBS[Globals.stamps])



func _on_item_used(_item: PopochiuInventoryItem) -> void:
	await C.player.say("Don't want to smudge it.")
