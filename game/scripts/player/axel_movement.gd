extends CharacterBody2D

enum PowerMode {
	NONE,
	BURNING_BUFFALO
}

@export var speed := 200.0
@export var acceleration := 900.0
@export var friction := 800.0
@export var jump_force := -350.0
@export var gravity := 900.0
@export var invuln_time: float = 0.6
@export var knockback_x: float = 160.0
@export var knockback_y: float = -120.0

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
var is_buffalo_mode := false
var current_power_mode: PowerMode = PowerMode.NONE
var max_stickers := 4
var hits_per_sticker := 3
var current_stickers := 0
var current_sticker_hits_remaining := 0
var is_hurt := false
var is_invulnerable := false

func _ready() -> void:
	attack_hitbox.monitoring = false
	attack_hitbox.area_entered.connect(_on_attack_hitbox_area_entered)
	current_stickers = max_stickers
	current_sticker_hits_remaining = hits_per_sticker
	if sticker_health:
		max_stickers = sticker_health.max_stickers
		hits_per_sticker = sticker_health.hits_per_sticker
		invuln_time = sticker_health.invuln_time
		knockback_x = sticker_health.knockback_x
		knockback_y = sticker_health.knockback_y
		current_stickers = max_stickers
		current_sticker_hits_remaining = hits_per_sticker
		sticker_health.died.connect(_on_sticker_health_depleted)
	if hurtbox:
		hurtbox.set_owner_axel(self)
	if PowerManager.power_changed:
		PowerManager.power_changed.connect(_on_power_changed)
	_sync_power_mode_from_id(PowerManager.get_active_power())
	if has_node("DamageFlash"):
		$DamageFlash.visible = false

func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y += gravity * delta

	var dir := Input.get_axis("move_left", "move_right")

	if not is_attacking and not is_smashing and not is_hurt:
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
	if is_buffalo_mode:
		_handle_buffalo_breaks()

	move_and_slide()

func _handle_attack_input() -> void:
	if is_hurt:
		return
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
	if not attack_hitbox.monitoring:
		return
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
	take_damage(chips_damage, heavy_hit, from_position)


func take_damage(light_hits: int = 1, is_heavy: bool = false, from_position: Vector2 = Vector2.ZERO) -> void:
	if is_invulnerable:
		return

	is_hurt = true
	is_invulnerable = true
	is_attacking = false
	is_air_attacking = false
	is_smashing = false
	attack_queued = false
	_disable_attack_hitbox()

	if is_heavy:
		current_stickers -= 1
		current_sticker_hits_remaining = hits_per_sticker
	else:
		current_sticker_hits_remaining -= light_hits

	while current_sticker_hits_remaining <= 0 and current_stickers > 0:
		current_stickers -= 1
		if current_stickers > 0:
			current_sticker_hits_remaining += hits_per_sticker

	_hurt_feedback(from_position)

	if current_stickers <= 0:
		_die()
		return

	await get_tree().create_timer(invuln_time).timeout
	is_hurt = false
	is_invulnerable = false


func _hurt_feedback(from_position: Vector2) -> void:
	var dir := sign(global_position.x - from_position.x)
	if dir == 0:
		dir = -facing

	velocity.x = dir * knockback_x
	velocity.y = knockback_y

	_flash_damage()
	_flicker_brief()

func _flash_damage() -> void:
	if has_node("DamageFlash"):
		$DamageFlash.visible = true
		$DamageFlash.modulate = Color(1, 1, 1, 0.8)

		var t = create_tween()
		t.tween_property($DamageFlash, "modulate:a", 0.0, 0.08)
		await t.finished
		$DamageFlash.visible = false
	else:
		sprite.modulate = Color(1, 0.7, 0.7, 1)
		var t2 = create_tween()
		t2.tween_property(sprite, "modulate", Color.WHITE, 0.10)

func _flicker_brief() -> void:
	for i in 4:
		sprite.visible = false
		await get_tree().create_timer(0.04).timeout
		sprite.visible = true
		await get_tree().create_timer(0.04).timeout


func _die() -> void:
	queue_free()


func _on_sticker_health_depleted() -> void:
	_die()


func _on_power_changed(power_id: String, _seconds_left: float) -> void:
	_sync_power_mode_from_id(power_id)


func _sync_power_mode_from_id(power_id: String) -> void:
	if power_id == "burning_buffalo":
		current_power_mode = PowerMode.BURNING_BUFFALO
	else:
		current_power_mode = PowerMode.NONE
	_apply_power_mode_flags()


func _apply_power_mode_flags() -> void:
	is_buffalo_mode = false
	match current_power_mode:
		PowerMode.BURNING_BUFFALO:
			is_buffalo_mode = true


func _handle_buffalo_breaks() -> void:
	if abs(velocity.x) < 140.0:
		return

	for body in get_tree().get_nodes_in_group("breakable"):
		if body is Node2D:
			if body.global_position.distance_to(global_position) <= 26.0:
				if body.has_method("take_structure_hit"):
					body.take_structure_hit("buffalo")


func add_coin(value: int) -> void:
	GameState.add_coins(value)
	GameState.announce_pickup("Coins +%d" % value, Color(0.95, 0.86, 0.54, 1.0))


func add_scrap(value: int) -> void:
	GameState.add_scrap_parts(value)
	GameState.add_scrap_meter(8.0 * float(value))
	GameState.announce_pickup("Scrap +%d | Charge +%d" % [value, int(8 * value)], Color(0.73, 0.83, 0.91, 1.0))


func add_food(value: int) -> void:
	GameState.restore_health(max(1, value))
	GameState.announce_pickup("Repair snack +%d chips" % max(1, value), Color(0.9, 0.58, 0.44, 1.0))


func activate_power(power_id: String) -> void:
	PowerManager.activate_power(power_id)
