import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text("FreshCart", style: TextStyle(fontWeight: FontWeight.w900, fontSize: 20)),
            Text("Express 30-Min Delivery • Hitec City", style: TextStyle(fontSize: 11, color: Colors.black54)),
          ],
        ),
        actions: [
          IconButton(onPressed: () {}, icon: const Icon(Icons.shopping_cart_outlined)),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Banner
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              gradient: const LinearGradient(colors: [Color(0xFF065F46), Color(0xFF047857)]),
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text("⚡ 30-MIN GROCERY EXPRESS", style: TextStyle(color: Colors.white70, fontSize: 10, fontWeight: FontWeight.bold)),
                SizedBox(height: 4),
                Text("Farm Fresh Vegetables & Certified Organic Dairy", style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.w900)),
              ],
            ),
          ),
          const SizedBox(height: 20),
          const Text("Top Grocery Essentials", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          // Product Cards
          _buildItemCard("Organic Farm Tomatoes", "₹42.00 / kg", "Scale Weighed", true),
          const SizedBox(height: 10),
          _buildItemCard("Amul Pasteurised Butter 500g", "₹275.00 / pack", "FEFO Fresh", false),
          const SizedBox(height: 10),
          _buildItemCard("Daawat Basmati Rice 5kg", "₹520.00 / bag", "Aged Grain", false),
        ],
      ),
    );
  }

  Widget _buildItemCard(String title, String price, String tag, bool isVariable) {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16), side: BorderSide(color: Colors.grey.shade200)),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            Container(
              width: 50,
              height: 50,
              decoration: BoxDecoration(color: Colors.green.shade50, borderRadius: BorderRadius.circular(12)),
              child: const Icon(Icons.eco_rounded, color: Color(0xFF059669)),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                  Text(price, style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 14, color: Color(0xFF059669))),
                  Text(tag, style: const TextStyle(fontSize: 10, color: Colors.black45)),
                ],
              ),
            ),
            ElevatedButton(
              onPressed: () {},
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF059669),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
              child: const Text("Add", style: TextStyle(fontWeight: FontWeight.bold)),
            )
          ],
        ),
      ),
    );
  }
}
