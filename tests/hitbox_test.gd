extends Node
## NPC bodies must be clickable, not just a 20px square at their feet.

func _check(npc: PopochiuCharacter) -> void:
	var shape: CollisionPolygon2D = npc.get_node("InteractionPolygon")
	var chest := Vector2(0, -30)  # 30px up from the feet, in local space
	var ok := Geometry2D.is_point_in_polygon(chest - shape.position, shape.polygon)
	print("[test] %s %s chest clickable (polygon %s)" % ["PASS" if ok else "FAIL", npc.script_name, shape.polygon])


func _ready() -> void:
	await get_tree().create_timer(2.0).timeout
	R.goto_room("HopPole")
	await get_tree().create_timer(3.0).timeout
	_check(C.Reg)
	_check(C.Barmaid)
	R.goto_room("CrossHouseTavern")
	await get_tree().create_timer(3.0).timeout
	_check(C.Landlord)
	R.goto_room("BerkeleyArms")
	await get_tree().create_timer(3.0).timeout
	_check(C.Clive)
	_check(C.Dot)
	R.goto_room("NottinghamArms")
	await get_tree().create_timer(3.0).timeout
	_check(C.Jackie)
	_check(C.Gaz)
	_check(C.Norman)
	get_tree().quit()
