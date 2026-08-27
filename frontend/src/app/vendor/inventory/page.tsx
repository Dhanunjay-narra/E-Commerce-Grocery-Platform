"use client";
import React, { useState } from "react";
import Link from "next/link";
import { Package, Search, Plus, AlertTriangle, ShieldCheck, Scale, ArrowUpDown } from "lucide-react";

export default function VendorInventoryPage() {
  const [searchTerm, setSearchTerm] = useState("");

  const INVENTORY_ROWS = [
    { lot: "LOT-TOM-2026-001", sku: "PROD-TOMATOES-HYBRID-RED", name: "Organic Hybrid Tomatoes", stock: "250.0 kg", expiry: "in 6 days", status: "HEALTHY", cost: "₹30.00", mrp: "₹48.00" },
    { lot: "LOT-BTR-2026-001", sku: "PROD-AMUL-BUTTER-500G", name: "Amul Pasteurised Butter 500g", stock: "500 pcs", expiry: "in 180 days", status: "HEALTHY", cost: "₹220.00", mrp: "₹285.00" },
    { lot: "LOT-RCE-2026-001", sku: "PROD-DAAWAT-ROZANA-GOLD-5KG", name: "Daawat Basmati Rice 5kg", stock: "300 bags", expiry: "in 730 days", status: "HEALTHY", cost: "₹410.00", mrp: "₹580.00" },
    { lot: "LOT-OIL-2026-001", sku: "PROD-PUVI-COLD-PRESSED-GROUNDNUT-OIL-1L", name: "Puvi Cold Pressed Oil 1L", stock: "400 bottles", expiry: "in 365 days", status: "HEALTHY", cost: "₹185.00", mrp: "₹260.00" },
    { lot: "LOT-SPN-2026-009", sku: "PROD-SPINACH-PALAK-BABY", name: "Organic Baby Spinach 250g", stock: "15 bunches", expiry: "in 2 days", status: "NEAR_EXPIRY", cost: "₹14.00", mrp: "₹25.00" },
  ];

  const filtered = INVENTORY_ROWS.filter((r) => r.name.toLowerCase().includes(searchTerm.toLowerCase()) || r.lot.toLowerCase().includes(searchTerm.toLowerCase()));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-bold text-emerald-600 uppercase tracking-wider block">Dark Store Inventory Control</span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">FEFO Lot Inventory & Batch Health</h1>
          <p className="text-xs text-slate-500">Track lot expiries, stock reserves, cold-chain compliance, and write-offs</p>
        </div>

        <button
          onClick={() => alert("Opening Inward Stock Receipt modal...")}
          className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-3 rounded-2xl font-bold text-xs shadow-md transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>Inward New Lot Batch</span>
        </button>
      </div>

      <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center gap-3">
          <div className="flex-1 relative">
            <input
              type="text"
              placeholder="Search lot number (LOT-TOM-...) or product name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-100 text-slate-400 font-bold uppercase tracking-wider text-[10px]">
                <th className="pb-3">Batch / Lot #</th>
                <th className="pb-3">Product Name</th>
                <th className="pb-3">Available Stock</th>
                <th className="pb-3">FEFO Expiration</th>
                <th className="pb-3">Unit Cost</th>
                <th className="pb-3">Selling Price</th>
                <th className="pb-3 text-right">Lot Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
              {filtered.map((row) => (
                <tr key={row.lot} className="hover:bg-slate-50 transition-colors">
                  <td className="py-3 font-mono font-bold text-slate-900">{row.lot}</td>
                  <td className="py-3 font-bold text-slate-900">{row.name}</td>
                  <td className="py-3 font-black text-slate-900">{row.stock}</td>
                  <td className="py-3 text-slate-500">{row.expiry}</td>
                  <td className="py-3 font-mono text-slate-500">{row.cost}</td>
                  <td className="py-3 font-mono font-bold text-slate-900">{row.mrp}</td>
                  <td className="py-3 text-right">
                    <span
                      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                        row.status === "HEALTHY"
                          ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                          : "bg-amber-50 text-amber-800 border border-amber-200"
                      }`}
                    >
                      {row.status === "HEALTHY" ? <ShieldCheck className="w-3 h-3 text-emerald-600" /> : <AlertTriangle className="w-3 h-3 text-amber-600" />}
                      <span>{row.status}</span>
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
