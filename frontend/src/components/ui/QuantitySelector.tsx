import * as React from "react";
import { Plus, Minus } from "lucide-react";

export interface QuantitySelectorProps {
  value: number;
  min?: number;
  max?: number;
  step?: number;
  unit?: string;
  onChange: (val: number) => void;
}

export function QuantitySelector({ value, min = 1, max = 50, step = 1, unit, onChange }: QuantitySelectorProps) {
  const handleDecrement = () => {
    if (value - step >= min) onChange(Math.round((value - step) * 100) / 100);
  };

  const handleIncrement = () => {
    if (value + step <= max) onChange(Math.round((value + step) * 100) / 100);
  };

  return (
    <div className="inline-flex items-center bg-slate-50 border border-slate-200 rounded-xl p-1 shadow-inner">
      <button
        onClick={handleDecrement}
        disabled={value <= min}
        className="w-7 h-7 flex items-center justify-center rounded-lg bg-white text-slate-700 hover:bg-emerald-50 hover:text-emerald-700 disabled:opacity-40 shadow-xs transition-colors"
      >
        <Minus className="w-3.5 h-3.5" />
      </button>
      <div className="px-3 text-center">
        <span className="font-black text-xs text-slate-900 block">{value}</span>
        {unit && <span className="text-[9px] text-slate-400 font-semibold uppercase">{unit}</span>}
      </div>
      <button
        onClick={handleIncrement}
        disabled={value >= max}
        className="w-7 h-7 flex items-center justify-center rounded-lg bg-white text-slate-700 hover:bg-emerald-50 hover:text-emerald-700 disabled:opacity-40 shadow-xs transition-colors"
      >
        <Plus className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}
