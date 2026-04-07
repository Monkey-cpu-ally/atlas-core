extends EnemyBase


func _ready() -> void:
	enemy_id = "gear_bug"
	enemy_display_name = "Gear Bug"
	enemy_category = "Machine"
	weakness_rule = "attackable_back_seam"
	patrol_speed = 96.0
	chase_speed = 160.0
	detect_radius = 260.0
	max_health = 2
	scrap_reward = 2
	coin_reward = 2
	base_color = Color(0.29, 0.66, 0.69, 1.0)
	alert_color = Color(0.46, 0.84, 0.89, 1.0)
	log_note = "Turquoise casing, fast jitter. Back seam pops first."
	super._ready()
