"use client";
import React, { useState } from "react";
import { Users, Plus, CheckCircle, Share2, ShoppingCart, Trash2 } from "lucide-react";

export default function HouseholdsPage() {
  const [items, setItems] = useState([
    { id: "1", name: "Amul Pasteurised Butter 500g", addedBy: "Priya (Owner)", done: false },
    { id: "2", name: "Organic Hybrid Tomatoes 1.5kg", addedBy: "Arun (Member)", done: true },
    { id: "3", name: "Daawat Basmati Rice 5kg", addedBy: "Priya (Owner)", done: false },
    { id: "4", name: "Country Delight Cow Milk 1L", addedBy: "Priya (Owner)", done: false },
  ]);

  const toggleDone = (id: string) => {
    setItems((prev) => prev.map((it) => (it.id === id ? { ...it, done: !it.done } : it)));
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-bold text-emerald-600 uppercase tracking-wider block">Collaborative Grocery Cart</span>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Sharma Family Household</h1>
          <p className="text-xs text-slate-500">Shared shopping list synchronized across 3 family members</p>
        </div>

        <button
          onClick={() => alert("Invite link copied to clipboard: https://freshcart.com/join/sharma-family")}
          className="flex items-center gap-1.5 px-4 py-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 rounded-xl text-xs font-bold transition-colors"
        >
          <Share2 className="w-4 h-4" />
          <span>Invite Member</span>
        </button>
      </div>

      <div className="bg-white rounded-3xl border border-slate-200 p-6 space-y-4 shadow-sm">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <h3 className="font-bold text-sm text-slate-900">Active Grocery Checklist</h3>
          <span className="text-xs text-slate-400">{items.filter(i => i.done).length} of {items.length} items checked</span>
        </div>

        <div className="divide-y divide-slate-100">
          {items.map((it) => (
            <div key={it.id} className="py-3 flex items-center justify-between">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={it.done}
                  onChange={() => toggleDone(it.id)}
                  className="w-4 h-4 text-emerald-600 rounded border-slate-300 focus:ring-emerald-500"
                />
                <div>
                  <span className={`text-xs font-bold block ${it.done ? "line-through text-slate-400" : "text-slate-900"}`}>
                    {it.name}
                  </span>
                  <span className="text-[10px] text-slate-400">Added by {it.addedBy}</span>
                </div>
              </label>
            </div>
          ))}
        </div>

        <button
          onClick={() => alert("Moving all pending checklist items to Unified Shopping Cart...")}
          className="w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white rounded-2xl font-bold text-xs shadow-md transition-all flex items-center justify-center gap-2"
        >
          <ShoppingCart className="w-4 h-4" />
          <span>Move All Items to Cart & Order Together</span>
        </button>
      </div>
    </div>
  );
}
