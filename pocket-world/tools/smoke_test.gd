extends Node
## Automated gameplay smoke test. Run headless:
##   godot --headless --path . res://tools/smoke_test.tscn
## Exits with code 0 when every check passes.

var _failures := 0


func _ready() -> void:
	var tree := get_tree()
	await _load("meadow_village")

	var player: Player = tree.get_first_node_in_group("player")
	await _frames(60)
	_check(player.is_on_floor(), "player stands on the village ground")

	# Walking.
	var start := player.global_position
	Input.action_press("move_forward")
	await _frames(60)
	Input.action_release("move_forward")
	_check(player.global_position.distance_to(start) > 3.0, "player walks forward (moved %.1fm)" % player.global_position.distance_to(start))

	# Talking to the mayor.
	var mayor: NPC = tree.current_scene.get_node("NPCs/MayorBun")
	player.global_position = mayor.global_position + Vector3(0, 0.3, -1.6)
	await _frames(20)
	var hud := tree.get_first_node_in_group("hud")
	_press("interact")
	await _frames(2)
	_check(hud.is_dialogue_open(), "pressing E near Mayor Bun opens dialogue")
	_check(player.controls_locked, "player is locked during dialogue")
	for i in 12:
		if not hud.is_dialogue_open():
			break
		_press("interact")
		await _frames(2)
		_press("interact")
		await _frames(2)
	_check(not hud.is_dialogue_open(), "dialogue closes after the last line")
	_check(GameState.has_met("mayor_bun"), "Mayor Bun counts as a friend")
	_check(not player.controls_locked, "player is unlocked after dialogue")

	# Reading a sign.
	var sign_node: Node3D = null
	for n in tree.get_nodes_in_group("interactable"):
		if n.get("title") == "Village Square":
			sign_node = n
	player.global_position = sign_node.global_position + sign_node.global_basis.z * 1.5 + Vector3(0, 0.3, 0)
	await _frames(20)
	_press("interact")
	await _frames(2)
	_check(hud.is_dialogue_open(), "signs can be read")
	for i in 10:
		_press("interact")
		await _frames(2)

	# Every villager should be standing on something after a few seconds.
	await _frames(120)
	_check_npcs()

	# Walk into the north portal.
	var portal: Node3D = tree.current_scene.get_node("Portals/ToWhisperingWoods")
	player.global_position = portal.global_position + Vector3(0, 0.5, 0)
	await _wait_for_scene("WhisperingWoods")
	player = tree.get_first_node_in_group("player")
	var spawn: Node3D = tree.current_scene.get_node("Spawns/from_village")
	_check(player.global_position.distance_to(spawn.global_position) < 1.0, "arrived at the woods spawn point")
	await _frames(60)
	_check(player.is_on_floor(), "player stands on the woods ground")
	_check_npcs()

	# Cross the bridge over the stream heading north.
	player.global_position = Vector3(0, 3.6, 38)
	await _frames(10)
	Input.action_press("move_forward")
	var min_y := 100.0
	for i in 260:
		await tree.physics_frame
		min_y = minf(min_y, player.global_position.y)
	Input.action_release("move_forward")
	_check(player.global_position.z < 21.0, "crossed the bridge (z=%.1f)" % player.global_position.z)
	_check(min_y > 2.5, "stayed on the bridge deck (lowest y=%.2f)" % min_y)

	# Visit the remaining maps through GameState.
	for map in ["sunny_shores", "frosty_peaks", "meadow_village"]:
		GameState.travel(map, "from_village" if map != "meadow_village" else "from_peaks")
		await _wait_for_scene(map.to_pascal_case())
		await _frames(90)
		player = tree.get_first_node_in_group("player")
		_check(player.is_on_floor() and player.global_position.y > -5.0, "%s: player lands safely" % map)
		_check_npcs()

	print("SMOKE TEST: %s (%d failures)" % ["PASS" if _failures == 0 else "FAIL", _failures])
	tree.quit(0 if _failures == 0 else 1)


func _load(map_id: String) -> void:
	var level: Node = load("res://levels/%s.tscn" % map_id).instantiate()
	get_tree().root.add_child.call_deferred(level)
	await get_tree().process_frame
	await get_tree().process_frame
	get_tree().current_scene = level


func _wait_for_scene(scene_name: String) -> void:
	for i in 400:
		await get_tree().process_frame
		var cs := get_tree().current_scene
		if cs and cs.name == scene_name and cs.is_node_ready():
			await _frames(5)
			return
	_check(false, "travelled to %s" % scene_name)


func _check_npcs() -> void:
	var bad := []
	for npc in get_tree().get_nodes_in_group("interactable"):
		if npc is NPC and (npc.global_position.y < -5.0 or not npc.is_on_floor()):
			bad.append(npc.display_name)
	_check(bad.is_empty(), "%s: all villagers grounded %s" % [get_tree().current_scene.name, bad])


func _press(action: String) -> void:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	Input.parse_input_event(ev)
	var up := InputEventAction.new()
	up.action = action
	up.pressed = false
	Input.parse_input_event(up)


func _frames(n: int) -> void:
	for i in n:
		await get_tree().physics_frame


func _check(ok: bool, what: String) -> void:
	print(("  ok   " if ok else "  FAIL ") + what)
	if not ok:
		_failures += 1
