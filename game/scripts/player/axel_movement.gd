extends CharacterBody2D
class_name AxelMovementController

@export var move_speed: float = 238.0
@export var ground_acceleration: float = 1800.0
@export var ground_deceleration: float = 2300.0
@export var air_acceleration: float = 1200.0
@export var air_deceleration: float = 950.0
@export var jump_velocity: float = -438.0
@export var gravity: float = 1240.0
@export var fall_gravity_multiplier: float = 1.45
@export var low_jump_gravity_multiplier: float = 1.85
@export var max_fall_speed: float = 940.0
@export var coyote_time: float = 0.1
@export var jump_buffer_time: float = 0.1

var _coyote_timer: float = 0.0
var _jump_buffer_timer: float = 0.0
var _facing_dir: int = 1


func _physics_process(delta: float) -> void:
	_handle_jump_press_buffer()
	_apply_timers(delta)
	_update_vertical_motion(delta)
	_handle_horizontal_input(delta)
	_try_jump()
	move_and_slide()
	_update_facing()


func _handle_jump_press_buffer() -> void:
	if Input.is_action_just_pressed("jump"):
		_jump_buffer_timer = jump_buffer_time


func _apply_timers(delta: float) -> void:
	if is_on_floor():
		_coyote_timer = coyote_time
	else:
		_coyote_timer = maxf(_coyote_timer - delta, 0.0)
	_jump_buffer_timer = maxf(_jump_buffer_timer - delta, 0.0)


func _update_vertical_motion(delta: float) -> void:
	if is_on_floor():
		if velocity.y > 0.0:
			velocity.y = 0.0
		return

	var gravity_multiplier := 1.0
	if velocity.y > 0.0:
		gravity_multiplier = fall_gravity_multiplier
	elif not Input.is_action_pressed("jump"):
		# Releasing jump early adds weight to avoid floaty arcs.
		gravity_multiplier = low_jump_gravity_multiplier

	velocity.y += gravity * gravity_multiplier * delta
	velocity.y = minf(velocity.y, max_fall_speed)


func _try_jump() -> void:
	if _jump_buffer_timer <= 0.0 or _coyote_timer <= 0.0:
		return
	velocity.y = jump_velocity
	_jump_buffer_timer = 0.0
	_coyote_timer = 0.0


func _handle_horizontal_input(delta: float) -> void:
	var input_axis := Input.get_axis("move_left", "move_right")
	var target_speed := input_axis * move_speed

	var accel := ground_acceleration
	var decel := ground_deceleration
	if not is_on_floor():
		accel = air_acceleration
		decel = air_deceleration

	if absf(target_speed) > 0.001:
		velocity.x = move_toward(velocity.x, target_speed, accel * delta)
	else:
		velocity.x = move_toward(velocity.x, 0.0, decel * delta)


func _update_facing() -> void:
	if velocity.x > 8.0:
		_facing_dir = 1
	elif velocity.x < -8.0:
		_facing_dir = -1
	scale.x = float(_facing_dir)
