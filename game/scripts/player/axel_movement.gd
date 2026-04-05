extends CharacterBody2D

@export var speed := 200
@export var acceleration := 900
@export var friction := 800
@export var jump_force := -350
@export var gravity := 900

func _physics_process(delta):
	# Gravity
	if not is_on_floor():
		velocity.y += gravity * delta

	# Input
	var dir = Input.get_axis("move_left", "move_right")

	# Movement
	if dir != 0:
		velocity.x = move_toward(velocity.x, dir * speed, acceleration * delta)
	else:
		velocity.x = move_toward(velocity.x, 0, friction * delta)

	# Jump
	if Input.is_action_just_pressed("jump") and is_on_floor():
		velocity.y = jump_force

	move_and_slide()
