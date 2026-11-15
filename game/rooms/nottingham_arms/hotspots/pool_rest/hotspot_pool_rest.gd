@tool
extends PopochiuHotspot
## The pool rest leaning on the wall (Props/PoolRestProp). Norman will swap his poker for it.


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("The pool rest. A long stick with a brass cross on top, for shots out of reach.")
	await C.player.say("You could reach a long way with that.")


func on_pick_up() -> void:
	await C.player.walk_to_clicked()
	C.player.face_up()
	await C.player.say("Nobody's using it. I'll look after it.")
	Globals.rest_taken = true
	I.PoolRest.add()
	R.current.update_props()


func on_use() -> void:
	await C.player.say("No tricky shots to play yet.")


func _on_item_used(_item: PopochiuInventoryItem) -> void:
	await C.player.say("Hmm. No.")
