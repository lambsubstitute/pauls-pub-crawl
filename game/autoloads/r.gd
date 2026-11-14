@tool
extends "res://addons/popochiu/engine/interfaces/i_room.gd"

# classes ----
const PRChurchSt := preload("res://game/rooms/church_st/room_church_st.gd")
const PRCrossHouseTavern := preload("res://game/rooms/cross_house_tavern/room_cross_house_tavern.gd")
# ---- classes

# nodes ----
var ChurchSt: PRChurchSt : get = get_ChurchSt
var CrossHouseTavern: PRCrossHouseTavern : get = get_CrossHouseTavern
# ---- nodes

# functions ----
func get_ChurchSt() -> PRChurchSt: return get_runtime_room("ChurchSt")
func get_CrossHouseTavern() -> PRCrossHouseTavern: return get_runtime_room("CrossHouseTavern")
# ---- functions

