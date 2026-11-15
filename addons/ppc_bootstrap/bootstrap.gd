@tool
extends EditorPlugin
## One-shot scaffolder: run `godot --headless --editor` with this plugin enabled.
## Creates GUI template, rooms, characters, items and room objects via Popochiu's own
## factories, then quits. Safe to re-run: skips anything that already exists.

const ROOMS := {
	"ChurchSt": {
		"main": true,
		"hotspots": ["TavernDoor", "Abbey", "Bench", "HopPoleDoor", "ToTheCross"],
	},
	"CrossHouseTavern": {
		"main": false,
		"hotspots": ["Bar", "QuizMachine", "ExitDoor", "Doorstop"],
	},
	"HopPole": {
		"main": false,
		"hotspots": ["Bar", "SkittleAlley", "ExitDoor", "Portrait"],
	},
	"TheCross": {
		"main": false,
		"hotspots": ["BerkeleyDoor", "BerkeleySign", "Memorial", "ToChurchSt", "ToHighSt"],
	},
	"BerkeleyArms": {
		"main": false,
		"hotspots": [
			"Bar", "Pumps", "WaterJug", "Snug", "ExitDoor", "Fireplace", "Post", "Dartboard",
			"Scoreboard", "BeamDarts",
		],
	},
	"NottinghamArms": {
		"main": false,
		"hotspots": [
			"Bar", "Pumps", "WaterJug", "ExitDoor", "CueRack", "PoolTable", "PoolRest", "Jukebox",
			"Fireplace", "CueShaft", "LeagueBoard",
		],
	},
}
const CHARACTERS := {
	"Paul": true, "Landlord": false, "Barmaid": false, "Reg": false, "Clive": false, "Dot": false,
	"Jackie": false, "Gaz": false, "Norman": false,
}
const ITEMS := [
	"CrawlCard", "Coin", "Pint", "SkittlePin", "Darts", "CueButt", "CueShaft", "HouseCue", "PoolRest",
]
const PopochiuGuiTemplatesHelper = preload(
	"res://addons/popochiu/editor/helpers/popochiu_gui_templates_helper.gd"
)


func _enter_tree() -> void:
	if not OS.get_cmdline_user_args().has("--ppc-bootstrap"):
		return
	_run.call_deferred()


func _wait(t := 0.5) -> void:
	await get_tree().create_timer(t).timeout


func _run() -> void:
	await _wait(3.0)
	print("[ppc] bootstrap start")

	# GUI: 9-verb low-res template
	if not PopochiuResources.is_gui_set():
		PopochiuResources.set_data_value("setup", "done", true)
		ProjectSettings.set_setting(PopochiuResources.DISPLAY_WIDTH, 320)
		ProjectSettings.set_setting(PopochiuResources.DISPLAY_HEIGHT, 200)
		ProjectSettings.set_setting(PopochiuResources.TEST_WIDTH, 1280)
		ProjectSettings.set_setting(PopochiuResources.TEST_HEIGHT, 800)
		ProjectSettings.set_setting(PopochiuResources.STRETCH_MODE, "canvas_items")
		ProjectSettings.set_setting(PopochiuResources.STRETCH_ASPECT, "keep")
		PopochiuConfig.set_pixel_art_textures(true)
		ProjectSettings.save()
		var done := [false]
		await PopochiuGuiTemplatesHelper.copy_gui_template(
			"9 Verb",
			func(p, m): print("[ppc] gui %s%% %s" % [p, m]),
			func(): done[0] = true
		)
		while not done[0]:
			await _wait(0.2)
		print("[ppc] gui done")

	for c in CHARACTERS:
		if not DirAccess.dir_exists_absolute("res://game/characters/%s" % c.to_snake_case()):
			print("[ppc] character ", c, " -> ", PopochiuCharacterFactory.new().create(c, CHARACTERS[c]))
			await _wait()

	for it in ITEMS:
		if not DirAccess.dir_exists_absolute("res://game/inventory_items/%s" % it.to_snake_case()):
			print("[ppc] item ", it, " -> ", PopochiuInventoryItemFactory.new().create(it))
			await _wait()

	for r in ROOMS:
		var dir := "res://game/rooms/%s" % r.to_snake_case()
		var scene_path := "%s/room_%s.tscn" % [dir, r.to_snake_case()]
		# Check for the scene, not the folder: tools/pixelate.py writes props/ into the room folder
		# before the room exists, and a skipped room put its hotspots in the previous scene.
		if not FileAccess.file_exists(scene_path):
			print("[ppc] room ", r, " -> ", PopochiuRoomFactory.new().create(r, ROOMS[r].main))
			await _wait()
		EditorInterface.open_scene_from_path(scene_path)
		await _wait()
		var room: PopochiuRoom = EditorInterface.get_edited_scene_root()
		if not room or room.scene_file_path != scene_path:
			push_error("[ppc] could not open %s, skipping its objects" % scene_path)
			continue
		if not room.has_node("WalkableAreas/Floor"):
			var wp := PopochiuWalkableAreaFactory.PopochiuWalkableAreaFactoryParam.new()
			wp.obj_name = "Floor"
			wp.room = room
			print("[ppc]  walkable Floor -> ", PopochiuWalkableAreaFactory.new().create(wp))
			await _wait()
		for h in ROOMS[r].hotspots:
			if not room.has_node("Hotspots/%s" % h):
				var hp := PopochiuHotspotFactory.PopochiuHotspotFactoryParam.new()
				hp.obj_name = h
				hp.room = room
				print("[ppc]  hotspot ", h, " -> ", PopochiuHotspotFactory.new().create(hp))
				await _wait()
		EditorInterface.save_scene()
		await _wait()

	await _wait(1.0)
	print("[ppc] bootstrap done")
	get_tree().quit()
