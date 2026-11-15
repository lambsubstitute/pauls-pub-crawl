@tool
extends PopochiuHotspot
## The champions' honours board: gold leaf names going back to a bear in 1308.


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("BLACK BEAR CHAMPIONS. Gold leaf on black oak.")
	await C.player.say("At the top: '1308 - A BEAR'. At the bottom: '1999 - 2026 - BERNIE'.")
	if Globals.finale_won:
		await C.player.say("Someone's chalked underneath, for now: 'PAUL. Gold leaf to follow.'")


func on_pick_up() -> void:
	await C.player.say("It's screwed to the wall. And possibly to history.")


func on_use() -> void:
	await on_look_at()
