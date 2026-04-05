extends Area2D
class_name PickupItem

@export_enum("coin", "scrap", "food", "power") var pickup_type: String = "coin"
@export var amount: int = 1
@export var power_name: String = "burning_buffalo"

@onready var sprite: Polygon2D = $Sprite

func _ready() -> void:
	body_entered.connect(_on_body_entered)
	_update_visual()

func _process(delta: float) -> void:
	position.y += sin(Time.get_ticks_msec() * 0.005) * delta * 10.0

func _update_visual() -> void:
	match pickup_type:
		"coin":
			sprite.color = Color(0.95, 0.79, 0.34)
		"scrap":
			sprite.color = Color(0.62, 0.72, 0.79)
		"food":
			sprite.color = Color(0.87, 0.38, 0.37)
		"power":
			var meta := PowerManager.get_power_meta(power_name)
			sprite.color = meta.get("color", Color(0.85, 0.56, 0.97, 1.0))
		_:
			sprite.color = Color(0.8, 0.8, 0.8)

func _on_body_entered(body: Node) -> void:
	if not body is PlayerController:
		return
	match pickup_type:
		"coin":
			GameState.add_coins(amount)
			GameState.announce_pickup("Coins +%d" % amount, Color(0.95, 0.86, 0.54, 1.0))
		"scrap":
			GameState.add_scrap_parts(amount)
			GameState.add_scrap_meter(8.0 * amount)
			GameState.announce_pickup("Scrap +%d | Charge +%d" % [amount, int(8 * amount)], Color(0.73, 0.83, 0.91, 1.0))
		"food":
			GameState.restore_health(amount * 2)
			GameState.announce_pickup("Repair snack +%d chips" % (amount * 2), Color(0.9, 0.58, 0.44, 1.0))
		"power":
			PowerManager.activate_power(power_name)
			var pmeta := PowerManager.get_power_meta(power_name)
			GameState.announce_pickup("%s online (15s)" % pmeta.get("display", power_name), pmeta.get("color", Color(0.82, 0.82, 0.82, 1.0)))
	queue_free()
