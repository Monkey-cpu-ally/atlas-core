import 'dart:async';

abstract class PersistenceService {
  Future<void> writeString(String key, String value);
  Future<String?> readString(String key);
}

class InMemoryPersistenceService implements PersistenceService {
  final Map<String, String> _store = <String, String>{};

  @override
  Future<String?> readString(String key) async => _store[key];

  @override
  Future<void> writeString(String key, String value) async {
    _store[key] = value;
  }
}

