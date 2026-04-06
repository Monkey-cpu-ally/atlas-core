extends CharacterBody2D
class_name EnemyBase

@export var enemy_id: String = "enemy"
@export var enemy_display_name: String = "Enemy Unit"
@export var enemy_category: String = "generic"
@export var enemy_family: String = "machine"
@export var weakness_rule: String = "attackable"
@export var patrol_speed: float = 72.0
@export var chase_speed: float = 112.0
@export var detect_radius: float = 210.0
@export var max_health: int = 2
@export var scrap_reward: int = 1
@export var coin_reward: int = 1
@export var enemy_size_class: String = "weak"
@export var base_color: Color = Color(0.46, 0.53, 0.58, 1.0)
@export var alert_color: Color = Color(0.62, 0.71, 0.76, 1.0)
@export var log_note: String = "Pattern noted."

var gravity: float = 1300.0
var direction: int = -1
var state: String = "patrol"
var current_health: int = 2
var player: CharacterBody2D
var hit_cooldown: float = 0.0
var contact_cooldown: float = 0.0
var flicker_cycle: float = 0.0
var flicker_open: bool = true

@onready var body_poly: Polygon2D = $Body


func _ready() -> void:
	add_to_group("enemies")
	collision_layer = 4
	collision_mask = 3
	current_health = max_health
	body_poly.color = base_color


func set_player_target(target: CharacterBody2D) -> void:
	player = target


func _physics_process(delta: float) -> void:
	if player == null:
		player = get_tree().get_first_node_in_group("player") as CharacterBody2D

	hit_cooldown = maxf(hit_cooldown - delta, 0.0)
	contact_cooldown = maxf(contact_cooldown - delta, 0.0)

	if not is_on_floor():
		velocity.y += gravity * delta
	else:
		velocity.y = 0.0

	_update_state_logic(delta)
	move_and_slide()
	_try_contact_damage()
	_restore_visual_after_hit()


func _update_state_logic(delta: float) -> void:
	if enemy_category.to_lower() == "flicker enemies":
		flicker_cycle -= delta
		if flicker_cycle <= 0.0:
			flicker_cycle = 0.95
			flicker_open = not flicker_open
			body_poly.modulate.a = 1.0 if flicker_open else 0.32

	if player != null and global_position.distance_to(player.global_position) <= detect_radius:
		state = "chase"
	else:
		state = "patrol"

	if state == "chase" and player != null:
		direction = 1 if player.global_position.x >= global_position.x else -1
		velocity.x = direction * chase_speed
		body_poly.color = alert_color
	else:
		velocity.x = direction * patrol_speed
		if is_on_wall():
			direction *= -1
		body_poly.color = base_color


func receive_hit(damage_scale: float, attack_kind: String) -> Dictionary:
	var result := {"hit": false, "defeated": false, "shadow_tag_eligible": true}
	if hit_cooldown > 0.0:
		return result
	if enemy_category.to_lower() == "flicker enemies" and not flicker_open:
		GameState.announce_pickup("Flicker shell sealed. Wait for the blink dip.", Color(0.74, 0.66, 0.94, 1.0))
		result["shadow_tag_eligible"] = false
		return result

	if enemy_category.to_lower() == "heavy enemies":
		var empowered := (
			PowerManager.get_active_power() == "golden_gloves"
			or PowerManager.get_active_power() == "burning_buffalo"
		)
		if not empowered:
			GameState.announce_pickup("Heavy shell shrugged it off. Bring empowered force.", Color(0.85, 0.77, 0.55, 1.0))
			result["shadow_tag_eligible"] = false
			return result

	if attack_kind == "stomp" and weakness_rule.find("stomp") == -1:
		result["shadow_tag_eligible"] = false
		return result

	var damage := max(1, int(round(damage_scale)))
	if enemy_category.to_lower() == "heavy enemies":
		damage += 1

	var hit_origin: Vector2 = player.global_position if player != null else global_position
	var defeated := _apply_direct_hit(damage, hit_origin)
	result["hit"] = true

	if defeated:
		result["defeated"] = true

	return result


func take_hit(damage: int, from_position: Vector2) -> void:
	if is_dead() or is_invulnerable():
		return
	_apply_direct_hit(max(1, damage), from_position)


func take_percent_damage(percent: float, from_position: Vector2) -> void:
	if is_dead() or is_invulnerable():
		return
	var damage: int = max(1, int(ceil(float(max_health) * percent)))
	take_hit(damage, from_position)


func is_dead() -> bool:
	return current_health <= 0


func is_invulnerable() -> bool:
	return hit_cooldown > 0.0


func is_weak_enemy() -> bool:
	return enemy_size_class.to_lower() == "weak"


func is_large_enemy() -> bool:
	return enemy_size_class.to_lower() == "large"


func _try_contact_damage() -> void:
	if player == null or contact_cooldown > 0.0:
		return
	if global_position.distance_to(player.global_position) > 22.0:
		return
	if not player.has_method("receive_contact_hit"):
		return

	var heavy := enemy_category.to_lower() == "heavy enemies"
	player.receive_contact_hit(1, heavy)
	contact_cooldown = 0.75 if heavy else 0.45


func _die() -> void:
	GameState.add_scrap_parts(scrap_reward)
	GameState.add_coins(coin_reward)
	GameState.add_scrap_meter(9.0)
	FlightLog.add_enemy_note("%s [%s]" % [enemy_display_name, _family_display()], log_note)
	GameState.announce_pickup("%s cracked open (+%d scrap)" % [enemy_display_name, scrap_reward], Color(0.74, 0.83, 0.91, 1.0))
	queue_free()


func _restore_visual_after_hit() -> void:
	if hit_cooldown > 0.0:
		return
	body_poly.color = alert_color if state == "chase" else base_color


func _family_display() -> String:
	match enemy_family.to_lower():
		"element":
			return "Element"
		"dinosaur":
			return "Dinosaur"
		"machine":
			return "Machine"
		_:
			return "Unknown"


func _apply_direct_hit(damage: int, from_position: Vector2) -> bool:
	current_health -= max(1, damage)
	hit_cooldown = 0.1
	var dir: float = sign(global_position.x - from_position.x)
	if is_zero_approx(dir):
		dir = -1.0 if direction >= 0 else 1.0
	velocity = Vector2(dir * 95.0, -145.0)
	body_poly.color = body_poly.color.lightened(0.22)
	if current_health <= 0:
		_die()
		return true
	return false
