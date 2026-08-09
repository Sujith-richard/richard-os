
import 'dart:convert';
import 'package:http/http.dart' as http;

class RichardApi {
  static String baseUrl = 'http://127.0.0.1:8000';
  static final RichardApi I = RichardApi._();
  RichardApi._();

  Future<Map<String, dynamic>> post(String path, [Map<String, dynamic>? body]) async {
    final uri = Uri.parse(RichardApi.baseUrl + path);
    final r = await http.post(uri, headers: {'Content-Type': 'application/json'}, body: body == null ? null : jsonEncode(body));
    return Map<String, dynamic>.from(jsonDecode(r.body) as Map);
  }
  Future<Map<String, dynamic>> get(String path) async {
    final uri = Uri.parse(RichardApi.baseUrl + path);
    final r = await http.get(uri);
    return Map<String, dynamic>.from(jsonDecode(r.body) as Map);
  }
  Future<Map<String, dynamic>> voice(String text) => post('/api/v1/voice/command', {'text': text});
  Future<Map<String, dynamic>> devices() => get('/api/v1/devices');
  Future<Map<String, dynamic>> homeState() => get('/api/v1/home/state');
  Future<Map<String, dynamic>> homeCommand(String text) => post('/api/v1/home/command', {'request': text});
  Future<Map<String, dynamic>> graph() => get('/graph');
}
