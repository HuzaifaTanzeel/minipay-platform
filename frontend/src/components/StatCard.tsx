import type { LucideIcon } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface StatCardProps {
  label: string;
  value: string;
  hint?: string;
  icon: LucideIcon;
  accent?: "default" | "success" | "danger" | "warning";
  testId?: string;
}

const ACCENT: Record<NonNullable<StatCardProps["accent"]>, string> = {
  default: "bg-slate-100 text-slate-600",
  success: "bg-emerald-100 text-emerald-600",
  danger: "bg-rose-100 text-rose-600",
  warning: "bg-amber-100 text-amber-600",
};

const VALUE_COLOR: Record<NonNullable<StatCardProps["accent"]>, string> = {
  default: "text-foreground",
  success: "text-emerald-600",
  danger: "text-rose-600",
  warning: "text-amber-600",
};

export function StatCard({
  label,
  value,
  hint,
  icon: Icon,
  accent = "default",
  testId,
}: StatCardProps) {
  return (
    <Card data-testid={testId}>
      <CardContent className="p-5">
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-muted-foreground">{label}</p>
          <span
            className={cn(
              "inline-flex h-9 w-9 items-center justify-center rounded-lg",
              ACCENT[accent]
            )}
          >
            <Icon className="h-5 w-5" />
          </span>
        </div>
        <p className={cn("mt-2 text-3xl font-bold tracking-tight", VALUE_COLOR[accent])}>
          {value}
        </p>
        {hint && <p className="mt-1 text-xs text-muted-foreground">{hint}</p>}
      </CardContent>
    </Card>
  );
}
