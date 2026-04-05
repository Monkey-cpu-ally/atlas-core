extends Area2D
class_name AxelHurtbox

var _owner_axel: Node
var is_invulnerable := false

func _ready() -> void:
	monitoring = true
	monitorable = true
	area_entered.connect(_on_hurtbox_area_entered)


func set_owner_axel(owner: Node) -> void:
	_owner_axel = owner


func take_damage(light_hits: int, is_heavy: bool, from_position: Vector2) -> void:
	if _owner_axel == null:
		_owner_axel = get_parent()
	if _owner_axel == null:
		return
	if _owner_axel.has_method("receive_contact_hit"):
		_owner_axel.receive_contact_hit(light_hits, is_heavy, from_position)


func _on_hurtbox_area_entered(area: Area2D) -> void:
	if is_invulnerable:
		return
	if not area.has_method("get_damage_data"):
		return

	var data = area.get_damage_data()
	take_damage(
		int(data.get("light_hits", 1)),
		bool(data.get("is_heavy", false)),
		Vector2(data.get("from_position", area.global_position))
	)
