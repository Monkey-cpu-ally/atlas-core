extends Node

signal stats_changed(snapshot: Dictionary)
signal pickup_noted(text: String, color: Color)
signal damage_noted(text: String)

const MAX_STICKERS: int = 4
const CHIP_PER_STICKER: int = 4
const MAX_SCRAP_METER: float = 100.0

var sticker_chips: Array[int] = []
var coins: int = 0
var scrap_parts: int = 0
var scrap_meter: float = 0.0


func _ready() -> void:
	reset_run()


func reset_run() -> void:
	sticker_chips = []
	for i in range(MAX_STICKERS):
		sticker_chips.append(CHIP_PER_STICKER)
	coins = 0
	scrap_parts = 0
	scrap_meter = 0.0
	_emit_stats()


func apply_hit(chip_damage: int = 1, heavy_hit: bool = false) -> void:
	if is_player_down():
		return
	if heavy_hit:
		_remove_full_sticker()
		damage_noted.emit("Heavy impact tore a full sticker.")
	else:
		_remove_chips(max(1, chip_damage))
		damage_noted.emit("Chip damage on current sticker.")
	_emit_stats()


func restore_health(chips: int = 1) -> void:
	var remaining: int = max(1, chips)
	for i in range(MAX_STICKERS - 1, -1, -1):
		if remaining <= 0:
			break
		var gap := CHIP_PER_STICKER - sticker_chips[i]
		if gap <= 0:
			continue
		var recovered: int = min(gap, remaining)
		sticker_chips[i] += recovered
		remaining -= recovered
	_emit_stats()


func add_coins(amount: int = 1) -> void:
	coins = max(0, coins + amount)
	_emit_stats()


func add_scrap_parts(amount: int = 1) -> void:
	scrap_parts = max(0, scrap_parts + amount)
	_emit_stats()


func add_scrap_meter(amount: float) -> void:
	scrap_meter = clampf(scrap_meter + amount, 0.0, MAX_SCRAP_METER)
	_emit_stats()


func consume_scrap_meter(amount: float) -> bool:
	if scrap_meter < amount:
		return false
	scrap_meter -= amount
	_emit_stats()
	return true


func get_health_fraction() -> float:
	return float(get_total_health_chips()) / float(MAX_STICKERS * CHIP_PER_STICKER)


func get_total_health_chips() -> int:
	var sum := 0
	for chips in sticker_chips:
		sum += chips
	return sum


func is_player_down() -> bool:
	return get_total_health_chips() <= 0


func get_state_snapshot() -> Dictionary:
	return {
		"stickers": sticker_chips.duplicate(),
		"coins": coins,
		"scrap_parts": scrap_parts,
		"scrap_meter": scrap_meter,
		"health_chips": get_total_health_chips()
	}


func announce_pickup(text: String, color: Color = Color(0.94, 0.86, 0.54, 1.0)) -> void:
	pickup_noted.emit(text, color)


func _remove_chips(chips_to_remove: int) -> void:
	var remaining: int = chips_to_remove
	for i in range(MAX_STICKERS):
		if remaining <= 0:
			break
		if sticker_chips[i] <= 0:
			continue
		var loss: int = min(sticker_chips[i], remaining)
		sticker_chips[i] -= loss
		remaining -= loss


func _remove_full_sticker() -> void:
	for i in range(MAX_STICKERS):
		if sticker_chips[i] > 0:
			sticker_chips[i] = 0
			return


func _emit_stats() -> void:
	stats_changed.emit(get_state_snapshot())
