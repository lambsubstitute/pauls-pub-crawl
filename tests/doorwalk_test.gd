extends Node
## Start a walk on Church St, change room mid-walk (double-click on a door does this):
## Paul must appear at the Hop Pole spawn and stay there, not keep walking.

func _ready() -> void:
	E.settings.auto_continue_text = true
	await get_tree().create_timer(4.0).timeout
	C.player.walk_to(Vector2(280, 126))
	await get_tree().create_timer(0.5).timeout
	R.goto_room("HopPole")
	await get_tree().create_timer(4.0).timeout
	var p := C.player.position
	print("[test] %s paul at %s moving=%s (spawn 128,126)" % [
		"PASS" if p.distance_to(Vector2(128, 126)) < 3 and not C.player.is_moving else "FAIL", p, C.player.is_moving])
	get_tree().quit()
