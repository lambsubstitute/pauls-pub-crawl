extends Node
## Regression: entering the tavern with no coin/stamp must not trap Paul inside.

func _ready() -> void:
	await get_tree().create_timer(2.0).timeout
	R.goto_room("CrossHouseTavern")
	await get_tree().create_timer(3.0).timeout
	print("[test] in ", R.current.script_name, " stamps ", Globals.stamps, " coin ", I.is_item_in_inventory("Coin"))
	E.settings.auto_continue_text = true  # no player to click through Paul's line
	R.current.get_node("Hotspots/ExitDoor").on_open()
	for i in 20:
		await get_tree().create_timer(0.5).timeout
		if R.current and R.current.script_name == "ChurchSt":
			break
	print("[test] after exit: ", R.current.script_name if R.current else "none")
	get_tree().quit()
