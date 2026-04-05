extends Node2D

@onready var axel = $Axel
@onready var hud = $HUD

func _ready() -> void:
	if hud.has_method("connect_player"):
		hud.connect_player(axel)
