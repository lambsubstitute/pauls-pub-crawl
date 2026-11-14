@tool
extends "res://addons/popochiu/engine/interfaces/i_character.gd"

# classes ----
const PCPaul := preload("res://game/characters/paul/character_paul.gd")
const PCLandlord := preload("res://game/characters/landlord/character_landlord.gd")
const PCBarmaid := preload("res://game/characters/barmaid/character_barmaid.gd")
const PCReg := preload("res://game/characters/reg/character_reg.gd")
# ---- classes

# nodes ----
var Paul: PCPaul : get = get_Paul
var Landlord: PCLandlord : get = get_Landlord
var Barmaid: PCBarmaid : get = get_Barmaid
var Reg: PCReg : get = get_Reg
# ---- nodes

# functions ----
func get_Paul() -> PCPaul: return get_runtime_character("Paul")
func get_Landlord() -> PCLandlord: return get_runtime_character("Landlord")
func get_Barmaid() -> PCBarmaid: return get_runtime_character("Barmaid")
func get_Reg() -> PCReg: return get_runtime_character("Reg")
# ---- functions

