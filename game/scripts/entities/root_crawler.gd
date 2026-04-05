extends EnemyBase


func _ready() -> void:
	enemy_id = "root_crawler"
	enemy_display_name = "Root Crawler"
	enemy_category = "Root Crawlers"
	weakness_rule = "stomp_or_basic_attack"
	patrol_speed = 78.0
	chase_speed = 124.0
	detect_radius = 220.0
	max_health = 2
	scrap_reward = 1
	coin_reward = 1
	base_color = Color(0.345, 0.486, 0.329, 1.0)
	alert_color = Color(0.47, 0.64, 0.39, 1.0)
	log_note = "Burrow tracks stay shallow. Slow march. Folded from above."
	super._ready()
