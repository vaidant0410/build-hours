extends CanvasLayer
## On-screen UI: area title banner, friends counter, interact prompt and dialogue box.

const TEXT_SPEED := 45.0 # characters per second

var _title: Label
var _friends: Label
var _prompt: PanelContainer
var _prompt_label: Label
var _dialogue: PanelContainer
var _speaker: Label
var _text: Label
var _next_hint: Label

var _lines: PackedStringArray = []
var _line_index := 0
var _source: Node
var _typing := false


func _ready() -> void:
	add_to_group("hud")
	_build_ui()
	_update_friends()
	GameState.friend_met.connect(func(_id): _update_friends(); _pulse(_friends))


func show_area_title(text: String) -> void:
	_title.text = text
	_title.modulate.a = 0.0
	var tween := create_tween()
	tween.tween_property(_title, "modulate:a", 1.0, 0.6)
	tween.tween_interval(2.5)
	tween.tween_property(_title, "modulate:a", 0.0, 1.0)


func set_prompt(text: String) -> void:
	_prompt.visible = text != "" and not _dialogue.visible
	_prompt_label.text = "[E]  %s" % text


func start_dialogue(speaker: String, lines: PackedStringArray, source: Node) -> void:
	if lines.is_empty():
		return
	_lines = lines
	_line_index = 0
	_source = source
	_speaker.text = speaker
	_dialogue.visible = true
	_prompt.visible = false
	_set_player_locked(true)
	_show_line()


func is_dialogue_open() -> bool:
	return _dialogue.visible


func _unhandled_input(event: InputEvent) -> void:
	if not _dialogue.visible or not event.is_action_pressed("interact"):
		return
	get_viewport().set_input_as_handled()
	if _typing:
		_text.visible_ratio = 1.0
		return
	_line_index += 1
	if _line_index >= _lines.size():
		_close_dialogue()
	else:
		_show_line()


func _process(delta: float) -> void:
	if _typing:
		var total := maxi(_text.get_total_character_count(), 1)
		_text.visible_ratio = minf(_text.visible_ratio + TEXT_SPEED * delta / total, 1.0)
	_typing = _dialogue.visible and _text.visible_ratio < 1.0
	_next_hint.visible = _dialogue.visible and not _typing
	if _next_hint.visible:
		_next_hint.position.y = sin(Time.get_ticks_msec() * 0.008) * 3.0


func _show_line() -> void:
	_text.text = _lines[_line_index]
	_text.visible_ratio = 0.0
	_typing = true
	_next_hint.text = "[E] next" if _line_index < _lines.size() - 1 else "[E] done"
	if _source and _source.has_method("on_dialogue_line"):
		_source.on_dialogue_line()


func _close_dialogue() -> void:
	_dialogue.visible = false
	_set_player_locked(false)
	if _source and _source.has_method("on_dialogue_finished"):
		_source.on_dialogue_finished()
	_source = null


func _set_player_locked(locked: bool) -> void:
	var player := get_tree().get_first_node_in_group("player")
	if player:
		player.controls_locked = locked


func _update_friends() -> void:
	_friends.text = "Friends met: %d / %d" % [GameState.friends_met.size(), GameState.TOTAL_FRIENDS]


func _pulse(node: Control) -> void:
	node.pivot_offset = node.size * 0.5
	var tween := create_tween()
	tween.tween_property(node, "scale", Vector2.ONE * 1.25, 0.12)
	tween.tween_property(node, "scale", Vector2.ONE, 0.25).set_trans(Tween.TRANS_BACK)


# --- UI construction -------------------------------------------------------

func _build_ui() -> void:
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)

	_title = _label(52, Color(1, 0.98, 0.9))
	_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_title.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	_title.offset_top = 40
	_title.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_title.modulate.a = 0.0
	root.add_child(_title)

	_friends = _label(22, Color(1, 0.9, 0.95))
	var friends_panel := _panel(Color(0.95, 0.45, 0.55, 0.9))
	friends_panel.add_child(_friends)
	friends_panel.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	friends_panel.offset_left = -270
	friends_panel.offset_right = -20
	friends_panel.offset_top = 20
	friends_panel.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	root.add_child(friends_panel)

	var help := _label(16, Color(1, 1, 1, 0.85))
	help.text = "WASD move  |  Shift sprint  |  Space jump  |  E talk  |  Click to look around (Esc frees mouse)  |  Z/C turn camera"
	help.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_LEFT)
	help.offset_left = 16
	help.offset_top = -34
	help.grow_vertical = Control.GROW_DIRECTION_BEGIN
	root.add_child(help)

	_prompt = _panel(Color(0.2, 0.18, 0.3, 0.85))
	_prompt_label = _label(24, Color.WHITE)
	_prompt.add_child(_prompt_label)
	_prompt.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	_prompt.offset_top = -150
	_prompt.offset_bottom = -100
	_prompt.grow_horizontal = Control.GROW_DIRECTION_BOTH
	_prompt.visible = false
	root.add_child(_prompt)

	_dialogue = _panel(Color(1.0, 0.97, 0.88, 0.97), Color(0.35, 0.25, 0.2), 4)
	_dialogue.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	_dialogue.offset_left = -440
	_dialogue.offset_right = 440
	_dialogue.offset_top = -210
	_dialogue.offset_bottom = -40
	_dialogue.visible = false
	root.add_child(_dialogue)

	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 8)
	_dialogue.add_child(box)
	_speaker = _label(26, Color(0.85, 0.35, 0.3), false)
	box.add_child(_speaker)
	_text = _label(22, Color(0.25, 0.2, 0.2), false)
	_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_text.size_flags_vertical = Control.SIZE_EXPAND_FILL
	box.add_child(_text)
	var hint_row := Control.new()
	hint_row.custom_minimum_size = Vector2(0, 24)
	box.add_child(hint_row)
	_next_hint = _label(20, Color(0.55, 0.4, 0.35), false)
	_next_hint.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	_next_hint.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	hint_row.add_child(_next_hint)


func _label(font_size: int, color: Color, outlined := true) -> Label:
	var l := Label.new()
	l.add_theme_font_size_override("font_size", font_size)
	l.add_theme_color_override("font_color", color)
	if outlined:
		l.add_theme_color_override("font_outline_color", Color(0.15, 0.1, 0.2))
		l.add_theme_constant_override("outline_size", 8)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


func _panel(bg: Color, border := Color(0.15, 0.1, 0.2), border_width := 3) -> PanelContainer:
	var p := PanelContainer.new()
	var style := StyleBoxFlat.new()
	style.bg_color = bg
	style.border_color = border
	style.set_border_width_all(border_width)
	style.set_corner_radius_all(18)
	style.content_margin_left = 22
	style.content_margin_right = 22
	style.content_margin_top = 12
	style.content_margin_bottom = 12
	style.shadow_color = Color(0, 0, 0, 0.25)
	style.shadow_size = 6
	style.shadow_offset = Vector2(0, 4)
	p.add_theme_stylebox_override("panel", style)
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return p
