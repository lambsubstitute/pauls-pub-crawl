@tool
extends PopochiuHotspot

const QuizMachine := preload("res://game/minigames/quiz/quiz_machine.gd")


func _on_click() -> void:
	E.command_fallback()


func on_look_at() -> void:
	await C.player.face_clicked()
	await C.player.say("Quiz-O-Matic. One pound a go.")
	if not Globals.quiz_won:
		await C.player.say("The landlord stamps your card if you beat it.")


func on_use() -> void:
	if Globals.quiz_won:
		await C.player.say("Already beaten it. Quit while I'm ahead.")
	elif I.is_item_in_inventory("Coin"):
		await _play()
	else:
		await C.player.say("It wants a pound.")
		await C.player.say("And my wallet's at home on the sideboard.")


func on_push() -> void:
	await C.player.say("Best not. It's bigger than me.")


func _on_item_used(item: PopochiuInventoryItem) -> void:
	if item == I.Coin:
		await _play()
	else:
		await C.player.say("It only takes pound coins.")


func _play() -> void:
	await C.player.walk_to_clicked()
	await C.player.face_clicked()
	I.Coin.remove()
	var won: bool = await QuizMachine.play(get_tree())
	if won:
		Globals.quiz_won = true
		await C.player.say("Winner! Get in!")
		await C.Landlord.say("Well done. Come here and I'll stamp that card.")
	else:
		await C.player.say("Rubbish. Rigged, that.")
		await C.player.say("...Oh, it gave my pound back. Must be faulty.")
		I.Coin.add()
