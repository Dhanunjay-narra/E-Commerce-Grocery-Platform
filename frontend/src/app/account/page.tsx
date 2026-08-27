"use client";
import React from "react";
import Link from "next/link";
import { User, MapPin, Package, Heart, RefreshCw, Shield, Bell, LogOut, ChevronRight } from "lucide-react";

export default function AccountPage() {
  const MENU_SECTIONS = [
    {
      title: "Orders & Reordering",
      items: [
        { label: "My Orders & Live Tracking", href: "/orders/ORD-20260827-HYD01", icon: Package, badge: "1 Active Drop" },
        { label: "Weekly Grocery Subscriptions", href: "/recipes", icon: RefreshCw, badge: "2 Active" },
        { label: "Household Shopping Lists", href: "/catalog", icon: Heart },
      ],
    },
    {
      title: "Personal Information & Delivery",
      items: [
        { label: "Saved Delivery Addresses", href: "/checkout", icon: MapPin },
        { label: "Dietary & Allergen Exclusions", href: "/catalog?is_organic=true", icon: Shield, desc: "Vegetarian, Gluten-Free, Organic Only" },
        { label: "Notification Channels & SMS OTP", href: "/admin", icon: Bell },
      ],
    },
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Profile Header */}
      <div className="bg-white p-6 md:p-8 rounded-3xl border border-slate-200 shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-black text-2xl">
            PS
          </div>
          <div>
            <h1 className="text-xl font-black text-slate-900">Priya Sharma</h1>
            <p className="text-xs text-slate-500">priya.sharma@gmail.com • +91 98765 43210</p>
            <span className="inline-block mt-1 text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-full">
              FreshCart Gold Member (Free Delivery Active)
            </span>
          </div>
        </div>
        <button className="text-xs font-bold text-red-600 hover:text-red-700 flex items-center gap-1 p-2 rounded-xl hover:bg-red-50 transition-colors">
          <LogOut className="w-4 h-4" />
          <span>Sign Out</span>
        </button>
      </div>

      {/* Settings Grid */}
      <div className="space-y-6">
        {MENU_SECTIONS.map((sec, idx) => (
          <div key={idx} className="bg-white rounded-3xl border border-slate-200 overflow-hidden shadow-sm">
            <div className="bg-slate-50 px-6 py-3 border-b border-slate-200 font-bold text-xs text-slate-500 uppercase tracking-wider">
              {sec.title}
            </div>
            <div className="divide-y divide-slate-100">
              {sec.items.map((it, i) => {
                const Icon = it.icon;
                return (
                  <Link
                    key={i}
                    href={it.href}
                    className="p-4 md:p-5 flex items-center justify-between hover:bg-slate-50 transition-colors group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-xl bg-slate-100 text-slate-700 group-hover:bg-emerald-50 group-hover:text-emerald-600 transition-colors">
                        <Icon className="w-4 h-4" />
                      </div>
                      <div>
                        <span className="font-bold text-xs md:text-sm text-slate-900 block">{it.label}</span>
                        {it.desc && <span className="text-[11px] text-slate-400">{it.desc}</span>}
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      {it.badge && (
                        <span className="text-[10px] font-bold bg-emerald-100 text-emerald-800 px-2.5 py-0.5 rounded-full">
                          {it.badge}
                        </span>
                      )}
                      <ChevronRight className="w-4 h-4 text-slate-400 group-hover:translate-x-0.5 transition-transform" />
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
