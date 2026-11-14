extends Node
## Visual check (use with --write-movie): the Cross, Paul walking up to the Berkeley, the bar,
## the darts falling out of the beam, then the darts board mid-aim (sober, then seeing double).
##   PPC_TEST=berkview godot --write-movie /tmp/bv/f.png --fixed-fps 10

func _ready() -> void:
	E.settings.auto_continue_text = true
	await get_tree().create_timer(2.0).timeout
	Globals.stamps = 2
	R.goto_room("TheCross")
	await get_tree().create_timer(3.0).timeout
	C.player.walk_to(Vector2(80, 124))
	await get_tree().create_timer(4.0).timeout
	R.goto_room("BerkeleyArms")
	await get_tree().create_timer(4.0).timeout
	C.player.walk_to(Vector2(199, 126))
	await get_tree().create_timer(2.5).timeout
	Globals.drunk = 35
	await R.current.knock_darts_down()
	await get_tree().create_timer(1.0).timeout
	Globals.drunk = 0
	var Darts = load("res://game/minigames/darts/darts.gd")
	Darts.play(get_tree(), 70)
	await get_tree().create_timer(2.0).timeout
	Globals.drunk = 75
	await get_tree().create_timer(2.0).timeout
	get_tree().quit()
