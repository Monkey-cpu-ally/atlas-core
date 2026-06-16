extends Node2D

signal landed

@export var fall_speed: float = 80.0
@export var ground_y: float = 0.0

func _process(delta: float) -> void:
	global_position.y += fall_speed * delta

	if global_position.y >= ground_y:
		global_position.y = ground_y
		emit_signal("landed")
		set_process(false)
