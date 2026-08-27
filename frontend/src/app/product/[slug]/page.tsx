"use client";

import { useState } from "react";
import Link from "next/link";
import { Star, ShieldCheck, Scale, RefreshCw, ShoppingCart, Check, Truck } from "lucide-react";

export default function ProductDetailPage({ params }: { params: { slug: string } }) {
  const [selectedQty, setSelectedQty] = useState(1.0);
  const [isAdded, setIsAdded] = useState(false);

  // Mock product state based on slug
  const isTomato = params.slug.includes("tomato");
  const isButter = params.slug.includes("butter");

  const product = {
    name: isTomato ? "Organic Farm-Fresh Hybrid Tomatoes" : "Amul Pasteurised Salted Butter 500g",
    brand: isTomato ? "FarmDirect" : "Amul",
    price: isTomato ? 42.0 : 275.0,
    mrp: isTomato ? 48.0 : 285.0,
    unit: isTomato ? "kg" : "pack",
    is_variable: isTomato,
    weight_increment: 0.5,
    tolerance: 15.0,
    is_organic: isTomato,
    rating: 4.8,
    rating_count: 24,
    description: isTomato
      ? "Naturally ripened on vines without artificial chemicals. Juicy and firm texture packed with antioxidants."
      : "The classic taste of India. Pure cream butter made with natural salt and fresh cow and buffalo milk cream.",
    img: isTomato
      ? "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=800"
      : "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=800",
    nutrition: {
      energy: isTomato ? "18 kcal" : "717 kcal",
      carbs: isTomato ? "3.9 g" : "0.0 g",
      protein: isTomato ? "0.9 g" : "0.5 g",
      fat: isTomato ? "0.2 g" : "80.0 g",
    },
    substitute: isButter
      ? {
          name: "Mother Dairy Pure Table Butter 500g",
          price: 270.0,
          delta: "-₹5.00",
          img: "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=300",
        }
      : null,
  };

  const estimatedTotal = round(selectedQty * product.price, 2);

  function round(val: number, dec: number) {
    return Number(Math.round(Number(val + "e" + dec)) + "e-" + dec);
  }

  const handleAdd = () => {
    setIsAdded(true);
    setTimeout(() => setIsAdded(false), 2000);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12">
      {/* Breadcrumbs */}
      <div className="text-xs text-slate-400">
        <Link href="/" className="hover:text-slate-600">Home</Link> / <Link href="/catalog" className="hover:text-slate-600">Catalog</Link> / <span className="text-slate-900 font-semibold">{product.name}</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
        {/* Media Preview */}
        <div className="space-y-4">
          <div className="relative h-96 rounded-3xl bg-slate-100 overflow-hidden border border-slate-200">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={product.img}
              alt={product.name}
              className="w-full h-full object-cover"
            />
            {product.is_organic && (
              <span className="absolute top-4 left-4 bg-emerald-600 text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider shadow">
                100% Certified Organic
              </span>
            )}
          </div>
        </div>

        {/* Product Details & Scale Weight Selector */}
        <div className="space-y-6">
          <div>
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">{product.brand}</span>
            <h1 className="text-2xl md:text-3xl font-black text-slate-900 tracking-tight">{product.name}</h1>
            <div className="flex items-center gap-2 mt-2">
              <div className="flex items-center gap-1 text-amber-500 text-xs font-bold bg-amber-50 px-2.5 py-1 rounded-lg border border-amber-200">
                <Star className="w-4 h-4 fill-current" />
                <span>{product.rating}</span>
              </div>
              <span className="text-xs text-slate-500">({product.rating_count} verified reviews)</span>
            </div>
          </div>

          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-2">
            <div className="flex items-baseline gap-3">
              <span className="text-3xl font-black text-slate-900">₹{product.price}</span>
              <span className="text-sm text-slate-400 line-through">₹{product.mrp}</span>
              <span className="text-xs font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full">
                Save ₹{product.mrp - product.price}
              </span>
            </div>
            <span className="text-xs text-slate-500 block">Unit base price per {product.unit}</span>
          </div>

          {/* Variable weight scale configuration */}
          {product.is_variable && (
            <div className="p-4 bg-emerald-50 rounded-2xl border border-emerald-200 space-y-3">
              <div className="flex items-center gap-2 text-emerald-900 font-bold text-xs">
                <Scale className="w-4 h-4 text-emerald-600" />
                <span>Variable-Weight Produce Precision Pricing</span>
              </div>
              <p className="text-[11px] text-emerald-800 leading-relaxed">
                Produce weights vary naturally. Your picker will weigh this accurately at the dark store scale (tolerance ±{product.tolerance}%). Your final invoice will automatically adjust to the exact grams picked.
              </p>

              {/* Increments Selector */}
              <div className="flex items-center gap-3 pt-1">
                <span className="text-xs font-semibold text-slate-700">Choose Quantity:</span>
                {[0.5, 1.0, 1.5, 2.0].map((qty) => (
                  <button
                    key={qty}
                    onClick={() => setSelectedQty(qty)}
                    className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all border ${
                      selectedQty === qty
                        ? "bg-emerald-600 text-white border-emerald-600 shadow-sm"
                        : "bg-white text-slate-700 border-slate-200 hover:border-emerald-400"
                    }`}
                  >
                    {qty} {product.unit}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Add to Cart Button */}
          <div className="flex items-center gap-4 pt-2">
            <button
              onClick={handleAdd}
              className={`flex-1 py-4 px-6 rounded-2xl font-bold text-sm shadow-md transition-all flex items-center justify-center gap-2 ${
                isAdded
                  ? "bg-emerald-700 text-white"
                  : "bg-emerald-600 hover:bg-emerald-700 text-white hover:shadow-lg"
              }`}
            >
              {isAdded ? (
                <>
                  <Check className="w-5 h-5" />
                  <span>Added {selectedQty} {product.unit} to Cart (₹{estimatedTotal})</span>
                </>
              ) : (
                <>
                  <ShoppingCart className="w-5 h-5" />
                  <span>Add {selectedQty} {product.unit} to Cart — ₹{estimatedTotal}</span>
                </>
              )}
            </button>
          </div>

          <div className="grid grid-cols-2 gap-4 text-xs pt-4 border-t border-slate-100">
            <div className="flex items-center gap-2 text-slate-600">
              <Truck className="w-4 h-4 text-emerald-600" />
              <span>Express 30-Min Delivery Slot</span>
            </div>
            <div className="flex items-center gap-2 text-slate-600">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>FEFO Lot Freshness Guarantee</span>
            </div>
          </div>
        </div>
      </div>

      {/* Smart Substitute Recommendation */}
      {product.substitute && (
        <section className="p-6 bg-slate-50 rounded-3xl border border-slate-200 space-y-4">
          <div className="flex items-center gap-2 text-slate-900 font-bold text-sm">
            <RefreshCw className="w-4 h-4 text-emerald-600" />
            <span>Smart Out-of-Stock Fallback Substitute</span>
          </div>
          <p className="text-xs text-slate-500">
            If this item runs out at the vendor fulfillment store, our algorithm has verified this alternative:
          </p>

          <div className="flex items-center justify-between bg-white p-4 rounded-2xl border border-slate-200">
            <div className="flex items-center gap-4">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={product.substitute.img}
                alt={product.substitute.name}
                className="w-12 h-12 rounded-xl object-cover"
              />
              <div>
                <h4 className="font-bold text-xs text-slate-900">{product.substitute.name}</h4>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="font-bold text-xs text-slate-900">₹{product.substitute.price}</span>
                  <span className="text-[10px] text-emerald-700 font-bold">{product.substitute.delta}</span>
                </div>
              </div>
            </div>
            <span className="text-[10px] font-bold bg-emerald-50 text-emerald-700 px-3 py-1 rounded-full border border-emerald-200">
              95% Match Score
            </span>
          </div>
        </section>
      )}
    </div>
  );
}
