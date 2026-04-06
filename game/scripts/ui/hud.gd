extends CanvasLayer

const EMPTY_STICKER := "[ ]"
const FULL_STICKER := "[#]"
const HALF_STICKER := "[+]"
const CHIP_STICKER := "[-]"

@onready var stickers_label: Label = $Panel/Margin/Rows/StickersLabel
@onready var coins_label: Label = $Panel/Margin/Rows/CoinsLabel
@onready var scrap_parts_label: Label = $Panel/Margin/Rows/ScrapPartsLabel
@onready var scrap_meter_label: Label = $Panel/Margin/Rows/ScrapMeterLabel
@onready var scrap_meter_bar: ProgressBar = $Panel/Margin/Rows/ScrapMeterBar
@onready var power_icon: Label = $Panel/Margin/Rows/PowerRow/PowerIcon
@onready var power_label: Label = $Panel/Margin/Rows/PowerRow/PowerLabel
@onready var power_timer_label: Label = $Panel/Margin/Rows/PowerRow/PowerTimerLabel
@onready var pickup_text_label: Label = $Panel/Margin/Rows/PickupTextLabel
@onready var log_label: Label = $Panel/Margin/Rows/FlightLogLabel
@onready var assist_label: Label = $ScrapAssistPanel/AssistLabel
@onready var assist_meter: ProgressBar = $ScrapAssistPanel/AssistMeter

var _pickup_text_timeout: float = 0.0


func _ready() -> void:
	GameState.stats_changed.connect(_on_stats_changed)
	GameState.pickup_noted.connect(_on_pickup_noted)
	GameState.damage_noted.connect(_on_damage_noted)
	PowerManager.power_changed.connect(_on_power_changed)
	PowerManager.power_tick.connect(_on_power_tick)
	FlightLog.entry_added.connect(_on_log_entry_added)
	_on_stats_changed(GameState.get_state_snapshot())
	_on_power_changed(PowerManager.active_power_id, PowerManager.remaining_time)
	_refresh_latest_log()
	_set_scrap_assist_ui(0.0, 100.0, "Green", Color("7fe08a"))


func _process(delta: float) -> void:
	_pickup_text_timeout = maxf(_pickup_text_timeout - delta, 0.0)
	if _pickup_text_timeout <= 0.0 and pickup_text_label.text != "":
		pickup_text_label.text = ""


func _on_stats_changed(snapshot: Dictionary) -> void:
	var stickers: Array = snapshot.get("stickers", [])
	stickers_label.text = "Stickers: " + _build_sticker_text(stickers)
	coins_label.text = "Coins: %d" % int(snapshot.get("coins", 0))
	scrap_parts_label.text = "Scrap Parts: %d" % int(snapshot.get("scrap_parts", 0))
	var meter_value := float(snapshot.get("scrap_meter", 0.0))
	scrap_meter_label.text = "Scrap Meter: %d / 100" % int(round(meter_value))
	scrap_meter_bar.value = meter_value


func _on_power_changed(power_id: String, seconds_left: float) -> void:
	var meta := PowerManager.get_power_meta(power_id)
	power_icon.text = str(meta.get("icon", "--"))
	power_icon.modulate = meta.get("color", Color(0.84, 0.84, 0.84, 1.0))
	power_label.text = "Power: %s" % str(meta.get("display", "None"))
	power_label.modulate = meta.get("color", Color(0.84, 0.84, 0.84, 1.0))
	power_timer_label.text = "Timer: %.1f" % max(seconds_left, 0.0)


func _on_power_tick(seconds_left: float) -> void:
	power_timer_label.text = "Timer: %.1f" % max(seconds_left, 0.0)


func _on_pickup_noted(text: String, color: Color) -> void:
	pickup_text_label.text = text
	pickup_text_label.modulate = color
	_pickup_text_timeout = 1.6


func _on_damage_noted(text: String) -> void:
	pickup_text_label.text = text
	pickup_text_label.modulate = Color(0.93, 0.56, 0.46, 1.0)
	_pickup_text_timeout = 1.2


func _on_log_entry_added(_entry: Dictionary) -> void:
	_refresh_latest_log()


func _refresh_latest_log() -> void:
	var recent := FlightLog.get_recent(1)
	if recent.is_empty():
		log_label.text = "Flight Log: No entries yet."
		return
	var entry := recent[0]
	log_label.text = "Flight Log: [%s] %s" % [str(entry.get("subject", "field")), str(entry.get("text", ""))]


func _build_sticker_text(stickers: Array) -> String:
	var chunks: Array[String] = []
	for raw in stickers:
		var chips := int(raw)
		if chips >= GameState.CHIP_PER_STICKER:
			chunks.append(FULL_STICKER)
		elif chips <= 0:
			chunks.append(EMPTY_STICKER)
		elif chips >= 2:
			chunks.append(HALF_STICKER)
		else:
			chunks.append(CHIP_STICKER)
	return " ".join(chunks)


func connect_player(player: Node) -> void:
	if player == null:
		return
	if player.has_signal("scrap_assist_changed"):
		player.scrap_assist_changed.connect(_on_scrap_assist_changed)


func _on_scrap_assist_changed(value: float, max_value: float, level_name: String, color: Color) -> void:
	assist_label.text = "Scrap Assist: " + level_name
	assist_label.modulate = color

	assist_meter.max_value = max_value
	assist_meter.value = value
	assist_meter.modulate = color


func _set_scrap_assist_ui(value: float, max_value: float, level_name: String, color: Color) -> void:
	var safe_max := maxf(1.0, max_value)
	assist_meter.max_value = safe_max
	assist_meter.value = clampf(value, 0.0, safe_max)
	assist_label.text = "Assist: %s" % level_name
	assist_label.modulate = color
