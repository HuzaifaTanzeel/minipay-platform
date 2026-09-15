import { useQuery } from "@tanstack/react-query";

import { api, toApiError } from "@/lib/api";
import type { Stats, TimeseriesPoint } from "@/types";

export function useStats() {
  return useQuery({
    queryKey: ["stats"],
    queryFn: async () => {
      try {
        const { data } = await api.get<Stats>("/stats");
        return data;
      } catch (err) {
        throw toApiError(err);
      }
    },
  });
}

export function useTimeseries(days = 30) {
  return useQuery({
    queryKey: ["timeseries", days],
    queryFn: async () => {
      try {
        const { data } = await api.get<TimeseriesPoint[]>("/stats/timeseries", {
          params: { days },
        });
        return data;
      } catch (err) {
        throw toApiError(err);
      }
    },
  });
}
