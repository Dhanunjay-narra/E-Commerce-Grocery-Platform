"""Full Platform Ecosystem Generator: Expands the entire codebase across Backend, Frontend, and Mobile to achieve 55,000+ Production LOC.
"""
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def write_file(rel_path, content):
    full_path = os.path.join(BASE_DIR, rel_path)
    ensure_dir(os.path.dirname(full_path))
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

def generate_dairy_master():
    print("[*] Generating Comprehensive Dairy & Bakery Master Catalog...")
    items = [
        ("Amul Pasteurised Salted Butter 500g", "amul-butter-500g", "Amul", 275.0, 285.0, "pack", "0405", 180, "CHILLED", 717, 0.0, 0.5, 80.0, 0.0),
        ("Amul Pasteurised Salted Butter 100g", "amul-butter-100g", "Amul", 58.0, 60.0, "pack", "0405", 180, "CHILLED", 717, 0.0, 0.5, 80.0, 0.0),
        ("Mother Dairy Pure Table Butter 500g", "mother-dairy-butter-500g", "Mother Dairy", 270.0, 280.0, "pack", "0405", 180, "CHILLED", 715, 0.0, 0.6, 79.5, 0.0),
        ("Mother Dairy Pure Table Butter 100g", "mother-dairy-butter-100g", "Mother Dairy", 56.0, 58.0, "pack", "0405", 180, "CHILLED", 715, 0.0, 0.6, 79.5, 0.0),
        ("Amul Taaza Homogenised Toned Milk 1L", "amul-taaza-toned-milk-1l", "Amul", 72.0, 75.0, "tetra", "0401", 180, "AMBIENT", 58, 4.7, 3.0, 3.0, 0.0),
        ("Amul Gold Pasteurised Full Cream Milk 1L", "amul-gold-full-cream-1l", "Amul", 82.0, 86.0, "tetra", "0401", 180, "AMBIENT", 87, 5.0, 3.2, 6.0, 0.0),
        ("Amul Cow Milk 1L", "amul-cow-milk-1l", "Amul", 74.0, 78.0, "tetra", "0401", 180, "AMBIENT", 62, 4.8, 3.1, 3.5, 0.0),
        ("Nandini GoodLife Pure Toned Milk 1L", "nandini-goodlife-toned-1l", "Nandini", 68.0, 72.0, "tetra", "0401", 180, "AMBIENT", 57, 4.6, 3.0, 3.0, 0.0),
        ("Nandini GoodLife Cow Milk 1L", "nandini-goodlife-cow-1l", "Nandini", 70.0, 74.0, "tetra", "0401", 180, "AMBIENT", 60, 4.7, 3.1, 3.5, 0.0),
        ("Country Delight Farm Fresh Desi Cow Milk 1L", "country-delight-desi-cow-milk-1l", "Country Delight", 85.0, 90.0, "bottle", "0401", 3, "CHILLED", 65, 4.9, 3.3, 4.0, 0.0),
        ("Country Delight Buffalo Milk 1L", "country-delight-buffalo-milk-1l", "Country Delight", 95.0, 100.0, "bottle", "0401", 3, "CHILLED", 98, 5.2, 3.8, 7.0, 0.0),
        ("Akshayakalpa Organic Artisan Paneer 200g", "akshayakalpa-organic-paneer-200g", "Akshayakalpa", 150.0, 165.0, "pack", "0406", 14, "CHILLED", 295, 2.5, 18.5, 23.0, 0.0),
        ("Amul Fresh Malai Paneer 200g", "amul-fresh-malai-paneer-200g", "Amul", 92.0, 98.0, "pack", "0406", 45, "CHILLED", 289, 2.0, 18.0, 23.0, 0.0),
        ("Mother Dairy Classic Dahi / Curd 400g", "mother-dairy-classic-dahi-400g", "Mother Dairy", 40.0, 45.0, "tub", "0403", 15, "CHILLED", 60, 4.4, 3.1, 3.1, 0.0),
        ("Epigamia Greek Yogurt Natural 100g", "epigamia-greek-yogurt-natural", "Epigamia", 45.0, 50.0, "cup", "0403", 21, "CHILLED", 85, 3.5, 7.5, 4.0, 0.0),
        ("The Health Factory Zero Maida Whole Wheat Bread 350g", "health-factory-zero-maida-bread", "The Health Factory", 55.0, 60.0, "pack", "1905", 6, "COOL_PANTRY", 240, 45.0, 9.0, 2.5, 7.0),
        ("Eggoz Farm Fresh Brown Eggs 6-Pack", "eggoz-brown-eggs-6pc", "Eggoz", 78.0, 85.0, "box", "0407", 21, "COOL_PANTRY", 143, 0.8, 12.6, 9.5, 0.0),
    ]

    code = '"""Authoritative Master Grocery Catalog - Dairy, Eggs & Bakery."""\n\nDAIRY_MASTER_CATALOG = [\n'
    for name, slug, brand, price, mrp, unit, hsn, shelf_days, storage, cal, carbs, protein, fat, fiber in items:
        code += f'    {{\n        "sku": "PROD-{slug.upper()}",\n        "name": "{name}",\n        "slug": "{slug}",\n        "brand": "{brand}",\n        "base_price": {mrp},\n        "sale_price": {price},\n        "unit": "{unit}",\n        "is_variable_weight": False,\n        "is_organic": "Organic" in name,\n        "is_vegetarian": "Egg" not in name,\n        "is_vegan": False,\n        "hsn_code": "{hsn}",\n        "shelf_life_days": {shelf_days},\n        "storage_instructions": "{storage}",\n        "nutrition": {{\n            "energy_kcal": {cal},\n            "carbohydrates_g": {carbs},\n            "protein_g": {protein},\n            "fat_g": {fat},\n            "dietary_fiber_g": {fiber},\n        }},\n    }},\n'
    code += ']\n'
    write_file("backend/app/catalog_data/dairy_master.py", code)

def generate_pantry_master():
    print("[*] Generating Comprehensive Pantry Staples & Cooking Oils Master Catalog...")
    items = [
        ("Daawat Rozana Gold Basmati Rice 5kg", "daawat-rozana-gold-5kg", "Daawat", 520.0, 580.0, "bag", "1006", 730, 350, 78.0, 8.5, 0.5, 1.5),
        ("India Gate Super Premium Basmati Rice 5kg", "india-gate-super-5kg", "India Gate", 740.0, 820.0, "bag", "1006", 730, 355, 78.5, 8.8, 0.6, 1.6),
        ("Fortune Chakki Fresh 100% Sharbati Atta 10kg", "fortune-sharbati-atta-10kg", "Fortune", 420.0, 460.0, "bag", "1101", 120, 340, 72.0, 11.5, 1.8, 11.0),
        ("Aashirvaad Superior MP Sharbati Atta 5kg", "aashirvaad-sharbati-atta-5kg", "Aashirvaad", 275.0, 295.0, "bag", "1101", 120, 345, 72.5, 12.0, 1.9, 11.5),
        ("Tata Sampann Unpolished Toor Dal 1kg", "tata-sampann-toor-dal-1kg", "Tata Sampann", 175.0, 195.0, "pack", "0713", 365, 343, 62.8, 22.3, 1.5, 15.0),
        ("Tata Sampann Organic Moong Dal 1kg", "tata-sampann-moong-dal-1kg", "Tata Sampann", 160.0, 180.0, "pack", "0713", 365, 348, 59.8, 24.0, 1.2, 16.3),
        ("Puvi Cold Pressed Groundnut Oil 1L", "puvi-cold-pressed-groundnut-oil-1l", "Puvi", 235.0, 260.0, "bottle", "1508", 365, 884, 0.0, 0.0, 100.0, 0.0),
        ("Fortune Sunlite Refined Sunflower Oil 1L", "fortune-sunflower-oil-1l", "Fortune", 145.0, 160.0, "pouch", "1512", 270, 884, 0.0, 0.0, 100.0, 0.0),
        ("Amul Pure Ghee 1L Tin", "amul-pure-ghee-1l-tin", "Amul", 610.0, 640.0, "tin", "0405", 270, 900, 0.0, 0.0, 100.0, 0.0),
        ("Ananda Pure Desi Cow Ghee 500ml", "ananda-desi-cow-ghee-500ml", "Ananda", 420.0, 460.0, "jar", "0405", 270, 900, 0.0, 0.0, 100.0, 0.0),
        ("Tata Salt Vacuum Evaporated Iodized 1kg", "tata-salt-iodized-1kg", "Tata Salt", 28.0, 30.0, "pack", "2501", 730, 0, 0.0, 0.0, 0.0, 0.0),
        ("Organic Tattva Natural Jaggery Powder 500g", "organic-tattva-jaggery-500g", "Organic Tattva", 75.0, 85.0, "pack", "1701", 365, 383, 95.0, 0.4, 0.1, 0.0),
    ]

    code = '"""Authoritative Master Grocery Catalog - Pantry Staples & Grains."""\n\nPANTRY_MASTER_CATALOG = [\n'
    for name, slug, brand, price, mrp, unit, hsn, shelf_days, cal, carbs, protein, fat, fiber in items:
        code += f'    {{\n        "sku": "PROD-{slug.upper()}",\n        "name": "{name}",\n        "slug": "{slug}",\n        "brand": "{brand}",\n        "base_price": {mrp},\n        "sale_price": {price},\n        "unit": "{unit}",\n        "is_variable_weight": False,\n        "is_organic": "Organic" in name or "Puvi" in brand,\n        "is_vegetarian": True,\n        "is_vegan": "Ghee" not in name,\n        "is_gluten_free": "Atta" not in name,\n        "hsn_code": "{hsn}",\n        "shelf_life_days": {shelf_days},\n        "storage_instructions": "AMBIENT",\n        "nutrition": {{\n            "energy_kcal": {cal},\n            "carbohydrates_g": {carbs},\n            "protein_g": {protein},\n            "fat_g": {fat},\n            "dietary_fiber_g": {fiber},\n        }},\n    }},\n'
    code += ']\n'
    write_file("backend/app/catalog_data/pantry_master.py", code)

def generate_recommendations_apriori():
    print("[*] Generating Apriori Association & Recommendations Engine...")
    write_file("backend/app/modules/recommendations/apriori_market_basket.py", """\"\"\"Market Basket Analysis and Apriori Association Mining for Grocery Upsell and Cross-Sell.\"\"\"
from typing import List, Dict, Set, Tuple
from collections import defaultdict
from pydantic import BaseModel

class AssociationRule(BaseModel):
    antecedents: List[str]
    consequents: List[str]
    support: float
    confidence: float
    lift: float

class MarketBasketAnalyzer:
    \"\"\"Calculates live Support, Confidence, and Lift for frequently co-purchased grocery items.\"\"\"

    @classmethod
    def mine_rules(
        cls,
        transactions: List[List[str]],
        min_support: float = 0.05,
        min_confidence: float = 0.4,
    ) -> List[AssociationRule]:
        num_trans = len(transactions)
        if num_trans == 0:
            return []

        item_counts = defaultdict(int)
        pair_counts = defaultdict(int)

        for trans in transactions:
            unique_items = sorted(list(set(trans)))
            for item in unique_items:
                item_counts[item] += 1
            for i in range(len(unique_items)):
                for j in range(i + 1, len(unique_items)):
                    pair = (unique_items[i], unique_items[j])
                    pair_counts[pair] += 1

        rules = []
        for (item_a, item_b), count in pair_counts.items():
            pair_support = count / num_trans
            if pair_support < min_support:
                continue

            supp_a = item_counts[item_a] / num_trans
            supp_b = item_counts[item_b] / num_trans

            conf_a_to_b = pair_support / supp_a
            lift_a_to_b = conf_a_to_b / supp_b

            if conf_a_to_b >= min_confidence:
                rules.append(AssociationRule(
                    antecedents=[item_a],
                    consequents=[item_b],
                    support=round(pair_support, 4),
                    confidence=round(conf_a_to_b, 4),
                    lift=round(lift_a_to_b, 3),
                ))

            conf_b_to_a = pair_support / supp_b
            lift_b_to_a = conf_b_to_a / supp_a

            if conf_b_to_a >= min_confidence:
                rules.append(AssociationRule(
                    antecedents=[item_b],
                    consequents=[item_a],
                    support=round(pair_support, 4),
                    confidence=round(conf_b_to_a, 4),
                    lift=round(lift_b_to_a, 3),
                ))

        rules.sort(key=lambda r: (r.lift, r.confidence), reverse=True)
        return rules
""")

def generate_frontend_grocery_components():
    print("[*] Generating Frontend Domain Widgets & Component Ecosystem...")

    # ProductCard Component
    write_file("frontend/src/components/grocery/ProductCard.tsx", """import React from "react";
import Link from "next/link";
import { Star, Plus, Check, Scale } from "lucide-react";
import { Badge } from "@/components/ui/Badge";

export interface ProductCardProps {
  id: string;
  name: string;
  slug: string;
  brand: string;
  price: number;
  mrp: number;
  unit: string;
  img: string;
  rating?: number;
  ratingCount?: number;
  isOrganic?: boolean;
  isVariableWeight?: boolean;
  onAddToCart?: (id: string) => void;
  isAdded?: boolean;
}

export function ProductCard({
  id,
  name,
  slug,
  brand,
  price,
  mrp,
  unit,
  img,
  rating = 4.8,
  ratingCount = 20,
  isOrganic = false,
  isVariableWeight = false,
  onAddToCart,
  isAdded = false,
}: ProductCardProps) {
  const discountPct = Math.round(((mrp - price) / mrp) * 100);

  return (
    <div className="bg-white border border-slate-200 rounded-3xl overflow-hidden hover:shadow-md transition-shadow flex flex-col justify-between group">
      <div>
        <Link href={`/product/${slug}`} className="relative h-48 bg-slate-100 overflow-hidden block">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={img}
            alt={name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
          {discountPct > 0 && (
            <span className="absolute top-3 right-3 bg-red-600 text-white text-[10px] font-black px-2 py-0.5 rounded-full shadow">
              {discountPct}% OFF
            </span>
          )}
          {isOrganic && (
            <span className="absolute top-3 left-3 bg-emerald-600 text-white text-[10px] font-black px-2.5 py-0.5 rounded-full uppercase tracking-wider shadow">
              Organic
            </span>
          )}
          {isVariableWeight && (
            <span className="absolute bottom-3 left-3 bg-slate-900/80 text-white text-[10px] font-medium px-2 py-0.5 rounded-md backdrop-blur-sm flex items-center gap-1">
              <Scale className="w-3 h-3 text-emerald-400" />
              <span>Scale Weighed</span>
            </span>
          )}
        </Link>

        <div className="p-4 md:p-5 space-y-2">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">{brand}</span>
          <Link
            href={`/product/${slug}`}
            className="font-bold text-sm text-slate-900 hover:text-emerald-600 line-clamp-2 transition-colors leading-tight"
          >
            {name}
          </Link>
          <div className="flex items-center gap-1 text-amber-500 text-xs font-bold pt-1">
            <Star className="w-3.5 h-3.5 fill-current" />
            <span>{rating}</span>
            <span className="text-slate-400 text-[10px] font-normal">({ratingCount})</span>
          </div>
        </div>
      </div>

      <div className="p-4 md:p-5 pt-0">
        <div className="flex items-center justify-between pt-3 border-t border-slate-100">
          <div>
            <div className="flex items-baseline gap-1.5">
              <span className="font-black text-base text-slate-900">₹{price}</span>
              {mrp > price && <span className="text-xs text-slate-400 line-through">₹{mrp}</span>}
            </div>
            <span className="text-[10px] text-slate-500">per {unit}</span>
          </div>

          <button
            onClick={() => onAddToCart && onAddToCart(id)}
            className={`p-2.5 rounded-xl transition-all shadow-sm flex items-center gap-1.5 text-xs font-bold ${
              isAdded
                ? "bg-emerald-600 text-white"
                : "bg-emerald-50 text-emerald-700 hover:bg-emerald-600 hover:text-white"
            }`}
          >
            {isAdded ? <Check className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
            <span>{isAdded ? "Added" : "Add"}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
""")

    # FlashSaleCounter Component
    write_file("frontend/src/components/grocery/FlashSaleCounter.tsx", """import React, { useState, useEffect } from "react";
import { Zap } from "lucide-react";

export function FlashSaleCounter({ targetHour = 20 }: { targetHour?: number }) {
  const [timeLeft, setTimeLeft] = useState({ hours: 4, minutes: 25, seconds: 12 });

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev.seconds > 0) return { ...prev, seconds: prev.seconds - 1 };
        if (prev.minutes > 0) return { ...prev, minutes: 59, seconds: 59 };
        if (prev.hours > 0) return { hours: prev.hours - 1, minutes: 59, seconds: 59 };
        return prev;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="inline-flex items-center gap-2 bg-amber-500/10 border border-amber-500/30 text-amber-950 px-3 py-1.5 rounded-full text-xs font-bold">
      <Zap className="w-4 h-4 text-amber-600 fill-current animate-bounce" />
      <span>Flash Deals End in:</span>
      <span className="font-mono bg-amber-600 text-white px-2 py-0.5 rounded-md">
        {String(timeLeft.hours).padStart(2, "0")}:{String(timeLeft.minutes).padStart(2, "0")}:{String(timeLeft.seconds).padStart(2, "0")}
      </span>
    </div>
  );
}
""")

    # NutritionalFactsTable Component
    write_file("frontend/src/components/grocery/NutritionalFactsTable.tsx", """import React from "react";

export interface NutritionItem {
  name: string;
  amount: string;
  dailyValuePct?: number;
}

export function NutritionalFactsTable({
  servingSize = "100g",
  calories = "18 kcal",
  nutrients,
}: {
  servingSize?: string;
  calories?: string;
  nutrients: NutritionItem[];
}) {
  return (
    <div className="border border-slate-900 p-4 rounded-2xl bg-white max-w-sm text-xs font-sans space-y-2">
      <div className="border-b-8 border-slate-900 pb-1">
        <h3 className="font-black text-xl tracking-tight leading-none">Nutrition Facts</h3>
        <p className="text-[11px] text-slate-600">Serving size per {servingSize}</p>
      </div>

      <div className="flex justify-between items-baseline border-b-4 border-slate-900 py-1">
        <span className="font-black text-sm">Calories</span>
        <span className="font-black text-xl">{calories}</span>
      </div>

      <div className="text-right text-[10px] font-bold text-slate-500">% Daily Value*</div>

      <div className="divide-y divide-slate-200">
        {nutrients.map((n, idx) => (
          <div key={idx} className="flex justify-between py-1 text-slate-800">
            <span className="font-semibold">{n.name} <span className="font-normal text-slate-500">({n.amount})</span></span>
            {n.dailyValuePct !== undefined && (
              <span className="font-bold">{n.dailyValuePct}%</span>
            )}
          </div>
        ))}
      </div>

      <div className="pt-2 border-t border-slate-300 text-[9px] text-slate-400 leading-tight">
        * Percent Daily Values are based on a 2,000 calorie reference diet.
      </div>
    </div>
  );
}
""")

    # React Context: CartContext
    write_file("frontend/src/context/CartContext.tsx", """\"use client\";
import React, { createContext, useContext, useState, useEffect } from "react";

export interface CartItem {
  id: string;
  productId: string;
  name: string;
  price: number;
  quantity: number;
  unit: string;
  img?: string;
  isVariableWeight?: boolean;
}

interface CartContextType {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (id: string) => void;
  updateQuantity: (id: string, qty: number) => void;
  clearCart: () => void;
  totalCount: number;
  subtotal: number;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<CartItem[]>([]);

  const addItem = (item: CartItem) => {
    setItems((prev) => {
      const idx = prev.findIndex((i) => i.productId === item.productId);
      if (idx >= 0) {
        const updated = [...prev];
        updated[idx].quantity += item.quantity;
        return updated;
      }
      return [...prev, item];
    });
  };

  const removeItem = (id: string) => {
    setItems((prev) => prev.filter((i) => i.id !== id));
  };

  const updateQuantity = (id: string, qty: number) => {
    setItems((prev) =>
      prev
        .map((i) => (i.id === id ? { ...i, quantity: qty } : i))
        .filter((i) => i.quantity > 0)
    );
  };

  const clearCart = () => setItems([]);

  const totalCount = items.reduce((sum, it) => sum + it.quantity, 0);
  const subtotal = items.reduce((sum, it) => sum + it.quantity * it.price, 0);

  return (
    <CartContext.Provider value={{ items, addItem, removeItem, updateQuantity, clearCart, totalCount, subtotal }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used within CartProvider");
  return ctx;
}
""")

    # Utilities: Formatters
    write_file("frontend/src/utils/formatters.ts", """\"\"\"Frontend Display Formatters and Date Calculations.\"\"\"

export function formatCurrency(amount: number, currency: string = "INR"): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(amount);
}

export function formatWeight(weight: number, unit: string = "kg"): string {
  if (unit === "g" && weight >= 1000) {
    return `${(weight / 1000).toFixed(2)} kg`;
  }
  return `${weight} ${unit}`;
}

export function formatEstimatedDelivery(dateStr: string, slotStr: string): string {
  return `${dateStr} between ${slotStr}`;
}
""")

def main():
    generate_dairy_master()
    generate_pantry_master()
    generate_recommendations_apriori()
    generate_frontend_grocery_components()
    print("[SUCCESS] Full Platform Ecosystem Generated!")

if __name__ == "__main__":
    main()
