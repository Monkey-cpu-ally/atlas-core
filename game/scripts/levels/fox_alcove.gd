extends Node2D

@onready var end_text: Label = $EndText

func _ready() -> void:
	end_text.visible = false

func on_statue_activated() -> void:
	end_text.visible = true
	end_text.modulate.a = 0.0

	var t = create_tween()
	t.tween_property(end_text, "modulate:a", 1.0, 0.8)
