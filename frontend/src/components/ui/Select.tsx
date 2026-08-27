import * as React from "react";
import { ChevronDown } from "lucide-react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export interface SelectOption {
  label: string;
  value: string | number;
}

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: SelectOption[];
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, label, error, options, id, ...props }, ref) => {
    const selectId = id || (label ? label.toLowerCase().replace(/\s+/g, "-") : undefined);

    return (
      <div className="w-full space-y-1.5 text-left">
        {label && (
          <label htmlFor={selectId} className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
            {label}
          </label>
        )}
        <div className="relative rounded-2xl bg-slate-50">
          <select
            id={selectId}
            ref={ref}
            className={twMerge(
              clsx(
                "block w-full appearance-none rounded-2xl border border-slate-200 bg-slate-50 py-2.5 pl-4 pr-10 text-xs text-slate-900 focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all cursor-pointer",
                error && "border-red-500 ring-1 ring-red-500",
                className
              )
            )}
            {...props}
          >
            {options.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <div className="absolute inset-y-0 right-0 pr-3.5 flex items-center pointer-events-none text-slate-400">
            <ChevronDown className="w-4 h-4" />
          </div>
        </div>
        {error && <p className="text-[11px] font-semibold text-red-600">{error}</p>}
      </div>
    );
  }
);
Select.displayName = "Select";
