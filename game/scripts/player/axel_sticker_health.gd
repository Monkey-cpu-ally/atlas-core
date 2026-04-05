extends Node
class_name AxelStickerHealth

signal health_changed(stickers: Array[int], total_chips: int)
signal damaged(heavy_hit: bool, chips_lost: int)
signal died

@export var sticker_count: int = 4
@export var chips_per_sticker: int = 3
@export var invulnerability_time: float = 0.55
@export var knockback_x: float = 180.0
@export var knockback_y: float = -120.0

var stickers: Array[int] = []
var invulnerable: bool = false
var _owner_axel: CharacterBody2D


func _ready() -> void:
	_owner_axel = get_parent() as CharacterBody2D
	_reset_health()


func is_alive() -> bool:
	return get_total_chips() > 0


func is_depleted() -> bool:
	return not is_alive()


func get_total_chips() -> int:
	var total := 0
	for chips in stickers:
		total += chips
	return total


func take_hit(chips: int) -> bool:
	if invulnerable or not is_alive():
		return false
	var removed := _remove_chips(max(1, chips))
	_start_invulnerability()
	damaged.emit(false, removed)
	_emit_health_changed()
	if not is_alive():
		died.emit()
	return removed > 0


func apply_light_hit(from_position: Vector2, chips: int = 1) -> void:
	if invulnerable or not is_alive():
		return
	var removed := _remove_chips(max(1, chips))
	_apply_knockback(from_position)
	_start_invulnerability()
	damaged.emit(false, removed)
	_emit_health_changed()
	if not is_alive():
		died.emit()


func apply_heavy_hit(from_position: Vector2) -> void:
	if invulnerable or not is_alive():
		return
	var removed := _remove_full_sticker()
	_apply_knockback(from_position)
	_start_invulnerability()
	damaged.emit(true, removed)
	_emit_health_changed()
	if not is_alive():
		died.emit()


func _reset_health() -> void:
	stickers.clear()
	for i in range(sticker_count):
		stickers.append(chips_per_sticker)
	_emit_health_changed()


func _remove_chips(amount: int) -> int:
	var remaining := amount
	var removed := 0
	for i in range(sticker_count):
		if remaining <= 0:
			break
		if stickers[i] <= 0:
			continue
		var loss := min(stickers[i], remaining)
		stickers[i] -= loss
		remaining -= loss
		removed += loss
	return removed


func _remove_full_sticker() -> int:
	for i in range(sticker_count):
		if stickers[i] <= 0:
			continue
		var removed := stickers[i]
		stickers[i] = 0
		return removed
	return 0


func _apply_knockback(from_position: Vector2) -> void:
	if _owner_axel == null:
		return
	var dir := signf(_owner_axel.global_position.x - from_position.x)
	if is_zero_approx(dir):
		dir = 1.0
	_owner_axel.velocity.x = dir * knockback_x
	_owner_axel.velocity.y = knockback_y


func _start_invulnerability() -> void:
	invulnerable = true
	await get_tree().create_timer(invulnerability_time).timeout
	invulnerable = false


func _emit_health_changed() -> void:
	health_changed.emit(stickers.duplicate(), get_total_chips())
