extends Node

func _probe(room: String) -> void:
	R.goto_room(room)
	await get_tree().create_timer(3.0).timeout
	var wa = R.current.get_node("WalkableAreas/Floor")
	var nav: NavigationRegion2D = wa.get_node("Perimeter")
	var np := nav.navigation_polygon
	print("[test] ", room, " wa_pos ", wa.position, " outlines ", np.get_outline_count(), " polys ", np.get_polygon_count(), " verts ", np.vertices.size(), " enabled ", nav.enabled)
	print("[test]   active wa ", R.current.active_walkable_area_name if "active_walkable_area_name" in R.current else "?", " nav_path ", R.current.get("_nav_path"))
	for target in [Vector2(240, 20), Vector2(200, 120)]:
		var p = R.current.get_navigation_path(C.player.position, target)
		print("[test]   path ", C.player.position, " -> ", target, " = ", p)

func _ready() -> void:
	await get_tree().create_timer(2.0).timeout
	await _probe("ChurchSt")
	await _probe("CrossHouseTavern")
	get_tree().quit()
