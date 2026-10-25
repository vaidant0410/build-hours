extends Node3D
## Keeps this node (e.g. a snowfall emitter) hovering above the player.

@export var offset := Vector3(0, 12, 0)

var _player: Node3D


func _process(_delta: float) -> void:
	if _player == null:
		_player = get_tree().get_first_node_in_group("player")
		return
	global_position = _player.global_position + offset
