import 'package:flutter/material.dart';

class DriverPodScreen extends StatefulWidget {
  const DriverPodScreen({super.key});

  @override
  State<DriverPodScreen> createState() => _DriverPodScreenState();
}

class _DriverPodScreenState extends State<DriverPodScreen> {
  final TextEditingController _otpController = TextEditingController();
  bool _isDelivered = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Delivery Fleet Hub", style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16), side: BorderSide(color: Colors.grey.shade200)),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.between,
                      children: [
                        const Text("ACTIVE DROP: ORD-20260827-01", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(color: Colors.amber.shade100, borderRadius: BorderRadius.circular(8)),
                          child: const Text("OUT FOR DELIVERY", style: TextStyle(color: Colors.amber, fontSize: 10, fontWeight: FontWeight.bold)),
                        )
                      ],
                    ),
                    const SizedBox(height: 12),
                    const Text("Customer: Priya Sharma", style: TextStyle(fontWeight: FontWeight.w900, fontSize: 15)),
                    const Text("Flat 402, Green Valley Apartments, Hitec City", style: TextStyle(fontSize: 12, color: Colors.black54)),
                    const Text("Collect Cash: ₹648.00 (COD)", style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF059669))),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),

            if (!_isDelivered) ...[
              const Text("Enter Customer 4-Digit Delivery OTP:", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
              const SizedBox(height: 8),
              TextField(
                controller: _otpController,
                keyboardType: TextInputType.number,
                maxLength: 4,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, letterSpacing: 8),
                decoration: InputDecoration(
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(16)),
                  hintText: "••••",
                ),
              ),
              const SizedBox(height: 12),
              ElevatedButton.icon(
                onPressed: () {
                  if (_otpController.text.length == 4) {
                    setState(() => _isDelivered = true);
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text("Proof of Delivery Verified! Order completed successfully.")),
                    );
                  }
                },
                icon: const Icon(Icons.verified_user_rounded),
                label: const Text("Verify Doorstep Proof of Delivery"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF059669),
                  foregroundColor: Colors.white,
                  minimumSize: const Size.fromHeight(50),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                ),
              )
            ] else ...[
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(color: Colors.green.shade50, borderRadius: BorderRadius.circular(20)),
                child: const Column(
                  children: [
                    Icon(Icons.check_circle_rounded, color: Color(0xFF059669), size: 48),
                    SizedBox(height: 8),
                    Text("Delivery Completed Successfully", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                    Text("Cash Collected: ₹648.00 • Commission Settled", style: TextStyle(fontSize: 12, color: Colors.black54)),
                  ],
                ),
              )
            ]
          ],
        ),
      ),
    );
  }
}
