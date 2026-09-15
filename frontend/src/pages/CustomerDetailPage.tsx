import { ArrowLeft } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { ErrorState } from "@/components/ErrorState";
import { Pagination } from "@/components/Pagination";
import { StatusBadge } from "@/components/StatusBadge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useCustomer, useCustomerPayments } from "@/hooks/useCustomers";
import type { ApiError } from "@/lib/api";
import { formatDateTime, formatMoney } from "@/lib/utils";

const LIMIT = 25;

export function CustomerDetailPage() {
  const { id } = useParams<{ id: string }>();
  const customerId = id ? Number(id) : undefined;
  const navigate = useNavigate();
  const [offset, setOffset] = useState(0);

  const detail = useCustomer(customerId);
  const payments = useCustomerPayments(customerId, LIMIT, offset);

  if (detail.error) {
    return (
      <div>
        <Button variant="ghost" size="sm" asChild className="mb-4">
          <Link to="/customers">
            <ArrowLeft className="h-4 w-4" /> Back to customers
          </Link>
        </Button>
        <ErrorState error={detail.error as unknown as ApiError} title="Customer not found" />
      </div>
    );
  }

  return (
    <div>
      <Button variant="ghost" size="sm" asChild className="mb-4">
        <Link to="/customers">
          <ArrowLeft className="h-4 w-4" /> Back to customers
        </Link>
      </Button>

      {detail.isLoading || !detail.data ? (
        <Skeleton className="h-36 w-full" />
      ) : (
        <Card data-testid="customer-card">
          <CardContent className="p-6">
            <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Customer
            </p>
            <h1 className="text-2xl font-bold">{detail.data.customer.name}</h1>
            <p className="font-mono text-sm text-muted-foreground">
              {detail.data.customer.customer_ref}
            </p>
            <div className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
              <Metric label="Transactions" value={detail.data.summary.txn_count.toLocaleString()} />
              <Metric
                label="Successful"
                value={detail.data.summary.success_count.toLocaleString()}
              />
              <Metric label="Failed" value={detail.data.summary.failed_count.toLocaleString()} />
              <Metric
                label="Confirmed value"
                value={formatMoney(detail.data.summary.success_value)}
              />
            </div>
          </CardContent>
        </Card>
      )}

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Transactions</CardTitle>
        </CardHeader>
        <CardContent>
          <Table data-testid="customer-payments-table">
            <TableHeader>
              <TableRow>
                <TableHead>Reference</TableHead>
                <TableHead className="text-right">Amount</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Created</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {payments.isLoading || !payments.data
                ? Array.from({ length: 5 }).map((_, i) => (
                    <TableRow key={i}>
                      {Array.from({ length: 4 }).map((_c, j) => (
                        <TableCell key={j}>
                          <Skeleton className="h-4 w-full" />
                        </TableCell>
                      ))}
                    </TableRow>
                  ))
                : payments.data.items.map((p) => (
                    <TableRow
                      key={p.id}
                      className="cursor-pointer"
                      onClick={() => navigate(`/payments/${p.transaction_ref}`)}
                    >
                      <TableCell className="font-mono text-primary">
                        {p.transaction_ref}
                      </TableCell>
                      <TableCell className="text-right tabular-nums">
                        {formatMoney(p.amount)}
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={p.status} />
                      </TableCell>
                      <TableCell className="tabular-nums text-muted-foreground">
                        {formatDateTime(p.created_at)}
                      </TableCell>
                    </TableRow>
                  ))}
            </TableBody>
          </Table>
          {payments.data && (
            <Pagination
              total={payments.data.total}
              limit={LIMIT}
              offset={offset}
              onChange={setOffset}
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-0.5 text-lg font-semibold tabular-nums">{value}</p>
    </div>
  );
}
