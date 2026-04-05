extends CharacterBody2D

signal defeated

@export var max_hp: int = 12
@export var attack_phase_time: float = 1.4
@export var vulnerable_phase_time: float = 1.0
@export var recover_phase_time: float = 0.8

@onready var body_visual: ColorRect = $BodyVisual
@onready var weak_point: ColorRect = $WeakPoint

enum BossPhase {
	ATTACK,
	VULNERABLE,
	RECOVER
}

const ATTACK := BossPhase.ATTACK
const VULNERABLE := BossPhase.VULNERABLE
const RECOVER := BossPhase.RECOVER

var hp: int
var is_active := false
var is_defeated := false
var state: BossPhase = ATTACK
var _phase_timer_running := false


func _ready() -> void:
	hp = max_hp


func start_fight() -> void:
	if is_defeated:
		return
	is_active = true
	_set_phase(ATTACK)
	if not _phase_timer_running:
		_phase_cycle_loop()


func take_hit(damage: int, _from_position: Vector2) -> void:
	if not is_active or is_defeated:
		return
	if not (state == VULNERABLE):
		return
	hp -= max(1, damage)
	if body_visual:
		body_visual.modulate = Color(1.0, 0.68, 0.68, 1.0)
		var t = create_tween()
		t.tween_property(body_visual, "modulate", _phase_body_color(state), 0.12)
	if hp <= 0:
		_defeat()


func _defeat() -> void:
	if is_defeated:
		return
	is_defeated = true
	is_active = false
	_phase_timer_running = false
	if body_visual:
		body_visual.modulate = Color(0.65, 0.65, 0.65, 1.0)
	if weak_point:
		weak_point.modulate = Color(0.65, 0.65, 0.65, 0.7)
	defeated.emit()


func _phase_cycle_loop() -> void:
	_phase_timer_running = true
	while is_active and not is_defeated:
		_set_phase(ATTACK)
		await get_tree().create_timer(attack_phase_time).timeout
		if not is_active or is_defeated:
			break
		_set_phase(VULNERABLE)
		await get_tree().create_timer(vulnerable_phase_time).timeout
		if not is_active or is_defeated:
			break
		_set_phase(RECOVER)
		await get_tree().create_timer(recover_phase_time).timeout
	_phase_timer_running = false


func _set_phase(phase: BossPhase) -> void:
	state = phase
	if body_visual:
		body_visual.modulate = _phase_body_color(phase)
	if weak_point:
		weak_point.modulate = _phase_weak_point_color(phase)


func _phase_body_color(phase: BossPhase) -> Color:
	match phase:
		BossPhase.ATTACK:
			return Color(0.95, 0.78, 0.42, 1.0)
		BossPhase.VULNERABLE:
			return Color(0.95, 0.62, 0.52, 1.0)
		BossPhase.RECOVER:
			return Color(0.72, 0.72, 0.78, 1.0)
	return Color(0.95, 0.78, 0.42, 1.0)


func _phase_weak_point_color(phase: BossPhase) -> Color:
	match phase:
		BossPhase.ATTACK:
			return Color(0.86, 0.31, 0.24, 0.55)
		BossPhase.VULNERABLE:
			return Color(1.0, 0.2, 0.2, 0.95)
		BossPhase.RECOVER:
			return Color(0.86, 0.31, 0.24, 0.35)
	return Color(0.86, 0.31, 0.24, 0.55)
