extends Area2D

@export var power_id: String = "burning_buffalo"
@export var duration: float = 15.0

var collected := false


func _ready() -> void:
	body_entered.connect(_on_body_entered)


func _on_body_entered(body: Node) -> void:
	if collected:
		return
	if body.name != "Axel":
		return

	collected = true
	PowerManager.activate_power(power_id, duration)
	var meta := PowerManager.get_power_meta(power_id)
	GameState.announce_pickup("%s online (15s)" % str(meta.get("display", power_id)), meta.get("color", Color(0.82, 0.82, 0.82, 1.0)))
	queue_free()
