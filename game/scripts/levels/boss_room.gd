extends Node2D

@onready var axel_spawn: Marker2D = $AxelSpawn
@onready var axel: CharacterBody2D = $Axel
@onready var start_trigger: Area2D = $BossStartTrigger
@onready var exit_blocker: StaticBody2D = $ExitBlocker
@onready var boss: RootboundSiegeTank = $RootboundSiegeTank

var fight_started := false


func _ready() -> void:
	start_trigger.body_entered.connect(_on_boss_start_trigger_body_entered)
	if boss and boss.has_signal("defeated"):
		boss.defeated.connect(_on_boss_defeated)
	if axel and axel_spawn:
		axel.global_position = axel_spawn.global_position
	_set_exit_blocker_enabled(true)
	if boss:
		boss.visible = true


func _on_boss_start_trigger_body_entered(body: Node) -> void:
	if fight_started:
		return
	if body == null or body.name != "Axel":
		return
	fight_started = true
	if boss:
		boss.start_fight()
	GameState.announce_pickup("Boss fight begins.", Color(0.95, 0.58, 0.42, 1.0))


func _on_boss_defeated() -> void:
	_set_exit_blocker_enabled(false)
	GameState.announce_pickup("Arena unlocked -> next event", Color(0.74, 0.88, 0.64, 1.0))


func _set_exit_blocker_enabled(enabled: bool) -> void:
	if exit_blocker == null:
		return
	if exit_blocker.has_node("CollisionShape2D"):
		var shape := exit_blocker.get_node("CollisionShape2D") as CollisionShape2D
		if shape:
			shape.disabled = not enabled
	if exit_blocker.has_node("GateVisual"):
		var visual := exit_blocker.get_node("GateVisual") as ColorRect
		if visual:
			visual.modulate.a = 0.85 if enabled else 0.2
