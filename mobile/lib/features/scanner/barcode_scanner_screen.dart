import 'package:flutter/material.dart';

class BarcodeScannerScreen extends StatefulWidget {
  const BarcodeScannerScreen({super.key});

  @override
  State<BarcodeScannerScreen> createState() => _BarcodeScannerScreenState();
}

class _BarcodeScannerScreenState extends State<BarcodeScannerScreen> {
  final TextEditingController _weightController = TextEditingController(text: "1.08");
  bool _itemScanned = true;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Dark Store Picker Station", style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Scanner Viewfinder Card
            Container(
              height: 180,
              decoration: BoxDecoration(
                color: Colors.black87,
                borderRadius: BorderRadius.circular(20),
              ),
              child: const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.qr_code_scanner_rounded, size: 60, color: Colors.greenAccent),
                    SizedBox(height: 8),
                    Text("Point at Product / Lot Barcode", style: TextStyle(color: Colors.white, fontSize: 12)),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),

            if (_itemScanned) ...[
              Card(
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16), side: BorderSide(color: Colors.grey.shade200)),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text("PICKING QUEUE: ORDER #ORD-20260827-01", style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.black54)),
                      const SizedBox(height: 6),
                      const Text("Organic Farm-Fresh Tomatoes", style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900)),
                      const Text("Ordered: 1.00 kg • Unit Price: ₹42.00 / kg", style: TextStyle(fontSize: 12, color: Colors.black54)),
                      const SizedBox(height: 16),
                      const Text("Enter Packing Scale Weight (kg):", style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 8),
                      TextField(
                        controller: _weightController,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        decoration: InputDecoration(
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                          suffixText: "kg",
                          prefixIcon: const Icon(Icons.scale_rounded, color: Color(0xFF059669)),
                        ),
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton.icon(
                        onPressed: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text("Item verified at 1.08 kg! Invoice reconciled.")),
                          );
                        },
                        icon: const Icon(Icons.check_circle_outline),
                        label: const Text("Confirm Picked Scale Weight"),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF059669),
                          foregroundColor: Colors.white,
                          minimumSize: const Size.fromHeight(48),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                      )
                    ],
                  ),
                ),
              )
            ]
          ],
        ),
      ),
    );
  }
}
