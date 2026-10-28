import 'package:flutter/material.dart';
import '../services/api_service.dart';

class AdminDashboard extends StatefulWidget {
  @override
  _AdminDashboardState createState() => _AdminDashboardState();
}

class _AdminDashboardState extends State<AdminDashboard> {
  Map<String, dynamic>? status;

  @override
  void initState() {
    super.initState();
    loadStatus();
  }

  void loadStatus() async {
    final data = await ApiService.getAdminStatus();
    setState(() => status = data);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Admin Dashboard')),
      backgroundColor: Colors.black87,
      body: status == null
          ? Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  Text("Total Users: ${status!['total_users']}", style: TextStyle(color: Colors.white)),
                  Text("Total Trades: ${status!['total_trades']}", style: TextStyle(color: Colors.white)),
                  Text("Platform Profit: \$${status!['platform_profit']}", style: TextStyle(color: Colors.greenAccent)),
                  Text("Profit Margin: ${status!['profit_margin']}", style: TextStyle(color: Colors.blueAccent)),
                ],
              ),
            ),
    );
  }
}
