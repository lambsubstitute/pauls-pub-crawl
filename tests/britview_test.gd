extends Node
## Visual check (use with --write-movie): High St, Paul walking to the Britannia, the bar with
## Gwen and Stan, the room seeing double (ghost picture), then the shove ha'penny board mid-game
## sober and seeing double.
##   PPC_TEST=britview godot --write-movie /tmp/bv/f.png --fixed-fps 10

const Shove := preload("res://game/minigames/shove/shove.gd")


func _ready() -> void:
	E.settings.auto_continue_text = true
	await get_tree().create_timer(2.0).timeout
	Globals.stamps = 3
	R.goto_room("HighSt")
	await get_tree().create_timer(3.0).timeout
	C.player.walk_to(Vector2(150, 124))
	await get_tree().create_timer(4.0).timeout
	R.goto_room("Britannia")
	await get_tree().create_timer(4.0).timeout
	C.player.walk_to(Vector2(170, 128))
	await get_tree().create_timer(2.5).timeout
	Globals.drunk = 65
	await get_tree().create_timer(2.5).timeout
	Globals.drunk = 0
	var s = Shove.new()
	s.target = 20
	get_tree().root.add_child(s)
	s.coins = [Vector2(0.1, 2.05), Vector2(-0.45, 2.75), Vector2(0.5, 1.4)]
	s.coin = 3
	s.score = Shove.score_coins(s.coins)
	s._mouse = Vector2(175, 120)
	await get_tree().create_timer(1.5).timeout
	s.phase = Shove.Phase.CHARGE
	await get_tree().create_timer(1.0).timeout
	Globals.drunk = 80
	await get_tree().create_timer(2.0).timeout
	get_tree().quit()
