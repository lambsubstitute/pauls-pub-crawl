extends Node
## Visual check (use with --write-movie): the Nottingham Arms, Paul walking behind and in front
## of the pool table, the NPCs, then the pool table mid-aim sober and seeing double.
##   PPC_TEST=nottview godot --path . --write-movie /tmp/nv/f.png --fixed-fps 10

func _ready() -> void:
	E.settings.auto_continue_text = true
	await get_tree().create_timer(2.0).timeout
	Globals.stamps = 4
	R.goto_room("NottinghamArms")
	await get_tree().create_timer(5.0).timeout
	C.player.walk_to(Vector2(260, 112))     # along the back, behind the table
	await get_tree().create_timer(5.0).timeout
	C.player.walk_to(Vector2(140, 132))     # round the front
	await get_tree().create_timer(5.0).timeout
	C.player.walk_to(Vector2(190, 111))     # stop right behind the table
	await get_tree().create_timer(4.0).timeout
	Globals.drunk = 0
	var Pool = load("res://game/minigames/pool/pool.gd")
	Pool.play(get_tree(), "Gaz", 0.5)
	await get_tree().create_timer(2.0).timeout
	Globals.drunk = 75
	await get_tree().create_timer(2.0).timeout
	get_tree().quit()
