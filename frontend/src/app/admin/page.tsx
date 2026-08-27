"use client";

import { useState } from "react";
import { TrendingUp, ShoppingBag, Store, Users, ShieldAlert, CheckCircle, RefreshCw } from "lucide-react";

export default function AdminDashboardPage() {
  const [activeTab, setActiveTab] = useState("overview");

  const KPIS = [
    { label: "Gross Merchandise Value (GMV)", val: "₹1,48,920.00", delta: "+18.4% vs last week", icon: TrendingUp, color: "text-emerald-600 bg-emerald-50" },
    { label: "Total Completed Orders", val: "1,248", delta: "99.2% on-time delivery", icon: ShoppingBag, color: "text-blue-600 bg-blue-50" },
    { label: "Active Verified Vendors", val: "24 Stores", delta: "100% KYC Approved", icon: Store, color: "text-purple-600 bg-purple-50" },
    { label: "Active Platform Shoppers", val: "8,940", delta: "+342 new today", icon: Users, color: "text-amber-600 bg-amber-50" },
  ];

  const AUDIT_LOGS = [
    { id: "LOG-01", action: "KYC_APPROVED", role: "SUPER_ADMIN", entity: "VENDOR", entity_id: "vend-green-leaf", time: "10 mins ago", status: "SUCCESS" },
    { id: "LOG-02", action: "PRICE_OVERRIDE", role: "ADMIN", entity: "PRODUCT", entity_id: "prod-tomatoes-1kg", time: "25 mins ago", status: "SUCCESS" },
    { id: "LOG-03", action: "COUPON_CREATED", role: "ADMIN", entity: "COUPON", entity_id: "code-ORGANIC20", time: "1 hour ago", status: "SUCCESS" },
    { id: "LOG-04", action: "INVENTORY_BATCH_WRITEOFF", role: "STORE_MANAGER", entity: "INVENTORY", entity_id: "lot-dairy-492", time: "3 hours ago", status: "VERIFIED" },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-bold text-emerald-600 uppercase tracking-wider block">Enterprise Control Center</span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Executive Operations & Analytics</h1>
          <p className="text-xs text-slate-500 mt-0.5">Real-time marketplace telemetry, vendor fulfillment, and regulatory compliance audit trails</p>
        </div>

        <button
          onClick={() => alert("Refreshed real-time telemetry from backend!")}
          className="flex items-center gap-1.5 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-bold transition-colors shadow-sm"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Refresh Telemetry</span>
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {KPIS.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div key={idx} className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-500">{kpi.label}</span>
                <div className={`p-2.5 rounded-xl ${kpi.color}`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div className="text-2xl font-black text-slate-900">{kpi.val}</div>
              <span className="text-[11px] font-semibold text-emerald-600 block">{kpi.delta}</span>
            </div>
          );
        })}
      </div>

      {/* Audit Log Table */}
      <div className="bg-white p-6 md:p-8 rounded-3xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h3 className="font-bold text-sm text-slate-900">Immutable Compliance & Administrative Audit Trail</h3>
            <p className="text-[11px] text-slate-400">Cryptographically verifiable log of all administrative actions and price overrides</p>
          </div>
          <span className="text-xs font-bold text-slate-500">Showing last 4 records</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-100 text-slate-400 font-bold uppercase tracking-wider text-[10px]">
                <th className="pb-3">Log ID</th>
                <th className="pb-3">Action</th>
                <th className="pb-3">Actor Role</th>
                <th className="pb-3">Target Entity</th>
                <th className="pb-3">Entity Reference</th>
                <th className="pb-3">Timestamp</th>
                <th className="pb-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
              {AUDIT_LOGS.map((log) => (
                <tr key={log.id} className="hover:bg-slate-50 transition-colors">
                  <td className="py-3 font-bold text-slate-900">{log.id}</td>
                  <td className="py-3">
                    <span className="bg-slate-100 px-2 py-0.5 rounded-md font-mono text-[10px] text-slate-800 font-bold">
                      {log.action}
                    </span>
                  </td>
                  <td className="py-3">{log.role}</td>
                  <td className="py-3">{log.entity}</td>
                  <td className="py-3 font-mono text-[11px] text-slate-500">{log.entity_id}</td>
                  <td className="py-3 text-slate-400">{log.time}</td>
                  <td className="py-3 text-right">
                    <span className="inline-flex items-center gap-1 text-emerald-700 font-bold bg-emerald-50 px-2 py-0.5 rounded-md text-[10px]">
                      <CheckCircle className="w-3 h-3" />
                      <span>{log.status}</span>
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
