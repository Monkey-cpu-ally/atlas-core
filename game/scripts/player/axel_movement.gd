extends CharacterBody2D
class_name AxelMovementController

@export var move_speed: float = 238.0
@export var acceleration: float = 1750.0
@export var friction: float = 2150.0
@export var jump_velocity: float = -438.0
@export var gravity: float = 1240.0
@export var coyote_time: float = 0.1
@export var jump_buffer_time: float = 0.1

var _coyote_timer: float = 0.0
var _jump_buffer_timer: float = 0.0
var _facing_dir: int = 1


func _physics_process(delta: float) -> void:
	_apply_timers(delta)
	_update_vertical_motion(delta)
	_handle_jump_input()
	_handle_horizontal_input(delta)
	move_and_slide()
	_update_facing()


func _apply_timers(delta: float) -> void:
	if is_on_floor():
		_coyote_timer = coyote_time
	else:
		_coyote_timer = maxf(_coyote_timer - delta, 0.0)
	_jump_buffer_timer = maxf(_jump_buffer_timer - delta, 0.0)


func _update_vertical_motion(delta: float) -> void:
	if not is_on_floor():
		velocity.y += gravity * delta
	elif velocity.y > 0.0:
		velocity.y = 0.0


func _handle_jump_input() -> void:
	if Input.is_action_just_pressed("jump"):
		_jump_buffer_timer = jump_buffer_time
	if _jump_buffer_timer > 0.0 and _coyote_timer > 0.0:
		velocity.y = jump_velocity
		_jump_buffer_timer = 0.0
		_coyote_timer = 0.0


func _handle_horizontal_input(delta: float) -> void:
	var input_axis := Input.get_axis("move_left", "move_right")
	var target_speed := input_axis * move_speed
	if absf(target_speed) > 0.001:
		velocity.x = move_toward(velocity.x, target_speed, acceleration * delta)
	else:
		velocity.x = move_toward(velocity.x, 0.0, friction * delta)


func _update_facing() -> void:
	if velocity.x > 8.0:
		_facing_dir = 1
	elif velocity.x < -8.0:
		_facing_dir = -1
	scale.x = float(_facing_dir)
