@tool
extends PopochiuRoom
## High Street, Tewkesbury: from the Cross (off the left-hand edge) up towards the Mythe.
## Left to right: the Britannia Inn (30 High St, stop 4), the Nottingham Arms (129, stop 5) and
## Ye Olde Black Bear (68, the finale) at the far end on the right. The Nottingham and Black Bear
## doors are stubs until their pubs are built; each has a spawn waiting below.

const Data := preload('room_high_st_state.gd')

## Spawn points from art/renders/high_st.json, keyed by the room Paul has just left.
const SPAWNS := {
	"Britannia": Vector2(64, 123),        # from_britannia
	"NottinghamArms": Vector2(159, 123),  # from_nottingham
	"BlackBear": Vector2(274, 123),       # from_black_bear
}
const FROM_THE_CROSS := Vector2(23, 130)

var state: Data = load("res://game/rooms/high_st/room_high_st.tres")


func _on_room_entered() -> void:
	# Same street camera as Church St and the Cross: 30px figures. A walk started in the
	# previous room must not carry on here.
	C.player.stop_walking()
	C.player.set_height(30)
	C.player.position = SPAWNS.get(Globals.last_room, FROM_THE_CROSS)
	if Globals.last_room == "BlackBear":
		C.player.face_left()
	else:
		C.player.face_right()


func _on_room_transition_finished() -> void:
	if state.visited_first_time:
		await C.player.say("High Street. Georgian brick, crooked timber, and three pubs in a row.")


func _on_room_exited() -> void:
	Globals.last_room = "HighSt"


func _on_restore_from_savegame() -> void:
	pass
