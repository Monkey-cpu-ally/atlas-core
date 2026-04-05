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
	FlightLog.add_enemy_note(
		"Root Crawler",
		"Burrow tracks stay shallow. Slow march. Folded from above."
	)
	FlightLog.add_enemy_note(
		"Gear Bug",
		"Wheel-joint twitch before burst. Back seam takes the hit."
	)
	FlightLog.add_enemy_note(
		"Flicker Unit",
		"Short blink phase. Strike after glow dip."
	)
	FlightLog.add_enemy_note(
		"Heavy Chassis",
		"Front plating drinks light hits. Needs empowered force."
	)
	FlightLog.add_power_note(
		"Burning Buffalo",
		"Torque line spikes forward. Wall braces fail on contact."
	)
	FlightLog.add_power_note(
		"Shadow Tag",
		"Contact steals random resource pulse. Most reliable on quick cycles."
	)
	FlightLog.add_power_note(
		"Golden Gloves",
		"Impact grade rises. Some armor classes collapse in one chain."
	)
	FlightLog.add_power_note(
		"Super Mode",
		"Hull ignores impact for short window. Keep pressure high."
	)
	FlightLog.add_power_note(
		"Specter Mode",
		"Body phases through contact lines. Reposition before timer burn."
	)
	FlightLog.add_power_note(
		"Fighter Plane",
		"Flight frame available while charge holds. Meter discipline required."
	)
	FlightLog.add_observation("Scrap UI ping cadence marks threat tempo.")


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
