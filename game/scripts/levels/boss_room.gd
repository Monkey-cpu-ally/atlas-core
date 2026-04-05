extends Node2D

@onready var boss = $RootboundSiegeTank
@onready var exit_blocker = $ExitBlocker
@onready var axel_spawn: Marker2D = $AxelSpawn
@onready var axel: CharacterBody2D = $Axel
@onready var fox = $FoxSpirit
@onready var fox_glow: Node2D = $FoxGlow
@onready var follow_marker: Marker2D = $FollowMarker
@onready var discovery_marker: Marker2D = $DiscoveryMarker

var started := false
var post_boss_sequence_started := false


func _ready() -> void:
	if boss and boss.has_signal("defeated"):
		boss.defeated.connect(on_boss_defeated)
	if axel and axel_spawn:
		axel.global_position = axel_spawn.global_position
	_set_exit_blocker_state(true)
	if boss:
		boss.visible = true


func start_boss_intro() -> void:
	if started:
		return
	started = true

	# lock player in
	_set_exit_blocker_state(true)

	var axel_node = get_tree().get_first_node_in_group("player")
	if axel_node:
		axel_node.set_physics_process(false)

	await get_tree().create_timer(0.5).timeout

	if boss:
		boss.start_fight()
	if axel_node:
		axel_node.set_physics_process(true)
	GameState.announce_pickup("I understand what to do", Color(0.9, 0.86, 0.58, 1.0))


func on_boss_defeated() -> void:
	print("Boss defeated!")
	exit_blocker.visible = false
	if exit_blocker and exit_blocker.has_node("CollisionShape2D"):
		var exit_shape := exit_blocker.get_node("CollisionShape2D") as CollisionShape2D
		if exit_shape:
			exit_shape.disabled = true

	await get_tree().create_timer(0.5).timeout

	spawn_fox()


func spawn_fox() -> void:
	if fox == null:
		return
	fox.visible = true
	if follow_marker:
		fox.global_position = follow_marker.global_position
	if fox.has_method("start_guiding"):
		fox.start_guiding()
	if not post_boss_sequence_started:
		post_boss_sequence_started = true
		_run_post_boss_sequence()


func _set_exit_blocker_state(visible_state: bool) -> void:
	if exit_blocker == null:
		return
	exit_blocker.visible = visible_state
	if exit_blocker.has_node("CollisionShape2D"):
		var shape := exit_blocker.get_node("CollisionShape2D") as CollisionShape2D
		if shape:
			shape.disabled = not visible_state
	if exit_blocker.has_node("GateVisual"):
		var visual := exit_blocker.get_node("GateVisual") as ColorRect
		if visual:
			visual.modulate.a = 0.85 if visible_state else 0.2


func _run_post_boss_sequence() -> void:
	# Fight -> silence -> glow -> curiosity -> follow -> discovery
	GameState.announce_pickup("Silence.", Color(0.74, 0.79, 0.85, 1.0))
	FlightLog.add_observation("The arena falls silent after the impact.")
	await get_tree().create_timer(0.65).timeout

	if fox_glow and fox_glow.has_node("GlowVisual"):
		var glow_visual := fox_glow.get_node("GlowVisual") as ColorRect
		fox_glow.visible = true
		glow_visual.modulate = Color(0.72, 0.9, 1.0, 0.05)
		var t = create_tween()
		t.tween_property(glow_visual, "modulate:a", 0.9, 0.5)
		await t.finished

	GameState.announce_pickup("A glow flickers in the chamber...", Color(0.72, 0.9, 1.0, 1.0))
	await get_tree().create_timer(0.4).timeout

	GameState.announce_pickup("Curiosity rises. Follow the signal.", Color(0.93, 0.88, 0.62, 1.0))
	FlightLog.add_observation("A pale glow points beyond the arena gate.")
	await get_tree().create_timer(0.45).timeout

	if follow_marker:
		GameState.announce_pickup("Follow -> (%d, %d)" % [int(follow_marker.global_position.x), int(follow_marker.global_position.y)], Color(0.74, 0.88, 0.64, 1.0))
	await get_tree().create_timer(0.45).timeout

	if discovery_marker:
		GameState.announce_pickup("Discovery -> (%d, %d)" % [int(discovery_marker.global_position.x), int(discovery_marker.global_position.y)], Color(0.98, 0.84, 0.54, 1.0))
	FlightLog.add_observation("Discovery waits where the glow settles.")
