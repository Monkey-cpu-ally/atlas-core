extends Area2D
class_name AxelHurtbox

var _owner_axel: Node
var _recent_hits: Dictionary = {}


func _ready() -> void:
	monitoring = true
	monitorable = true
	area_entered.connect(_on_area_entered)


func set_owner_axel(owner: Node) -> void:
	_owner_axel = owner


func _physics_process(delta: float) -> void:
	if _recent_hits.is_empty():
		return
	var next_cache: Dictionary = {}
	for id in _recent_hits.keys():
		var ttl := float(_recent_hits[id]) - delta
		if ttl > 0.0:
			next_cache[id] = ttl
	_recent_hits = next_cache


func _on_area_entered(area: Area2D) -> void:
	if _owner_axel == null:
		return
	if not area.has_method("is_enemy_contact"):
		return
	if not bool(area.is_enemy_contact()):
		return

	var hit_id := area.get_instance_id()
	if _recent_hits.has(hit_id):
		return
	_recent_hits[hit_id] = 0.12

	if _owner_axel.has_method("receive_contact_hit"):
		var chips_damage := int(area.get_meta("contact_damage", 1))
		var heavy_hit := bool(area.get_meta("heavy_hit", false))
		_owner_axel.receive_contact_hit(chips_damage, heavy_hit, area.global_position)
