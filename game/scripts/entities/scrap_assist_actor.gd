extends Node2D
class_name ScrapAssistActor

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var bag_drop_point: Marker2D = $BagDropPoint
@onready var timer: Timer = $Timer


func _ready() -> void:
	if timer and not timer.timeout.is_connected(_on_timer_timeout):
		timer.timeout.connect(_on_timer_timeout)


func _on_timer_timeout() -> void:
	# Placeholder hook for future assist behavior timing.
	pass
