@tool
extends "res://addons/popochiu/engine/interfaces/i_character.gd"

# classes ----
const PCPaul := preload("res://game/characters/paul/character_paul.gd")
const PCLandlord := preload("res://game/characters/landlord/character_landlord.gd")
const PCBarmaid := preload("res://game/characters/barmaid/character_barmaid.gd")
const PCReg := preload("res://game/characters/reg/character_reg.gd")
const PCClive := preload("res://game/characters/clive/character_clive.gd")
const PCDot := preload("res://game/characters/dot/character_dot.gd")
const PCGwen := preload("res://game/characters/gwen/character_gwen.gd")
const PCStan := preload("res://game/characters/stan/character_stan.gd")
# ---- classes

# nodes ----
var Paul: PCPaul : get = get_Paul
var Landlord: PCLandlord : get = get_Landlord
var Barmaid: PCBarmaid : get = get_Barmaid
var Reg: PCReg : get = get_Reg
var Clive: PCClive : get = get_Clive
var Dot: PCDot : get = get_Dot
var Gwen: PCGwen : get = get_Gwen
var Stan: PCStan : get = get_Stan
# ---- nodes

# functions ----
func get_Paul() -> PCPaul: return get_runtime_character("Paul")
func get_Landlord() -> PCLandlord: return get_runtime_character("Landlord")
func get_Barmaid() -> PCBarmaid: return get_runtime_character("Barmaid")
func get_Reg() -> PCReg: return get_runtime_character("Reg")
func get_Clive() -> PCClive: return get_runtime_character("Clive")
func get_Dot() -> PCDot: return get_runtime_character("Dot")
func get_Gwen() -> PCGwen: return get_runtime_character("Gwen")
func get_Stan() -> PCStan: return get_runtime_character("Stan")
# ---- functions

