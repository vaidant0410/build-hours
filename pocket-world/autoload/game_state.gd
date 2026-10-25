extends Node
## Global game state: map travel, which villagers you've met, and input setup.

signal friend_met(npc_id: String)

const MAPS := {
	"meadow_village": {"title": "Meadow Village", "scene": "res://levels/meadow_village.tscn"},
	"whispering_woods": {"title": "Whispering Woods", "scene": "res://levels/whispering_woods.tscn"},
	"sunny_shores": {"title": "Sunny Shores", "scene": "res://levels/sunny_shores.tscn"},
	"frosty_peaks": {"title": "Frosty Peaks", "scene": "res://levels/frosty_peaks.tscn"},
}

## Total number of villagers across every map (used by the HUD counter).
const TOTAL_FRIENDS := 18

## Spawn marker the next level should place the player at ("" = default spawn).
var pending_spawn := ""
var friends_met := {}

var _fade_layer: CanvasLayer
var _fade_rect: ColorRect
var _travelling := false


func _ready() -> void:
	_setup_input()
	_fade_layer = CanvasLayer.new()
	_fade_layer.layer = 100
	add_child(_fade_layer)
	_fade_rect = ColorRect.new()
	_fade_rect.color = Color(0.08, 0.06, 0.12, 0.0)
	_fade_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fade_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	_fade_layer.add_child(_fade_rect)


func travel(map_id: String, spawn: String = "") -> void:
	if _travelling or not MAPS.has(map_id):
		return
	_travelling = true
	pending_spawn = spawn
	var tween := create_tween()
	tween.tween_property(_fade_rect, "color:a", 1.0, 0.35)
	await tween.finished
	get_tree().change_scene_to_file(MAPS[map_id].scene)
	await get_tree().process_frame
	await get_tree().process_frame
	tween = create_tween()
	tween.tween_property(_fade_rect, "color:a", 0.0, 0.45)
	await tween.finished
	_travelling = false


func map_title(map_id: String) -> String:
	return MAPS[map_id].title if MAPS.has(map_id) else map_id


func meet(npc_id: String) -> bool:
	if friends_met.has(npc_id):
		return false
	friends_met[npc_id] = true
	friend_met.emit(npc_id)
	return true


func has_met(npc_id: String) -> bool:
	return friends_met.has(npc_id)


func _setup_input() -> void:
	_add_action("move_forward", [KEY_W, KEY_UP], [[JOY_AXIS_LEFT_Y, -1.0]])
	_add_action("move_back", [KEY_S, KEY_DOWN], [[JOY_AXIS_LEFT_Y, 1.0]])
	_add_action("move_left", [KEY_A, KEY_LEFT], [[JOY_AXIS_LEFT_X, -1.0]])
	_add_action("move_right", [KEY_D, KEY_RIGHT], [[JOY_AXIS_LEFT_X, 1.0]])
	_add_action("cam_left", [KEY_Z], [[JOY_AXIS_RIGHT_X, -1.0]])
	_add_action("cam_right", [KEY_C], [[JOY_AXIS_RIGHT_X, 1.0]])
	_add_action("cam_up", [], [[JOY_AXIS_RIGHT_Y, -1.0]])
	_add_action("cam_down", [], [[JOY_AXIS_RIGHT_Y, 1.0]])
	_add_action("jump", [KEY_SPACE], [], [JOY_BUTTON_A])
	_add_action("sprint", [KEY_SHIFT], [], [JOY_BUTTON_LEFT_SHOULDER])
	_add_action("interact", [KEY_E, KEY_ENTER], [], [JOY_BUTTON_X])


func _add_action(action: String, keys: Array, axes: Array = [], buttons: Array = []) -> void:
	if InputMap.has_action(action):
		return
	InputMap.add_action(action, 0.25)
	for key in keys:
		var ev := InputEventKey.new()
		ev.physical_keycode = key
		InputMap.action_add_event(action, ev)
	for axis in axes:
		var ev := InputEventJoypadMotion.new()
		ev.axis = axis[0]
		ev.axis_value = axis[1]
		InputMap.action_add_event(action, ev)
	for button in buttons:
		var ev := InputEventJoypadButton.new()
		ev.button_index = button
		InputMap.action_add_event(action, ev)
