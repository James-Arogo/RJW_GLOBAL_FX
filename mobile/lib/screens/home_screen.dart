import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'admin_dashboard.dart';

class HomeScreen extends StatefulWidget {
  final String username;
  final double balance;

  const HomeScreen({required this.username, required this.balance});

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Map<String, dynamic>? prices;
  double balance = 0;

  @override
  void initState() {
    super.initState();
    balance = widget.balance;
    fetchPrices();
  }

  void fetchPrices() async {
    final data = await ApiService.getLivePrices();
    setState(() => prices = data);
  }

  void makeTrade(String pair) async {
    final res = await ApiService.executeTrade(widget.username, pair, 100);
    setState(() => balance = res['balance']);
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('${res['result']} ${res['profit_loss']}')));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black87,
      appBar: AppBar(title: Text('Welcome, ${widget.username}')),
      body: prices == null
          ? Center(child: CircularProgressIndicator())
          : ListView(
              children: prices!.keys.map((pair) {
                return Card(
                  color: Colors.grey[900],
                  margin: EdgeInsets.all(8),
                  child: ListTile(
                    title: Text(pair, style: TextStyle(color: Colors.white)),
                    subtitle: Text('Price: ${prices![pair]}', style: TextStyle(color: Colors.greenAccent)),
                    trailing: ElevatedButton(
                      onPressed: () => makeTrade(pair),
                      child: Text('Trade'),
                    ),
                  ),
                );
              }).toList(),
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (context) => AdminDashboard())),
        child: Icon(Icons.admin_panel_settings),
      ),
    );
  }
}
