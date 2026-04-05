extends CharacterBody2D

@export var speed := 200
@export var acceleration := 900
@export var friction := 800
@export var jump_force := -350
@export var gravity := 900
@export var combo_reset_time := 0.35

@export var combo_damages: Array[float] = [1.0, 1.2, 1.5]
@export var combo_durations: Array[float] = [0.11, 0.13, 0.16]

@export var air_swat_damage := 1.1
@export var air_swat_duration := 0.13

@export var down_smash_damage := 1.8
@export var down_smash_duration := 0.18

@export var ground_hitbox_offset := Vector2(22, -6)
@export var ground_hitbox_size := Vector2(34, 24)
@export var air_hitbox_offset := Vector2(18, -10)
@export var air_hitbox_size := Vector2(28, 20)
@export var smash_hitbox_offset := Vector2(0, 20)
@export var smash_hitbox_size := Vector2(32, 22)

var _combo_step := 0
var _combo_timer := 0.0
var _is_attacking := false
var _facing_dir := 1
var _attack_locked_velocity_scale := 0.4

@onready var attack_pivot: Node2D = $AttackPivot
@onready var attack_hitbox: AxelAttackHitbox = $AttackPivot/AttackHitbox
@onready var animated_sprite: AnimatedSprite2D = $AnimatedSprite2D

func _physics_process(delta):
	# Gravity
	if not is_on_floor():
		velocity.y += gravity * delta

	# Input
	var dir = Input.get_axis("move_left", "move_right")

	# Movement
	if dir != 0:
		velocity.x = move_toward(velocity.x, dir * speed, acceleration * delta)
	else:
		velocity.x = move_toward(velocity.x, 0, friction * delta)
	if _is_attacking:
		velocity.x *= _attack_locked_velocity_scale

	# Facing and combo timer
	_update_facing()
	_combo_timer = maxf(_combo_timer - delta, 0.0)
	if _combo_timer <= 0.0 and not _is_attacking:
		_combo_step = 0

	# Jump
	if Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = jump_force

	# Combat
	_handle_attack_input()

	move_and_slide()


func _handle_attack_input() -> void:
	if _is_attacking:
		return
	if not Input.is_action_just_pressed("attack"):
		return

	if not is_on_floor():
		if Input.is_action_pressed("down"):
			_start_attack("down_smash", "smash", down_smash_damage, down_smash_duration, smash_hitbox_offset, smash_hitbox_size)
		else:
			_start_attack("air_swat", "air", air_swat_damage, air_swat_duration, air_hitbox_offset, air_hitbox_size)
		return

	if Input.is_action_pressed("down"):
		_start_attack("down_smash", "smash", down_smash_damage, down_smash_duration, smash_hitbox_offset, smash_hitbox_size)
		_combo_step = 0
		_combo_timer = 0.0
		return

	if _combo_timer <= 0.0:
		_combo_step = 0
	_combo_step = clampi(_combo_step + 1, 1, 3)
	_combo_timer = combo_reset_time

	var attack_idx := _combo_step - 1
	_start_attack(
		"ground_combo_%d" % _combo_step,
		"ground",
		combo_damages[attack_idx],
		combo_durations[attack_idx],
		ground_hitbox_offset,
		ground_hitbox_size
	)


func _start_attack(
	attack_name: String,
	attack_kind: String,
	damage: float,
	active_time: float,
	hitbox_offset: Vector2,
	hitbox_size: Vector2
) -> void:
	if attack_hitbox == null:
		return
	_is_attacking = true

	attack_hitbox.start_attack(
		{
			"name": attack_name,
			"kind": attack_kind,
			"damage": damage,
			"offset": hitbox_offset,
			"size": hitbox_size,
		},
		_facing_dir
	)

	await get_tree().create_timer(active_time).timeout
	attack_hitbox.end_attack()
	_is_attacking = false


func _update_facing() -> void:
	if velocity.x > 5.0:
		_facing_dir = 1
	elif velocity.x < -5.0:
		_facing_dir = -1
	if attack_pivot:
		attack_pivot.scale.x = float(_facing_dir)
	if animated_sprite:
		animated_sprite.flip_h = _facing_dir < 0
