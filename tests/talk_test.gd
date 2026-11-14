extends Node

func _ready() -> void:
	await get_tree().create_timer(2.0).timeout
	R.goto_room("CrossHouseTavern")
	await get_tree().create_timer(3.0).timeout
	C.player.position = Vector2(240, 106)
	print("[test] path to 170,112: ", R.current.get_navigation_path(C.player.position, Vector2(170, 112)))
	print("[test] path no-obst: ", R.current.get_navigation_path(C.player.position, Vector2(170, 112), false, true))
	C.player.walk_to(Vector2(170, 112))
	await get_tree().create_timer(1.5).timeout
	print("[test] after walk_to pos ", C.player.position)
	var wa = R.current.get_node("WalkableAreas/Floor")
	print("[test] obstacles in room: ", get_tree().get_nodes_in_group("navigation_obstacles").size())
	for n in R.current.find_children("*", "NavigationObstacle2D", true, false):
		print("[test] obstacle ", n.get_path(), " gpos ", n.global_position, " verts ", n.vertices, " carve ", n.carve_navigation_mesh, " affect ", n.affect_navigation_mesh)
	var np: NavigationPolygon = wa.get_node("Perimeter").navigation_polygon
	print("[test] navpoly verts ", np.vertices, " polys ", np.get_polygon_count())
	get_tree().quit()
