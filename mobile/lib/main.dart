import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'screens/login_screen.dart';

void main() {
  runApp(const RJWGlobalFX());
}

class RJWGlobalFX extends StatelessWidget {
  const RJWGlobalFX({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'RJW GLOBAL FX',
      theme: ThemeData(
        primaryColor: Colors.blueAccent,
        textTheme: GoogleFonts.poppinsTextTheme(),
        colorScheme: ColorScheme.fromSwatch(primarySwatch: Colors.indigo)
            .copyWith(secondary: Colors.amber),
      ),
      home: const LoginScreen(),
    );
  }
}
