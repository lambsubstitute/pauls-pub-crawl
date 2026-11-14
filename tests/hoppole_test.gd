extends Node
## Royal Hop Pole chain: doorstop pin -> Reg -> skittles -> Bev's stamp. Plus roll-maths sanity.

const Skittles := preload("res://game/minigames/skittles/skittles.gd")


func _ok(cond: bool, what: String) -> void:
	print("[test] %s %s" % ["PASS" if cond else "FAIL", what])


func _finish_skittles(score: int) -> void:
	# The mini-game waits for clicks; find it and end it with a given score.
	for i in 200:  # dialogue lines auto-continue first; poll on real time (headless runs uncapped)
		await get_tree().create_timer(0.2).timeout
		for n in get_tree().root.get_children():
			if n.get_script() == Skittles:
				n.finished.emit(score)
				return
	_ok(false, "skittles overlay appeared")
	for n in get_tree().root.get_children():
		print("[test]   root child ", n.name, " ", n.get_script().resource_path if n.get_script() else "")
	get_tree().quit()


func _ready() -> void:
	E.settings.auto_continue_text = true
	await get_tree().create_timer(2.0).timeout
	Globals.stamps = 1
	Globals.quiz_won = true

	R.goto_room("CrossHouseTavern")
	await get_tree().create_timer(2.5).timeout
	_ok(R.current.get_node("Props/DoorstopPin").visible, "doorstop pin visible before pickup")
	await R.current.get_node("Hotspots/Doorstop").on_pick_up()
	_ok(Globals.pin_taken and I.is_item_in_inventory("SkittlePin"), "picked up pin")
	_ok(not R.current.get_node("Props/DoorstopPin").visible, "doorstop sprite hidden")

	R.goto_room("HopPole")
	await get_tree().create_timer(3.0).timeout
	_ok(R.current.script_name == "HopPole", "entered Hop Pole")
	_finish_skittles.call_deferred(5)
	await C.Reg._on_item_used(I.SkittlePin)
	_ok(Globals.pin_returned and not I.is_item_in_inventory("SkittlePin"), "pin returned to Reg")
	_ok(not Globals.skittles_won, "losing score (5) does not win")
	_finish_skittles.call_deferred(8)
	await R.current.play_skittles()
	_ok(Globals.skittles_won, "winning score (8) beats Reg")
	await C.Barmaid.on_talk_to()
	_ok(Globals.stamps == 2, "Bev stamps card (2/6)")
	_ok(I.is_item_in_inventory("Pint"), "free pint from Bev")

	var good := 0
	var edge := 0
	for s in 200:
		var up := [true, true, true, true, true, true, true, true, true]
		for k in Skittles.simulate_roll(0.0, 0.85, 0.0, up, s):
			good += k.knocked.size()
		up = [true, true, true, true, true, true, true, true, true]
		for k in Skittles.simulate_roll(0.92, 0.85, 0.0, up, s):
			edge += k.knocked.size()
	print("[test] avg pins: centre %.1f  edge %.1f" % [good / 200.0, edge / 200.0])
	_ok(good / 200.0 >= 4.0 and edge / 200.0 <= 1.5, "roll maths: centre hits, edge mostly misses")
	get_tree().quit()
