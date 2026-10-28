import 'package:flutter/material.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({Key? key}) : super(key: key);

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  String _email = '';
  String _password = '';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Create Account"),
        backgroundColor: Colors.blueAccent,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextFormField(
                decoration: const InputDecoration(labelText: "Email"),
                onSaved: (value) => _email = value ?? '',
              ),
              const SizedBox(height: 20),
              TextFormField(
                obscureText: true,
                decoration: const InputDecoration(labelText: "Password"),
                onSaved: (value) => _password = value ?? '',
              ),
              const SizedBox(height: 40),
              ElevatedButton(
                onPressed: () {
                  _formKey.currentState?.save();
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text("Account Created for $_email")),
                  );
                  Navigator.pop(context);
                },
                child: const Text("Register"),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
