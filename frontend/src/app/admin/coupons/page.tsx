"use client";
import React, { useState } from "react";
import { Tag, Plus, CheckCircle, Percent, Clock } from "lucide-react";

export default function AdminCouponsPage() {
  const COUPONS = [
    { code: "FRESHSTART", desc: "Flat ₹100 Off on First Order above ₹500", type: "FIXED_AMOUNT", value: "₹100.00", min: "₹500.00", used: 342, status: "ACTIVE" },
    { code: "ORGANIC20", desc: "20% Discount up to ₹150 on Fresh Produce", type: "PERCENTAGE", value: "20%", min: "₹400.00", used: 890, status: "ACTIVE" },
    { code: "WEEKEND50", desc: "Flat ₹50 Off on Weekend Groceries", type: "FIXED_AMOUNT", value: "₹50.00", min: "₹300.00", used: 1240, status: "ACTIVE" },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-bold text-emerald-600 uppercase tracking-wider block">Marketing & Promotions</span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Promotional Discount Coupons</h1>
          <p className="text-xs text-slate-500">Configure discount rules, order minimums, category targeting, and user limits</p>
        </div>
      </div>

      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-100 text-slate-400 font-bold uppercase tracking-wider text-[10px]">
              <th className="pb-3">Coupon Code</th>
              <th className="pb-3">Promotion Description</th>
              <th className="pb-3">Discount Value</th>
              <th className="pb-3">Min Order</th>
              <th className="pb-3">Times Used</th>
              <th className="pb-3 text-right">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
            {COUPONS.map((c) => (
              <tr key={c.code} className="hover:bg-slate-50 transition-colors">
                <td className="py-3 font-mono font-black text-emerald-700">{c.code}</td>
                <td className="py-3 font-bold text-slate-900">{c.desc}</td>
                <td className="py-3 font-mono font-bold text-slate-900">{c.value}</td>
                <td className="py-3 font-mono text-slate-500">{c.min}</td>
                <td className="py-3 font-bold text-slate-900">{c.used} redemptions</td>
                <td className="py-3 text-right">
                  <span className="inline-flex items-center gap-1 bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full text-[10px] font-bold border border-emerald-200">
                    <CheckCircle className="w-3 h-3" />
                    <span>{c.status}</span>
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
