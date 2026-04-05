extends Area2D
class_name EnemyContactHitbox

@export var chip_damage: int = 1
@export var heavy_hit: bool = false

func _ready() -> void:
	monitoring = true
	monitorable = true
	set_meta("contact_damage", chip_damage)
	set_meta("heavy_hit", heavy_hit)

func is_enemy_contact() -> bool:
	return true


func get_knockback(hit_position: Vector2) -> Vector2:
	var dir := signf(hit_position.x - global_position.x)
	if is_zero_approx(dir):
		dir = 1.0
	var x_force := 140.0 * dir
	var y_force := -130.0
	if heavy_hit:
		x_force *= 1.35
		y_force = -150.0
	return Vector2(x_force, y_force)


func set_damage_profile(chips: int, is_heavy: bool) -> void:
	chip_damage = max(1, chips)
	heavy_hit = is_heavy
	set_meta("contact_damage", chip_damage)
	set_meta("heavy_hit", heavy_hit)
