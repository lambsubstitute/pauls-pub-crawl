@tool
extends "res://addons/popochiu/engine/interfaces/i_room.gd"

# classes ----
const PRChurchSt := preload("res://game/rooms/church_st/room_church_st.gd")
const PRCrossHouseTavern := preload("res://game/rooms/cross_house_tavern/room_cross_house_tavern.gd")
const PRHopPole := preload("res://game/rooms/hop_pole/room_hop_pole.gd")
const PRTheCross := preload("res://game/rooms/the_cross/room_the_cross.gd")
const PRBerkeleyArms := preload("res://game/rooms/berkeley_arms/room_berkeley_arms.gd")
const PRHighSt := preload("res://game/rooms/high_st/room_high_st.gd")
const PRBritannia := preload("res://game/rooms/britannia/room_britannia.gd")
const PRNottinghamArms := preload("res://game/rooms/nottingham_arms/room_nottingham_arms.gd")
# ---- classes

# nodes ----
var ChurchSt: PRChurchSt : get = get_ChurchSt
var CrossHouseTavern: PRCrossHouseTavern : get = get_CrossHouseTavern
var HopPole: PRHopPole : get = get_HopPole
var TheCross: PRTheCross : get = get_TheCross
var BerkeleyArms: PRBerkeleyArms : get = get_BerkeleyArms
var HighSt: PRHighSt : get = get_HighSt
var Britannia: PRBritannia : get = get_Britannia
var NottinghamArms: PRNottinghamArms : get = get_NottinghamArms
# ---- nodes

# functions ----
func get_ChurchSt() -> PRChurchSt: return get_runtime_room("ChurchSt")
func get_CrossHouseTavern() -> PRCrossHouseTavern: return get_runtime_room("CrossHouseTavern")
func get_HopPole() -> PRHopPole: return get_runtime_room("HopPole")
func get_TheCross() -> PRTheCross: return get_runtime_room("TheCross")
func get_BerkeleyArms() -> PRBerkeleyArms: return get_runtime_room("BerkeleyArms")
func get_HighSt() -> PRHighSt: return get_runtime_room("HighSt")
func get_Britannia() -> PRBritannia: return get_runtime_room("Britannia")
func get_NottinghamArms() -> PRNottinghamArms: return get_runtime_room("NottinghamArms")
# ---- functions

