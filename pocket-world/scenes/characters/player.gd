class_name Player
extends CharacterBody3D
## Third-person player: WASD to move, Shift to sprint, Space to jump, E to talk.
## Click to capture the mouse for camera control, Esc to release it.

@export var walk_speed := 5.0
@export var sprint_speed := 8.5
@export var jump_velocity := 7.0
@export var gravity := 20.0
@export var turn_speed := 12.0
@export var mouse_sensitivity := 0.004
@export var interact_radius := 2.6

var controls_locked := false

@onready var model: CharacterModel = $Model
@onready var cam_yaw: Node3D = $CameraYaw
@onready var cam_pitch: Node3D = $CameraYaw/CameraPitch

var _focus: Node3D


func _ready() -> void:
	add_to_group("player")
	$CameraYaw/CameraPitch/SpringArm.add_excluded_object(get_rid())
	# The camera rig follows the player but rotates independently.
	cam_yaw.top_level = true
	cam_yaw.global_position = global_position
	cam_yaw.rotation.y = rotation.y
	model.rotation.y = 0.0


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	elif event.is_action_pressed("ui_cancel"):
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	elif event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		_rotate_camera(-event.relative.x * mouse_sensitivity, -event.relative.y * mouse_sensitivity)
	elif event.is_action_pressed("interact") and not controls_locked and _focus:
		_focus.interact(self)
		get_viewport().set_input_as_handled()


func _rotate_camera(yaw: float, pitch: float) -> void:
	cam_yaw.rotation.y += yaw
	cam_pitch.rotation.x = clampf(cam_pitch.rotation.x + pitch, -1.2, 0.35)


func _physics_process(delta: float) -> void:
	var input := Vector2.ZERO
	if not controls_locked:
		input = Input.get_vector("move_left", "move_right", "move_forward", "move_back")
		var cam_input := Input.get_vector("cam_left", "cam_right", "cam_up", "cam_down")
		_rotate_camera(-cam_input.x * 2.5 * delta, -cam_input.y * 1.8 * delta)

	var dir := (cam_yaw.global_basis * Vector3(input.x, 0, input.y))
	dir.y = 0
	dir = dir.normalized() * minf(input.length(), 1.0)
	var speed := sprint_speed if Input.is_action_pressed("sprint") else walk_speed

	velocity.x = move_toward(velocity.x, dir.x * speed, 40.0 * delta)
	velocity.z = move_toward(velocity.z, dir.z * speed, 40.0 * delta)
	if is_on_floor():
		if not controls_locked and Input.is_action_just_pressed("jump"):
			velocity.y = jump_velocity
	else:
		velocity.y -= gravity * delta
	move_and_slide()

	if dir.length() > 0.05:
		var target := atan2(-dir.x, -dir.z)
		model.rotation.y = lerp_angle(model.rotation.y, target, turn_speed * delta)

	var horizontal := Vector2(velocity.x, velocity.z).length()
	model.move_amount = horizontal / sprint_speed * 1.3
	model.airborne = not is_on_floor()

	# Safety net: if we ever fall out of the world, pop back to the spawn.
	if global_position.y < -40.0:
		get_tree().reload_current_scene()

	_update_focus()


func _process(delta: float) -> void:
	cam_yaw.global_position = cam_yaw.global_position.lerp(global_position + Vector3(0, 1.2, 0), clampf(delta * 12.0, 0.0, 1.0))


## Teleport to a spawn point, facing the same way the marker faces.
func place_at(marker: Node3D) -> void:
	global_position = marker.global_position
	velocity = Vector3.ZERO
	var yaw := marker.global_rotation.y
	model.rotation.y = yaw
	cam_yaw.rotation.y = yaw
	cam_yaw.global_position = global_position + Vector3(0, 1.2, 0)


func face_towards(point: Vector3) -> void:
	var d := point - global_position
	model.rotation.y = atan2(-d.x, -d.z)


func _update_focus() -> void:
	var best: Node3D = null
	var best_dist := interact_radius
	if not controls_locked:
		for node in get_tree().get_nodes_in_group("interactable"):
			var n := node as Node3D
			var dist := n.global_position.distance_to(global_position)
			if dist < best_dist:
				best = n
				best_dist = dist
	if best != _focus:
		_focus = best
		var hud := get_tree().get_first_node_in_group("hud")
		if hud:
			hud.set_prompt(_focus.get_prompt() if _focus else "")
