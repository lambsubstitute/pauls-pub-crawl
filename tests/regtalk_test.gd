extends Node
## Talking to Reg must walk Paul to his talk spot (not onto Reg) and get a reply.

func _ready() -> void:
	E.settings.auto_continue_text = true
	await get_tree().create_timer(2.0).timeout
	R.goto_room("HopPole")
	await get_tree().create_timer(3.0).timeout
	E.clicked = C.Reg
	var done := [false]
	var run := func():
		await C.Reg.on_talk_to()
		done[0] = true
	run.call()
	for i in 100:
		await get_tree().create_timer(0.2).timeout
		if done[0]:
			break
	var gap := C.player.position.distance_to(C.Reg.position)
	print("[test] %s talk finished=%s paul=%s reg=%s gap=%.0f" % [
		"PASS" if done[0] and gap > 15 else "FAIL", done[0], C.player.position, C.Reg.position, gap])
	get_tree().quit()
