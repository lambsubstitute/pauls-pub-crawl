extends Node
## Records a walk along Church St (use with --write-movie) to eyeball the 30px walk cycle.

func _ready() -> void:
	E.settings.auto_continue_text = true
	await get_tree().create_timer(6.0).timeout
	C.player.walk_to(Vector2(200, 134))
	await get_tree().create_timer(4.5).timeout
	get_tree().quit()
