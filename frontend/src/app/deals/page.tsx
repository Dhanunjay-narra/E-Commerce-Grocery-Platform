"use client";
import React, { useState } from "react";
import Link from "next/link";
import { Zap, Flame, Clock, Tag, Plus, Check } from "lucide-react";
import { FlashSaleCounter } from "@/components/grocery/FlashSaleCounter";

export default function DealsPage() {
  const DEALS = [
    { id: "d-1", name: "Organic Farm-Fresh Tomatoes", brand: "FarmDirect", price: 29.0, mrp: 48.0, unit: "kg", discount: "40% OFF", img: "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=400" },
    { id: "d-2", name: "Amul Pasteurised Butter 500g", brand: "Amul", price: 235.0, mrp: 285.0, unit: "pack", discount: "18% OFF", img: "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=400" },
    { id: "d-3", name: "Royal Gala Crisp Apples 4-Pack", brand: "Himalayan Orchards", price: 125.0, mrp: 190.0, unit: "pack", discount: "34% OFF", img: "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=400" },
    { id: "d-4", name: "Puvi Cold Pressed Groundnut Oil 1L", brand: "Puvi", price: 195.0, mrp: 260.0, unit: "bottle", discount: "25% OFF", img: "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400" },
    { id: "d-5", name: "Daawat Rozana Gold Basmati 5kg", brand: "Daawat", price: 440.0, mrp: 580.0, unit: "bag", discount: "24% OFF", img: "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400" },
    { id: "d-6", name: "Tata Sampann Toor Dal 1kg", brand: "Tata Sampann", price: 145.0, mrp: 195.0, unit: "pack", discount: "26% OFF", img: "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400" },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      <div className="bg-gradient-to-r from-red-600 via-orange-600 to-amber-600 rounded-3xl p-8 text-white flex flex-col md:flex-row items-center justify-between gap-6 shadow-xl">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-1.5 bg-black/20 px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider">
            <Flame className="w-4 h-4 text-amber-300 fill-current" />
            <span>Today&apos;s Mega Flash Markdown</span>
          </div>
          <h1 className="text-3xl md:text-5xl font-black tracking-tight">Save Up to 50% on Daily Staples</h1>
          <p className="text-orange-100 text-xs md:text-sm">Limited stock available at nearest dark-store fulfillment hubs.</p>
        </div>
        <FlashSaleCounter />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {DEALS.map((deal) => (
          <div key={deal.id} className="bg-white rounded-3xl border border-slate-200 p-4 flex flex-col justify-between shadow-sm hover:shadow-md transition-shadow group">
            <div>
              <div className="relative h-36 bg-slate-100 rounded-2xl overflow-hidden mb-3">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={deal.img} alt={deal.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform" />
                <span className="absolute top-2 left-2 bg-red-600 text-white text-[10px] font-black px-2 py-0.5 rounded-full shadow">
                  {deal.discount}
                </span>
              </div>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">{deal.brand}</span>
              <h3 className="font-bold text-xs text-slate-900 line-clamp-2 mt-0.5">{deal.name}</h3>
            </div>

            <div className="pt-3 border-t border-slate-100 mt-3 flex items-center justify-between">
              <div>
                <span className="font-black text-sm text-slate-900 block">₹{deal.price}</span>
                <span className="text-[10px] text-slate-400 line-through">₹{deal.mrp}</span>
              </div>
              <button
                onClick={() => alert(`Added ${deal.name} to Cart!`)}
                className="p-2 rounded-xl bg-emerald-50 text-emerald-700 hover:bg-emerald-600 hover:text-white transition-colors"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
