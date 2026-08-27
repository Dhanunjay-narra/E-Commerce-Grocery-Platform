import * as React from "react";
import { Star } from "lucide-react";

export function RatingStars({ rating, count, showCount = true }: { rating: number; count?: number; showCount?: boolean }) {
  return (
    <div className="flex items-center gap-1.5">
      <div className="flex items-center text-amber-400">
        {[1, 2, 3, 4, 5].map((s) => (
          <Star
            key={s}
            className={`w-3.5 h-3.5 ${
              rating >= s
                ? "fill-current text-amber-400"
                : rating >= s - 0.5
                ? "fill-current text-amber-300 opacity-70"
                : "text-slate-200 fill-slate-100"
            }`}
          />
        ))}
      </div>
      <span className="font-extrabold text-xs text-slate-800">{rating.toFixed(1)}</span>
      {showCount && count !== undefined && (
        <span className="text-[10px] text-slate-400 font-medium">({count})</span>
      )}
    </div>
  );
}
