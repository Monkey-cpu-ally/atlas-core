extends Area2D
class_name AxelAttackHitbox

var _shape: CollisionShape2D
var _already_hit: Dictionary = {}

const ATTACK_MODE_DATA := {
	"ground_1": {"damage": 1.0, "kind": "ground"},
	"ground_2": {"damage": 1.2, "kind": "ground"},
	"ground_3": {"damage": 1.5, "kind": "ground"},
	"air": {"damage": 1.1, "kind": "air"},
	"smash": {"damage": 1.8, "kind": "smash"},
}


func _ready() -> void:
	monitoring = false
	monitorable = true
	_shape = get_node_or_null("CollisionShape2D") as CollisionShape2D
	if _shape and _shape.shape is RectangleShape2D:
		_set_shape_size(Vector2(34, 24))
	body_entered.connect(_on_body_entered)


func start_attack(attack_mode: String = "") -> void:
	_already_hit.clear()
	set_meta("attack_mode", attack_mode)
	monitoring = true


func end_attack() -> void:
	monitoring = false
	set_meta("attack_mode", "")
	_already_hit.clear()


func _on_body_entered(body: Node) -> void:
	if _already_hit.has(body):
		return
	_already_hit[body] = true

	if not body.has_method("receive_hit"):
		return
	var mode := str(get_meta("attack_mode", "ground_1"))
	var mode_data := ATTACK_MODE_DATA.get(mode, ATTACK_MODE_DATA["ground_1"])
	body.receive_hit(float(mode_data["damage"]), str(mode_data["kind"]))
