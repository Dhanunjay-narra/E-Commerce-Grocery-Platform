/** Frontend Display Formatters and Date Calculations. */

export function formatCurrency(amount: number, currency: string = "INR"): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(amount);
}

export function formatWeight(weight: number, unit: string = "kg"): string {
  if (unit === "g" && weight >= 1000) {
    return `${(weight / 1000).toFixed(2)} kg`;
  }
  return `${weight} ${unit}`;
}

export function formatEstimatedDelivery(dateStr: string, slotStr: string): string {
  return `${dateStr} between ${slotStr}`;
}
