import * as React from "react";
import { Check } from "lucide-react";

export interface StepItem {
  label: string;
  description?: string;
}

export function Stepper({ steps, currentStep }: { steps: StepItem[]; currentStep: number }) {
  return (
    <div className="w-full py-4">
      <div className="flex items-center justify-between relative">
        <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-slate-200 -translate-y-1/2 z-0" />
        <div
          className="absolute top-1/2 left-0 h-0.5 bg-emerald-600 -translate-y-1/2 z-0 transition-all duration-300"
          style={{ width: `${(currentStep / (steps.length - 1)) * 100}%` }}
        />

        {steps.map((step, idx) => {
          const isDone = idx < currentStep;
          const isCurrent = idx === currentStep;

          return (
            <div key={idx} className="relative z-10 flex flex-col items-center gap-1.5">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs shadow-sm transition-all ${
                  isDone
                    ? "bg-emerald-600 text-white"
                    : isCurrent
                    ? "bg-white text-emerald-600 border-2 border-emerald-600 ring-4 ring-emerald-50"
                    : "bg-white text-slate-400 border border-slate-200"
                }`}
              >
                {isDone ? <Check className="w-4 h-4" /> : idx + 1}
              </div>
              <span className={`text-[11px] font-bold ${isCurrent ? "text-slate-900" : "text-slate-400"}`}>
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
