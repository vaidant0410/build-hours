@tool
extends StaticBody3D
## A wooden sign you can read with E.

@export var title := "Sign":
	set(v):
		title = v
		if is_node_ready():
			$Text.text = title
@export_multiline var lines: PackedStringArray = ["..."]


func _ready() -> void:
	$Text.text = title
	if not Engine.is_editor_hint():
		add_to_group("interactable")


func get_prompt() -> String:
	return "Read %s" % title


func interact(_player: Node3D) -> void:
	var hud := get_tree().get_first_node_in_group("hud")
	if hud:
		hud.start_dialogue(title, lines, self)
