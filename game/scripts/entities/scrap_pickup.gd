extends Area2D

@export var value: int = 1
var collected := false


func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node) -> void:
	if collected:
		return
	if body.name != "Axel":
		return

	collected = true

	if body.has_method("add_scrap"):
		body.add_scrap(value)
	elif body.has_method("add_scrap_pickup"):
		body.add_scrap_pickup(value)

	queue_free()
