@tool
extends PopochiuRoom
## The Mythe Bridge at night: the ending. Telford's cast-iron arch over the Severn, seen from the
## riverside path on the Tewkesbury bank. Paul walks out here from the Black Bear after beating
## Bernie; the closing scene plays once, then THE END / credits (game/ending/credits.gd) with
## "keep exploring" or "start again". Very merry Paul doesn't walk home: Rosie has rung his
## family and his lift comes over the bridge to collect the champion.
## Back to town (off the left edge) is always open; HighSt spawns Paul at the Mythe end.

const Data := preload('room_mythe_bridge_state.gd')
const Credits := preload("res://game/ending/credits.gd")

## Spots from art/renders/mythe_bridge.json (street camera: 30 px figures).
const SPAWN := Vector2(22, 132)
const ENDING_SPOT := Vector2(155, 128)
const WALK_OFF_RIGHT := Vector2(312, 127)
const WALK_OFF_LEFT := Vector2(8, 133)
## The lift home drives along the deck between these (deck_far -> deck_near).
const DECK_FAR := Vector2(24, 40)
const DECK_NEAR := Vector2(202, 46)
## From here up (seeing double, Globals.SEEING_DOUBLE) the ending sends a lift instead of
## letting Paul walk home.
const VERY_MERRY := 60

var state: Data = load("res://game/rooms/mythe_bridge/room_mythe_bridge.tres")


func _on_room_entered() -> void:
	C.player.stop_walking()
	C.player.set_height(30)
	C.player.position = SPAWN
	C.player.face_right()
	$Props/Car.visible = false
	$Props/Headlights.visible = false


func _on_room_transition_finished() -> void:
	if Globals.finale_won and not Globals.ending_seen:
		await play_ending()
	elif state.visited_first_time:
		await C.player.say("The Mythe bridge. Lovely and quiet down by the river.")


func _on_room_exited() -> void:
	Globals.last_room = "MytheBridge"


func _on_restore_from_savegame() -> void:
	pass


## The closing scene, then the credits.
func play_ending() -> void:
	await C.player.walk_to(ENDING_SPOT)
	C.player.face_up()
	await C.player.say("The Mythe bridge. Thomas Telford, 1826. One iron arch, right over the Severn.")
	await C.player.say("Six pubs. Six stamps. Champion of the Black Bear.")
	await C.player.say("Not bad for one night in Tewkesbury.")
	if Globals.drunk >= VERY_MERRY:
		await C.player.say("Mind you, there seem to be two bridges. And two moons.")
		await _lift_home()
	else:
		await C.player.say("Right. Home, the long way, along the river. Sensible shoes, sensible lad.")
		C.player.face_left()
		await C.player.walk_to(WALK_OFF_LEFT)
	Globals.ending_seen = true
	await roll_credits()


## Headlights on the bridge: Paul's family, rung by Rosie, come to collect the champion.
func _lift_home() -> void:
	var car: Sprite2D = $Props/Car
	var lights: Sprite2D = $Props/Headlights
	car.position = DECK_FAR
	lights.position = DECK_FAR
	car.visible = true
	lights.visible = true
	await C.player.say("Hang on. Headlights on the bridge...")
	var tw := create_tween().set_parallel()
	tw.tween_property(car, "position", DECK_NEAR, 4.0).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	tw.tween_property(lights, "position", DECK_NEAR, 4.0).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	await tw.finished
	await C.player.say("*PARP PARP!*  That's our car!")
	await C.player.say("Rosie must have rung home. 'Come and fetch your champion,' I bet she said.")
	await C.player.say("Coming! I'll tell you all about it. Twice, probably.")
	C.player.face_right()
	await C.player.walk_to(WALK_OFF_RIGHT)
	car.visible = false
	lights.visible = false


## THE END. Keep exploring puts Paul back on the path; start again reloads the game.
func roll_credits() -> void:
	var choice: String = await Credits.play(get_tree())
	if choice == "restart":
		Credits.restart(get_tree())
		return
	C.player.position = ENDING_SPOT
	C.player.face_right()
	await C.player.say("Actually, one last look round. The night is young. Well, middle-aged.")
