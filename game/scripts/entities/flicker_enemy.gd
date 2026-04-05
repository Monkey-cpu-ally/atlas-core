extends EnemyBase


func _ready() -> void:
	enemy_id = "flicker_enemy"
	enemy_display_name = "Flicker Unit"
	enemy_category = "Flicker enemies"
	weakness_rule = "attack_after_blink"
	patrol_speed = 62.0
	chase_speed = 112.0
	detect_radius = 235.0
	max_health = 2
	scrap_reward = 2
	coin_reward = 1
	base_color = Color(0.58, 0.44, 0.78, 1.0)
	alert_color = Color(0.76, 0.62, 0.94, 1.0)
	log_note = "Blink shell jitters violet. Hit right after the dim frame."
	super._ready()

