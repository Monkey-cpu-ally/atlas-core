extends Node

signal power_changed(power_id: String, seconds_left: float)
signal power_tick(seconds_left: float)
signal power_expired(previous_power_id: String)

const DEFAULT_DURATION: float = 15.0
const POWER_IDS := [
	"burning_buffalo",
	"shadow_tag",
	"golden_gloves",
	"super_mode",
	"specter_mode",
	"fighter_plane",
]

const POWER_META := {
	"burning_buffalo": {
		"display": "Burning Buffalo",
		"color": Color(0.96, 0.44, 0.28, 1.0),
		"icon": "BB",
	},
	"shadow_tag": {
		"display": "Shadow Tag",
		"color": Color(0.62, 0.47, 0.94, 1.0),
		"icon": "ST",
	},
	"golden_gloves": {
		"display": "Golden Gloves",
		"color": Color(0.94, 0.78, 0.35, 1.0),
		"icon": "GG",
	},
	"super_mode": {
		"display": "Super Mode",
		"color": Color(0.7, 0.8, 0.95, 1.0),
		"icon": "SM",
	},
	"specter_mode": {
		"display": "Specter Mode",
		"color": Color(0.76, 0.9, 0.98, 1.0),
		"icon": "SP",
	},
	"fighter_plane": {
		"display": "Fighter Plane",
		"color": Color(0.6, 0.84, 0.88, 1.0),
		"icon": "FP",
	},
}

var active_power_id: String = ""
var remaining_time: float = 0.0


func _process(delta: float) -> void:
	if active_power_id.is_empty():
		return

	remaining_time = maxf(0.0, remaining_time - delta)
	power_tick.emit(remaining_time)
	if remaining_time <= 0.0:
		var previous := active_power_id
		active_power_id = ""
		remaining_time = 0.0
		power_expired.emit(previous)
		power_changed.emit(active_power_id, remaining_time)


func _ready() -> void:
	randomize()


func activate_power(power_id: String, duration: float = DEFAULT_DURATION) -> void:
	if not POWER_IDS.has(power_id):
		return
	active_power_id = power_id
	remaining_time = duration
	power_changed.emit(active_power_id, remaining_time)


func clear_power() -> void:
	active_power_id = ""
	remaining_time = 0.0
	power_changed.emit(active_power_id, remaining_time)


func get_active_power() -> String:
	return active_power_id


func get_attack_multiplier() -> float:
	if active_power_id == "golden_gloves":
		return 1.8
	if active_power_id == "burning_buffalo":
		return 1.35
	if active_power_id == "fighter_plane":
		return 1.2
	return 1.0


func get_move_speed_multiplier() -> float:
	if active_power_id == "burning_buffalo":
		return 1.55
	if active_power_id == "fighter_plane":
		return 1.35
	return 1.0


func is_invulnerable() -> bool:
	return active_power_id == "super_mode"


func is_intangible() -> bool:
	return active_power_id == "specter_mode"


func get_power_meta(power_id: String = "") -> Dictionary:
	var id := power_id
	if id.is_empty():
		id = active_power_id
	if POWER_META.has(id):
		return POWER_META[id]
	return {
		"display": "None",
		"color": Color(0.85, 0.85, 0.85, 1.0),
		"icon": "--",
	}


func apply_shadow_tag_to_enemy(enemy: Node) -> void:
	if active_power_id != "shadow_tag":
		return
	var roll := randi() % 3
	if roll == 0:
		GameState.add_scrap_meter(10.0)
		GameState.announce_pickup("Shadow Tag stole charge +10", Color(0.72, 0.6, 0.95, 1.0))
	elif roll == 1:
		GameState.add_coins(3)
		GameState.announce_pickup("Shadow Tag stole coins +3", Color(0.95, 0.86, 0.55, 1.0))
	else:
		GameState.add_scrap_parts(1)
		GameState.announce_pickup("Shadow Tag stole scrap +1", Color(0.74, 0.82, 0.9, 1.0))
