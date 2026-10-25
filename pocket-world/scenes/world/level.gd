extends Node3D
## Root of every map: puts the player at the right spawn point and announces the area.

@export var map_id := "meadow_village"


func _ready() -> void:
	PropBaker.bake_children($Props)
	if RenderingServer.get_rendering_device() == null:
		_soften_lighting_for_compatibility()
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


## The Compatibility renderer (used on the web) lights scenes noticeably brighter
## than Forward+, which washes out the pastel palette. Pull it back a little.
func _soften_lighting_for_compatibility() -> void:
	var env: Environment = $WorldEnvironment.environment.duplicate()
	$WorldEnvironment.environment = env
	env.ambient_light_energy *= 0.55
	env.fog_density *= 0.6
	$Sun.light_energy *= 0.8
