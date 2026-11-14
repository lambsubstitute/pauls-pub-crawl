extends Node

func _ready() -> void:
	await get_tree().create_timer(2.0).timeout
	I.CrawlCard.add()
	await get_tree().create_timer(0.3).timeout
	I.Coin.add()
	await get_tree().create_timer(0.3).timeout
	var grid = get_tree().root.find_children("*", "HBoxContainer", true, false).filter(func(n): return n is PopochiuInventoryGrid)
	for g in grid:
		print("[test] grid ", g.get_path(), " script ", g.get_script().resource_path, " slots ", g.box.get_child_count())
		for s in g.box.get_children():
			print("[test]   slot ", s.name, " kids ", s.get_children().map(func(c): return c.name))
	get_tree().quit()
