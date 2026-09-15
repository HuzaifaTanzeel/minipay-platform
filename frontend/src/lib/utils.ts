import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** Format a numeric string/number as money with thousands separators. */
export function formatMoney(value: string | number | null | undefined): string {
  if (value === null || value === undefined) return "-";
  const n = typeof value === "string" ? Number(value) : value;
  if (Number.isNaN(n)) return String(value);
  return n.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

/** Format an ISO datetime string for display. */
export function formatDateTime(value: string | null | undefined): string {
  if (!value) return "-";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}
