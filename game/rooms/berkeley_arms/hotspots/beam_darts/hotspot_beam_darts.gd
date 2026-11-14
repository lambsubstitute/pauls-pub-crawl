@tool
extends PopochiuHotspot


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("The house darts! Stuck point-first in the beam over the oche.")
	await C.player.say("Just out of reach. That beam sits on the big oak post.")


func on_pick_up() -> void:
	await C.player.walk_to_clicked()
	C.player.face_up()
	if Globals.drunk < Globals.WOBBLY:
		await C.player.say("Can't reach. And Clive says nobody stands on his furniture.")
		return
	# a wobbly stretch: Paul grabs the post to steady himself, which does the job anyway
	await C.player.say("Nearly... nearly...")
	await C.player.walk_to(R.current.get_node("Hotspots/Post").walk_to_point)
	C.player.face_right()
	await R.current.knock_darts_down()


func on_pull() -> void:
	await on_pick_up()


func _on_item_used(_item: PopochiuInventoryItem) -> void:
	await C.player.say("Can't reach with that either.")
