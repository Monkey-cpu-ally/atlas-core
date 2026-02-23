import 'dart:convert';

import 'package:http/http.dart' as http;

class AtlasBackendException implements Exception {
  AtlasBackendException({
    required this.message,
    this.statusCode,
    this.responseBody,
  });

  final String message;
  final int? statusCode;
  final String? responseBody;

  @override
  String toString() =>
      'AtlasBackendException(statusCode: $statusCode, message: $message)';
}

class AtlasBackendClient {
  const AtlasBackendClient({
    http.Client? httpClient,
  }) : _httpClient = httpClient;

  final http.Client? _httpClient;

  /// Calls:
  /// - GET /health  -> {"ok": true, "version": "..."}
  Future<Map<String, dynamic>> health({
    required String baseUrl,
  }) async {
    final uri = Uri.parse('${_normalizeBaseUrl(baseUrl)}/health');
    final client = _httpClient ?? http.Client();
    try {
      final res = await client.get(
        uri,
        headers: const {
          'Accept': 'application/json',
        },
      );
      if (res.statusCode < 200 || res.statusCode >= 300) {
        throw AtlasBackendException(
          message: 'Atlas /health failed',
          statusCode: res.statusCode,
          responseBody: res.body,
        );
      }

      final decoded = jsonDecode(res.body);
      if (decoded is! Map<String, dynamic>) {
        throw AtlasBackendException(
          message: 'Unexpected response type from /health',
          statusCode: res.statusCode,
          responseBody: res.body,
        );
      }
      return decoded;
    } on FormatException catch (e) {
      throw AtlasBackendException(
        message: 'Invalid JSON from backend: $e',
      );
    } finally {
      if (_httpClient == null) {
        client.close();
      }
    }
  }

  /// Calls FastAPI public route alias:
  /// - POST /route  (AtlasOrchestrateRequest -> AtlasOrchestrateResponse)
  Future<Map<String, dynamic>> orchestrate({
    required String baseUrl,
    required String project,
    required String userInput,
    String mode = 'mentor',
    Map<String, dynamic>? context,
    String? pipelineStage,
  }) async {
    final uri = Uri.parse('${_normalizeBaseUrl(baseUrl)}/route');
    final body = <String, dynamic>{
      'project': project,
      'user_input': userInput,
      'mode': mode,
      if (context != null) 'context': context,
      if (pipelineStage != null) 'pipeline_stage': pipelineStage,
    };

    final client = _httpClient ?? http.Client();
    try {
      final res = await client.post(
        uri,
        headers: const {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: jsonEncode(body),
      );

      if (res.statusCode < 200 || res.statusCode >= 300) {
        throw AtlasBackendException(
          message: 'Atlas /route failed',
          statusCode: res.statusCode,
          responseBody: res.body,
        );
      }

      final decoded = jsonDecode(res.body);
      if (decoded is! Map<String, dynamic>) {
        throw AtlasBackendException(
          message: 'Unexpected response type from /route',
          statusCode: res.statusCode,
          responseBody: res.body,
        );
      }
      return decoded;
    } on FormatException catch (e) {
      throw AtlasBackendException(
        message: 'Invalid JSON from backend: $e',
      );
    } finally {
      if (_httpClient == null) {
        client.close();
      }
    }
  }

  static String _normalizeBaseUrl(String baseUrl) {
    var v = baseUrl.trim();
    while (v.endsWith('/')) {
      v = v.substring(0, v.length - 1);
    }
    return v;
  }
}
