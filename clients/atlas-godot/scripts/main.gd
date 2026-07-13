extends Control

@onready var status_label: Label = $Center/Status

var socket := WebSocketPeer.new()
var socket_url := "ws://127.0.0.1:8000/api/atlas/visual/ws"
var connected := false
var reconnect_seconds := 0.0

func _ready() -> void:
	_connect_visual_bridge()

func _process(delta: float) -> void:
	socket.poll()
	var state := socket.get_ready_state()

	if state == WebSocketPeer.STATE_OPEN:
		if not connected:
			connected = true
			status_label.text = "ATLAS CONSOLE // CONNECTED"
		_read_messages()
	elif state == WebSocketPeer.STATE_CLOSED:
		if connected:
			connected = false
			status_label.text = "ATLAS CONSOLE // BRIDGE OFFLINE"
		reconnect_seconds += delta
		if reconnect_seconds >= 3.0:
			reconnect_seconds = 0.0
			socket = WebSocketPeer.new()
			_connect_visual_bridge()

func _connect_visual_bridge() -> void:
	var error := socket.connect_to_url(socket_url)
	if error != OK:
		status_label.text = "ATLAS CONSOLE // CONNECTION ERROR"
	else:
		status_label.text = "ATLAS CONSOLE // CONNECTING"

func _read_messages() -> void:
	while socket.get_available_packet_count() > 0:
		var text := socket.get_packet().get_string_from_utf8()
		var event = JSON.parse_string(text)
		if typeof(event) != TYPE_DICTIONARY:
			continue
		_apply_visual_event(event)

func _apply_visual_event(event: Dictionary) -> void:
	var event_name := str(event.get("event", "unknown"))
	var payload: Dictionary = event.get("payload", {})
	var persona := str(payload.get("persona", "atlas")).to_upper()
	var state := str(payload.get("state", "active")).to_upper()
	status_label.text = "%s // %s // %s" % [persona, event_name.to_upper(), state]
