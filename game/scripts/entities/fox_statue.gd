extends Node2D

@onready var interaction_area: Area2D = $InteractionArea
@onready var prompt_label: Label = $PromptLabel

var can_interact := false
var current_player: Node = null
var activated := false

func _ready() -> void:
	prompt_label.visible = false
	interaction_area.body_entered.connect(_on_body_entered)
	interaction_area.body_exited.connect(_on_body_exited)

func _process(_delta: float) -> void:
	if can_interact and Input.is_action_just_pressed("interact"):
		activate_statue()

func _on_body_entered(body: Node) -> void:
	if body.name != "Axel":
		return

	current_player = body
	can_interact = true
	prompt_label.visible = true
	prompt_label.text = "Press USE"

func _on_body_exited(body: Node) -> void:
	if body != current_player:
		return

	current_player = null
	can_interact = false
	prompt_label.visible = false

func activate_statue() -> void:
	if current_player == null:
		return

	if activated:
		return

	activated = true
	prompt_label.visible = false

	if current_player.has_method("restore_hits"):
		current_player.restore_hits(2)

	if current_player.has_signal("pickup_feedback_requested"):
		current_player.emit_signal("pickup_feedback_requested", "Fox Statue Restored You", Color("7fe0d6"))

	var room = get_parent()
	if room and room.has_method("on_statue_activated"):
		room.on_statue_activated()
