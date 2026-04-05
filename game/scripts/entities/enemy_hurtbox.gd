extends Area2D
class_name EnemyHurtbox

var _enemy: Node


func _ready() -> void:
	monitoring = true
	monitorable = true
	set_meta("enemy_owner", get_parent())


func set_enemy(enemy: Node) -> void:
	_enemy = enemy
	set_meta("enemy_owner", enemy)
