import type { ColumnDef } from "@tanstack/react-table";
import { X } from "lucide-react";
import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { DataTable } from "@/components/DataTable";
import { ErrorState } from "@/components/ErrorState";
import { PageHeader } from "@/components/PageHeader";
import { Pagination } from "@/components/Pagination";
import { StatusBadge } from "@/components/StatusBadge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { usePayments } from "@/hooks/usePayments";
import type { ApiError } from "@/lib/api";
import { formatDateTime, formatMoney } from "@/lib/utils";
import type { Payment } from "@/types";

const LIMIT = 25;
const ALL = "ALL";

export function PaymentsPage() {
  const navigate = useNavigate();
  const [status, setStatus] = useState<string>(ALL);
  const [ref, setRef] = useState("");
  const [customerRef, setCustomerRef] = useState("");
  const [sort, setSort] = useState("created_at");
  const [order, setOrder] = useState("desc");
  const [offset, setOffset] = useState(0);

  const filters = useMemo(
    () => ({
      status: status === ALL ? undefined : status,
      ref: ref.trim() || undefined,
      customer_ref: customerRef.trim() || undefined,
      sort,
      order,
      limit: LIMIT,
      offset,
    }),
    [status, ref, customerRef, sort, order, offset]
  );

  const { data, isLoading, error } = usePayments(filters);

  const columns = useMemo<ColumnDef<Payment>[]>(
    () => [
      {
        header: "Reference",
        accessorKey: "transaction_ref",
        cell: ({ row }) => (
          <span className="font-mono text-primary">{row.original.transaction_ref}</span>
        ),
      },
      {
        header: "Customer",
        accessorKey: "customer_ref",
        cell: ({ row }) => (
          <span className="font-mono text-muted-foreground">{row.original.customer_ref}</span>
        ),
      },
      {
        header: "Amount",
        accessorKey: "amount",
        cell: ({ row }) => (
          <span className="tabular-nums">{formatMoney(row.original.amount)}</span>
        ),
      },
      {
        header: "Status",
        accessorKey: "status",
        cell: ({ row }) => <StatusBadge status={row.original.status} />,
      },
      {
        header: "Created",
        accessorKey: "created_at",
        cell: ({ row }) => (
          <span className="tabular-nums text-muted-foreground">
            {formatDateTime(row.original.created_at)}
          </span>
        ),
      },
    ],
    []
  );

  function resetFilters() {
    setStatus(ALL);
    setRef("");
    setCustomerRef("");
    setSort("created_at");
    setOrder("desc");
    setOffset(0);
  }

  const hasFilters =
    status !== ALL || ref || customerRef || sort !== "created_at" || order !== "desc";

  return (
    <div>
      <PageHeader
        title="Payments"
        description="Browse and filter all transactions."
        actions={
          <Button onClick={() => navigate("/payments/new")} data-testid="new-payment-button">
            New payment
          </Button>
        }
      />

      <Card className="mb-4">
        <CardContent className="grid grid-cols-1 gap-4 p-4 sm:grid-cols-2 lg:grid-cols-5">
          <div className="space-y-1">
            <Label>Status</Label>
            <Select
              value={status}
              onValueChange={(v) => {
                setStatus(v);
                setOffset(0);
              }}
            >
              <SelectTrigger data-testid="filter-status">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={ALL}>All statuses</SelectItem>
                <SelectItem value="SUCCESS">Success</SelectItem>
                <SelectItem value="FAILED">Failed</SelectItem>
                <SelectItem value="PROCESSING">Processing</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1">
            <Label>Reference contains</Label>
            <Input
              value={ref}
              onChange={(e) => {
                setRef(e.target.value.toUpperCase());
                setOffset(0);
              }}
              placeholder="TXN..."
              data-testid="filter-ref"
            />
          </div>
          <div className="space-y-1">
            <Label>Customer contains</Label>
            <Input
              value={customerRef}
              onChange={(e) => {
                setCustomerRef(e.target.value.toUpperCase());
                setOffset(0);
              }}
              placeholder="CUST..."
              data-testid="filter-customer"
            />
          </div>
          <div className="space-y-1">
            <Label>Sort by</Label>
            <Select value={sort} onValueChange={setSort}>
              <SelectTrigger data-testid="filter-sort">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="created_at">Created</SelectItem>
                <SelectItem value="amount">Amount</SelectItem>
                <SelectItem value="status">Status</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-1">
            <Label>Order</Label>
            <Select value={order} onValueChange={setOrder}>
              <SelectTrigger data-testid="filter-order">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="desc">Descending</SelectItem>
                <SelectItem value="asc">Ascending</SelectItem>
              </SelectContent>
            </Select>
          </div>
          {hasFilters && (
            <div className="flex items-end">
              <Button variant="ghost" size="sm" onClick={resetFilters} data-testid="filter-reset">
                <X className="h-4 w-4" /> Clear filters
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {error ? (
        <ErrorState error={error as unknown as ApiError} />
      ) : (
        <>
          <DataTable
            columns={columns}
            data={data?.items ?? []}
            isLoading={isLoading}
            onRowClick={(p) => navigate(`/payments/${p.transaction_ref}`)}
            emptyMessage="No payments match these filters."
            testId="payments-table"
          />
          {data && (
            <Pagination
              total={data.total}
              limit={LIMIT}
              offset={offset}
              onChange={setOffset}
            />
          )}
        </>
      )}
    </div>
  );
}
