import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiClient {
  static const String baseUrl = "http://10.0.2.2:8000/api/v1"; // Android emulator localhost
  String? authToken;

  void setToken(String token) {
    authToken = token;
  }

  Map<String, String> get _headers => {
        "Content-Type": "application/json",
        if (authToken != null) "Authorization": "Bearer $authToken",
      };

  Future<dynamic> get(String endpoint) async {
    final response = await http.get(Uri.parse("$baseUrl$endpoint"), headers: _headers);
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return jsonDecode(response.body);
    }
    throw Exception("API Error: ${response.statusCode} - ${response.body}");
  }

  Future<dynamic> post(String endpoint, Map<String, dynamic> body) async {
    final response = await http.post(
      Uri.parse("$baseUrl$endpoint"),
      headers: _headers,
      body: jsonEncode(body),
    );
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return jsonDecode(response.body);
    }
    throw Exception("API Error: ${response.statusCode} - ${response.body}");
  }
}
