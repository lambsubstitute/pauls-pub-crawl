@tool
extends "res://addons/popochiu/engine/interfaces/i_inventory.gd"

# classes ----
const PIICrawlCard := preload("res://game/inventory_items/crawl_card/inventory_item_crawl_card.gd")
const PIICoin := preload("res://game/inventory_items/coin/inventory_item_coin.gd")
const PIIPint := preload("res://game/inventory_items/pint/inventory_item_pint.gd")
const PIISkittlePin := preload("res://game/inventory_items/skittle_pin/inventory_item_skittle_pin.gd")
const PIIDarts := preload("res://game/inventory_items/darts/inventory_item_darts.gd")
const PIIHalfpenny := preload("res://game/inventory_items/halfpenny/inventory_item_halfpenny.gd")
# ---- classes

# nodes ----
var CrawlCard: PIICrawlCard : get = get_CrawlCard
var Coin: PIICoin : get = get_Coin
var Pint: PIIPint : get = get_Pint
var SkittlePin: PIISkittlePin : get = get_SkittlePin
var Darts: PIIDarts : get = get_Darts
var Halfpenny: PIIHalfpenny : get = get_Halfpenny
# ---- nodes

# functions ----
func get_CrawlCard() -> PIICrawlCard: return get_item_instance("CrawlCard")
func get_Coin() -> PIICoin: return get_item_instance("Coin")
func get_Pint() -> PIIPint: return get_item_instance("Pint")
func get_SkittlePin() -> PIISkittlePin: return get_item_instance("SkittlePin")
func get_Darts() -> PIIDarts: return get_item_instance("Darts")
func get_Halfpenny() -> PIIHalfpenny: return get_item_instance("Halfpenny")
# ---- functions

