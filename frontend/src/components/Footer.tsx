import Link from "next/link";
import { Leaf, Clock, Shield, RefreshCw } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-300 mt-20 border-t border-slate-800">
      {/* Value props banner */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 border-b border-slate-800">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-emerald-950 text-emerald-400 rounded-xl">
              <Leaf className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-white font-semibold text-sm">100% Organic & Fresh</h4>
              <p className="text-xs text-slate-400">Directly sourced daily from certified farms</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="p-3 bg-emerald-950 text-emerald-400 rounded-xl">
              <Clock className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-white font-semibold text-sm">30-Min Express Slots</h4>
              <p className="text-xs text-slate-400">Real-time GPS slot allocation</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="p-3 bg-emerald-950 text-emerald-400 rounded-xl">
              <Shield className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-white font-semibold text-sm">FEFO Guaranteed</h4>
              <p className="text-xs text-slate-400">Dual expiry lot tracking quality guarantee</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="p-3 bg-emerald-950 text-emerald-400 rounded-xl">
              <RefreshCw className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-white font-semibold text-sm">Smart Substitutions</h4>
              <p className="text-xs text-slate-400">AI alternatives for zero unfulfilled carts</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Links */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 grid grid-cols-2 md:grid-cols-5 gap-8 text-xs">
        <div className="col-span-2">
          <span className="font-extrabold text-xl tracking-tight text-white block mb-2">
            Fresh<span className="text-emerald-500">Cart</span>
          </span>
          <p className="text-slate-400 leading-relaxed max-w-sm mb-4">
            Next-generation grocery marketplace empowering local farm vendors, dark-store fulfillment, variable produce scale weighing, and scheduled slot logistics.
          </p>
          <p className="text-slate-500">© 2026 FreshCart Technologies Pvt Ltd. All rights reserved.</p>
        </div>

        <div>
          <h5 className="font-bold text-white uppercase tracking-wider mb-3">Shop Categories</h5>
          <ul className="space-y-2">
            <li><Link href="/catalog?cat=produce" className="hover:text-white transition-colors">Fresh Produce</Link></li>
            <li><Link href="/catalog?cat=dairy" className="hover:text-white transition-colors">Dairy & Bakery</Link></li>
            <li><Link href="/catalog?cat=pantry" className="hover:text-white transition-colors">Pantry Staples</Link></li>
            <li><Link href="/catalog?cat=organic" className="hover:text-white transition-colors">Certified Organic</Link></li>
          </ul>
        </div>

        <div>
          <h5 className="font-bold text-white uppercase tracking-wider mb-3">Partner With Us</h5>
          <ul className="space-y-2">
            <li><Link href="/vendor/register" className="hover:text-white transition-colors">Vendor Onboarding</Link></li>
            <li><Link href="/driver/apply" className="hover:text-white transition-colors">Delivery Fleet Partner</Link></li>
            <li><Link href="/darkstore" className="hover:text-white transition-colors">Dark Store Franchise</Link></li>
          </ul>
        </div>

        <div>
          <h5 className="font-bold text-white uppercase tracking-wider mb-3">Legal & Security</h5>
          <ul className="space-y-2">
            <li><Link href="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link></li>
            <li><Link href="/terms" className="hover:text-white transition-colors">Terms of Service</Link></li>
            <li><Link href="/fssai" className="hover:text-white transition-colors">FSSAI Compliance</Link></li>
          </ul>
        </div>
      </div>
    </footer>
  );
}
