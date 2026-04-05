extends CharacterBody2D

@export var move_speed: float = 30.0
@export var gravity: float = 900.0
@export var max_hp: int = 2

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var floor_ray: RayCast2D = $FloorRay
@onready var wall_ray: RayCast2D = $WallRay
@onready var hurtbox: EnemyHurtbox = $Hurtbox

var hp: int
var facing := -1
var is_dead := false
var invulnerable := false


func _ready() -> void:
	hp = max_hp
	add_to_group("enemies")
	if hurtbox:
		hurtbox.set_enemy(self)


func _physics_process(delta: float) -> void:
	if is_dead:
		return

	if not is_on_floor():
		velocity.y += gravity * delta

	velocity.x = facing * move_speed

	var should_turn := false
	if wall_ray.is_colliding():
		should_turn = true
	if not floor_ray.is_colliding():
		should_turn = true

	if should_turn:
		turn_around()

	move_and_slide()
	_update_anim()


func turn_around() -> void:
	facing *= -1
	floor_ray.target_position.x *= -1
	wall_ray.target_position.x *= -1


func take_hit(damage: int, from_position: Vector2) -> void:
	if is_dead or invulnerable:
		return

	hp -= damage
	invulnerable = true

	var dir := sign(global_position.x - from_position.x)
	if dir == 0:
		dir = 1

	velocity.x = dir * 90.0
	velocity.y = -80.0

	if sprite:
		sprite.modulate = Color(1.0, 0.7, 0.7)
		var t = create_tween()
		t.tween_property(sprite, "modulate", Color.WHITE, 0.10)

	if hp <= 0:
		die()
		return

	await get_tree().create_timer(0.18).timeout
	invulnerable = false


func die() -> void:
	is_dead = true
	queue_free()


func _update_anim() -> void:
	sprite.flip_h = facing > 0
	if sprite.sprite_frames and sprite.sprite_frames.has_animation("walk"):
		sprite.play("walk")
