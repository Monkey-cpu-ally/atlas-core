extends Node2D

@onready var axel_spawn: Marker2D = $AxelSpawn
@onready var axel: CharacterBody2D = $Axel
@onready var camera: Camera2D = $Camera2D
@onready var end_text: Label = $EndText


func _ready() -> void:
	if axel and axel_spawn:
		axel.global_position = axel_spawn.global_position
	if camera and axel:
		camera.global_position = axel.global_position + Vector2(220.0, -100.0)
	if end_text:
		end_text.text = "A quiet discovery settles in."


func on_statue_activated() -> void:
	if end_text:
		end_text.text = "The fox statue hums. Your path feels clearer."
