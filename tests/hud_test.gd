extends Node

func _ready() -> void:
	await get_tree().create_timer(2.0).timeout
	print("[test] before: ", Globals._label.text)
	Globals.stamps = 1
	print("[test] after stamp: ", Globals._label.text)
	Globals.drink(35)
	print("[test] after pint: ", Globals._label.text)
	get_tree().quit()
