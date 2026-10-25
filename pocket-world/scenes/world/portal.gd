@tool
extends Area3D
## A glowing travel ring. Walk through it to travel to another map.

@export var target_map := "meadow_village":
	set(v): target_map = v; _update_label()
## Name of the spawn marker to use in the target map ("" = its default spawn).
@export var target_spawn := ""
@export var ring_color := Color(0.55, 0.85, 1.0):
	set(v): ring_color = v; _update_color()

var _time := 0.0


func _ready() -> void:
	_update_label()
	_update_color()
	if not Engine.is_editor_hint():
		body_entered.connect(_on_body_entered)


func _process(delta: float) -> void:
	_time += delta
	$Swirl.rotation.z = _time * 1.5
	$Swirl.scale = Vector3.ONE * (1.0 + sin(_time * 3.0) * 0.04)
	$Label.position.y = 4.4 + sin(_time * 2.0) * 0.1


func _update_label() -> void:
	if is_node_ready():
		$Label.text = "To %s" % GameState.map_title(target_map) if not Engine.is_editor_hint() else "To %s" % target_map.capitalize()


func _update_color() -> void:
	if not is_node_ready():
		return
	$Ring.material_override = Toon.material(ring_color, true, 1.5)
	var swirl := Toon.material(Color(ring_color, 0.45), false, 2.0).duplicate() as StandardMaterial3D
	swirl.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	swirl.cull_mode = BaseMaterial3D.CULL_DISABLED
	swirl.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	$Swirl/Disk.material_override = swirl


func _on_body_entered(body: Node3D) -> void:
	if body.is_in_group("player"):
		GameState.travel(target_map, target_spawn)
