extends Area2D

func is_player_attack() -> bool:
	return true

var _hit_targets: Dictionary = {}

func _ready() -> void:
	monitoring = false
	monitorable = true
	area_entered.connect(_on_area_entered)


func _process(_delta: float) -> void:
	if not monitoring and not _hit_targets.is_empty():
		_hit_targets.clear()


func _on_area_entered(area: Area2D) -> void:
	if not monitoring:
		return

	var enemy_owner: Node = area.get_meta("enemy_owner", null)
	if enemy_owner == null:
		return
	if not enemy_owner.has_method("take_attack_hit"):
		return

	var id := enemy_owner.get_instance_id()
	if _hit_targets.has(id):
		return
	_hit_targets[id] = true

	var mode := str(get_meta("attack_mode", "ground_1"))
	enemy_owner.take_attack_hit(mode)
