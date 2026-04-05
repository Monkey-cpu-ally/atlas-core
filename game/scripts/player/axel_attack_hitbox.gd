extends Area2D

func is_player_attack() -> bool:
	return true

var _hit_targets: Dictionary = {}
const MODE_DAMAGE := {
	"ground_1": 1,
	"ground_2": 1,
	"ground_3": 2,
	"air": 1,
	"smash": 2,
}

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
	if not area.has_method("take_hit"):
		return

	var id := area.get_instance_id()
	if _hit_targets.has(id):
		return
	_hit_targets[id] = true

	var mode := str(get_meta("attack_mode", "ground_1"))
	var damage := int(MODE_DAMAGE.get(mode, 1))
	area.take_hit(damage, global_position)
