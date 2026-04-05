extends Area2D
class_name AxelHurtbox

var _owner_axel: Node

func _ready() -> void:
	monitoring = true
	monitorable = true
	area_entered.connect(_on_hurtbox_area_entered)


func set_owner_axel(owner: Node) -> void:
	_owner_axel = owner


func _on_hurtbox_area_entered(area: Area2D) -> void:
	if _owner_axel == null:
		_owner_axel = get_parent()
	if not area.has_method("is_enemy_contact"):
		return
	if not bool(area.is_enemy_contact()):
		return
	if not area.has_method("get_damage_data"):
		return

	var damage_data := area.get_damage_data()
	var chips_damage := int(damage_data.get("light_hits", 1))
	var heavy_hit := bool(damage_data.get("is_heavy", false))
	var from_position := Vector2(damage_data.get("from_position", area.global_position))
	if _owner_axel.has_method("receive_contact_hit"):
		_owner_axel.receive_contact_hit(chips_damage, heavy_hit, from_position)
