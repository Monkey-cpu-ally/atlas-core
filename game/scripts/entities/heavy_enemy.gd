extends EnemyBase


func _ready() -> void:
	enemy_id = "heavy_enemy"
	enemy_display_name = "Heavy Chassis"
	enemy_family = EnemyFamily.MACHINE
	enemy_family_name = "Machine"
	enemy_category = "Machine - Heavy enemies"
	weakness_rule = "empowered_attack_or_burning_buffalo"
	patrol_speed = 58.0
	chase_speed = 88.0
	detect_radius = 260.0
	max_health = 5
	scrap_reward = 3
	coin_reward = 2
	base_color = Color(0.4, 0.51, 0.63, 1.0)
	alert_color = Color(0.64, 0.78, 0.4, 1.0)
	log_note = "Chunky shell shrugs weak taps. Empowered impact pops the seams."
	super._ready()
