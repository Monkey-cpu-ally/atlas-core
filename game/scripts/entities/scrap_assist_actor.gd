extends Node2D

signal assist_finished

@export var run_speed: float = 220.0

@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D

var active := false
var target_x: float = 0.0
var mode: String = ""

func start_entry(entry_mode: String, start_pos: Vector2, stop_x: float) -> void:
	mode = entry_mode
	global_position = start_pos
	target_x = stop_x
	visible = true
	active = true

	if sprite and sprite.sprite_frames:
		if sprite.sprite_frames.has_animation("run"):
			sprite.play("run")

func _process(delta: float) -> void:
	if not active:
		return

	if global_position.x < target_x:
		global_position.x += run_speed * delta

		# jitter feel
		rotation_degrees = sin(Time.get_ticks_msec() * 0.03) * 1.5
	else:
		active = false
		rotation_degrees = 0.0

		if sprite and sprite.sprite_frames:
			if sprite.sprite_frames.has_animation("idle"):
				sprite.play("idle")

		emit_signal("assist_finished")

func exit_left() -> void:
	if sprite and sprite.sprite_frames:
		if sprite.sprite_frames.has_animation("run"):
			sprite.play("run")

	var t = create_tween()
	t.tween_property(self, "global_position:x", global_position.x - 220.0, 0.5)
	await t.finished
	queue_free()
