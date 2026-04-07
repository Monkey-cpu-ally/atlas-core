extends Node2D

@onready var axel := $SpawnLayer/Axel


func _ready() -> void:
	GameState.reset_run()
	PowerManager.clear_power()
	_register_breakables()
	_seed_flight_log()
	_connect_enemy_targets()


func _seed_flight_log() -> void:
	FlightLog.entries.clear()
	FlightLog.add_observation("Enemy families mapped: Element / Dinosaur / Machine.")
	FlightLog.add_enemy_note(
		"Root Crawler",
		"Family: Dinosaur. Round shell, moss trim. Slow march with a clear turn cue."
	)
	FlightLog.add_enemy_note(
		"Gear Bug",
		"Family: Machine. Turquoise wheel-shell jitters before burst. Back seam is the weak read."
	)
	FlightLog.add_enemy_note(
		"Flicker Unit",
		"Family: Element. Violet blink loop. Strike right after the glow dip."
	)
	FlightLog.add_enemy_note(
		"Heavy Chassis",
		"Family: Machine. Chunky front shell shrugs weak taps. Use empowered force."
	)
	FlightLog.add_power_note(
		"Burning Buffalo",
		"Torque surges forward in a clean line. Fragile braces fail on contact."
	)
	FlightLog.add_power_note(
		"Shadow Tag",
		"Contact siphons a random resource pulse. Best during quick cycles."
	)
	FlightLog.add_power_note(
		"Golden Gloves",
		"Impact grade rises sharply. Mid armor can collapse in one chain."
	)
	FlightLog.add_power_note(
		"Super Mode",
		"Hull ignores impact for a short window. Keep pressure steady."
	)
	FlightLog.add_power_note(
		"Specter Mode",
		"Body phases through contact lines. Reposition before timer burn-out."
	)
	FlightLog.add_power_note(
		"Fighter Plane",
		"Flight frame remains available while charge holds. Meter discipline required."
	)
	FlightLog.add_observation("Scrap ping cadence tracks threat rhythm across the lane.")


func _connect_enemy_targets() -> void:
	for enemy in get_tree().get_nodes_in_group("enemies"):
		if enemy.has_method("set_player_target"):
			enemy.set_player_target(axel)


func _register_breakables() -> void:
	for node in get_tree().get_nodes_in_group("breakable"):
		node.remove_from_group("breakable")
	if has_node("BreakableWall"):
		$BreakableWall.add_to_group("breakable")
	if has_node("BreakableFloor"):
		$BreakableFloor.add_to_group("breakable")
