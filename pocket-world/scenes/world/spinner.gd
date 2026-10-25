extends Node3D
## Spins this node around one of its local axes (windmill blades, sparkles...).

@export var axis := Vector3(0, 0, 1)
@export var speed := 1.0


func _process(delta: float) -> void:
	rotate_object_local(axis.normalized(), speed * delta)
