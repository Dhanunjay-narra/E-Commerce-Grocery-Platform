"use client";

import { useState } from "react";
import Link from "next/link";
import { Filter, Star, Plus, Check } from "lucide-react";

const PRODUCTS_DATA = [
  {
    id: "1",
    name: "Organic Farm-Fresh Hybrid Tomatoes",
    slug: "organic-farm-fresh-hybrid-tomatoes",
    brand: "FarmDirect",
    category: "Produce",
    price: 42.0,
    mrp: 48.0,
    unit: "kg",
    is_organic: true,
    is_variable: true,
    rating: 4.8,
    img: "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500",
  },
  {
    id: "2",
    name: "Fresh Nashik Red Onions",
    slug: "fresh-nashik-red-onions",
    brand: "FarmDirect",
    category: "Produce",
    price: 28.0,
    mrp: 35.0,
    unit: "kg",
    is_organic: false,
    is_variable: true,
    rating: 4.6,
    img: "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=500",
  },
  {
    id: "3",
    name: "Royal Gala Crisp Red Apples 4-Pack",
    slug: "royal-gala-crisp-red-apples-4-pack",
    brand: "Himalayan Orchards",
    category: "Produce",
    price: 165.0,
    mrp: 190.0,
    unit: "pack",
    is_organic: true,
    is_variable: false,
    rating: 4.9,
    img: "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=500",
  },
  {
    id: "4",
    name: "Amul Pasteurised Butter 500g",
    slug: "amul-pasteurised-butter-500g",
    brand: "Amul",
    category: "Dairy",
    price: 275.0,
    mrp: 285.0,
    unit: "pack",
    is_organic: false,
    is_variable: false,
    rating: 4.9,
    img: "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=500",
  },
  {
    id: "5",
    name: "Mother Dairy Pure Table Butter 500g",
    slug: "mother-dairy-pure-table-butter-500g",
    brand: "Mother Dairy",
    category: "Dairy",
    price: 270.0,
    mrp: 280.0,
    unit: "pack",
    is_organic: false,
    is_variable: false,
    rating: 4.7,
    img: "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=500",
  },
  {
    id: "6",
    name: "Daawat Rozana Gold Basmati Rice 5kg",
    slug: "daawat-rozana-gold-basmati-rice-5kg",
    brand: "Daawat",
    category: "Pantry",
    price: 520.0,
    mrp: 580.0,
    unit: "bag",
    is_organic: false,
    is_variable: false,
    rating: 4.8,
    img: "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=500",
  },
  {
    id: "7",
    name: "Puvi Cold Pressed Groundnut Oil 1L",
    slug: "puvi-cold-pressed-groundnut-oil-1l",
    brand: "Puvi",
    category: "Pantry",
    price: 235.0,
    mrp: 260.0,
    unit: "bottle",
    is_organic: true,
    is_variable: false,
    rating: 4.9,
    img: "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500",
  },
];

export default function CatalogPage() {
  const [selectedCat, setSelectedCat] = useState("All");
  const [organicOnly, setOrganicOnly] = useState(false);
  const [addedItems, setAddedItems] = useState<Record<string, boolean>>({});

  const filtered = PRODUCTS_DATA.filter((p) => {
    if (selectedCat !== "All" && p.category !== selectedCat) return false;
    if (organicOnly && !p.is_organic) return false;
    return true;
  });

  const handleAddToCart = (id: string) => {
    setAddedItems((prev) => ({ ...prev, [id]: true }));
    setTimeout(() => {
      setAddedItems((prev) => ({ ...prev, [id]: false }));
    }, 1500);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumbs & Header */}
      <div className="mb-8">
        <div className="text-xs text-slate-400 mb-1">
          <Link href="/" className="hover:text-slate-600">Home</Link> / <span className="text-slate-900 font-semibold">Grocery Catalog</span>
        </div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">All Grocery Essentials</h1>
        <p className="text-xs text-slate-500 mt-1">Showing {filtered.length} products available for 30-min express slot</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
        {/* Facet Sidebar */}
        <aside className="space-y-6 bg-white p-6 rounded-2xl border border-slate-200 h-fit">
          <div className="flex items-center gap-2 font-bold text-slate-900 pb-3 border-b border-slate-100">
            <Filter className="w-4 h-4 text-emerald-600" />
            <span>Faceted Filters</span>
          </div>

          {/* Category Filter */}
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-800 uppercase tracking-wider block">Department</label>
            {["All", "Produce", "Dairy", "Pantry"].map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCat(cat)}
                className={`w-full text-left px-3 py-2 rounded-lg text-xs font-medium transition-colors flex items-center justify-between ${
                  selectedCat === cat ? "bg-emerald-50 text-emerald-800 font-bold" : "text-slate-600 hover:bg-slate-50"
                }`}
              >
                <span>{cat}</span>
                {selectedCat === cat && <Check className="w-3.5 h-3.5 text-emerald-600" />}
              </button>
            ))}
          </div>

          {/* Dietary Filters */}
          <div className="space-y-3 pt-3 border-t border-slate-100">
            <label className="text-xs font-bold text-slate-800 uppercase tracking-wider block">Dietary & Health</label>
            <label className="flex items-center gap-2 text-xs text-slate-700 cursor-pointer">
              <input
                type="checkbox"
                checked={organicOnly}
                onChange={(e) => setOrganicOnly(e.target.checked)}
                className="w-4 h-4 text-emerald-600 rounded border-slate-300 focus:ring-emerald-500"
              />
              <span>100% Certified Organic</span>
            </label>
          </div>
        </aside>

        {/* Products Grid */}
        <main className="md:col-span-3">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {filtered.map((prod) => (
              <div
                key={prod.id}
                className="bg-white border border-slate-200 rounded-2xl overflow-hidden hover:shadow-md transition-shadow flex flex-col group"
              >
                <Link href={`/product/${prod.slug}`} className="relative h-48 bg-slate-100 overflow-hidden block">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={prod.img}
                    alt={prod.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  {prod.is_organic && (
                    <span className="absolute top-2.5 left-2.5 bg-emerald-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider shadow">
                      Organic
                    </span>
                  )}
                  {prod.is_variable && (
                    <span className="absolute bottom-2.5 left-2.5 bg-slate-900/80 text-white text-[10px] font-medium px-2 py-0.5 rounded-md backdrop-blur-sm">
                      ⚖️ Scale Weighed
                    </span>
                  )}
                </Link>

                <div className="p-4 flex-1 flex flex-col justify-between space-y-3">
                  <div>
                    <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                      {prod.brand}
                    </span>
                    <Link
                      href={`/product/${prod.slug}`}
                      className="font-bold text-sm text-slate-900 hover:text-emerald-600 line-clamp-2 transition-colors"
                    >
                      {prod.name}
                    </Link>
                    <div className="flex items-center gap-1 mt-1 text-amber-500 text-xs font-semibold">
                      <Star className="w-3.5 h-3.5 fill-current" />
                      <span>{prod.rating}</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-slate-100">
                    <div>
                      <div className="flex items-baseline gap-1.5">
                        <span className="font-extrabold text-base text-slate-900">₹{prod.price}</span>
                        <span className="text-xs text-slate-400 line-through">₹{prod.mrp}</span>
                      </div>
                      <span className="text-[10px] text-slate-500">per {prod.unit}</span>
                    </div>

                    <button
                      onClick={() => handleAddToCart(prod.id)}
                      className={`p-2 rounded-xl transition-all shadow-sm flex items-center gap-1 text-xs font-bold ${
                        addedItems[prod.id]
                          ? "bg-emerald-600 text-white"
                          : "bg-emerald-50 text-emerald-700 hover:bg-emerald-600 hover:text-white"
                      }`}
                    >
                      {addedItems[prod.id] ? <Check className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
                      <span>{addedItems[prod.id] ? "Added" : "Add"}</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </main>
      </div>
    </div>
  );
}
