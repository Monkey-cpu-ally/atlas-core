extends Area2D
class_name EnemyHurtbox

func take_hit(damage: int, from_position: Vector2) -> void:
	var owner_enemy = get_parent()
	if owner_enemy and owner_enemy.has_method("take_hit"):
		owner_enemy.take_hit(damage, from_position)
