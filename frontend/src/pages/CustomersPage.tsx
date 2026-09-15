import type { ColumnDef } from "@tanstack/react-table";
import { Search } from "lucide-react";
import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { DataTable } from "@/components/DataTable";
import { ErrorState } from "@/components/ErrorState";
import { PageHeader } from "@/components/PageHeader";
import { Pagination } from "@/components/Pagination";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useCustomers } from "@/hooks/useCustomers";
import type { ApiError } from "@/lib/api";
import { formatDateTime } from "@/lib/utils";
import type { Customer } from "@/types";

const LIMIT = 25;

export function CustomersPage() {
  const navigate = useNavigate();
  const [q, setQ] = useState("");
  const [offset, setOffset] = useState(0);

  const params = useMemo(() => ({ q: q.trim() || undefined, limit: LIMIT, offset }), [q, offset]);
  const { data, isLoading, error } = useCustomers(params);

  const columns = useMemo<ColumnDef<Customer>[]>(
    () => [
      {
        header: "Reference",
        accessorKey: "customer_ref",
        cell: ({ row }) => (
          <span className="font-mono text-primary">{row.original.customer_ref}</span>
        ),
      },
      { header: "Name", accessorKey: "name" },
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

  return (
    <div>
      <PageHeader title="Customers" description="All registered customers." />

      <Card className="mb-4">
        <CardContent className="p-4">
          <div className="relative max-w-sm">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={q}
              onChange={(e) => {
                setQ(e.target.value);
                setOffset(0);
              }}
              placeholder="Search by reference or name"
              className="pl-9"
              data-testid="customer-search"
            />
          </div>
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
            onRowClick={(c) => navigate(`/customers/${c.id}`)}
            emptyMessage="No customers match your search."
            testId="customers-table"
          />
          {data && (
            <Pagination total={data.total} limit={LIMIT} offset={offset} onChange={setOffset} />
          )}
        </>
      )}
    </div>
  );
}
