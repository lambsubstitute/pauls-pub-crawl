extends Node
## Plain "Walk to <NPC>" must stop beside them, not on their feet (which never finishes).

func _walk_to_npc(npc: PopochiuCharacter) -> String:
	E.clicked = npc
	var done := [false]
	var run := func():
		await npc.on_walk_to()
		done[0] = true
	run.call()
	for i in 60:
		await get_tree().create_timer(0.2).timeout
		if done[0]:
			break
	var gap := C.player.position.distance_to(npc.position)
	return "%s %s finished=%s gap=%.0f" % ["PASS" if done[0] and gap > 10 else "FAIL", npc.script_name, done[0], gap]


func _ready() -> void:
	E.settings.auto_continue_text = true
	await get_tree().create_timer(2.0).timeout
	R.goto_room("HopPole")
	await get_tree().create_timer(3.0).timeout
	print("[test] ", await _walk_to_npc(C.Reg))
	print("[test] ", await _walk_to_npc(C.Barmaid))
	R.goto_room("CrossHouseTavern")
	await get_tree().create_timer(3.0).timeout
	print("[test] ", await _walk_to_npc(C.Landlord))
	R.goto_room("BerkeleyArms")
	await get_tree().create_timer(3.0).timeout
	print("[test] ", await _walk_to_npc(C.Clive))
	print("[test] ", await _walk_to_npc(C.Dot))
	get_tree().quit()
