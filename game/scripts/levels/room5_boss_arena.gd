extends Node2D

enum ArenaState {
	ENTRY,
	LOCKED,
	FIGHT,
	DEFEATED,
	UNLOCKED
}

@onready var boss_gate: Node2D = $BossGate
@onready var exit_gate: Node2D = $ExitGate
@onready var fight_trigger: Area2D = $FightTrigger
@onready var defeat_trigger: Area2D = $DefeatTrigger
@onready var boss_placeholder: Node2D = $BossPlaceholder
@onready var arena_state_label: Label = $ArenaStateLabel
@onready var arena_unlock_marker: Marker2D = $ArenaUnlockMarker

var arena_state: ArenaState = ArenaState.ENTRY


func _ready() -> void:
	fight_trigger.body_entered.connect(_on_fight_trigger_body_entered)
	defeat_trigger.body_entered.connect(_on_defeat_trigger_body_entered)
	defeat_trigger.monitoring = false
	if boss_placeholder:
		boss_placeholder.visible = false
	_set_gate_blocking(exit_gate, true)
	_set_gate_blocking(boss_gate, false)
	_set_state_label("Entry corridor -> move into arena trigger.")


func _on_fight_trigger_body_entered(body: Node) -> void:
	if body == null or body.name != "Axel":
		return
	if arena_state != ArenaState.ENTRY:
		return
	_begin_fight()


func _begin_fight() -> void:
	arena_state = ArenaState.LOCKED
	_set_gate_blocking(boss_gate, true)
	_set_gate_blocking(exit_gate, true)
	GameState.announce_pickup("Boss arena locked. Fight begins.", Color(0.95, 0.58, 0.42, 1.0))
	arena_state = ArenaState.FIGHT
	if boss_placeholder:
		boss_placeholder.visible = true
	defeat_trigger.monitoring = true
	_set_state_label("Fight in progress. Defeat boss to unlock arena.")


func _on_defeat_trigger_body_entered(body: Node) -> void:
	if body == null or body.name != "Axel":
		return
	if arena_state != ArenaState.FIGHT:
		return
	on_boss_defeated()


func on_boss_defeated() -> void:
	if arena_state != ArenaState.FIGHT:
		return
	arena_state = ArenaState.DEFEATED
	_unlock_arena()


func _unlock_arena() -> void:
	_set_gate_blocking(exit_gate, false)
	arena_state = ArenaState.UNLOCKED
	defeat_trigger.monitoring = false
	if boss_placeholder:
		boss_placeholder.queue_free()
	GameState.announce_pickup("Arena unlocked -> next event", Color(0.74, 0.88, 0.64, 1.0))
	_set_state_label("Boss defeated. Arena unlocked -> next event.")


func _set_gate_blocking(gate: Node2D, blocked: bool) -> void:
	if gate == null:
		return
	if gate.has_node("CollisionShape2D"):
		var shape := gate.get_node("CollisionShape2D") as CollisionShape2D
		if shape:
			shape.disabled = not blocked
	if gate.has_node("GateVisual"):
		var visual := gate.get_node("GateVisual") as ColorRect
		if visual:
			visual.modulate.a = 0.85 if blocked else 0.2


func _set_state_label(text: String) -> void:
	if arena_state_label:
		arena_state_label.text = text
