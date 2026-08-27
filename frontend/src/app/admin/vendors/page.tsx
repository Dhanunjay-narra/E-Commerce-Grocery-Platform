"use client";
import React, { useState } from "react";
import { Store, CheckCircle, Clock, ShieldCheck, Search, Filter } from "lucide-react";

export default function AdminVendorsPage() {
  const VENDORS = [
    { id: "VEND-01", name: "Green Leaf Organics Pvt Ltd", owner: "Vikram Reddy", email: "support@greenleaf.com", gstin: "36AABCB1234D1Z5", stores: 3, commission: "8.5%", kyc: "APPROVED", status: "ACTIVE" },
    { id: "VEND-02", name: "Himalayan Fresh Orchards", owner: "Rohit Sharma", email: "sales@himalayan.com", gstin: "02AABCH5678E1Z9", stores: 2, commission: "8.0%", kyc: "APPROVED", status: "ACTIVE" },
    { id: "VEND-03", name: "Deccan Dairy & Milk Hub", owner: "Anil Kumar", email: "vendor@deccanmilk.com", gstin: "36AABCD9012F1Z3", stores: 5, commission: "6.5%", kyc: "PENDING", status: "UNDER_REVIEW" },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-bold text-emerald-600 uppercase tracking-wider block">Enterprise Control</span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Marketplace Vendors & Dark Store Hubs</h1>
          <p className="text-xs text-slate-500">Manage vendor KYC approval workflows, commission splits, and dark-store geofences</p>
        </div>
      </div>

      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden p-6 space-y-4">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-100 text-slate-400 font-bold uppercase tracking-wider text-[10px]">
                <th className="pb-3">Vendor ID</th>
                <th className="pb-3">Business Name</th>
                <th className="pb-3">Owner Contact</th>
                <th className="pb-3">GSTIN / Tax ID</th>
                <th className="pb-3">Dark Stores</th>
                <th className="pb-3">Commission</th>
                <th className="pb-3 text-right">KYC Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
              {VENDORS.map((v) => (
                <tr key={v.id} className="hover:bg-slate-50 transition-colors">
                  <td className="py-3 font-mono font-bold text-slate-900">{v.id}</td>
                  <td className="py-3 font-bold text-slate-900">{v.name}</td>
                  <td className="py-3">{v.owner} ({v.email})</td>
                  <td className="py-3 font-mono text-slate-500">{v.gstin}</td>
                  <td className="py-3 font-bold text-slate-900">{v.stores} Hubs</td>
                  <td className="py-3 font-mono text-emerald-700 font-bold">{v.commission}</td>
                  <td className="py-3 text-right">
                    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                      v.kyc === "APPROVED" ? "bg-emerald-50 text-emerald-800 border border-emerald-200" : "bg-amber-50 text-amber-800 border border-amber-200"
                    }`}>
                      {v.kyc === "APPROVED" ? <CheckCircle className="w-3 h-3 text-emerald-600" /> : <Clock className="w-3 h-3 text-amber-600" />}
                      <span>{v.kyc}</span>
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
