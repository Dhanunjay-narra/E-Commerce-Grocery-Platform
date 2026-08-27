import React from "react";
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
