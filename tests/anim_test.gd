extends Node
## Walk animation check: frames should cycle 1-6 and sprite flip while walking left.

func _ready() -> void:
	await get_tree().create_timer(2.0).timeout
	R.goto_room("CrossHouseTavern")
	await get_tree().create_timer(3.0).timeout
	var spr: Sprite2D = C.player.get_node("Sprite2D")
	print("[test] speed ", C.player.walk_speed, " fps ", C.player.walk_fps(), " hframes ", spr.hframes, " script ", C.player.get_script().resource_path)
	C.player.walk_to(Vector2(200, 120))
	var seen := {}
	for i in 14:
		await get_tree().create_timer(0.1).timeout
		seen[spr.frame] = true
		print("[test] t=%.1f pos %s moving %s frame %d flip %s" % [i * 0.1, C.player.position, C.player.is_moving, spr.frame, spr.flip_h])
	print("[test] frames seen: ", seen.keys())
	get_tree().quit()
