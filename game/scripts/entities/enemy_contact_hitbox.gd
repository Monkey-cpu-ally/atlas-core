extends Area2D

@export var light_hits: int = 1
@export var is_heavy: bool = false

func is_enemy_contact() -> bool:
	return true

func get_damage_data() -> Dictionary:
	return {
		"light_hits": light_hits,
		"is_heavy": is_heavy,
		"from_position": global_position
	}
