import 'dart:convert';
import 'package:http/http.dart' as http;

/// Richard OS API client — talks to the FastAPI backend.
class RichardApi {
  static String base = 'http://127.0.0.1:8000';
  static final RichardApi I = RichardApi._();
  RichardApi._();

  Future<Map> post(String path, [Map? body]) async {
    final r = await http.post(Uri.parse('$baseUrl$path'),
        headers: {'Content-Type': 'application/json'},
        body: body == null ? null : jsonEncode(body));
    return jsonDecode(r.body) as Map;
  }
  Future<Map> get(String path) async {
    final r = await http.get(Uri.parse('$baseUrl$path'));
    return jsonDecode(r.body) as Map;
  }

  // Voice: send a command, get route/reply
  Future<Map> voice(String text) => post('/api/v1/voice/command', {'text': text});

  // Devices
  Future<Map> devices() => get('/api/v1/devices');

  // Home
  Future<Map> homeState() => get('/api/v1/home/state');
  Future<Map> homeCommand(String text) => post('/api/v1/home/command', {'request': text});

  // Graph (brain/avatar)
  Future<Map> graph() => get('/graph');
}
