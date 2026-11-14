@tool
extends "res://addons/popochiu/engine/interfaces/i_inventory.gd"

# classes ----
const PIICrawlCard := preload("res://game/inventory_items/crawl_card/inventory_item_crawl_card.gd")
const PIICoin := preload("res://game/inventory_items/coin/inventory_item_coin.gd")
const PIIPint := preload("res://game/inventory_items/pint/inventory_item_pint.gd")
# ---- classes

# nodes ----
var CrawlCard: PIICrawlCard : get = get_CrawlCard
var Coin: PIICoin : get = get_Coin
var Pint: PIIPint : get = get_Pint
# ---- nodes

# functions ----
func get_CrawlCard() -> PIICrawlCard: return get_item_instance("CrawlCard")
func get_Coin() -> PIICoin: return get_item_instance("Coin")
func get_Pint() -> PIIPint: return get_item_instance("Pint")
# ---- functions

