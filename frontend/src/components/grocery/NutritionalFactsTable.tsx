import React from "react";

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
