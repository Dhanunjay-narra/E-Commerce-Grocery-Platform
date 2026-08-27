import * as React from "react";
import { CheckCircle2, AlertCircle, Info, X } from "lucide-react";

export type ToastType = "success" | "error" | "info";

export interface ToastMessage {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

export function ToastItem({ toast, onDismiss }: { toast: ToastMessage; onDismiss: (id: string) => void }) {
  React.useEffect(() => {
    const timer = setTimeout(() => onDismiss(toast.id), toast.duration || 4000);
    return () => clearTimeout(timer);
  }, [toast, onDismiss]);

  const icons = {
    success: <CheckCircle2 className="w-5 h-5 text-emerald-600" />,
    error: <AlertCircle className="w-5 h-5 text-red-600" />,
    info: <Info className="w-5 h-5 text-blue-600" />,
  };

  const borders = {
    success: "border-emerald-200 bg-emerald-50/90 text-emerald-950",
    error: "border-red-200 bg-red-50/90 text-red-950",
    info: "border-blue-200 bg-blue-50/90 text-blue-950",
  };

  return (
    <div className={`flex items-start gap-3 p-4 rounded-2xl border shadow-lg backdrop-blur-md transition-all ${borders[toast.type]}`}>
      <div className="shrink-0 pt-0.5">{icons[toast.type]}</div>
      <div className="flex-1">
        <h4 className="font-bold text-xs">{toast.title}</h4>
        {toast.message && <p className="text-[11px] opacity-85 mt-0.5">{toast.message}</p>}
      </div>
      <button onClick={() => onDismiss(toast.id)} className="opacity-60 hover:opacity-100 p-0.5">
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}
