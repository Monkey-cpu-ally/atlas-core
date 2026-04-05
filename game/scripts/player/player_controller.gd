extends CharacterBody2D
class_name PlayerController

signal attack_started(attack_name: String)

@export var move_speed: float = 238.0
@export var acceleration: float = 1750.0
@export var friction: float = 2150.0
@export var jump_velocity: float = -438.0
@export var gravity: float = 1240.0
@export var coyote_time: float = 0.1
@export var jump_buffer_time: float = 0.1
@export var combo_reset_time: float = 0.55
@export var scrap_gain_per_hit: float = 4.0
@export var scrap_gain_per_kill: float = 8.0
@export var fighter_plane_meter_cost: float = 22.0

var _coyote_timer: float = 0.0
var _jump_buffer_timer: float = 0.0
var _combo_timer: float = 0.0
var _combo_step: int = 0
var _is_attacking: bool = false
var _facing_dir: int = 1
var _fighter_plane_active: bool = false
var _buffalo_charge_time: float = 0.0

@onready var _attack_area: Area2D = $AttackArea
@onready var _body: Polygon2D = $Body
@onready var _cap: Polygon2D = $Cap
@onready var _wrench: Line2D = $Wrench


func _ready() -> void:
	add_to_group("player")
	collision_layer = 2
	collision_mask = 5
	_attack_area.monitoring = false
	_attack_area.body_entered.connect(_on_attack_area_body_entered)
	PowerManager.power_expired.connect(_on_power_expired)


func _physics_process(delta: float) -> void:
	_apply_timers(delta)
	_update_vertical_motion(delta)
	_handle_jump_input()
	_handle_horizontal_input(delta)
	_handle_power_ability_input()
	_handle_attack_input()
	_handle_environment_interactions(delta)

	move_and_slide()
	_update_facing()
	_update_visual_feedback(delta)


func _apply_timers(delta: float) -> void:
	if is_on_floor():
		_coyote_timer = coyote_time
	else:
		_coyote_timer = maxf(_coyote_timer - delta, 0.0)

	_jump_buffer_timer = maxf(_jump_buffer_timer - delta, 0.0)
	_combo_timer = maxf(_combo_timer - delta, 0.0)

	if _combo_timer <= 0.0 and not _is_attacking:
		_combo_step = 0


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
	var speed_mult := PowerManager.get_move_speed_multiplier()
	var input_axis := Input.get_axis("move_left", "move_right")
	var target_speed := input_axis * move_speed * speed_mult

	if not _is_attacking:
		if absf(target_speed) > 0.001:
			velocity.x = move_toward(velocity.x, target_speed, acceleration * delta)
		else:
			velocity.x = move_toward(velocity.x, 0.0, friction * delta)
	else:
		velocity.x = move_toward(velocity.x, 0.0, friction * delta)

	if _fighter_plane_active:
		velocity.y = lerpf(velocity.y, 0.0, clampf(7.0 * delta, 0.0, 1.0))


func _handle_power_ability_input() -> void:
	if not Input.is_action_just_pressed("special"):
		return
	var active := PowerManager.get_active_power()
	if active == "":
		return

	match active:
		"fighter_plane":
			_toggle_fighter_plane()
		"burning_buffalo":
			_buffalo_charge_time = 0.24
			GameState.announce_pickup("Buffalo torque primed.", Color(0.95, 0.53, 0.3, 1.0))
		"specter_mode":
			GameState.announce_pickup("Specter drift: pass-through phase.", Color(0.73, 0.87, 0.97, 1.0))
		"super_mode":
			GameState.announce_pickup("Super Mode stable. Heavy impacts ignored.", Color(0.78, 0.86, 0.98, 1.0))
		"shadow_tag":
			GameState.announce_pickup("Shadow Tag queued on next enemy hit.", Color(0.66, 0.55, 0.95, 1.0))
		"golden_gloves":
			GameState.announce_pickup("Golden Gloves loaded. Punch class upgraded.", Color(0.95, 0.84, 0.45, 1.0))


func _toggle_fighter_plane() -> void:
	if _fighter_plane_active:
		_fighter_plane_active = false
		GameState.announce_pickup("Fighter Plane disengaged.", Color(0.64, 0.82, 0.88, 1.0))
		return

	if not GameState.consume_scrap_meter(fighter_plane_meter_cost):
		GameState.announce_pickup("Need Scrap charge for Fighter Plane.", Color(0.9, 0.45, 0.42, 1.0))
		return

	_fighter_plane_active = true
	GameState.announce_pickup("Fighter Plane engaged.", Color(0.64, 0.82, 0.88, 1.0))


func _handle_attack_input() -> void:
	if not Input.is_action_just_pressed("attack"):
		return

	if not is_on_floor() and not _fighter_plane_active:
		_start_attack("air_swat", 0.18, 1.0, "air")
		return

	if Input.is_action_pressed("down") and not _fighter_plane_active:
		_start_attack("down_smash", 0.24, 1.7, "smash")
		return

	if _combo_timer <= 0.0:
		_combo_step = 0
	_combo_step = clampi(_combo_step + 1, 1, 3)
	_combo_timer = combo_reset_time
	_start_attack("ground_combo_%d" % _combo_step, 0.14 + (_combo_step * 0.02), 1.0 + (_combo_step * 0.15), "ground")


func _handle_environment_interactions(delta: float) -> void:
	if _buffalo_charge_time > 0.0:
		_buffalo_charge_time = maxf(_buffalo_charge_time - delta, 0.0)
		if _buffalo_charge_time > 0.0:
			velocity.x = float(_facing_dir) * move_speed * 1.9

	var breakables := get_tree().get_nodes_in_group("breakable")
	for node in breakables:
		if not (node is Node2D):
			continue
		var node2d := node as Node2D
		if global_position.distance_to(node2d.global_position) > 34.0:
			continue
		if PowerManager.get_active_power() == "burning_buffalo" and _buffalo_charge_time > 0.0:
			GameState.announce_pickup("Buffalo charge shattered wall.", Color(0.96, 0.56, 0.33, 1.0))
			node.queue_free()
		elif _attack_area.monitoring and str(_attack_area.get_meta("attack_kind", "")) == "smash":
			if bool(node.get_meta("is_breakable_floor", false)):
				GameState.announce_pickup("Smash cracked weak floor.", Color(0.89, 0.71, 0.48, 1.0))
				node.queue_free()


func _start_attack(attack_name: String, active_time: float, damage_scale: float, attack_kind: String) -> void:
	if _is_attacking:
		return
	_is_attacking = true
	attack_started.emit(attack_name)

	var bonus_scale := PowerManager.get_attack_multiplier()
	var total_scale := damage_scale * bonus_scale

	_attack_area.set_meta("damage_scale", total_scale)
	_attack_area.set_meta("attack_kind", attack_kind)
	_attack_area.monitoring = true

	await get_tree().create_timer(active_time).timeout
	_attack_area.monitoring = false
	_is_attacking = false


func _update_facing() -> void:
	if velocity.x > 8.0:
		_facing_dir = 1
	elif velocity.x < -8.0:
		_facing_dir = -1
	scale.x = float(_facing_dir)


func _update_visual_feedback(_delta: float) -> void:
	var active := PowerManager.get_active_power()
	match active:
		"burning_buffalo":
			_body.color = Color(0.91, 0.4, 0.28, 1.0)
			_wrench.default_color = Color(1.0, 0.77, 0.42, 1.0)
		"shadow_tag":
			_body.color = Color(0.72, 0.63, 0.95, 1.0)
			_wrench.default_color = Color(0.85, 0.75, 0.99, 1.0)
		"golden_gloves":
			_body.color = Color(0.95, 0.78, 0.42, 1.0)
			_wrench.default_color = Color(1.0, 0.93, 0.62, 1.0)
		"super_mode":
			_body.color = Color(0.84, 0.91, 1.0, 1.0)
			_wrench.default_color = Color(0.92, 0.97, 1.0, 1.0)
		"specter_mode":
			_body.color = Color(0.8, 0.91, 1.0, 0.7)
			_wrench.default_color = Color(0.89, 0.97, 1.0, 0.8)
		"fighter_plane":
			_body.color = Color(0.67, 0.83, 0.9, 1.0)
			_wrench.default_color = Color(0.85, 0.97, 1.0, 1.0)
		_:
			_body.color = Color(0.835, 0.357, 0.333, 1.0)
			_wrench.default_color = Color(0.82, 0.84, 0.87, 1.0)
	_cap.color = Color(0.74, 0.13, 0.18, 1.0)


func receive_contact_hit(chip_damage: int = 1, heavy_hit: bool = false) -> void:
	if PowerManager.is_invulnerable():
		return
	if PowerManager.is_intangible():
		return
	GameState.apply_hit(chip_damage, heavy_hit)


func _on_attack_area_body_entered(body: Node) -> void:
	if not body.has_method("receive_hit"):
		return

	var damage_scale := float(_attack_area.get_meta("damage_scale", 1.0))
	var attack_kind := str(_attack_area.get_meta("attack_kind", "ground"))
	var info := body.receive_hit(damage_scale, attack_kind)
	if typeof(info) == TYPE_DICTIONARY:
		if bool(info.get("hit", false)):
			GameState.add_scrap_meter(scrap_gain_per_hit)
		if bool(info.get("defeated", false)):
			GameState.add_scrap_meter(scrap_gain_per_kill)
		if bool(info.get("shadow_tag_eligible", true)):
			PowerManager.apply_shadow_tag_to_enemy(body)


func _on_power_expired(power_id: String) -> void:
	if power_id == "fighter_plane":
		_fighter_plane_active = false
