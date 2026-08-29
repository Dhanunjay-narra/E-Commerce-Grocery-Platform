import 'package:flutter/material.dart';
import 'package:freshcart_mobile/features/home/home_screen.dart';
import 'package:freshcart_mobile/features/scanner/barcode_scanner_screen.dart';
import 'package:freshcart_mobile/features/delivery/driver_pod_screen.dart';

void main() {
  runApp(const FreshCartApp());
}

class FreshCartApp extends StatelessWidget {
  const FreshCartApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'FreshCart Grocery',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF059669),
          primary: const Color(0xFF059669),
        ),
        useMaterial3: true,
      ),
      home: const MainNavigationScreen(),
    );
  }
}

class MainNavigationScreen extends StatefulWidget {
  const MainNavigationScreen({super.key});

  @override
  State<MainNavigationScreen> createState() => _MainNavigationScreenState();
}

class _MainNavigationScreenState extends State<MainNavigationScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    HomeScreen(),
    BarcodeScannerScreen(),
    DriverPodScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_currentIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (idx) => setState(() => _currentIndex = idx),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.store_mall_directory_rounded), label: "Store"),
          NavigationDestination(icon: Icon(Icons.qr_code_scanner_rounded), label: "Picker Scan"),
          NavigationDestination(icon: Icon(Icons.delivery_dining_rounded), label: "Driver POD"),
        ],
      ),
    );
  }
}
