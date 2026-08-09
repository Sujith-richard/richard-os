
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class RichardApi {
  static String baseUrl = 'http://127.0.0.1:8000';
  static Future<void> setBase(String url) async {
    baseUrl = url;
    final p = await SharedPreferences.getInstance();
    await p.setString('richard_base', url);
  }
  static Future<void> loadBase() async {
    final p = await SharedPreferences.getInstance();
    final u = p.getString('richard_base');
    if (u != null && u.isNotEmpty) baseUrl = u;
  }
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
