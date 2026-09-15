import { Badge } from "@/components/ui/badge";
import type { PaymentStatus } from "@/types";

const VARIANT: Record<PaymentStatus, "success" | "danger" | "warning"> = {
  SUCCESS: "success",
  FAILED: "danger",
  PROCESSING: "warning",
};

export function StatusBadge({ status }: { status: PaymentStatus }) {
  return (
    <Badge variant={VARIANT[status] ?? "secondary"} data-testid="status-badge">
      {status}
    </Badge>
  );
}
