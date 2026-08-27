"use client";

import Link from "next/link";
import { useState } from "react";
import { ShoppingCart, Heart, Search, MapPin, User, ShieldCheck } from "lucide-react";

export function Navbar() {
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-slate-100 shadow-sm">
      {/* Top Banner */}
      <div className="bg-emerald-700 text-white text-xs py-1.5 px-4 text-center font-medium tracking-wide">
        ⚡ 30-Minute Express Delivery on Daily Fresh Essentials | Free Delivery on Orders Over ₹499
      </div>

      {/* Main Nav */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex items-center justify-between gap-6">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-2">
          <div className="bg-emerald-600 text-white p-2 rounded-xl font-black text-xl shadow-md">
            FC
          </div>
          <div>
            <span className="font-extrabold text-2xl tracking-tight text-slate-900">
              Fresh<span className="text-emerald-600">Cart</span>
            </span>
            <span className="block text-[10px] text-slate-500 font-semibold tracking-wider uppercase">
              Farm-to-Door Grocery
            </span>
          </div>
        </Link>

        {/* Location selector */}
        <div className="hidden md:flex items-center gap-1.5 text-xs text-slate-600 bg-slate-50 px-3 py-2 rounded-lg border border-slate-200">
          <MapPin className="w-4 h-4 text-emerald-600" />
          <div>
            <span className="font-semibold text-slate-900 block">Deliver to: Hyderabad</span>
            <span className="text-[11px] text-slate-500">Hitec City - 500081</span>
          </div>
        </div>

        {/* Search Bar */}
        <div className="flex-1 max-w-lg relative">
          <input
            type="text"
            placeholder="Search farm fresh tomatoes, basmati rice, organic butter..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:bg-white transition-all shadow-inner"
          />
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
        </div>

        {/* Actions */}
        <div className="flex items-center gap-4">
          <Link
            href="/admin"
            className="hidden lg:flex items-center gap-1 text-xs font-semibold text-slate-700 hover:text-emerald-600 p-2 rounded-lg hover:bg-slate-50 transition-colors"
          >
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Admin</span>
          </Link>

          <Link
            href="/cart"
            className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-full text-sm font-semibold shadow-md hover:shadow-lg transition-all"
          >
            <ShoppingCart className="w-4 h-4" />
            <span>Cart</span>
          </Link>
        </div>
      </div>
    </header>
  );
}
