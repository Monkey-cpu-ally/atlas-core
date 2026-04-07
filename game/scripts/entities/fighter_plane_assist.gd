extends Node2D
class_name FighterPlaneAssist

signal strike_finished

@export var fly_speed: float = 340.0
var active := false


func start_strike(start_pos: Vector2) -> void:
	global_position = start_pos
	visible = true
	active = true


func _process(delta: float) -> void:
	if not active:
		return

	global_position.x += fly_speed * delta

	if global_position.x > 1600.0:
		active = false
		emit_signal("strike_finished")
		queue_free()
