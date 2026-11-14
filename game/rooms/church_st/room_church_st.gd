@tool
extends PopochiuRoom

const Data := preload('room_church_st_state.gd')

var state: Data = load("res://game/rooms/church_st/room_church_st.tres")


func _on_room_entered() -> void:
	# Spawn points and figure height come from art/renders/church_st.json (Blender projection).
	# A walk started in the previous room (e.g. click then double-click a door) must not
	# carry on here towards that room's coordinates.
	C.player.stop_walking()
	C.player.set_height(30)
	if Globals.last_room == "CrossHouseTavern":
		C.player.position = Vector2(157, 124)
	elif Globals.last_room == "HopPole":
		C.player.position = Vector2(272, 127)
		C.player.face_left()
		return
	elif Globals.last_room == "TheCross":
		C.player.position = Vector2(307, 130)  # from_cross: just in from the right-hand edge
		C.player.face_left()
		return
	else:
		C.player.position = Vector2(60, 132)
	C.player.face_right()


func _on_room_transition_finished() -> void:
	if not I.has_item_been_collected("CrawlCard"):
		await C.player.say("Right then. Six pubs, one crawl card.")
		await C.player.say("Last orders at the Black Bear. Let's go!")
		I.CrawlCard.add()


func _on_room_exited() -> void:
	Globals.last_room = "ChurchSt"


func _on_restore_from_savegame() -> void:
	pass
