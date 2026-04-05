extends Node2D

@onready var boss = $RootboundSiegeTank
@onready var exit_blocker = $ExitBlocker
@onready var axel_spawn: Marker2D = $AxelSpawn
@onready var axel: CharacterBody2D = $Axel

var started := false


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


func on_boss_defeated() -> void:
	print("Boss defeated!")
	_set_exit_blocker_state(false)
	GameState.announce_pickup("Arena unlocked -> next event", Color(0.74, 0.88, 0.64, 1.0))


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
