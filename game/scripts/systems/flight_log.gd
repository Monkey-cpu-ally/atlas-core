extends Node

signal entry_added(entry: Dictionary)

var entries: Array[Dictionary] = []


func add_entry(kind: String, subject: String, text: String) -> void:
	var clean_text := text.strip_edges()
	if clean_text.is_empty():
		return
	var entry := {
		"kind": kind,
		"subject": subject,
		"text": clean_text,
		"timestamp": Time.get_unix_time_from_system(),
	}
	entries.append(entry)
	entry_added.emit(entry)


func add_enemy_note(enemy_name: String, note: String) -> void:
	add_entry("enemy", enemy_name, note)


func add_power_note(power_name: String, note: String) -> void:
	add_entry("power", power_name, note)


func add_observation(note: String) -> void:
	add_entry("observation", "field", note)


func get_recent(limit: int = 8) -> Array[Dictionary]:
	if limit <= 0:
		return []
	if entries.size() <= limit:
		return entries.duplicate(true)
	return entries.slice(entries.size() - limit, entries.size())
