import { ArrowLeft } from "lucide-react";
import { Link, useLocation, useParams } from "react-router-dom";

import { CallbackTimeline } from "@/components/CallbackTimeline";
import { ErrorState } from "@/components/ErrorState";
import { StatusBadge } from "@/components/StatusBadge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { usePayment } from "@/hooks/usePayments";
import type { ApiError } from "@/lib/api";
import { formatDateTime, formatMoney } from "@/lib/utils";

export function PaymentDetailPage() {
  const { ref } = useParams<{ ref: string }>();
  const location = useLocation();
  const { data, isLoading, error } = usePayment(ref);

  const apiError = error as unknown as ApiError | null;
  const flash = (location.state as { flash?: string } | null)?.flash;

  return (
    <div>
      <Button variant="ghost" size="sm" asChild className="mb-4">
        <Link to="/payments">
          <ArrowLeft className="h-4 w-4" /> Back to payments
        </Link>
      </Button>

      {flash === "created" && (
        <div
          className="mb-4 rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800"
          data-testid="success-banner"
          role="status"
        >
          Payment created.
        </div>
      )}
      {flash === "replayed" && (
        <div
          className="mb-4 rounded-md border border-sky-200 bg-sky-50 px-4 py-3 text-sm text-sky-800"
          data-testid="success-banner"
          role="status"
        >
          Idempotent replay: existing payment returned.
        </div>
      )}

      {isLoading && <Skeleton className="h-64 w-full" />}

      {apiError && (
        <ErrorState
          error={apiError}
          title={
            apiError.status === 500
              ? "This reference could not be resolved"
              : apiError.status === 404
                ? "Payment not found"
                : undefined
          }
        />
      )}

      {apiError?.status === 500 && (
        <p className="mt-3 max-w-2xl text-sm text-muted-foreground" data-testid="incident-hint">
          The reference <span className="font-mono">{ref}</span> maps to more than one
          transaction in the data, and the lookup endpoint assumes references are unique. This
          is a known data-integrity defect under investigation (INCIDENT-001).
        </p>
      )}

      {data && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <Card className="lg:col-span-2" data-testid="result-card">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    Transaction reference
                  </p>
                  <h1 className="font-mono text-2xl font-bold">{data.transaction_ref}</h1>
                </div>
                <StatusBadge status={data.status} testId="result-status" />
              </div>

              <dl className="mt-6 grid grid-cols-2 gap-x-6 gap-y-4 text-sm">
                <div>
                  <dt className="text-muted-foreground">Amount</dt>
                  <dd className="mt-0.5 text-lg font-semibold tabular-nums">
                    {formatMoney(data.amount)}
                  </dd>
                </div>
                <div>
                  <dt className="text-muted-foreground">Customer</dt>
                  <dd className="mt-0.5">
                    <Link
                      to={`/customers/${data.customer_id}`}
                      className="font-medium text-primary hover:underline"
                    >
                      {data.customer_name}
                    </Link>
                    <span className="block font-mono text-xs text-muted-foreground">
                      {data.customer_ref}
                    </span>
                  </dd>
                </div>
                <div>
                  <dt className="text-muted-foreground">Created</dt>
                  <dd className="mt-0.5 tabular-nums">{formatDateTime(data.created_at)}</dd>
                </div>
                <div>
                  <dt className="text-muted-foreground">Completed</dt>
                  <dd className="mt-0.5 tabular-nums">{formatDateTime(data.completed_at)}</dd>
                </div>
                {data.failure_code && (
                  <div className="col-span-2">
                    <dt className="text-muted-foreground">Failure code</dt>
                    <dd className="mt-0.5">
                      <span className="rounded bg-rose-50 px-2 py-0.5 font-mono text-xs text-rose-600">
                        {data.failure_code}
                      </span>
                    </dd>
                  </div>
                )}
              </dl>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm uppercase tracking-wide text-muted-foreground">
                Callback history
              </CardTitle>
            </CardHeader>
            <CardContent>
              <CallbackTimeline callbacks={data.callbacks ?? []} />
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
