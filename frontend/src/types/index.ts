export type PaymentStatus = "SUCCESS" | "FAILED" | "PROCESSING";

export interface Callback {
  attempt_no: number;
  http_status: number | null;
  callback_status: "SUCCESS" | "FAILED";
  attempted_at: string;
}

export interface Payment {
  id: number;
  transaction_ref: string;
  customer_id: number;
  customer_ref: string;
  customer_name: string;
  amount: string;
  status: PaymentStatus;
  created_at: string;
  completed_at: string | null;
  failure_code: string | null;
  callbacks?: Callback[];
}

export interface Customer {
  id: number;
  customer_ref: string;
  name: string;
  created_at: string;
}

export interface CustomerSummary {
  txn_count: number;
  success_count: number;
  failed_count: number;
  processing_count: number;
  success_value: string;
}

export interface CustomerDetail {
  customer: Customer;
  summary: CustomerSummary;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface Stats {
  total: number;
  success: number;
  failed: number;
  processing: number;
  success_rate: number;
  stuck: number;
  stuck_minutes: number;
  total_value: string;
  recent: Payment[];
}

export interface TimeseriesPoint {
  day: string;
  total: number;
  success: number;
  failed: number;
  processing: number;
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    request_id: string;
    [key: string]: unknown;
  };
}
