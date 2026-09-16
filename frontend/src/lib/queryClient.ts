import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: (failureCount, error) => {
        // Do not retry 4xx (including 409 REFERENCE_AMBIGUOUS) or 5xx
        // from this API; only retry transient network issues once.
        const status = (error as { status?: number })?.status;
        if (status && status >= 400 && status < 600) return false;
        return failureCount < 1;
      },
      refetchOnWindowFocus: false,
    },
  },
});
