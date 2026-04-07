extends Node2D

@export var move_speed: float = 40.0
@export var path_points: Array[Vector2] = []

var active := false
var current_point := 0

func start_guiding():
	active = true
	current_point = 0

func _process(delta):
	if not active:
		return

	if current_point >= path_points.size():
		return

	var target = path_points[current_point]
	var dir = (target - global_position).normalized()

	global_position += dir * move_speed * delta

	if global_position.distance_to(target) < 4.0:
		current_point += 1
