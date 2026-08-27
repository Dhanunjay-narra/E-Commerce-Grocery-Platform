"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { MapPin, Clock, CreditCard, CheckCircle2, ShieldCheck } from "lucide-react";

export default function CheckoutPage() {
  const router = useRouter();
  const [selectedSlot, setSelectedSlot] = useState("slot-1");
  const [paymentMethod, setPaymentMethod] = useState("CASH_ON_DELIVERY");
  const [subPref, setSubPref] = useState("ASK_FIRST");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const SLOTS = [
    { id: "slot-1", time: "Today, 04:00 PM - 06:00 PM", type: "STANDARD_2HOUR", cap: "8 slots remaining" },
    { id: "slot-2", time: "Today, 06:00 PM - 08:00 PM", type: "STANDARD_2HOUR", cap: "14 slots remaining" },
    { id: "slot-3", time: "Tomorrow, 07:00 AM - 09:00 AM", type: "STANDARD_2HOUR", cap: "20 slots remaining" },
    { id: "slot-4", time: "Tomorrow, 09:00 AM - 11:00 AM", type: "STANDARD_2HOUR", cap: "18 slots remaining" },
  ];

  const handlePlaceOrder = () => {
    setIsSubmitting(true);
    setTimeout(() => {
      // Navigate to order confirmation / tracking page
      router.push("/orders/ORD-20260827-HYD01");
    }, 1200);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Delivery & Checkout</h1>
        <p className="text-xs text-slate-500 mt-1">Select your scheduled delivery slot and preferred payment method</p>
      </div>

      <div className="space-y-6">
        {/* Delivery Address Card */}
        <section className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center gap-2 font-bold text-sm text-slate-900">
              <MapPin className="w-4 h-4 text-emerald-600" />
              <span>Delivery Address</span>
            </div>
            <span className="text-xs text-emerald-600 font-bold hover:underline cursor-pointer">Change Address</span>
          </div>

          <div className="text-xs text-slate-700 space-y-1">
            <span className="font-bold text-slate-900 block text-sm">Priya Sharma (+91 98765 43210)</span>
            <p>Flat 402, Green Valley Apartments, Hitec City</p>
            <p>Hyderabad, Telangana - 500081</p>
          </div>
        </section>

        {/* Capacity-Aware Delivery Slot Engine */}
        <section className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center gap-2 font-bold text-sm text-slate-900 pb-3 border-b border-slate-100">
            <Clock className="w-4 h-4 text-emerald-600" />
            <span>Select Delivery Slot Window</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {SLOTS.map((slot) => (
              <button
                key={slot.id}
                onClick={() => setSelectedSlot(slot.id)}
                className={`p-4 rounded-2xl border text-left transition-all ${
                  selectedSlot === slot.id
                    ? "bg-emerald-50 border-emerald-600 ring-2 ring-emerald-500"
                    : "bg-slate-50 border-slate-200 hover:border-emerald-300"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-slate-900">{slot.time}</span>
                  {selectedSlot === slot.id && <CheckCircle2 className="w-4 h-4 text-emerald-600" />}
                </div>
                <span className="text-[10px] text-emerald-700 font-semibold block mt-1">{slot.cap}</span>
              </button>
            ))}
          </div>
        </section>

        {/* Out-of-Stock Substitution Preference */}
        <section className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3">
          <h3 className="font-bold text-sm text-slate-900">Substitution Preference (if item unavailable)</h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {[
              { id: "ASK_FIRST", label: "Call / SMS to Confirm", desc: "Picker contacts before swapping" },
              { id: "ALWAYS_SUBSTITUTE", label: "Smart Auto-Substitute", desc: "Closest brand & price match" },
              { id: "NEVER_SUBSTITUTE", label: "Do Not Substitute", desc: "Refund missing items instantly" },
            ].map((opt) => (
              <button
                key={opt.id}
                onClick={() => setSubPref(opt.id)}
                className={`p-3.5 rounded-2xl border text-left text-xs ${
                  subPref === opt.id
                    ? "bg-emerald-50 border-emerald-600 font-bold"
                    : "bg-slate-50 border-slate-200 hover:border-slate-300"
                }`}
              >
                <span className="text-slate-900 block">{opt.label}</span>
                <span className="text-[10px] text-slate-500 font-normal">{opt.desc}</span>
              </button>
            ))}
          </div>
        </section>

        {/* Payment Methods */}
        <section className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center gap-2 font-bold text-sm text-slate-900 pb-3 border-b border-slate-100">
            <CreditCard className="w-4 h-4 text-emerald-600" />
            <span>Payment Options</span>
          </div>

          <div className="space-y-2">
            {[
              { id: "UPI", title: "Instant UPI (Google Pay, PhonePe, Paytm)", desc: "Zero transaction charges" },
              { id: "CARD", title: "Credit / Debit Card", desc: "Visa, Mastercard, RuPay accepted" },
              { id: "CASH_ON_DELIVERY", title: "Cash / UPI on Delivery", desc: "Pay at your doorstep upon arrival" },
            ].map((m) => (
              <label
                key={m.id}
                className={`flex items-center gap-3 p-4 rounded-2xl border cursor-pointer transition-all ${
                  paymentMethod === m.id
                    ? "bg-emerald-50 border-emerald-600"
                    : "bg-slate-50 border-slate-200 hover:bg-slate-100/60"
                }`}
              >
                <input
                  type="radio"
                  name="payment"
                  checked={paymentMethod === m.id}
                  onChange={() => setPaymentMethod(m.id)}
                  className="w-4 h-4 text-emerald-600 focus:ring-emerald-500"
                />
                <div>
                  <span className="font-bold text-xs text-slate-900 block">{m.title}</span>
                  <span className="text-[10px] text-slate-500">{m.desc}</span>
                </div>
              </label>
            ))}
          </div>
        </section>

        {/* Place Order Button */}
        <button
          onClick={handlePlaceOrder}
          disabled={isSubmitting}
          className="w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white rounded-2xl font-bold text-sm shadow-lg hover:shadow-xl transition-all flex items-center justify-center gap-2"
        >
          <ShieldCheck className="w-5 h-5" />
          <span>{isSubmitting ? "Locking Stock & Reserving Slot..." : "Place Grocery Order — ₹648.00"}</span>
        </button>
      </div>
    </div>
  );
}
