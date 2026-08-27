"use client";
import React, { useState } from "react";
import { Package, Clock, CheckCircle2, Truck, Eye } from "lucide-react";

export default function VendorOrdersPage() {
  const ORDERS = [
    { id: "ORD-20260827-01", time: "10 mins ago", customer: "Priya Sharma", items: 3, total: "₹648.00", slot: "04:00 PM - 06:00 PM", stage: "OUT_FOR_DELIVERY" },
    { id: "ORD-20260827-02", time: "25 mins ago", customer: "Arun Patel", items: 5, total: "₹1,240.00", slot: "06:00 PM - 08:00 PM", stage: "PICKING" },
    { id: "ORD-20260827-03", time: "40 mins ago", customer: "Sneha Rao", items: 2, total: "₹385.00", slot: "06:00 PM - 08:00 PM", stage: "CONFIRMED" },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div>
        <span className="text-xs font-bold text-emerald-600 uppercase tracking-wider block">Vendor Operations Hub</span>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Active Fulfillment Order Queues</h1>
        <p className="text-xs text-slate-500">Real-time store picking orders, scale weighing reconciliation, and driver handoffs</p>
      </div>

      <div className="bg-white rounded-3xl border border-slate-200 overflow-hidden shadow-sm">
        <div className="divide-y divide-slate-100">
          {ORDERS.map((ord) => (
            <div key={ord.id} className="p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-slate-50 transition-colors">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-mono font-black text-sm text-slate-900">{ord.id}</span>
                  <span className="text-[11px] text-slate-400 font-semibold">• {ord.time}</span>
                </div>
                <p className="text-xs text-slate-600 font-medium">Customer: <strong className="text-slate-900">{ord.customer}</strong> • {ord.items} Grocery Items</p>
                <div className="flex items-center gap-2 text-[11px] text-slate-500">
                  <Clock className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Scheduled Slot: {ord.slot}</span>
                </div>
              </div>

              <div className="flex items-center gap-6">
                <div className="text-right">
                  <span className="font-black text-base text-slate-900 block">{ord.total}</span>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md">
                    {ord.stage}
                  </span>
                </div>

                <button
                  onClick={() => alert(`Opening Picker view for ${ord.id}...`)}
                  className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition-colors flex items-center gap-1.5"
                >
                  <Eye className="w-4 h-4" />
                  <span>Process Order</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
