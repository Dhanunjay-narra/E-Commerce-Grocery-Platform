"use client";
import React, { useState } from "react";
import Link from "next/link";
import { Utensils, Clock, Users, Plus, CheckCircle, Sparkles, ChefHat } from "lucide-react";

const RECIPES = [
  {
    id: "rec-1",
    title: "Classic Creamy Paneer Butter Masala",
    cuisine: "North Indian",
    prepTime: "25 mins",
    servings: 4,
    calories: "380 kcal",
    difficulty: "Easy",
    img: "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=600",
    ingredients: [
      { name: "Fresh Malai Paneer 200g", price: 92.0, unit: "pack", inStock: true },
      { name: "Organic Hybrid Tomatoes 500g", price: 21.0, unit: "kg", inStock: true },
      { name: "Amul Pasteurised Butter 100g", price: 58.0, unit: "pack", inStock: true },
      { name: "Fresh Ginger & Garlic 100g", price: 20.0, unit: "pack", inStock: true },
      { name: "Fresh Cream 200ml", price: 65.0, unit: "pack", inStock: true },
    ],
    bundlePrice: 256.0,
    mrp: 295.0,
  },
  {
    id: "rec-2",
    title: "South Indian Sambar & Steamed Idli Batter",
    cuisine: "South Indian",
    prepTime: "20 mins",
    servings: 4,
    calories: "240 kcal",
    difficulty: "Beginner",
    img: "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=600",
    ingredients: [
      { name: "Tata Sampann Toor Dal 500g", price: 88.0, unit: "pack", inStock: true },
      { name: "ID Fresh Idli & Dosa Batter 1kg", price: 80.0, unit: "pouch", inStock: true },
      { name: "Fresh Drumsticks / Moringa 250g", price: 30.0, unit: "pack", inStock: true },
      { name: "Shallots / Sambhar Onions 250g", price: 25.0, unit: "pack", inStock: true },
    ],
    bundlePrice: 223.0,
    mrp: 260.0,
  },
  {
    id: "rec-3",
    title: "Mediterranean Farm-Fresh Greek Salad",
    cuisine: "Continental",
    prepTime: "10 mins",
    servings: 2,
    calories: "190 kcal",
    difficulty: "Quick (No Cook)",
    img: "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=600",
    ingredients: [
      { name: "English Seedless Cucumbers 500g", price: 30.0, unit: "pack", inStock: true },
      { name: "Organic Cherry Tomatoes 250g", price: 45.0, unit: "pack", inStock: true },
      { name: "Greek Style Feta Cheese 150g", price: 180.0, unit: "tub", inStock: true },
      { name: "Extra Virgin Olive Oil 250ml", price: 290.0, unit: "bottle", inStock: true },
    ],
    bundlePrice: 545.0,
    mrp: 610.0,
  },
];

export default function RecipesPage() {
  const [addedRecipeId, setAddedRecipeId] = useState<string | null>(null);

  const handleAddBundleToCart = (id: string) => {
    setAddedRecipeId(id);
    setTimeout(() => setAddedRecipeId(null), 2500);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      {/* Header Banner */}
      <div className="relative rounded-3xl bg-gradient-to-r from-emerald-900 via-teal-900 to-slate-900 text-white p-8 md:p-12 overflow-hidden shadow-xl">
        <div className="max-w-2xl space-y-3 relative z-10">
          <div className="inline-flex items-center gap-2 bg-white/10 px-3 py-1 rounded-full text-xs font-semibold text-emerald-300">
            <ChefHat className="w-4 h-4" />
            <span>One-Click Recipe-to-Cart Grocery Bundling</span>
          </div>
          <h1 className="text-3xl md:text-5xl font-black tracking-tight">Cook Fresh at Home Tonight</h1>
          <p className="text-emerald-100 text-xs md:text-sm leading-relaxed">
            Select authentic chef-curated recipes and add exact measured ingredients directly to your FreshCart in 1 click. Zero food waste, guaranteed FEFO freshness.
          </p>
        </div>
      </div>

      {/* Recipe Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {RECIPES.map((rec) => (
          <div key={rec.id} className="bg-white rounded-3xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
            <div>
              <div className="relative h-52 bg-slate-100">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={rec.img} alt={rec.title} className="w-full h-full object-cover" />
                <span className="absolute top-3 left-3 bg-slate-900/80 text-white text-[10px] font-bold px-2.5 py-1 rounded-full backdrop-blur-sm">
                  {rec.cuisine}
                </span>
                <span className="absolute bottom-3 left-3 bg-emerald-600 text-white text-[10px] font-bold px-2.5 py-1 rounded-full shadow">
                  Save ₹{rec.mrp - rec.bundlePrice} Bundle Discount
                </span>
              </div>

              <div className="p-6 space-y-4">
                <div>
                  <h3 className="font-bold text-base text-slate-900 tracking-tight">{rec.title}</h3>
                  <div className="flex items-center gap-4 text-[11px] text-slate-500 mt-2">
                    <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5 text-emerald-600" /> {rec.prepTime}</span>
                    <span className="flex items-center gap-1"><Users className="w-3.5 h-3.5 text-emerald-600" /> {rec.servings} Servings</span>
                    <span className="flex items-center gap-1"><Sparkles className="w-3.5 h-3.5 text-amber-500" /> {rec.calories}</span>
                  </div>
                </div>

                <div className="space-y-2 pt-2 border-t border-slate-100">
                  <span className="text-xs font-bold text-slate-800 uppercase tracking-wider block">Bundle Ingredients:</span>
                  <div className="space-y-1.5">
                    {rec.ingredients.map((ing, i) => (
                      <div key={i} className="flex justify-between text-xs text-slate-600">
                        <span>• {ing.name}</span>
                        <span className="font-semibold text-slate-900">₹{ing.price}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="p-6 pt-0">
              <div className="flex items-baseline justify-between mb-3 pt-3 border-t border-slate-100">
                <div>
                  <span className="font-black text-lg text-slate-900">₹{rec.bundlePrice}</span>
                  <span className="text-xs text-slate-400 line-through ml-2">₹{rec.mrp}</span>
                </div>
                <span className="text-[10px] text-emerald-700 font-bold bg-emerald-50 px-2 py-0.5 rounded-full">
                  All Items in Stock
                </span>
              </div>

              <button
                onClick={() => handleAddBundleToCart(rec.id)}
                className={`w-full py-3 px-4 rounded-2xl font-bold text-xs shadow-md transition-all flex items-center justify-center gap-2 ${
                  addedRecipeId === rec.id
                    ? "bg-emerald-700 text-white"
                    : "bg-emerald-600 hover:bg-emerald-700 text-white"
                }`}
              >
                {addedRecipeId === rec.id ? (
                  <>
                    <CheckCircle className="w-4 h-4" />
                    <span>Added {rec.ingredients.length} Items to Cart!</span>
                  </>
                ) : (
                  <>
                    <Plus className="w-4 h-4" />
                    <span>Add All Recipe Ingredients to Cart</span>
                  </>
                )}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
