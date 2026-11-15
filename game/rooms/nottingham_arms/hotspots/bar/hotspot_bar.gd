@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("A long mahogany bar with beer mats from every pub in Tewkesbury.")


func on_use() -> void:
	await C.player.say("Jackie pulls the halves. The water jug's on the end, help yourself.")
