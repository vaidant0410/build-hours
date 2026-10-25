extends Node
## Plays a short automated tour of the game (for recording with --write-movie).

var tree: SceneTree


func _ready() -> void:
	tree = get_tree()
	var level: Node = load("res://levels/meadow_village.tscn").instantiate()
	tree.root.add_child.call_deferred(level)
	await _secs(0.1)
	tree.current_scene = level
	var player: Player = tree.get_first_node_in_group("player")

	# Look around the village, then stroll toward the fountain.
	for i in 75:
		player.cam_yaw.rotation.y += 0.025
		await tree.process_frame
	player.cam_yaw.rotation.y = 0.0
	await _walk(2.0)

	# Chat with Mayor Bun.
	var mayor: Node3D = level.get_node("NPCs/MayorBun")
	player.global_position = mayor.global_position + Vector3(0, 0.2, -3.2)
	player.cam_yaw.rotation.y = PI
	player.model.rotation.y = PI
	await _walk(0.6)
	await _secs(0.4)
	_press("interact")
	var hud := tree.get_first_node_in_group("hud")
	while hud.is_dialogue_open():
		await _secs(2.4)
		_press("interact")
		await _secs(0.05)
	await _secs(0.8)

	# Tour the other maps.
	for map in ["whispering_woods", "sunny_shores", "frosty_peaks"]:
		GameState.travel(map, "from_village")
		await _wait_scene(map.to_pascal_case())
		player = tree.get_first_node_in_group("player")
		await _secs(0.5)
		Input.action_press("sprint")
		await _walk(3.5, 0.008)
		Input.action_release("sprint")
		await _secs(0.5)
	tree.quit()


func _walk(seconds: float, turn := 0.0) -> void:
	var player: Player = tree.get_first_node_in_group("player")
	Input.action_press("move_forward")
	for i in int(seconds * 30):
		player.cam_yaw.rotation.y += turn
		await tree.process_frame
	Input.action_release("move_forward")


func _secs(seconds: float) -> void:
	for i in maxi(int(seconds * 30), 1):
		await tree.process_frame


func _wait_scene(scene_name: String) -> void:
	for i in 300:
		await tree.process_frame
		if tree.current_scene and tree.current_scene.name == scene_name:
			return


func _press(action: String) -> void:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	Input.parse_input_event(ev)
	var up := InputEventAction.new()
	up.action = action
	Input.parse_input_event(up)
