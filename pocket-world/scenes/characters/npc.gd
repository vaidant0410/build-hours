@tool
class_name NPC
extends CharacterBody3D
## A friendly villager. Wanders around its home spot, turns to look at the
## player and chats when you press E. Look options forward to the CharacterModel.

@export var npc_id := "villager"
@export var display_name := "Villager"
@export_multiline var lines: PackedStringArray = ["Hello there!"]
## Said on later visits, after you've already met. Falls back to `lines` if empty.
@export_multiline var repeat_lines: PackedStringArray = []
@export var wander_radius := 3.0
@export var walk_speed := 1.6

@export_group("Look")
@export var skin_color := Color(1.0, 0.82, 0.66):
	set(v): skin_color = v; _apply_look()
@export var shirt_color := Color(0.95, 0.45, 0.4):
	set(v): shirt_color = v; _apply_look()
@export var pants_color := Color(0.3, 0.4, 0.7):
	set(v): pants_color = v; _apply_look()
@export var shoe_color := Color(0.35, 0.22, 0.15):
	set(v): shoe_color = v; _apply_look()
@export var has_hair := true:
	set(v): has_hair = v; _apply_look()
@export var hair_color := Color(0.4, 0.25, 0.15):
	set(v): hair_color = v; _apply_look()
@export var hat: CharacterModel.Hat = CharacterModel.Hat.NONE:
	set(v): hat = v; _apply_look()
@export var hat_color := Color(0.9, 0.3, 0.3):
	set(v): hat_color = v; _apply_look()
@export var ears: CharacterModel.Ears = CharacterModel.Ears.NONE:
	set(v): ears = v; _apply_look()
@export var ear_color := Color(0.95, 0.95, 0.95):
	set(v): ear_color = v; _apply_look()

const GRAVITY := 20.0

var _home := Vector3.ZERO
var _target := Vector3.ZERO
var _wait := 0.0
var _talking := false
var _player: Node3D

@onready var model: CharacterModel = $Model
@onready var name_tag: Label3D = $NameTag
@onready var marker: Label3D = $NewMarker


func _ready() -> void:
	_apply_look()
	name_tag.text = display_name
	if Engine.is_editor_hint():
		return
	add_to_group("interactable")
	_home = global_position
	_target = _home
	_wait = randf_range(0.5, 3.0)
	name_tag.visible = false
	marker.visible = not GameState.has_met(npc_id)


func _apply_look() -> void:
	if not is_node_ready():
		return
	for prop in ["skin_color", "shirt_color", "pants_color", "shoe_color", "has_hair",
			"hair_color", "hat", "hat_color", "ears", "ear_color"]:
		model.set(prop, get(prop))
	if name_tag:
		name_tag.text = display_name


func get_prompt() -> String:
	return "Talk to %s" % display_name


func interact(player: Node3D) -> void:
	var hud := get_tree().get_first_node_in_group("hud")
	if hud == null:
		return
	_talking = true
	_player = player
	velocity = Vector3.ZERO
	player.face_towards(global_position)
	var first_time := GameState.meet(npc_id)
	marker.visible = false
	var to_say := lines if (first_time or repeat_lines.is_empty()) else repeat_lines
	hud.start_dialogue(display_name, to_say, self)


## Called by the HUD every time a new line of dialogue appears.
func on_dialogue_line() -> void:
	model.talk()


func on_dialogue_finished() -> void:
	_talking = false
	_wait = randf_range(1.5, 3.0)


func _physics_process(delta: float) -> void:
	if Engine.is_editor_hint():
		return
	if _player == null:
		_player = get_tree().get_first_node_in_group("player")

	var to_player := Vector3.INF
	if _player:
		to_player = _player.global_position - global_position
	var player_near := to_player.length() < 4.5
	name_tag.visible = player_near
	marker.position.y = 2.7 + sin(Time.get_ticks_msec() * 0.004) * 0.08

	var move := Vector3.ZERO
	if _talking or player_near:
		# Stop and look at the player: everyone here is very polite.
		_face(to_player, delta)
		_wait = maxf(_wait, 1.0)
	elif wander_radius > 0.1:
		var to_target := _target - global_position
		to_target.y = 0
		if _wait > 0.0:
			_wait -= delta
			if _wait <= 0.0:
				var angle := randf() * TAU
				_target = _home + Vector3(cos(angle), 0, sin(angle)) * randf_range(0.5, wander_radius)
		elif to_target.length() < 0.3 or get_slide_collision_count() > 0 and is_on_wall():
			_wait = randf_range(2.0, 5.0)
		else:
			move = to_target.normalized() * walk_speed
			_face(to_target, delta)

	velocity.x = move.x
	velocity.z = move.z
	velocity.y = 0.0 if is_on_floor() else velocity.y - GRAVITY * delta
	move_and_slide()
	model.move_amount = Vector2(velocity.x, velocity.z).length() / 6.0


func _face(dir: Vector3, delta: float) -> void:
	if Vector2(dir.x, dir.z).length() < 0.01:
		return
	model.rotation.y = lerp_angle(model.rotation.y, atan2(-dir.x, -dir.z), delta * 6.0)
