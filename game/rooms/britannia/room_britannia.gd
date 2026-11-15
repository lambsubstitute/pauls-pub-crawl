@tool
extends PopochiuRoom
## The Britannia Inn, 30 High St: stop 4, the shove ha'penny pub. The double-vision puzzle.
## Chain: Stan won't play with the house set one ha'penny short -> Gwen says old Ernie hid the
## fifth and left the clue in his Magic Eye picture, which nobody can see -> seeing double
## (drunk 60+: Gwen's free halves) a ghost copy of the picture floats beside it, and in the
## copy a long-case clock with a ha'penny in it stands out of the dots -> open the clock (any
## time after, drunk or sober) -> give the ha'penny to Stan -> beat his 20 at shove ha'penny
## (much easier sober: the water jug is always there) -> Gwen stamps the card.
## A win before the Berkeley stamp is remembered and stamped when Paul comes back with it.

const Data := preload('room_britannia_state.gd')
const Shove := preload("res://game/minigames/shove/shove.gd")
const STAN_SCORE := 20

var state: Data = load("res://game/rooms/britannia/room_britannia.tres")
var _ghost: Sprite2D
var _t := 0.0


func _on_room_entered() -> void:
	# Spawn, figure height and talk spots come from art/renders/britannia.json.
	# A walk started in the previous room must not carry on here.
	C.player.stop_walking()
	C.player.set_height(46)
	C.Gwen.set_height(46)
	C.Stan.set_height(46)
	C.Stan.face_left()
	# Popochiu re-instances characters on room entry and keeps only their position.
	C.Gwen.walk_to_point = Vector2(10, 6)
	C.Stan.walk_to_point = Vector2(-23, -1)
	C.player.position = Vector2(105, 125)
	C.player.face_right()
	_make_ghost()
	update_double_vision()


func _on_room_transition_finished() -> void:
	C.Stan.face_left()  # he isn't in the tree yet during _on_room_entered
	if state.visited_first_time:
		await C.Gwen.say("Evening, love! Welcome to the Britannia. Wipe your feet.")
	if Globals.shove_won and Globals.stamps == 3:
		await C.Gwen.say("Oh, you've got the Berkeley stamp now! Then you've earned this.")
		await stamp_card()


func _on_room_exited() -> void:
	Globals.last_room = "Britannia"


func _on_restore_from_savegame() -> void:
	update_double_vision()


func seeing_double() -> bool:
	return Globals.drunk >= Globals.SEEING_DOUBLE


# Seeing double, in the room: a see-through copy of the whole background drifts over the real
# one, and the ghost of the Magic Eye floats on the bare wallpaper beside it (sprite + hotspot
# that only exist from drunk 60).
func _make_ghost() -> void:
	if _ghost and is_instance_valid(_ghost):
		return
	_ghost = Sprite2D.new()
	_ghost.name = "DoubleVision"
	_ghost.texture = $Background.texture
	_ghost.centered = false
	_ghost.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_ghost.z_index = -9
	_ghost.modulate = Color(1, 1, 1, 0.22)
	add_child(_ghost)


func update_double_vision() -> void:
	var on := seeing_double()
	if _ghost:
		_ghost.visible = on
	$Props/GhostPicture.visible = on
	$Hotspots/GhostPicture.visible = on
	$Hotspots/GhostPicture.clickable = on


func _process(delta: float) -> void:
	if Engine.is_editor_hint():
		return
	_t += delta
	update_double_vision()
	if _ghost and _ghost.visible:
		var s := Globals.sway_amount()
		_ghost.position = Vector2(s * 1.5 + sin(_t * 0.9) * 2.0, sin(_t * 1.4) * 1.0).round()
		$Props/GhostPicture.modulate.a = 0.75 + 0.2 * sin(_t * 2.0)


## Paul opens the long-case clock. Only worth it once the Magic Eye has shown him where to look.
func search_clock() -> void:
	if Globals.halfpenny_found:
		await C.player.say("Just the pendulum now. Tick, tock.")
		return
	if not Globals.magic_eye_seen:
		await C.player.say("*creak*  A pendulum, a lot of dust and a dead moth. Tick, tock.")
		return
	await C.player.say("*creak*  The picture showed a ha'penny in the clock... behind the pendulum...")
	await C.player.say("Taped to the back of the case! A real old ha'penny, with a ship on it.")
	Globals.halfpenny_found = true
	I.Halfpenny.add()
	await C.Gwen.say("Well I never! Ernie's ha'penny! Twenty years that's been in there.")
	await C.Stan.say("Five! Bring it here, lad, and we'll have a proper game.")


## Gwen stamps the card (4/6) once Paul has beaten Stan, but crawl rules: Berkeley first.
func stamp_card() -> void:
	if Globals.stamps >= 4 or not Globals.shove_won:
		return
	if Globals.stamps < 3:
		await C.Gwen.say("You beat Stan! But crawl rules, love: the first three stamps come first.")
		await C.Gwen.say("Come back when you've got them. Your win's chalked up, it's not going anywhere.")
		return
	await C.Gwen.say("*STAMP*  Four down, two to go. Glass of water on the house, love.")
	Globals.stamps = 4
	Globals.sober(25)


## Stan vs Paul. Called from Stan, the board and handing him the ha'penny. Replayable.
func play_shove() -> void:
	if not Globals.halfpenny_given:
		await C.Stan.say("Four ha'pennies? It's five a turn, lad. Always has been.")
		return
	if Globals.shove_won:
		await C.Stan.say("A rematch? Go on then, just for the fun of it.")
	else:
		await C.Stan.say("Five ha'pennies each, clean in a bed scores the bed. Watch the master.")
		await C.Stan.say("...Seven, six, four, three. Twenty. Your turn, lad.")
	if seeing_double():
		await C.player.say("Which of the two boards are we playing on?")
		await C.Stan.say("The one that isn't moving, lad.")
	var score: int = await Shove.play(get_tree(), STAN_SCORE)
	Globals.shove_best = maxi(Globals.shove_best, score)
	if score > STAN_SCORE:
		var first := not Globals.shove_won
		Globals.shove_won = true
		await C.player.say("%d! I've beaten Stan!" % score)
		if first:
			await C.Stan.say("Hmph. Beginner's luck and a well-polished board.")
			await C.Gwen.say("Nobody beats Stan! Come here, love, and I'll stamp that card.")
	elif score == STAN_SCORE:
		await C.Stan.say("A tie. Honours even. Again whenever you like.")
	else:
		await C.player.say("%d. The board's slanted." % score)
		if Globals.drunk >= Globals.WOBBLY:
			await C.Stan.say("The board's level, lad. You're the one on a slant. Glass of water and go again.")
		else:
			await C.Stan.say("Gentle on the power. Aim between the lines, not at them. Again whenever you like.")
