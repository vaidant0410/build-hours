extends Node
## Renders screenshots of a map for quick visual checks.
##   godot --path . res://tools/screenshot.tscn -- <map_id> <out_dir> [x,y,z,tx,ty,tz ...]
## With no camera poses given it captures the player's view from the default spawn.

func _ready() -> void:
	var tree := get_tree()
	var args := OS.get_cmdline_user_args()
	var map_id: String = args[0] if args.size() > 0 else "meadow_village"
	var out_dir: String = args[1] if args.size() > 1 else "user://"
	var poses := args.slice(2)
	var level: Node = load("res://levels/%s.tscn" % map_id).instantiate()
	tree.root.add_child.call_deferred(level)
	for i in 30:
		await tree.process_frame
	var cam := Camera3D.new()
	cam.far = 800
	cam.fov = 60
	if poses.is_empty() or poses[0] == "player":
		poses = poses.slice(1)
		await _snap("%s/%s_player.png" % [out_dir, map_id])
	tree.root.add_child(cam)
	for i in poses.size():
		if poses[i].begins_with("talk:"):
			# Walk up to a villager, start chatting and capture the player camera.
			var npc: Node3D = tree.current_scene.get_node("NPCs/" + poses[i].trim_prefix("talk:"))
			var player: Player = tree.get_first_node_in_group("player")
			var dir := Vector3(0, 0, -1).rotated(Vector3.UP, npc.get_node("Model").rotation.y)
			player.global_position = npc.global_position + dir * 2.0 + Vector3(0, 0.2, 0)
			player.cam_yaw.rotation.y = atan2(dir.x, dir.z) + 0.5
			player.get_node("CameraYaw/CameraPitch/SpringArm/Camera").make_current()
			for f in 30:
				await tree.physics_frame
			npc.interact(player)
			for f in 120:
				await tree.process_frame
			await _snap("%s/%s_%d.png" % [out_dir, map_id, i])
			continue
		var v := poses[i].split_floats(",")
		cam.current = true
		cam.global_position = Vector3(v[0], v[1], v[2])
		cam.look_at(Vector3(v[3], v[4], v[5]))
		for f in 8:
			await tree.process_frame
		await _snap("%s/%s_%d.png" % [out_dir, map_id, i])
	tree.quit()


func _snap(path: String) -> void:
	await RenderingServer.frame_post_draw
	get_tree().root.get_viewport().get_texture().get_image().save_png(path)
	print("saved ", path)
