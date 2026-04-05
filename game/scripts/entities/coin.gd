extends Area2D
class_name Coin

@export var amount: int = 1

@onready var animated_sprite: AnimatedSprite2D = $AnimatedSprite2D

var _picked_up := false


func _ready() -> void:
	monitoring = true
	monitorable = true
	body_entered.connect(_on_body_entered)
	if animated_sprite and animated_sprite.sprite_frames and animated_sprite.sprite_frames.has_animation("idle"):
		animated_sprite.play("idle")


func _on_body_entered(body: Node) -> void:
	if _picked_up or body == null:
		return

	_picked_up = true
	GameState.add_coins(amount)
	GameState.announce_pickup("Coins +%d" % amount, Color(0.95, 0.86, 0.54, 1.0))
	queue_free()
