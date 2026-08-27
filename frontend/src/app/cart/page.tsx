"use client";

import { useState } from "react";
import Link from "next/link";
import { Trash2, Tag, ArrowRight, Store, ShieldCheck, Scale } from "lucide-react";

export default function CartPage() {
  const [couponCode, setCouponCode] = useState("");
  const [appliedCoupon, setAppliedCoupon] = useState<string | null>("FRESHSTART");
  const [discountAmount, setDiscountAmount] = useState(100.0);

  const [vendorGroups, setVendorGroups] = useState([
    {
      vendor_name: "Green Leaf Organics Pvt Ltd",
      items: [
        {
          id: "item-1",
          name: "Organic Farm-Fresh Hybrid Tomatoes",
          unit: "kg",
          price: 42.0,
          qty: 1.5,
          total: 63.0,
          is_variable: true,
          img: "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=200",
        },
        {
          id: "item-2",
          name: "Royal Gala Crisp Red Apples 4-Pack",
          unit: "pack",
          price: 165.0,
          qty: 1.0,
          total: 165.0,
          is_variable: false,
          img: "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=200",
        },
      ],
      subtotal: 228.0,
    },
    {
      vendor_name: "FreshCart Central Direct",
      items: [
        {
          id: "item-3",
          name: "Daawat Rozana Gold Basmati Rice 5kg",
          unit: "bag",
          price: 520.0,
          qty: 1.0,
          total: 520.0,
          is_variable: false,
          img: "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=200",
        },
      ],
      subtotal: 520.0,
    },
  ]);

  const rawSubtotal = vendorGroups.reduce((acc, g) => acc + g.subtotal, 0);
  const taxEstimate = Math.round(rawSubtotal * 0.05 * 100) / 100;
  const deliveryFee = rawSubtotal > 499 ? 0.0 : 35.0;
  const grandTotal = Math.max(0, rawSubtotal - discountAmount + taxEstimate + deliveryFee);

  const handleApplyCoupon = () => {
    if (couponCode.toUpperCase() === "ORGANIC20") {
      setAppliedCoupon("ORGANIC20");
      setDiscountAmount(Math.min(150, rawSubtotal * 0.2));
    } else if (couponCode.toUpperCase() === "FRESHSTART") {
      setAppliedCoupon("FRESHSTART");
      setDiscountAmount(100.0);
    } else {
      alert("Invalid promo code. Try FRESHSTART or ORGANIC20");
    }
  };

  const handleRemoveCoupon = () => {
    setAppliedCoupon(null);
    setDiscountAmount(0.0);
    setCouponCode("");
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Shopping Cart</h1>
        <p className="text-xs text-slate-500 mt-1">Multi-vendor fulfillment grouped into optimized packing queues</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Partitioned Items by Vendor */}
        <div className="lg:col-span-2 space-y-6">
          {vendorGroups.map((group, idx) => (
            <div key={idx} className="bg-white rounded-3xl border border-slate-200 overflow-hidden shadow-sm">
              {/* Vendor Store Header */}
              <div className="bg-slate-50 px-6 py-3.5 border-b border-slate-200 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Store className="w-4 h-4 text-emerald-600" />
                  <span className="font-bold text-xs text-slate-900">{group.vendor_name}</span>
                </div>
                <span className="text-xs text-slate-500 font-semibold">Store Subtotal: ₹{group.subtotal}</span>
              </div>

              {/* Line items */}
              <div className="divide-y divide-slate-100 p-6 space-y-4">
                {group.items.map((item) => (
                  <div key={item.id} className="pt-4 first:pt-0 flex items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={item.img} alt={item.name} className="w-16 h-16 rounded-xl object-cover" />
                      <div>
                        <h3 className="font-bold text-xs text-slate-900">{item.name}</h3>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs font-bold text-slate-900">₹{item.price}</span>
                          <span className="text-[10px] text-slate-400">/ {item.unit}</span>
                          {item.is_variable && (
                            <span className="inline-flex items-center gap-1 text-[10px] text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md font-semibold">
                              <Scale className="w-3 h-3" />
                              <span>Est. Weight: {item.qty} {item.unit}</span>
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-6">
                      <span className="font-black text-sm text-slate-900">₹{item.total}</span>
                      <button className="text-slate-400 hover:text-red-600 transition-colors p-1">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Checkout Summary Sidebar */}
        <div className="space-y-6">
          {/* Coupon Widget */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200 space-y-4 shadow-sm">
            <div className="flex items-center gap-2 font-bold text-xs text-slate-900">
              <Tag className="w-4 h-4 text-emerald-600" />
              <span>Promotional Discount Coupon</span>
            </div>

            {appliedCoupon ? (
              <div className="flex items-center justify-between p-3 bg-emerald-50 rounded-xl border border-emerald-200">
                <div>
                  <span className="font-bold text-xs text-emerald-800 uppercase block">{appliedCoupon}</span>
                  <span className="text-[11px] text-emerald-600">Saved ₹{discountAmount} on this order</span>
                </div>
                <button onClick={handleRemoveCoupon} className="text-xs text-red-600 font-bold hover:underline">
                  Remove
                </button>
              </div>
            ) : (
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Enter code (FRESHSTART)"
                  value={couponCode}
                  onChange={(e) => setCouponCode(e.target.value)}
                  className="flex-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs uppercase focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
                <button
                  onClick={handleApplyCoupon}
                  className="px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-bold hover:bg-slate-800 transition-colors"
                >
                  Apply
                </button>
              </div>
            )}
          </div>

          {/* Price Breakdown */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200 space-y-4 shadow-sm">
            <h3 className="font-bold text-sm text-slate-900 pb-3 border-b border-slate-100">Order Bill Summary</h3>

            <div className="space-y-2.5 text-xs text-slate-600">
              <div className="flex justify-between">
                <span>Items Subtotal</span>
                <span className="font-bold text-slate-900">₹{rawSubtotal}</span>
              </div>
              {discountAmount > 0 && (
                <div className="flex justify-between text-emerald-600 font-semibold">
                  <span>Coupon Discount</span>
                  <span>- ₹{discountAmount}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span>Estimated GST / Tax</span>
                <span className="font-semibold text-slate-900">₹{taxEstimate}</span>
              </div>
              <div className="flex justify-between">
                <span>Delivery Slot Fee</span>
                <span className="font-semibold text-slate-900">
                  {deliveryFee === 0.0 ? <span className="text-emerald-600 font-bold uppercase">Free</span> : `₹${deliveryFee}`}
                </span>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-200 flex justify-between items-baseline">
              <div>
                <span className="font-black text-sm text-slate-900 block">Grand Total</span>
                <span className="text-[10px] text-slate-400">Inclusive of all taxes</span>
              </div>
              <span className="text-2xl font-black text-slate-900">₹{grandTotal}</span>
            </div>

            <Link
              href="/checkout"
              className="w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white rounded-2xl font-bold text-xs shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2"
            >
              <span>Proceed to Delivery & Payment</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <div className="flex items-center justify-center gap-1.5 text-[10px] text-slate-400 pt-2">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              <span>Safe & Secure 256-Bit Encrypted Checkout</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
