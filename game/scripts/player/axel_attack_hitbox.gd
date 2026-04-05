extends Area2D

func is_player_attack() -> bool:
	return true

func _ready() -> void:
	monitoring = false
	monitorable = true
