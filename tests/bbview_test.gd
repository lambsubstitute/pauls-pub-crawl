extends Node
## Visual check (use with --write-movie): High St's Black Bear door, the Black Bear with Rosie,
## Bernie and Ursula asleep, Ursula moved and the wedge under the table, the darts and pool
## overlays "vs Bernie", then the Mythe bridge, the lift home and the credits.
##   PPC_TEST=bbview godot --path . --write-movie /tmp/bv/f.png --fixed-fps 10

const Darts := preload("res://game/minigames/darts/darts.gd")
const Pool := preload("res://game/minigames/pool/pool.gd")


func _close(script: Script, value) -> void:
	for n in get_tree().root.get_children():
		if n.get_script() == script:
			n.finished.emit(value)


func _ready() -> void:
	E.settings.auto_continue_text = true
	await get_tree().create_timer(2.0).timeout
	Globals.stamps = 5
	Globals.last_room = "BlackBear"
	R.goto_room("HighSt")
	await get_tree().create_timer(4.0).timeout              # frames ~60-100: High St, Paul at the door
	R.goto_room("BlackBear")
	await get_tree().create_timer(5.0).timeout              # the room, Ursula asleep
	C.player.walk_to(Vector2(170, 126))
	await get_tree().create_timer(4.0).timeout
	Globals.ursula_moved = true
	Globals.table_level = true
	R.current.update_props()
	C.player.walk_to(Vector2(240, 128))
	await get_tree().create_timer(4.0).timeout              # Ursula under the window, wedge under the table
	Darts.play(get_tree(), 104, "Bernie")
	await get_tree().create_timer(2.0).timeout              # darts overlay
	_close(Darts, 0)
	await get_tree().create_timer(0.5).timeout
	Pool.play(get_tree(), "Bernie", 0.8, 3)
	await get_tree().create_timer(2.0).timeout              # pool overlay
	_close(Pool, false)
	await get_tree().create_timer(0.5).timeout
	Globals.stamps = 6
	Globals.finale_won = true
	Globals.drunk = 75
	R.goto_room("MytheBridge")                               # the very merry ending plays
	await get_tree().create_timer(130.0).timeout
	get_tree().quit()
