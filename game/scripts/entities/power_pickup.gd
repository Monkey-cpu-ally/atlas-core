extends Area2D

const POWER_TYPE_TO_ID := {
	1: "burning_buffalo",
	2: "shadow_tag",
	3: "golden_gloves",
	4: "super_mode",
	5: "specter_mode",
	6: "fighter_plane",
}

@export var power_type: int = 1
@export var power_id: String = "burning_buffalo"
@export var duration: float = 15.0

var collected := false


func _ready() -> void:
	power_id = _resolve_power_id()
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


func _resolve_power_id() -> String:
	if POWER_TYPE_TO_ID.has(power_type):
		return str(POWER_TYPE_TO_ID[power_type])
	return power_id
