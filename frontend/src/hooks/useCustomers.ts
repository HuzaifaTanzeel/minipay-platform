import { useQuery } from "@tanstack/react-query";

import { api, toApiError } from "@/lib/api";
import type { Customer, CustomerDetail, Paginated, Payment } from "@/types";

export interface CustomerListParams {
  q?: string;
  limit: number;
  offset: number;
}

export function useCustomers(params: CustomerListParams) {
  return useQuery({
    queryKey: ["customers", params],
    queryFn: async () => {
      const query: Record<string, string | number> = {
        limit: params.limit,
        offset: params.offset,
      };
      if (params.q) query.q = params.q;
      try {
        const { data } = await api.get<Paginated<Customer>>("/customers", { params: query });
        return data;
      } catch (err) {
        throw toApiError(err);
      }
    },
  });
}

export function useCustomer(id: number | undefined) {
  return useQuery({
    queryKey: ["customer", id],
    enabled: !!id,
    queryFn: async () => {
      try {
        const { data } = await api.get<CustomerDetail>(`/customers/${id}`);
        return data;
      } catch (err) {
        throw toApiError(err);
      }
    },
  });
}

export function useCustomerPayments(
  id: number | undefined,
  limit: number,
  offset: number
) {
  return useQuery({
    queryKey: ["customer-payments", id, limit, offset],
    enabled: !!id,
    queryFn: async () => {
      try {
        const { data } = await api.get<{
          customer: Customer;
          total: number;
          limit: number;
          offset: number;
          items: Payment[];
        }>(`/customers/${id}/payments`, { params: { limit, offset } });
        return data;
      } catch (err) {
        throw toApiError(err);
      }
    },
  });
}
