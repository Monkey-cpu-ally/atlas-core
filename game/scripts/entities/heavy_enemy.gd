extends EnemyBase


func _ready() -> void:
	enemy_id = "heavy_enemy"
	enemy_display_name = "Heavy Chassis"
	enemy_category = "Heavy enemies"
	weakness_rule = "empowered_attack_or_burning_buffalo"
	patrol_speed = 58.0
	chase_speed = 88.0
	detect_radius = 260.0
	max_health = 5
	scrap_reward = 3
	coin_reward = 2
	base_color = Color(0.42, 0.42, 0.48, 1.0)
	alert_color = Color(0.63, 0.57, 0.41, 1.0)
	log_note = "Front plating drinks light hits. Needs empowered force."
	super._ready()
