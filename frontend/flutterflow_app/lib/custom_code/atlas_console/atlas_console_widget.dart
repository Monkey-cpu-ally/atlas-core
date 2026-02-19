import 'package:flutter/foundation.dart' show TargetPlatform, defaultTargetPlatform, kIsWeb;
import 'package:flutter/material.dart';

import 'package:flutter_atlas_scaffold/atlas_voice_core.dart';

import '/app_state.dart';
import '../atlas_backend/atlas_backend_client.dart';

class AtlasConsoleWidget extends StatefulWidget {
  const AtlasConsoleWidget({super.key});

  @override
  State<AtlasConsoleWidget> createState() => _AtlasConsoleWidgetState();
}

class _AtlasConsoleWidgetState extends State<AtlasConsoleWidget> {
  final _client = AtlasBackendClient();
  final _voiceCore = VoiceCoreController();

  late final TextEditingController _baseUrlController;
  final _projectController =
      TextEditingController(text: 'atlas_core_hybrid_system');
  final _inputController = TextEditingController();

  String _mode = 'mentor';
  late AtlasSkinId _skin;

  bool _loading = false;
  String? _error;
  Map<String, dynamic>? _last;

  bool _healthLoading = false;
  Map<String, dynamic>? _health;
  String? _healthError;

  @override
  void initState() {
    super.initState();
    // Defaults:
    // - Android emulator -> host machine: 10.0.2.2
    // - iOS simulator -> host machine: 127.0.0.1
    // - physical devices -> use your computer LAN IP (e.g. http://192.168.1.20:8000)
    final defaultBaseUrl = kIsWeb
        ? 'http://127.0.0.1:8000'
        : (defaultTargetPlatform == TargetPlatform.android
            ? 'http://10.0.2.2:8000'
            : 'http://127.0.0.1:8000');
    final saved = FFAppState().atlasBaseUrl.trim();
    _baseUrlController = TextEditingController(
      text: saved.isNotEmpty ? saved : defaultBaseUrl,
    );

    _skin = AtlasSkinIdX.fromId(FFAppState().skinId);
  }

  @override
  void dispose() {
    _voiceCore.dispose();
    _baseUrlController.dispose();
    _projectController.dispose();
    _inputController.dispose();
    super.dispose();
  }

  Future<void> _run() async {
    final baseUrl = _baseUrlController.text.trim();
    final project = _projectController.text.trim();
    final userInput = _inputController.text.trim();

    if (baseUrl.isEmpty || project.isEmpty || userInput.isEmpty) {
      setState(() {
        _error = 'Base URL, project, and input are required.';
      });
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
      _last = null;
    });

    try {
      final res = await _client.orchestrate(
        baseUrl: baseUrl,
        project: project,
        userInput: userInput,
        mode: _mode,
      );
      setState(() {
        _last = res;
      });
    } on AtlasBackendException catch (e) {
      setState(() {
        _error = '${e.message}\nHTTP: ${e.statusCode}\n${e.responseBody ?? ''}';
      });
    } catch (e) {
      setState(() {
        _error = 'Unexpected error: $e';
      });
    } finally {
      if (mounted) {
        setState(() {
          _loading = false;
        });
      }
    }
  }

  Future<void> _checkHealth() async {
    final baseUrl = _baseUrlController.text.trim();
    if (baseUrl.isEmpty) {
      setState(() {
        _healthError = 'Base URL is required.';
      });
      return;
    }
    setState(() {
      _healthLoading = true;
      _healthError = null;
      _health = null;
    });
    try {
      final res = await _client.health(baseUrl: baseUrl);
      setState(() {
        _health = res;
      });
    } on AtlasBackendException catch (e) {
      setState(() {
        _healthError =
            '${e.message}\nHTTP: ${e.statusCode}\n${e.responseBody ?? ''}';
      });
    } catch (e) {
      setState(() {
        _healthError = 'Unexpected error: $e';
      });
    } finally {
      if (mounted) {
        setState(() => _healthLoading = false);
      }
    }
  }

  void _setBaseUrl(String url) {
    _baseUrlController.text = url;
    FFAppState().atlasBaseUrl = url;
    setState(() {});
  }

  void _setSkin(AtlasSkinId skin) {
    setState(() => _skin = skin);
    FFAppState().skinId = skin.id;
  }

  Future<void> _promptLanIp() async {
    final ipController = TextEditingController();
    final value = await showDialog<String>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Computer LAN IP'),
          content: TextField(
            controller: ipController,
            decoration: const InputDecoration(
              hintText: 'Example: 192.168.1.20',
              border: OutlineInputBorder(),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(null),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () => Navigator.of(context).pop(ipController.text),
              child: const Text('Set'),
            ),
          ],
        );
      },
    );

    final ip = (value ?? '').trim();
    if (ip.isEmpty) return;
    _setBaseUrl('http://$ip:8000');
  }

  Widget _panel(
    BuildContext context, {
    required String title,
    required Widget child,
  }) {
    final scheme = Theme.of(context).colorScheme;
    final titleStyle = Theme.of(context).textTheme.titleSmall?.copyWith(
          fontWeight: FontWeight.w700,
          letterSpacing: 0.4,
        );
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: scheme.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: scheme.outline),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: titleStyle ??
                const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                ),
          ),
          const SizedBox(height: 8),
          child,
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final skinTokens = AtlasSkins.tokens(_skin);
    final skinTheme = AtlasSkins.themeData(
      _skin,
      base: Theme.of(context),
    );

    final suggestionSummary =
        (_last?['ajani']?['summary'] ?? _last?['ajani']?['goal'] ?? '')
            .toString();
    final minervaSummary = (_last?['minerva']?['summary'] ?? '').toString();
    final hermesSummary = (_last?['hermes']?['summary'] ?? '').toString();

    final validationStatus = (_last?['validation_status'] ?? '').toString();
    final intent = (_last?['intent'] ?? '').toString();
    final version = (_last?['version'] ?? '').toString();

    return AnimatedTheme(
      data: skinTheme,
      duration: AtlasSkins.transitionDuration,
      curve: Curves.easeInOut,
      child: AnimatedContainer(
        duration: AtlasSkins.transitionDuration,
        curve: Curves.easeInOut,
        color: skinTokens.background,
        child: AnimatedBuilder(
          animation: _voiceCore,
          builder: (context, _) {
            return ListView(
              padding: const EdgeInsets.all(16),
              children: [
            // Voice core visual layer (Unity placeholder for now).
            SizedBox(
              height: 280,
              child: VoiceCoreLayer(
                state: _voiceCore.state,
                coreWidget: _PlaceholderCore(
                  surface: skinTokens.surface,
                  border: skinTokens.border,
                  text: skinTokens.textSecondary,
                ),
                timing: _voiceCore.timing,
                ringColor: skinTokens.ringStroke,
                ringOpacity: skinTokens.ringOpacity,
                ringStrokeWidth: skinTokens.ringStrokeWidth,
              ),
            ),
            const SizedBox(height: 12),
            _panel(
              context,
              title: 'Connection',
              child: Column(
                children: [
                  TextField(
                    controller: _baseUrlController,
                    onChanged: (v) => FFAppState().atlasBaseUrl = v,
                    decoration: const InputDecoration(
                      labelText: 'Atlas Base URL',
                      hintText:
                          'Android emulator: http://10.0.2.2:8000  •  iOS simulator: http://127.0.0.1:8000  •  Physical device: http://<YOUR_LAN_IP>:8000',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      OutlinedButton(
                        onPressed: () => _setBaseUrl('http://10.0.2.2:8000'),
                        child: const Text('Android Emulator'),
                      ),
                      OutlinedButton(
                        onPressed: () => _setBaseUrl('http://127.0.0.1:8000'),
                        child: const Text('iOS Simulator'),
                      ),
                      OutlinedButton(
                        onPressed: () => _setBaseUrl('http://127.0.0.1:8000'),
                        child: const Text('Android (adb reverse)'),
                      ),
                      OutlinedButton(
                        onPressed: _promptLanIp,
                        child: const Text('Physical device (LAN IP)'),
                      ),
                      OutlinedButton(
                        onPressed: _healthLoading ? null : _checkHealth,
                        child: Text(_healthLoading ? 'Checking…' : 'Check /health'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      Text(
                        'Skin:',
                        style: TextStyle(color: skinTokens.textPrimary),
                      ),
                      const SizedBox(width: 10),
                      DropdownButton<AtlasSkinId>(
                        value: _skin,
                        items: AtlasSkinId.values
                            .map(
                              (s) => DropdownMenuItem(
                                value: s,
                                child: Text(s.label),
                              ),
                            )
                            .toList(),
                        onChanged: (v) {
                          if (v == null) return;
                          _setSkin(v);
                        },
                      ),
                      const Spacer(),
                      Text(
                        'Manual only',
                        style: TextStyle(
                          color: skinTokens.textSecondary,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  if (_health != null)
                    Align(
                      alignment: Alignment.centerLeft,
                      child: Text(
                        'Backend ok: ${_health?['ok']}  •  version: ${_health?['version'] ?? '(unknown)'}',
                        style: const TextStyle(color: Color(0xFFB8F5C2)),
                      ),
                    ),
                  if (_healthError != null)
                    Align(
                      alignment: Alignment.centerLeft,
                      child: Text(
                        _healthError!,
                        style: const TextStyle(color: Color(0xFFFFB4B4)),
                      ),
                    ),
                  const SizedBox(height: 8),
                  const Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      'Tip (Samsung Z Fold over USB): run `adb reverse tcp:8000 tcp:8000` then use http://127.0.0.1:8000',
                      style: TextStyle(color: Color(0xFFB8B8C8), fontSize: 12),
                    ),
                  ),
                  const SizedBox(height: 10),
                  TextField(
                    controller: _projectController,
                    decoration: const InputDecoration(
                      labelText: 'Project ID',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      const Text(
                        'Mode:',
                        style: TextStyle(color: Color(0xFFE6E6F2)),
                      ),
                      const SizedBox(width: 10),
                      DropdownButton<String>(
                        value: _mode,
                        items: const [
                          DropdownMenuItem(
                            value: 'mentor',
                            child: Text('mentor'),
                          ),
                          DropdownMenuItem(
                            value: 'warrior',
                            child: Text('warrior'),
                          ),
                          DropdownMenuItem(
                            value: 'builder',
                            child: Text('builder'),
                          ),
                        ],
                        onChanged: (v) {
                          if (v == null) return;
                          setState(() => _mode = v);
                        },
                      ),
                      const Spacer(),
                      ElevatedButton(
                        onPressed: _loading ? null : _run,
                        child: Text(_loading ? 'Running…' : 'Run /route'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            _panel(
              context,
              title: 'Input',
              child: TextField(
                controller: _inputController,
                maxLines: 5,
                decoration: const InputDecoration(
                  labelText: 'User input',
                  border: OutlineInputBorder(),
                ),
              ),
            ),
            const SizedBox(height: 12),
            _panel(
              context,
              title: 'Council Visual Demo (local only)',
              child: Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  OutlinedButton(
                    onPressed: () => _voiceCore.resetIdle(),
                    child: const Text('Idle'),
                  ),
                  OutlinedButton(
                    onPressed: () => _voiceCore.enterCouncilActive(),
                    child: const Text('Council Activate'),
                  ),
                  OutlinedButton(
                    onPressed: () => _voiceCore.setCouncilSpeaker(
                      IdentitySpeaker.ajani,
                    ),
                    child: const Text('Ajani'),
                  ),
                  OutlinedButton(
                    onPressed: () => _voiceCore.setCouncilPause(),
                    child: const Text('Pause'),
                  ),
                  OutlinedButton(
                    onPressed: () => _voiceCore.setCouncilSpeaker(
                      IdentitySpeaker.minerva,
                    ),
                    child: const Text('Minerva'),
                  ),
                  OutlinedButton(
                    onPressed: () => _voiceCore.setCouncilPause(),
                    child: const Text('Pause'),
                  ),
                  OutlinedButton(
                    onPressed: () => _voiceCore.setCouncilSpeaker(
                      IdentitySpeaker.hermes,
                    ),
                    child: const Text('Hermes'),
                  ),
                  OutlinedButton(
                    onPressed: () => _voiceCore.completeCouncil(),
                    child: const Text('Complete'),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 12),
            if (_error != null)
              _panel(
                context,
                title: 'Error',
                child: SelectableText(
                  _error!,
                  style: const TextStyle(color: Color(0xFFFFB4B4)),
                ),
              ),
            if (_last != null) ...[
              _panel(
                context,
                title: 'Status',
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'intent: $intent',
                      style: const TextStyle(color: Color(0xFFE6E6F2)),
                    ),
                    Text(
                      'validation_status: $validationStatus',
                      style: const TextStyle(color: Color(0xFFE6E6F2)),
                    ),
                    Text(
                      'version: $version',
                      style: const TextStyle(color: Color(0xFFE6E6F2)),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              _panel(
                context,
                title: 'Ajani',
                child: SelectableText(
                  suggestionSummary,
                  style: TextStyle(color: skinTokens.textPrimary),
                ),
              ),
              const SizedBox(height: 12),
              _panel(
                context,
                title: 'Minerva',
                child: SelectableText(
                  minervaSummary,
                  style: TextStyle(color: skinTokens.textPrimary),
                ),
              ),
              const SizedBox(height: 12),
              _panel(
                context,
                title: 'Hermes',
                child: SelectableText(
                  hermesSummary,
                  style: TextStyle(color: skinTokens.textPrimary),
                ),
              ),
              const SizedBox(height: 12),
              _panel(
                context,
                title: 'Raw JSON',
                child: SelectableText(
                  _last.toString(),
                  style: TextStyle(color: skinTokens.textSecondary),
                ),
              ),
            ],
          ],
        );
          },
        ),
      ),
    );
  }
}

class _PlaceholderCore extends StatelessWidget {
  const _PlaceholderCore({
    required this.surface,
    required this.border,
    required this.text,
  });

  final Color surface;
  final Color border;
  final Color text;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: surface,
        border: Border.all(
          color: border,
          width: 2,
        ),
      ),
      child: Center(
        child: Text(
          '3D Core',
          style: TextStyle(
            color: text,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
    );
  }
}
