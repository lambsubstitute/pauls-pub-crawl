extends Node
## Debug harness: PPC_TEST=walk godot --path . -> loads tavern, walks Paul to the bar, logs.

func _ready() -> void:
	await get_tree().create_timer(2.0).timeout
	R.goto_room("CrossHouseTavern")
	await get_tree().create_timer(3.0).timeout
	print("[test] start pos ", C.player.position, " visible ", C.player.visible, " room ", R.current.script_name)
	C.player.walk_to(Vector2(200, 112))
	for i in 6:
		await get_tree().create_timer(0.5).timeout
		print("[test] t=", i * 0.5, " pos ", C.player.position, " vis ", C.player.visible, " scale ", C.player.scale, " mod ", C.player.modulate, " parent ", C.player.get_parent().get_path() if C.player.get_parent() else "none")
	get_tree().quit()
