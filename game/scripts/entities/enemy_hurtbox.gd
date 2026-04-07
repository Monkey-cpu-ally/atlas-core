extends Area2D
class_name EnemyHurtbox

var _owner_enemy: Node = null


func set_enemy(enemy: Node) -> void:
	_owner_enemy = enemy


func take_hit(damage: int, from_position: Vector2) -> void:
	var owner_enemy: Node = _owner_enemy if _owner_enemy != null else get_parent()
	if owner_enemy and owner_enemy.has_method("take_hit"):
		owner_enemy.take_hit(damage, from_position)
