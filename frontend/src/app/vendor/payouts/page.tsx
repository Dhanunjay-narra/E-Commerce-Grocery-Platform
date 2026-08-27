"use client";
import React from "react";
import { DollarSign, CheckCircle2, TrendingUp, Download } from "lucide-react";

export default function VendorPayoutsPage() {
  const PAYOUTS = [
    { id: "PAY-20260825-01", period: "18 Aug 2026 - 24 Aug 2026", gross: "₹48,920.00", comm: "₹4,158.20", tds: "₹489.20", net: "₹43,524.12", status: "PAID", date: "25 Aug 2026" },
    { id: "PAY-20260818-01", period: "11 Aug 2026 - 17 Aug 2026", gross: "₹42,100.00", comm: "₹3,578.50", tds: "₹421.00", net: "₹37,456.37", status: "PAID", date: "18 Aug 2026" },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <span className="text-xs font-bold text-emerald-600 uppercase tracking-wider block">Financial Settlements</span>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Vendor Payouts & Statutory Tax Statements</h1>
        <p className="text-xs text-slate-500">Weekly bank settlement batches with Section 194-O TDS and GST breakdown</p>
      </div>

      <div className="bg-white rounded-3xl border border-slate-200 p-6 space-y-4 shadow-sm overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-100 text-slate-400 font-bold uppercase tracking-wider text-[10px]">
              <th className="pb-3">Settlement ID</th>
              <th className="pb-3">Billing Period</th>
              <th className="pb-3">Gross Sales</th>
              <th className="pb-3">Commission (8.5%)</th>
              <th className="pb-3">TDS (1%)</th>
              <th className="pb-3 font-black text-slate-900">Net Bank Settlement</th>
              <th className="pb-3 text-right">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
            {PAYOUTS.map((p) => (
              <tr key={p.id} className="hover:bg-slate-50 transition-colors">
                <td className="py-3 font-mono font-bold text-slate-900">{p.id}</td>
                <td className="py-3 text-slate-500">{p.period}</td>
                <td className="py-3 font-mono font-bold text-slate-900">{p.gross}</td>
                <td className="py-3 font-mono text-red-600">- {p.comm}</td>
                <td className="py-3 font-mono text-slate-500">- {p.tds}</td>
                <td className="py-3 font-mono font-black text-emerald-700">{p.net}</td>
                <td className="py-3 text-right">
                  <span className="inline-flex items-center gap-1 bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full text-[10px] font-bold border border-emerald-200">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>{p.status}</span>
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
