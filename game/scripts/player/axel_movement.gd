extends CharacterBody2D

@export var speed := 200.0
@export var acceleration := 900.0
@export var friction := 800.0
@export var jump_force := -350.0
@export var gravity := 900.0

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var attack_pivot: Node2D = $AttackPivot
@onready var attack_hitbox: Area2D = $AttackPivot/AttackHitbox
@onready var sticker_health: AxelStickerHealth = $StickerHealth
@onready var hurtbox: AxelHurtbox = $Hurtbox

var facing := 1
var is_attacking := false
var is_air_attacking := false
var is_smashing := false
var combo_step := 0
var attack_queued := false
var _hit_targets: Dictionary = {}
var max_stickers := 4
var hits_per_sticker := 3
var current_stickers := 0
var current_sticker_hits_remaining := 0

func _ready() -> void:
	attack_hitbox.monitoring = false
	attack_hitbox.area_entered.connect(_on_attack_hitbox_area_entered)
	current_stickers = max_stickers
	current_sticker_hits_remaining = hits_per_sticker
	if sticker_health:
		max_stickers = sticker_health.max_stickers
		hits_per_sticker = sticker_health.hits_per_sticker
		current_stickers = max_stickers
		current_sticker_hits_remaining = hits_per_sticker
		sticker_health.died.connect(_on_sticker_health_depleted)
	if hurtbox:
		hurtbox.set_owner_axel(self)
	if has_node("DamageFlash"):
		$DamageFlash.visible = false

func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y += gravity * delta

	var dir := Input.get_axis("move_left", "move_right")

	if not is_attacking and not is_smashing:
		if dir != 0:
			velocity.x = move_toward(velocity.x, dir * speed, acceleration * delta)
		else:
			velocity.x = move_toward(velocity.x, 0.0, friction * delta)

	if Input.is_action_just_pressed("jump") and is_on_floor() and not is_attacking:
		velocity.y = jump_force

	if dir > 0:
		facing = 1
	elif dir < 0:
		facing = -1

	attack_pivot.scale.x = facing
	sprite.flip_h = facing < 0

	_handle_attack_input()

	move_and_slide()

func _handle_attack_input() -> void:
	if Input.is_action_just_pressed("attack"):
		if not is_on_floor():
			if Input.is_action_pressed("duck") or Input.is_action_pressed("down"):
				start_smash()
			else:
				do_air_swat()
			return

		if not is_attacking:
			start_ground_combo(1)
		else:
			attack_queued = true

func start_ground_combo(step: int) -> void:
	is_attacking = true
	is_air_attacking = false
	combo_step = step
	attack_queued = false

	match combo_step:
		1:
			await do_ground_swat_1()
		2:
			await do_ground_swat_2()
		3:
			await do_ground_swat_3()

func do_ground_swat_1() -> void:
	_enable_attack_hitbox("ground_1")
	await get_tree().create_timer(0.10).timeout
	_disable_attack_hitbox()
	await get_tree().create_timer(0.08).timeout
	_finish_or_chain_combo()

func do_ground_swat_2() -> void:
	_enable_attack_hitbox("ground_2")
	await get_tree().create_timer(0.12).timeout
	_disable_attack_hitbox()
	await get_tree().create_timer(0.08).timeout
	_finish_or_chain_combo()

func do_ground_swat_3() -> void:
	_enable_attack_hitbox("ground_3")
	await get_tree().create_timer(0.16).timeout
	_disable_attack_hitbox()
	await get_tree().create_timer(0.12).timeout
	is_attacking = false
	combo_step = 0

func _finish_or_chain_combo() -> void:
	if attack_queued and combo_step < 3:
		start_ground_combo(combo_step + 1)
	else:
		is_attacking = false
		combo_step = 0

func do_air_swat() -> void:
	if is_attacking or is_smashing:
		return

	is_attacking = true
	is_air_attacking = true
	_enable_attack_hitbox("air")
	await get_tree().create_timer(0.12).timeout
	_disable_attack_hitbox()
	await get_tree().create_timer(0.08).timeout
	is_attacking = false
	is_air_attacking = false

func start_smash() -> void:
	if is_smashing or is_on_floor():
		return

	is_smashing = true
	is_attacking = false
	is_air_attacking = false
	velocity.x = 0.0
	velocity.y = 520.0

func _process(_delta: float) -> void:
	if is_smashing and is_on_floor():
		do_smash_impact()
		is_smashing = false

func do_smash_impact() -> void:
	print("Smash impact")

func _enable_attack_hitbox(mode: String) -> void:
	attack_hitbox.monitoring = true
	attack_hitbox.set_meta("attack_mode", mode)
	_hit_targets.clear()

func _disable_attack_hitbox() -> void:
	attack_hitbox.monitoring = false
	attack_hitbox.set_meta("attack_mode", "")
	_hit_targets.clear()


func _on_attack_hitbox_area_entered(area: Area2D) -> void:
	if not area.has_method("take_hit"):
		return

	var mode := str(attack_hitbox.get_meta("attack_mode", "ground_1"))
	var damage := 1

	match mode:
		"ground_1":
			damage = 1
		"ground_2":
			damage = 1
		"ground_3":
			damage = 2
		"air":
			damage = 1

	area.take_hit(damage, global_position)


func receive_contact_hit(chips_damage: int, heavy_hit: bool, from_position: Vector2) -> void:
	if sticker_health == null:
		return
	if heavy_hit:
		sticker_health.apply_heavy_hit(from_position)
	else:
		sticker_health.apply_light_hit(from_position, chips_damage)


func _on_sticker_health_depleted() -> void:
	queue_free()
