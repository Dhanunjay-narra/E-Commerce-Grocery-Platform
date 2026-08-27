"use client";

import Link from "next/link";
import { CheckCircle2, Truck, Package, Clock, ShieldCheck, MapPin, FileText, KeyRound } from "lucide-react";

export default function OrderTrackingPage({ params }: { params: { id: string } }) {
  const STAGES = [
    { key: "CONFIRMED", label: "Confirmed", time: "04:02 PM", done: true },
    { key: "PICKING", label: "Scale Weighing", time: "04:10 PM", done: true },
    { key: "PACKED", label: "Packed & Sealed", time: "04:18 PM", done: true },
    { key: "OUT_FOR_DELIVERY", label: "Out for Delivery", time: "04:22 PM", done: true },
    { key: "DELIVERED", label: "Delivered", time: "Est. 04:45 PM", done: false },
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-bold text-emerald-600 uppercase tracking-wider block">Live Delivery Tracker</span>
          <h1 className="text-2xl md:text-3xl font-black text-slate-900 tracking-tight">Order #{params.id}</h1>
          <span className="text-xs text-slate-500">Placed on 27 Aug 2026, 04:00 PM • Cash on Delivery</span>
        </div>
        <button
          onClick={() => alert("Downloading GST Invoice PDF...")}
          className="flex items-center gap-1.5 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-xl text-xs font-bold transition-colors"
        >
          <FileText className="w-4 h-4 text-emerald-600" />
          <span>Tax Invoice</span>
        </button>
      </div>

      {/* Doorstep Proof-of-Delivery OTP Banner */}
      <div className="bg-gradient-to-r from-emerald-600 to-teal-700 p-6 rounded-3xl text-white flex items-center justify-between shadow-lg">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <KeyRound className="w-5 h-5 text-emerald-200" />
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-100">Proof of Delivery OTP</span>
          </div>
          <p className="text-xs text-emerald-50">Share this 4-digit code with your driver only at your doorstep:</p>
        </div>
        <div className="bg-white text-emerald-900 px-6 py-3 rounded-2xl font-black text-2xl tracking-widest shadow-md">
          4921
        </div>
      </div>

      {/* 11-Stage State Machine Progress Bar */}
      <div className="bg-white p-6 md:p-8 rounded-3xl border border-slate-200 shadow-sm space-y-6">
        <h3 className="font-bold text-sm text-slate-900">Live Fulfillment Timeline</h3>

        <div className="relative flex items-center justify-between">
          <div className="absolute top-1/2 left-0 right-0 h-1 bg-slate-100 -translate-y-1/2 z-0" />
          <div className="absolute top-1/2 left-0 w-3/4 h-1 bg-emerald-500 -translate-y-1/2 z-0" />

          {STAGES.map((st, i) => (
            <div key={i} className="relative z-10 flex flex-col items-center gap-2">
              <div
                className={`w-9 h-9 rounded-full flex items-center justify-center font-bold text-xs shadow-sm ${
                  st.done
                    ? "bg-emerald-600 text-white"
                    : "bg-white text-slate-400 border-2 border-slate-200"
                }`}
              >
                {st.done ? <CheckCircle2 className="w-5 h-5" /> : i + 1}
              </div>
              <span className={`text-xs font-bold text-center ${st.done ? "text-slate-900" : "text-slate-400"}`}>
                {st.label}
              </span>
              <span className="text-[10px] text-slate-400">{st.time}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Driver and Location Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center gap-2 font-bold text-xs text-slate-900">
            <Truck className="w-4 h-4 text-emerald-600" />
            <span>Assigned Delivery Driver</span>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <span className="font-bold text-sm text-slate-900 block">Ramesh Driver</span>
              <span className="text-xs text-slate-500">Express Delivery Partner (Electric Scooter)</span>
            </div>
            <a
              href="tel:+919000000004"
              className="px-3 py-1.5 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 rounded-xl text-xs font-bold transition-colors"
            >
              Call Driver
            </a>
          </div>
        </div>

        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center gap-2 font-bold text-xs text-slate-900">
            <MapPin className="w-4 h-4 text-emerald-600" />
            <span>Delivery Destination</span>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Flat 402, Green Valley Apartments, Hitec City, Hyderabad - 500081
          </p>
        </div>
      </div>

      {/* Reconciled Produce Items */}
      <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="font-bold text-sm text-slate-900">Scale Weighed Produce Items</h3>
        <div className="divide-y divide-slate-100 text-xs">
          <div className="py-3 flex justify-between items-center">
            <div>
              <span className="font-bold text-slate-900 block">Organic Farm-Fresh Hybrid Tomatoes</span>
              <span className="text-[11px] text-emerald-700 font-semibold">
                Ordered: 1.00 kg • Actual Picked Scale Weight: 1.08 kg
              </span>
            </div>
            <span className="font-black text-slate-900">₹43.20</span>
          </div>
          <div className="py-3 flex justify-between items-center">
            <div>
              <span className="font-bold text-slate-900 block">Daawat Rozana Gold Basmati Rice 5kg</span>
              <span className="text-[11px] text-slate-500">Ordered: 1 bag</span>
            </div>
            <span className="font-black text-slate-900">₹520.00</span>
          </div>
        </div>
      </div>
    </div>
  );
}
