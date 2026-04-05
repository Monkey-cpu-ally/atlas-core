extends CharacterBody2D
class_name BasicEnemy

signal damaged(current_health: int)
signal died

@export var move_speed: float = 70.0
@export var gravity: float = 1000.0
@export var max_health: int = 3
@export var hit_invuln_time: float = 0.12
@export var recoil_speed: float = 170.0
@export var recoil_lift: float = -120.0
@export var ledge_check_offset: float = 14.0
@export var ledge_check_depth: float = 24.0

var direction: int = -1
var current_health: int = 0
var _hit_invuln_timer: float = 0.0
var _recoil_timer: float = 0.0

@onready var animated_sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var ledge_detector: RayCast2D = $LedgeDetector
@onready var hurtbox: EnemyHurtbox = $Hurtbox


func _ready() -> void:
	current_health = max_health
	add_to_group("enemies")
	if hurtbox:
		hurtbox.set_enemy(self)


func _physics_process(delta: float) -> void:
	_hit_invuln_timer = maxf(_hit_invuln_timer - delta, 0.0)
	_recoil_timer = maxf(_recoil_timer - delta, 0.0)

	if not is_on_floor():
		velocity.y += gravity * delta

	if _recoil_timer <= 0.0:
		velocity.x = move_speed * float(direction)

	_update_ledge_detector()
	move_and_slide()
	_update_facing()

	if _recoil_timer <= 0.0 and is_on_floor():
		if is_on_wall() or not ledge_detector.is_colliding():
			_flip_direction()


func take_attack_hit(attack_mode: String) -> void:
	if _hit_invuln_timer > 0.0:
		return
	_hit_invuln_timer = hit_invuln_time

	var damage := _damage_from_mode(attack_mode)
	current_health -= damage
	damaged.emit(current_health)

	_apply_recoil_from_mode(attack_mode)
	if current_health <= 0:
		died.emit()
		queue_free()


func _damage_from_mode(mode: String) -> int:
	match mode:
		"ground_1":
			return 1
		"ground_2":
			return 1
		"ground_3":
			return 2
		"air":
			return 1
		"smash":
			return 2
		_:
			return 1


func _apply_recoil(attack_origin: Vector2) -> void:
	var recoil_dir := signf(global_position.x - attack_origin.x)
	if is_zero_approx(recoil_dir):
		recoil_dir = float(-direction)
	velocity.x = recoil_speed * recoil_dir
	velocity.y = recoil_lift
	_recoil_timer = 0.12

func _apply_recoil_from_mode(_attack_mode: String) -> void:
	var recoil_dir := float(-direction)
	velocity.x = recoil_speed * recoil_dir
	velocity.y = recoil_lift
	_recoil_timer = 0.12


func _update_ledge_detector() -> void:
	if not ledge_detector:
		return
	ledge_detector.position.x = absf(ledge_check_offset) * float(direction)
	ledge_detector.position.y = 0.0
	ledge_detector.target_position = Vector2(0.0, ledge_check_depth)
	ledge_detector.force_raycast_update()


func _flip_direction() -> void:
	direction *= -1


func _update_facing() -> void:
	if animated_sprite:
		animated_sprite.flip_h = direction < 0
