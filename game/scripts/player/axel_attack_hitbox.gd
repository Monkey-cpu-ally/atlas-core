extends Area2D
class_name AxelAttackHitbox

var _shape: CollisionShape2D
var _attack_kind: String = "ground"
var _attack_damage: float = 1.0
var _already_hit: Dictionary = {}


func _ready() -> void:
	monitoring = false
	monitorable = true
	_shape = get_node_or_null("CollisionShape2D") as CollisionShape2D
	body_entered.connect(_on_body_entered)


func start_attack(attack_data: Dictionary, facing_dir: int) -> void:
	# attack_data is intentionally dictionary-based to make adding future
	# attack types easy without changing this method's signature.
	_already_hit.clear()
	_attack_kind = str(attack_data.get("kind", "ground"))
	_attack_damage = float(attack_data.get("damage", 1.0))

	var offset: Vector2 = attack_data.get("offset", Vector2.ZERO)
	var size: Vector2 = attack_data.get("size", Vector2(28, 20))

	position.x = absf(offset.x) * float(signi(facing_dir))
	position.y = offset.y
	_set_shape_size(size)
	monitoring = true


func end_attack() -> void:
	monitoring = false
	_already_hit.clear()


func _set_shape_size(size: Vector2) -> void:
	if _shape == null:
		return
	var rect := _shape.shape as RectangleShape2D
	if rect == null:
		return
	rect.size = size


func _on_body_entered(body: Node) -> void:
	if _already_hit.has(body):
		return
	_already_hit[body] = true

	if not body.has_method("receive_hit"):
		return
	body.receive_hit(_attack_damage, _attack_kind)
