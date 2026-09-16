import axios from "axios";

// All requests go to the same-origin /api path. In dev, the Vite proxy injects
// the X-API-Key header; in prod, nginx does. The key is never in the browser.
export const api = axios.create({
  baseURL: "/api",
  timeout: 10000,
});

export interface ApiError {
  status: number;
  code: string;
  message: string;
  requestId?: string;
  ids?: number[];
}

/** Normalise an axios error into our envelope shape for the UI. */
export function toApiError(err: unknown): ApiError {
  if (axios.isAxiosError(err)) {
    const status = err.response?.status ?? 0;
    const body = err.response?.data as
      | {
          error?: {
            code?: string;
            message?: string;
            request_id?: string;
            ids?: unknown;
          };
        }
      | undefined;
    const rawIds = body?.error?.ids;
    const ids = Array.isArray(rawIds)
      ? rawIds.filter((n): n is number => typeof n === "number")
      : undefined;
    return {
      status,
      code: body?.error?.code ?? "NETWORK_ERROR",
      message: body?.error?.message ?? err.message,
      requestId: body?.error?.request_id,
      ...(ids && ids.length ? { ids } : {}),
    };
  }
  return { status: 0, code: "UNKNOWN", message: String(err) };
}
