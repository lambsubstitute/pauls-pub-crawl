@tool
extends "res://addons/popochiu/engine/interfaces/i_character.gd"

# classes ----
const PCPaul := preload("res://game/characters/paul/character_paul.gd")
const PCLandlord := preload("res://game/characters/landlord/character_landlord.gd")
# ---- classes

# nodes ----
var Paul: PCPaul : get = get_Paul
var Landlord: PCLandlord : get = get_Landlord
# ---- nodes

# functions ----
func get_Paul() -> PCPaul: return get_runtime_character("Paul")
func get_Landlord() -> PCLandlord: return get_runtime_character("Landlord")
# ---- functions

