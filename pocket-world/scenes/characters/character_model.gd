@tool
class_name CharacterModel
extends Node3D
## A chunky, cartoon character built from primitive meshes.
## Every look option is exported so villagers can be dressed up per-instance in the editor.
## The character faces -Z (Godot's forward), so look_at() works as expected.

enum Hat { NONE, CAP, TOP_HAT, BEANIE, STRAW, WIZARD, BOW }
enum Ears { NONE, BUNNY, CAT, BEAR }

@export var skin_color := Color(1.0, 0.82, 0.66):
	set(v): skin_color = v; _queue_rebuild()
@export var shirt_color := Color(0.95, 0.45, 0.4):
	set(v): shirt_color = v; _queue_rebuild()
@export var pants_color := Color(0.3, 0.4, 0.7):
	set(v): pants_color = v; _queue_rebuild()
@export var shoe_color := Color(0.35, 0.22, 0.15):
	set(v): shoe_color = v; _queue_rebuild()
@export var has_hair := true:
	set(v): has_hair = v; _queue_rebuild()
@export var hair_color := Color(0.4, 0.25, 0.15):
	set(v): hair_color = v; _queue_rebuild()
@export var hat: Hat = Hat.NONE:
	set(v): hat = v; _queue_rebuild()
@export var hat_color := Color(0.9, 0.3, 0.3):
	set(v): hat_color = v; _queue_rebuild()
@export var ears: Ears = Ears.NONE:
	set(v): ears = v; _queue_rebuild()
@export var ear_color := Color(0.95, 0.95, 0.95):
	set(v): ear_color = v; _queue_rebuild()

## 0 = standing still, 1 = full run. Set every frame by the owner.
var move_amount := 0.0
## True while the character is off the ground.
var airborne := false

const HEAD_CENTER := Vector3(0, 0.3, 0)

var _rig: Node3D
var _head: Node3D
var _arm_l: Node3D
var _arm_r: Node3D
var _leg_l: Node3D
var _leg_r: Node3D
var _phase := 0.0
var _time := 0.0
var _talk := 0.0
var _rebuild_queued := false


func _ready() -> void:
	_time = randf() * 10.0
	_rebuild()


func talk() -> void:
	_talk = 1.0


func _queue_rebuild() -> void:
	if not is_inside_tree() or _rebuild_queued:
		return
	_rebuild_queued = true
	_rebuild.call_deferred()


func _rebuild() -> void:
	_rebuild_queued = false
	if _rig:
		_rig.free()
	_rig = Node3D.new()
	_rig.name = "Rig"
	add_child(_rig)

	# Body and shorts.
	_part(_rig, _capsule(0.3, 0.78), shirt_color, Vector3(0, 0.8, 0))
	_part(_rig, _cylinder(0.31, 0.31, 0.16), pants_color, Vector3(0, 0.52, 0))

	# Legs pivot at the hips so they can swing.
	_leg_l = _pivot(_rig, Vector3(-0.14, 0.45, 0))
	_leg_r = _pivot(_rig, Vector3(0.14, 0.45, 0))
	for leg in [_leg_l, _leg_r]:
		_part(leg, _capsule(0.1, 0.4), pants_color, Vector3(0, -0.18, 0))
		_part(leg, _sphere(0.12), shoe_color, Vector3(0, -0.4, -0.05), Vector3.ZERO, Vector3(1, 0.6, 1.4))

	# Arms pivot at the shoulders.
	_arm_l = _pivot(_rig, Vector3(-0.36, 1.02, 0))
	_arm_r = _pivot(_rig, Vector3(0.36, 1.02, 0))
	for arm in [_arm_l, _arm_r]:
		_part(arm, _capsule(0.085, 0.45), shirt_color, Vector3(0, -0.2, 0))
		_part(arm, _sphere(0.1), skin_color, Vector3(0, -0.43, 0))

	# Head: a big round noggin with a simple, friendly face.
	_head = _pivot(_rig, Vector3(0, 1.15, 0))
	var c := HEAD_CENTER
	_part(_head, _sphere(0.34), skin_color, c)
	for side in [-1.0, 1.0]:
		_part(_head, _sphere(0.055), Color(0.1, 0.08, 0.1), c + Vector3(0.12 * side, 0.04, -0.3), Vector3.ZERO, Vector3(1, 1.5, 0.7), false)
		_part(_head, _sphere(0.018), Color.WHITE, c + Vector3(0.12 * side + 0.016, 0.075, -0.345), Vector3.ZERO, Vector3.ONE, false)
		_part(_head, _sphere(0.05), Color(1.0, 0.55, 0.55), c + Vector3(0.2 * side, -0.07, -0.25), Vector3.ZERO, Vector3(1, 0.6, 0.4), false)
	_part(_head, _sphere(0.045), skin_color.darkened(0.12), c + Vector3(0, -0.03, -0.335), Vector3.ZERO, Vector3.ONE, false)
	_part(_head, _sphere(0.03), Color(0.35, 0.12, 0.12), c + Vector3(0, -0.13, -0.3), Vector3.ZERO, Vector3(1.8, 0.6, 0.6), false)

	if has_hair and hat not in [Hat.CAP, Hat.BEANIE]:
		_part(_head, _sphere(0.36, true), hair_color, c + Vector3(0, 0.06, 0.04), Vector3(0.3, 0, 0))
	_build_ears(c)
	_build_hat(c)


func _build_ears(c: Vector3) -> void:
	match ears:
		Ears.BUNNY:
			for side in [-1.0, 1.0]:
				var ear := _part(_head, _capsule(0.075, 0.62), ear_color, c + Vector3(0.2 * side, 0.52, 0.03), Vector3(0, 0, -0.32 * side))
				_part(ear, _capsule(0.038, 0.46), Color(1.0, 0.7, 0.75), Vector3(0, 0, -0.05), Vector3.ZERO, Vector3.ONE, false)
		Ears.CAT:
			for side in [-1.0, 1.0]:
				_part(_head, _cylinder(0.0, 0.12, 0.22), ear_color, c + Vector3(0.2 * side, 0.3, 0.02), Vector3(0, 0, -0.5 * side))
		Ears.BEAR:
			for side in [-1.0, 1.0]:
				_part(_head, _sphere(0.11), ear_color, c + Vector3(0.25 * side, 0.24, 0.03), Vector3.ZERO, Vector3(1, 1, 0.6))


func _build_hat(c: Vector3) -> void:
	match hat:
		Hat.CAP:
			_part(_head, _sphere(0.365, true), hat_color, c + Vector3(0, 0.05, 0.02), Vector3(0.25, 0, 0))
			_part(_head, _cylinder(0.2, 0.2, 0.03), hat_color.darkened(0.15), c + Vector3(0, 0.16, -0.34), Vector3(0.15, 0, 0), Vector3(1, 1, 1.2))
		Hat.TOP_HAT:
			_part(_head, _cylinder(0.36, 0.36, 0.04), hat_color, c + Vector3(0, 0.28, 0))
			_part(_head, _cylinder(0.22, 0.22, 0.38), hat_color, c + Vector3(0, 0.47, 0))
			_part(_head, _cylinder(0.225, 0.225, 0.07), Color(0.85, 0.2, 0.25), c + Vector3(0, 0.33, 0), Vector3.ZERO, Vector3.ONE, false)
		Hat.BEANIE:
			_part(_head, _sphere(0.37, true), hat_color, c + Vector3(0, 0.04, 0.02), Vector3(0.2, 0, 0))
			_part(_head, _sphere(0.1), Color.WHITE, c + Vector3(0, 0.44, 0.08))
		Hat.STRAW:
			_part(_head, _cylinder(0.6, 0.6, 0.04), hat_color, c + Vector3(0, 0.24, 0))
			_part(_head, _cylinder(0.24, 0.27, 0.2), hat_color, c + Vector3(0, 0.34, 0))
			_part(_head, _cylinder(0.275, 0.275, 0.05), Color(0.85, 0.3, 0.3), c + Vector3(0, 0.27, 0), Vector3.ZERO, Vector3.ONE, false)
		Hat.WIZARD:
			_part(_head, _cylinder(0.5, 0.5, 0.04), hat_color, c + Vector3(0, 0.25, 0))
			_part(_head, _cylinder(0.0, 0.3, 0.75), hat_color, c + Vector3(0, 0.62, 0.06), Vector3(0.25, 0, 0))
		Hat.BOW:
			for side in [-1.0, 1.0]:
				_part(_head, _sphere(0.1), hat_color, c + Vector3(0.12 * side + 0.12, 0.3, 0.05), Vector3(0, 0, 0.6 * side), Vector3(1.3, 0.8, 0.6))
			_part(_head, _sphere(0.05), hat_color.darkened(0.2), c + Vector3(0.12, 0.3, 0.05))


func _process(delta: float) -> void:
	if _rig == null:
		return
	_time += delta
	var move := clampf(move_amount, 0.0, 1.0)
	_phase += delta * (7.0 + 6.0 * move) * move

	var swing := sin(_phase)
	_leg_l.rotation.x = swing * 0.8 * move
	_leg_r.rotation.x = -swing * 0.8 * move
	_arm_l.rotation.x = -swing * 0.7 * move
	_arm_r.rotation.x = swing * 0.7 * move
	var arm_out := 0.15
	if airborne:
		arm_out = 1.2
		_leg_l.rotation.x = 0.4
		_leg_r.rotation.x = -0.2
	_arm_l.rotation.z = lerpf(_arm_l.rotation.z, -arm_out, delta * 10.0)
	_arm_r.rotation.z = lerpf(_arm_r.rotation.z, arm_out, delta * 10.0)

	# Bouncy bob while moving, gentle breathing when idle.
	var bob := absf(sin(_phase)) * 0.09 * move + sin(_time * 2.2) * 0.012
	_rig.position.y = bob
	_rig.scale = Vector3(1.0 - bob * 0.3, 1.0 + bob * 0.5, 1.0 - bob * 0.3)

	# A happy little head bounce while talking.
	_talk = maxf(_talk - delta * 1.5, 0.0)
	_head.position.y = 1.15 + absf(sin(_time * 14.0)) * 0.06 * _talk
	_head.rotation.z = sin(_time * 1.3) * 0.05 + sin(_time * 9.0) * 0.08 * _talk


func _pivot(parent: Node3D, pos: Vector3) -> Node3D:
	var n := Node3D.new()
	n.position = pos
	parent.add_child(n)
	return n


func _part(parent: Node3D, mesh: Mesh, color: Color, pos: Vector3, rot := Vector3.ZERO, scl := Vector3.ONE, outline := true) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.material_override = Toon.material(color, outline)
	mi.position = pos
	mi.rotation = rot
	mi.scale = scl
	parent.add_child(mi)
	return mi


func _sphere(r: float, hemisphere := false) -> SphereMesh:
	var m := SphereMesh.new()
	m.radius = r
	m.height = r if hemisphere else r * 2.0
	m.is_hemisphere = hemisphere
	m.radial_segments = 24
	m.rings = 12
	return m


func _capsule(r: float, h: float) -> CapsuleMesh:
	var m := CapsuleMesh.new()
	m.radius = r
	m.height = h
	m.radial_segments = 16
	m.rings = 6
	return m


func _cylinder(top: float, bottom: float, h: float) -> CylinderMesh:
	var m := CylinderMesh.new()
	m.top_radius = top
	m.bottom_radius = bottom
	m.height = h
	m.radial_segments = 20
	return m
