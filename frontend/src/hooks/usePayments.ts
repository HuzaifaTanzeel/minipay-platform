import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api, toApiError } from "@/lib/api";
import type { Paginated, Payment } from "@/types";

export interface PaymentFilters {
  status?: string;
  customer_ref?: string;
  ref?: string;
  date_from?: string;
  date_to?: string;
  sort?: string;
  order?: string;
  limit: number;
  offset: number;
}

export function usePayments(filters: PaymentFilters) {
  return useQuery({
    queryKey: ["payments", filters],
    queryFn: async () => {
      const params: Record<string, string | number> = {
        limit: filters.limit,
        offset: filters.offset,
        sort: filters.sort ?? "created_at",
        order: filters.order ?? "desc",
      };
      if (filters.status) params.status = filters.status;
      if (filters.customer_ref) params.customer_ref = filters.customer_ref;
      if (filters.ref) params.ref = filters.ref;
      if (filters.date_from) params.date_from = filters.date_from;
      if (filters.date_to) params.date_to = filters.date_to;
      try {
        const { data } = await api.get<Paginated<Payment>>("/payments", { params });
        return data;
      } catch (err) {
        throw toApiError(err);
      }
    },
  });
}

export function usePayment(ref: string | undefined) {
  return useQuery({
    queryKey: ["payment", ref],
    enabled: !!ref,
    queryFn: async () => {
      try {
        const { data } = await api.get<Payment>(`/payments/${ref}`);
        return data;
      } catch (err) {
        throw toApiError(err);
      }
    },
  });
}

export interface CreatePaymentInput {
  customer_ref: string;
  amount: string;
  transaction_ref?: string;
}

export interface CreatePaymentResult {
  payment: Payment;
  replay: boolean;
}

export function useCreatePayment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: CreatePaymentInput): Promise<CreatePaymentResult> => {
      try {
        const body: CreatePaymentInput = {
          customer_ref: input.customer_ref,
          amount: input.amount,
        };
        if (input.transaction_ref) body.transaction_ref = input.transaction_ref;
        const res = await api.post<Payment>("/payments", body);
        const replay = res.headers["idempotent-replay"] === "true";
        return { payment: res.data, replay };
      } catch (err) {
        throw toApiError(err);
      }
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["payments"] });
      qc.invalidateQueries({ queryKey: ["stats"] });
    },
  });
}
