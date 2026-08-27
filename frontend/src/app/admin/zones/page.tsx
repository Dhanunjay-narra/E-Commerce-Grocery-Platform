"use client";
import React from "react";
import { MapPin, Clock, Plus, ShieldCheck } from "lucide-react";

export default function AdminZonesPage() {
  const ZONES = [
    { code: "HYD-CYBER-01", name: "Cyberabad Hitec City Zone", city: "Hyderabad", radius: "18.0 km", stores: 4, fee: "₹35.00", activeSlots: 7, status: "ACTIVE" },
    { code: "HYD-GACHI-02", name: "Gachibowli Financial Hub", city: "Hyderabad", radius: "15.0 km", stores: 3, fee: "₹35.00", activeSlots: 7, status: "ACTIVE" },
    { code: "HYD-BANJ-03", name: "Banjara Hills & Jubilee Hills", city: "Hyderabad", radius: "12.0 km", stores: 2, fee: "₹40.00", activeSlots: 7, status: "ACTIVE" },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-bold text-emerald-600 uppercase tracking-wider block">Logistics Management</span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Geofenced Delivery Zones & Capacity Slots</h1>
          <p className="text-xs text-slate-500">Configure spatial polygons, 30-min express radius, and dynamic capacity windows</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {ZONES.map((z) => (
          <div key={z.code} className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-bold text-slate-400">{z.code}</span>
              <span className="bg-emerald-50 text-emerald-700 text-[10px] font-bold px-2 py-0.5 rounded-full border border-emerald-200">
                {z.status}
              </span>
            </div>
            <h3 className="font-black text-base text-slate-900">{z.name}</h3>
            <p className="text-xs text-slate-500">{z.city} • {z.radius} Radius Coverage</p>
            <div className="pt-3 border-t border-slate-100 flex justify-between text-xs font-medium text-slate-700">
              <span>Base Delivery Fee: <strong className="text-slate-900">{z.fee}</strong></span>
              <span>{z.activeSlots} Time Slots</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
