extends EnemyBase


func _ready() -> void:
	enemy_id = "gear_bug"
	enemy_display_name = "Gear Bug"
	enemy_category = "Gear Bugs"
	weakness_rule = "attackable_back_seam"
	patrol_speed = 96.0
	chase_speed = 160.0
	detect_radius = 260.0
	max_health = 2
	scrap_reward = 2
	coin_reward = 2
	base_color = Color(0.42, 0.49, 0.56, 1.0)
	alert_color = Color(0.58, 0.66, 0.75, 1.0)
	log_note = "Wheel-joint twitch before burst. Back seam takes the hit."
	super._ready()
