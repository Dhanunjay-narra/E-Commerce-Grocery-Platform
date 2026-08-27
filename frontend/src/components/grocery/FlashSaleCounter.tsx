import React, { useState, useEffect } from "react";
import { Zap } from "lucide-react";

export function FlashSaleCounter({ targetHour = 20 }: { targetHour?: number }) {
  const [timeLeft, setTimeLeft] = useState({ hours: 4, minutes: 25, seconds: 12 });

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev.seconds > 0) return { ...prev, seconds: prev.seconds - 1 };
        if (prev.minutes > 0) return { ...prev, minutes: 59, seconds: 59 };
        if (prev.hours > 0) return { hours: prev.hours - 1, minutes: 59, seconds: 59 };
        return prev;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="inline-flex items-center gap-2 bg-amber-500/10 border border-amber-500/30 text-amber-950 px-3 py-1.5 rounded-full text-xs font-bold">
      <Zap className="w-4 h-4 text-amber-600 fill-current animate-bounce" />
      <span>Flash Deals End in:</span>
      <span className="font-mono bg-amber-600 text-white px-2 py-0.5 rounded-md">
        {String(timeLeft.hours).padStart(2, "0")}:{String(timeLeft.minutes).padStart(2, "0")}:{String(timeLeft.seconds).padStart(2, "0")}
      </span>
    </div>
  );
}
