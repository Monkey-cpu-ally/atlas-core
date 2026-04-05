extends CharacterBody2D

signal defeated

@export var max_hp: int = 12

@onready var body_visual: ColorRect = $BodyVisual

var hp: int
var is_active := false
var is_defeated := false


func _ready() -> void:
	hp = max_hp


func start_fight() -> void:
	if is_defeated:
		return
	is_active = true
	if body_visual:
		body_visual.modulate = Color(0.95, 0.78, 0.42, 1.0)


func take_hit(damage: int, _from_position: Vector2) -> void:
	if not is_active or is_defeated:
		return
	hp -= max(1, damage)
	if body_visual:
		body_visual.modulate = Color(1.0, 0.68, 0.68, 1.0)
		var t = create_tween()
		t.tween_property(body_visual, "modulate", Color(0.95, 0.78, 0.42, 1.0), 0.12)
	if hp <= 0:
		_defeat()


func _defeat() -> void:
	if is_defeated:
		return
	is_defeated = true
	is_active = false
	if body_visual:
		body_visual.modulate = Color(0.65, 0.65, 0.65, 1.0)
	defeated.emit()
