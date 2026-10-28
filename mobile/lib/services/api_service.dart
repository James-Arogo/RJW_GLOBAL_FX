import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = "http://10.146.51.160:5000"; // your backend IP

  static Future<Map<String, dynamic>> register(String username, String password) async {
    final res = await http.post(
      Uri.parse('$baseUrl/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'username': username, 'password': password}),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> login(String username, String password) async {
    final res = await http.post(
      Uri.parse('$baseUrl/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'username': username, 'password': password}),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> getLivePrices() async {
    final res = await http.get(Uri.parse('$baseUrl/live_prices'));
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> executeTrade(String username, String pair, double amount) async {
    final res = await http.post(
      Uri.parse('$baseUrl/trade'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'username': username, 'pair': pair, 'amount': amount}),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> getAdminStatus() async {
    final res = await http.get(Uri.parse('$baseUrl/admin/status'));
    return jsonDecode(res.body);
  }
}
