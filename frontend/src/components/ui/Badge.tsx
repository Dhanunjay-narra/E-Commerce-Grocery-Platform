import * as React from "react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "emerald" | "amber" | "blue" | "purple" | "red" | "slate";
  size?: "sm" | "md";
}

export function Badge({ className, variant = "emerald", size = "sm", children, ...props }: BadgeProps) {
  const base = "inline-flex items-center font-bold uppercase tracking-wider rounded-full border shadow-2xs";
  
  const variants = {
    emerald: "bg-emerald-50 text-emerald-800 border-emerald-200",
    amber: "bg-amber-50 text-amber-800 border-amber-200",
    blue: "bg-blue-50 text-blue-800 border-blue-200",
    purple: "bg-purple-50 text-purple-800 border-purple-200",
    red: "bg-red-50 text-red-800 border-red-200",
    slate: "bg-slate-100 text-slate-700 border-slate-200",
  };
  
  const sizes = {
    sm: "px-2 py-0.5 text-[10px]",
    md: "px-2.5 py-1 text-xs",
  };
  
  return (
    <span className={twMerge(clsx(base, variants[variant], sizes[size], className))} {...props}>
      {children}
    </span>
  );
}
