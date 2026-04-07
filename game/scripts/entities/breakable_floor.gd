extends StaticBody2D

@export var hp: int = 1
@export var break_by_smash_only: bool = true

@onready var crack_overlay = $CrackOverlay

var broken := false


func _ready() -> void:
	add_to_group("breakable")


func take_structure_hit(source: String = "normal") -> void:
	if broken:
		return

	if break_by_smash_only and source != "smash":
		return

	hp -= 1
	_update_crack_visual()

	if hp <= 0:
		break_floor()


func break_floor() -> void:
	broken = true

	# optional effect later
	queue_free()


func _update_crack_visual() -> void:
	if crack_overlay:
		crack_overlay.modulate.a = min(crack_overlay.modulate.a + 0.4, 1.0)
