import 'package:flutter/material.dart';
import '../services/api_service.dart';

class TradeScreen extends StatefulWidget {
  final String username;
  const TradeScreen({super.key, required this.username});

  @override
  State<TradeScreen> createState() => _TradeScreenState();
}

class _TradeScreenState extends State<TradeScreen> {
  final amountController = TextEditingController();
  String resultText = "";
  bool trading = false;

  Future<void> makeTrade() async {
    setState(() => trading = true);
    final response = await ApiService.makeTrade(widget.username, "EUR/USD", amountController.text);
    setState(() {
      resultText = "Trade Result: ${response['result']} | Balance: ${response['new_balance']}";
      trading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Trade Simulation")),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            TextField(
              controller: amountController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: "Enter Trade Amount",
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: trading ? null : makeTrade,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.indigo,
                minimumSize: const Size(double.infinity, 50),
              ),
              child: trading ? const CircularProgressIndicator() : const Text("Execute Trade"),
            ),
            const SizedBox(height: 20),
            Text(resultText),
          ],
        ),
      ),
    );
  }
}
