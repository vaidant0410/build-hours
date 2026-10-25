extends Node3D
## Root of every map: puts the player at the right spawn point and announces the area.

@export var map_id := "meadow_village"


func _ready() -> void:
	var player := $Player as Player
	var spawns := $Spawns
	var spawn: Node3D = null
	if GameState.pending_spawn != "":
		spawn = spawns.get_node_or_null(GameState.pending_spawn)
	if spawn == null:
		spawn = spawns.get_node("Default")
	player.place_at(spawn)
	GameState.pending_spawn = ""
	$HUD.show_area_title(GameState.map_title(map_id))
