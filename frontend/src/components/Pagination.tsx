import { ChevronLeft, ChevronRight } from "lucide-react";

import { Button } from "@/components/ui/button";

interface PaginationProps {
  total: number;
  limit: number;
  offset: number;
  onChange: (offset: number) => void;
}

export function Pagination({ total, limit, offset, onChange }: PaginationProps) {
  const from = total === 0 ? 0 : offset + 1;
  const to = Math.min(offset + limit, total);
  const canPrev = offset > 0;
  const canNext = offset + limit < total;

  return (
    <div className="flex items-center justify-between py-3">
      <p className="text-sm text-muted-foreground" data-testid="pagination-info">
        Showing <span className="font-medium text-foreground">{from.toLocaleString()}</span>
        {"–"}
        <span className="font-medium text-foreground">{to.toLocaleString()}</span> of{" "}
        <span className="font-medium text-foreground">{total.toLocaleString()}</span>
      </p>
      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          disabled={!canPrev}
          onClick={() => onChange(Math.max(0, offset - limit))}
          data-testid="page-prev"
        >
          <ChevronLeft className="h-4 w-4" /> Previous
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={!canNext}
          onClick={() => onChange(offset + limit)}
          data-testid="page-next"
        >
          Next <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
