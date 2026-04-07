extends Area2D

var triggered := false


func _ready():
	body_entered.connect(_on_body_entered)


func _on_body_entered(body):
	if triggered:
		return
	if body.name != "Axel":
		return

	triggered = true
	get_parent().start_boss_intro()
