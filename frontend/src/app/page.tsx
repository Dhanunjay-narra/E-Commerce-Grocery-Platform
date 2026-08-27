import Link from "next/link";
import { Sparkles, ArrowRight, Clock, Star, Plus } from "lucide-react";

const FEATURED_PRODUCTS = [
  {
    id: "1",
    name: "Organic Farm-Fresh Hybrid Tomatoes",
    slug: "organic-farm-fresh-hybrid-tomatoes",
    brand: "FarmDirect",
    price: 42.0,
    mrp: 48.0,
    unit: "kg",
    is_variable: true,
    is_organic: true,
    rating: 4.8,
    img: "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500",
  },
  {
    id: "2",
    name: "Amul Pasteurised Salted Butter 500g",
    slug: "amul-pasteurised-butter-500g",
    brand: "Amul",
    price: 275.0,
    mrp: 285.0,
    unit: "pack",
    is_variable: false,
    is_organic: false,
    rating: 4.9,
    img: "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=500",
  },
  {
    id: "3",
    name: "Royal Gala Crisp Red Apples 4-Pack",
    slug: "royal-gala-crisp-red-apples-4-pack",
    brand: "Himalayan Orchards",
    price: 165.0,
    mrp: 190.0,
    unit: "pack",
    is_variable: false,
    is_organic: true,
    rating: 4.9,
    img: "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=500",
  },
  {
    id: "4",
    name: "Puvi Cold Pressed Groundnut Oil 1L",
    slug: "puvi-cold-pressed-groundnut-oil-1l",
    brand: "Puvi",
    price: 235.0,
    mrp: 260.0,
    unit: "bottle",
    is_variable: false,
    is_organic: true,
    rating: 4.9,
    img: "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500",
  },
];

const CATEGORIES = [
  { name: "Fresh Produce", icon: "🥦", bg: "bg-emerald-50 text-emerald-900 border-emerald-200", href: "/catalog?cat=produce" },
  { name: "Dairy & Eggs", icon: "🥛", bg: "bg-blue-50 text-blue-900 border-blue-200", href: "/catalog?cat=dairy" },
  { name: "Pantry Staples", icon: "🌾", bg: "bg-amber-50 text-amber-900 border-amber-200", href: "/catalog?cat=pantry" },
  { name: "Cooking Oils", icon: "🌻", bg: "bg-orange-50 text-orange-900 border-orange-200", href: "/catalog?cat=oils" },
  { name: "Organic Specials", icon: "🌱", bg: "bg-green-50 text-green-900 border-green-200", href: "/catalog?is_organic=true" },
  { name: "Snacks & Drinks", icon: "🧃", bg: "bg-purple-50 text-purple-900 border-purple-200", href: "/catalog?cat=snacks" },
];

export default function HomePage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12">
      {/* Hero Banner */}
      <section className="relative rounded-3xl overflow-hidden bg-gradient-to-r from-emerald-800 via-emerald-700 to-teal-900 text-white p-8 md:p-14 shadow-xl">
        <div className="max-w-2xl space-y-4">
          <div className="inline-flex items-center gap-2 bg-emerald-900/60 border border-emerald-400/30 px-3.5 py-1 rounded-full text-xs font-semibold text-emerald-200 tracking-wide">
            <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
            <span>AI-Driven Grocery Marketplace & Fresh Delivery</span>
          </div>
          <h1 className="text-3xl md:text-5xl font-black tracking-tight leading-tight">
            Farm-Fresh Groceries Delivered in <span className="text-emerald-300 underline decoration-wavy">30 Minutes</span>.
          </h1>
          <p className="text-emerald-100 text-sm md:text-base leading-relaxed">
            Experience smart substitutions, variable produce scale precision, FEFO freshness lot guarantees, and multi-vendor fulfillment from one unified cart.
          </p>
          <div className="pt-2 flex flex-wrap items-center gap-4">
            <Link
              href="/catalog"
              className="inline-flex items-center gap-2 bg-white text-emerald-900 hover:bg-emerald-50 px-6 py-3.5 rounded-full font-bold text-sm shadow-lg hover:shadow-xl transition-all"
            >
              <span>Shop All Essentials</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <div className="flex items-center gap-2 text-xs text-emerald-200 font-medium">
              <Clock className="w-4 h-4 text-emerald-300" />
              <span>Next delivery slot: Today, 4:00 PM - 6:00 PM</span>
            </div>
          </div>
        </div>
      </section>

      {/* Category Grid */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">Explore Fresh Departments</h2>
            <p className="text-xs text-slate-500">Curated organic produce, dairy, bakery, and weekly pantry staples</p>
          </div>
          <Link href="/catalog" className="text-xs font-bold text-emerald-600 hover:text-emerald-700">
            View All →
          </Link>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
          {CATEGORIES.map((cat, idx) => (
            <Link
              key={idx}
              href={cat.href}
              className={`p-4 rounded-2xl border ${cat.bg} text-center hover:scale-105 transition-transform flex flex-col items-center justify-center gap-2 shadow-sm`}
            >
              <span className="text-3xl">{cat.icon}</span>
              <span className="font-bold text-xs">{cat.name}</span>
            </Link>
          ))}
        </div>
      </section>

      {/* Flash Deals / Best Sellers */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">Today&apos;s Fresh Deals & Staples</h2>
            <p className="text-xs text-slate-500">Verified FEFO lot tracking with guaranteed shelf-life freshness</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
          {FEATURED_PRODUCTS.map((prod) => (
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

                  <Link
                    href={`/product/${prod.slug}`}
                    className="p-2 bg-emerald-50 hover:bg-emerald-600 text-emerald-700 hover:text-white rounded-xl transition-all shadow-sm flex items-center justify-center"
                  >
                    <Plus className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Smart Pantry Replenishment Banner */}
      <section className="bg-gradient-to-r from-amber-500 to-orange-600 rounded-3xl p-8 text-white flex flex-col md:flex-row items-center justify-between gap-6 shadow-lg">
        <div className="space-y-2">
          <span className="bg-white/20 text-white text-[11px] font-bold px-3 py-1 rounded-full uppercase tracking-wider">
            Smart Grocery Planner
          </span>
          <h3 className="text-2xl font-black">Never Run Out of Milk, Eggs, or Staples</h3>
          <p className="text-amber-100 text-xs md:text-sm max-w-xl">
            Our predictive replenishment engine learns your family consumption cadence and auto-prepares your weekly cart before you run out.
          </p>
        </div>
        <Link
          href="/catalog"
          className="bg-white text-orange-700 font-bold px-6 py-3 rounded-full text-xs shadow-md hover:bg-amber-50 transition-colors whitespace-nowrap"
        >
          Create Weekly Plan →
        </Link>
      </section>
    </div>
  );
}
