import { Badge } from "@/components/ui/badge";
import { formatDateTime } from "@/lib/utils";
import type { Callback } from "@/types";

export function CallbackTimeline({ callbacks }: { callbacks: Callback[] }) {
  if (!callbacks.length) {
    return <p className="text-sm text-muted-foreground">No callback attempts recorded.</p>;
  }
  return (
    <ol className="relative ms-3 border-s" data-testid="callback-timeline">
      {callbacks.map((cb) => {
        const ok = cb.callback_status === "SUCCESS";
        return (
          <li key={cb.attempt_no} className="mb-6 ms-6">
            <span
              className={`absolute -start-3 flex h-6 w-6 items-center justify-center rounded-full ring-4 ring-background ${
                ok ? "bg-emerald-500" : "bg-rose-500"
              }`}
            >
              <span className="text-[10px] font-bold text-white">{cb.attempt_no}</span>
            </span>
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-medium">Attempt {cb.attempt_no}</span>
              <Badge variant={ok ? "success" : "danger"}>{cb.callback_status}</Badge>
              {cb.http_status != null && (
                <span className="rounded bg-muted px-2 py-0.5 font-mono text-xs text-muted-foreground">
                  HTTP {cb.http_status}
                </span>
              )}
            </div>
            <time className="text-xs text-muted-foreground">
              {formatDateTime(cb.attempted_at)}
            </time>
          </li>
        );
      })}
    </ol>
  );
}
