extends Node
## Visual check (use with --write-movie): Hop Pole room, then the skittles screen mid-aim.

func _ready() -> void:
	E.settings.auto_continue_text = true
	await get_tree().create_timer(2.0).timeout
	R.goto_room("HopPole")
	await get_tree().create_timer(5.0).timeout
	load("res://game/minigames/skittles/skittles.gd").play(get_tree(), 6)
	await get_tree().create_timer(2.0).timeout
	get_tree().quit()
