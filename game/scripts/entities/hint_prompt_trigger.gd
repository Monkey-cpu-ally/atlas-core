extends Area2D

@export var hint_text: String = "Look closely -> interact -> get rewarded"

var triggered := false


func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node) -> void:
	if triggered:
		return
	if body == null or body.name != "Axel":
		return

	triggered = true
	GameState.announce_pickup(hint_text, Color(0.96, 0.84, 0.55, 1.0))
	queue_free()
