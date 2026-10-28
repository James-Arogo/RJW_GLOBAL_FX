import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'home_screen.dart';
import 'register_screen.dart';

class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _username = TextEditingController();
  final _password = TextEditingController();
  bool loading = false;

  void login() async {
    setState(() => loading = true);
    final response = await ApiService.login(_username.text, _password.text);
    setState(() => loading = false);

    if (response['message'] == 'Login successful') {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => HomeScreen(username: _username.text, balance: response['balance'])),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(response['message'])));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black87,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
            Text('RJW GLOBAL FX', style: TextStyle(fontSize: 30, color: Colors.white, fontWeight: FontWeight.bold)),
            SizedBox(height: 30),
            TextField(controller: _username, decoration: InputDecoration(labelText: 'Username', filled: true, fillColor: Colors.white12)),
            SizedBox(height: 15),
            TextField(controller: _password, decoration: InputDecoration(labelText: 'Password', filled: true, fillColor: Colors.white12), obscureText: true),
            SizedBox(height: 20),
            loading ? CircularProgressIndicator() :
            ElevatedButton(onPressed: login, child: Text("Login")),
            TextButton(onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (context) => RegisterScreen())), child: Text("Create Account", style: TextStyle(color: Colors.white70)))
          ]),
        ),
      ),
    );
  }
}
