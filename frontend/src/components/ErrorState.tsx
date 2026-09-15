import { AlertTriangle } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import type { ApiError } from "@/lib/api";

interface ErrorStateProps {
  error: ApiError;
  title?: string;
}

export function ErrorState({ error, title }: ErrorStateProps) {
  return (
    <Card className="border-rose-200 bg-rose-50" data-testid="error-banner">
      <CardContent className="p-6">
        <div className="flex items-start gap-3">
          <AlertTriangle className="mt-0.5 h-5 w-5 text-rose-600" />
          <div>
            <h2 className="font-semibold text-rose-800">
              {title ?? error.code ?? "Something went wrong"}
            </h2>
            <p className="mt-1 text-sm text-rose-700">{error.message}</p>
            {error.requestId && (
              <p className="mt-2 font-mono text-xs text-rose-500">
                request_id: {error.requestId}
              </p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
