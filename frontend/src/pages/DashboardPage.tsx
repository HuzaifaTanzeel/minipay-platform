import { Activity, AlertCircle, CheckCircle2, Clock } from "lucide-react";
import { useNavigate } from "react-router-dom";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { ErrorState } from "@/components/ErrorState";
import { PageHeader } from "@/components/PageHeader";
import { StatCard } from "@/components/StatCard";
import { StatusBadge } from "@/components/StatusBadge";
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
import { useStats, useTimeseries } from "@/hooks/useStats";
import type { ApiError } from "@/lib/api";
import { formatDateTime, formatMoney } from "@/lib/utils";

export function DashboardPage() {
  const stats = useStats();
  const series = useTimeseries(30);
  const navigate = useNavigate();

  if (stats.error) {
    return (
      <>
        <PageHeader title="Operations dashboard" />
        <ErrorState error={stats.error as unknown as ApiError} />
      </>
    );
  }

  return (
    <div>
      <PageHeader
        title="Operations dashboard"
        description="Live view of transaction volume, health and recent activity."
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.isLoading || !stats.data ? (
          Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-32" />)
        ) : (
          <>
            <StatCard
              label="Total transactions"
              value={stats.data.total.toLocaleString()}
              hint={`Confirmed value ${formatMoney(stats.data.total_value)}`}
              icon={Activity}
              testId="stat-total"
            />
            <StatCard
              label="Success rate"
              value={`${stats.data.success_rate}%`}
              hint={`${stats.data.success.toLocaleString()} succeeded`}
              icon={CheckCircle2}
              accent="success"
              testId="stat-success-rate"
            />
            <StatCard
              label="Failed"
              value={stats.data.failed.toLocaleString()}
              hint={`${stats.data.processing.toLocaleString()} still processing`}
              icon={AlertCircle}
              accent="danger"
              testId="stat-failed"
            />
            <StatCard
              label={`Stuck > ${stats.data.stuck_minutes}m`}
              value={stats.data.stuck.toLocaleString()}
              hint="processing beyond threshold"
              icon={Clock}
              accent="warning"
              testId="stat-stuck"
            />
          </>
        )}
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Daily volume</CardTitle>
        </CardHeader>
        <CardContent>
          {series.isLoading || !series.data ? (
            <Skeleton className="h-72 w-full" />
          ) : (
            <ResponsiveContainer width="100%" height={288}>
              <AreaChart data={series.data} margin={{ left: -16, right: 8, top: 8 }}>
                <defs>
                  <linearGradient id="gSuccess" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gFailed" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="day" tick={{ fontSize: 12 }} tickLine={false} />
                <YAxis tick={{ fontSize: 12 }} tickLine={false} axisLine={false} />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="success"
                  stroke="#10b981"
                  fill="url(#gSuccess)"
                  strokeWidth={2}
                  name="Success"
                />
                <Area
                  type="monotone"
                  dataKey="failed"
                  stroke="#f43f5e"
                  fill="url(#gFailed)"
                  strokeWidth={2}
                  name="Failed"
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Recent transactions</CardTitle>
        </CardHeader>
        <CardContent>
          <Table data-testid="recent-table">
            <TableHeader>
              <TableRow>
                <TableHead>Reference</TableHead>
                <TableHead>Customer</TableHead>
                <TableHead className="text-right">Amount</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Created</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {stats.isLoading || !stats.data
                ? Array.from({ length: 6 }).map((_, i) => (
                    <TableRow key={i}>
                      {Array.from({ length: 5 }).map((_c, j) => (
                        <TableCell key={j}>
                          <Skeleton className="h-4 w-full" />
                        </TableCell>
                      ))}
                    </TableRow>
                  ))
                : stats.data.recent.map((p) => (
                    <TableRow
                      key={p.transaction_ref + p.created_at}
                      className="cursor-pointer"
                      onClick={() => navigate(`/payments/${p.transaction_ref}`)}
                    >
                      <TableCell className="font-mono text-primary">
                        {p.transaction_ref}
                      </TableCell>
                      <TableCell className="font-mono text-muted-foreground">
                        {p.customer_ref}
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
        </CardContent>
      </Card>
    </div>
  );
}
