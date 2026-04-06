extends EnemyBase


func _ready() -> void:
	enemy_id = "root_crawler"
	enemy_display_name = "Root Crawler"
	enemy_category = "element_type"
	enemy_family = "element"
	enemy_type_label = "Root Crawlers"
	weakness_rule = "stomp_or_basic_attack"
	patrol_speed = 78.0
	chase_speed = 124.0
	detect_radius = 220.0
	max_health = 2
	scrap_reward = 1
	coin_reward = 1
	base_color = Color(0.31, 0.63, 0.34, 1.0)
	alert_color = Color(0.45, 0.8, 0.39, 1.0)
	log_note = "Moss-backed crawler. Tiny stride, big tell before turn."
	super._ready()
