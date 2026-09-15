import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft } from "lucide-react";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { z } from "zod";

import { PageHeader } from "@/components/PageHeader";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCreatePayment } from "@/hooks/usePayments";
import type { ApiError } from "@/lib/api";

const schema = z.object({
  customer_ref: z
    .string()
    .min(3, "At least 3 characters")
    .max(40)
    .regex(/^[A-Z0-9_-]+$/, "Uppercase letters, digits, _ or - only"),
  amount: z
    .string()
    .refine((v) => Number(v) > 0, "Must be greater than 0")
    .refine((v) => /^\d+(\.\d{1,2})?$/.test(v), "At most 2 decimal places"),
  transaction_ref: z
    .string()
    .regex(/^[A-Z0-9_-]*$/, "Uppercase letters, digits, _ or - only")
    .optional(),
});

type FormValues = z.infer<typeof schema>;

export function NewPaymentPage() {
  const navigate = useNavigate();
  const createPayment = useCreatePayment();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { customer_ref: "", amount: "", transaction_ref: "" },
  });

  function onSubmit(values: FormValues) {
    createPayment.mutate(
      {
        customer_ref: values.customer_ref,
        amount: values.amount,
        transaction_ref: values.transaction_ref || undefined,
      },
      {
        onSuccess: ({ payment, replay }) => {
          toast.success(
            replay ? "Idempotent replay: existing payment returned" : "Payment created"
          );
          navigate(`/payments/${payment.transaction_ref}`);
        },
        onError: (err) => {
          const e = err as unknown as ApiError;
          toast.error(`${e.code}: ${e.message}`);
        },
      }
    );
  }

  return (
    <div className="mx-auto max-w-lg">
      <Button variant="ghost" size="sm" asChild className="mb-4">
        <Link to="/payments">
          <ArrowLeft className="h-4 w-4" /> Back to payments
        </Link>
      </Button>

      <PageHeader
        title="Create a payment"
        description="Submits through the same idempotent endpoint as the API."
      />

      <Card>
        <CardContent className="p-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" data-testid="payment-form">
            <div className="space-y-1.5">
              <Label htmlFor="customer_ref">Customer reference</Label>
              <Input
                id="customer_ref"
                placeholder="CUST000001"
                className="font-mono"
                data-testid="pay-customer"
                {...register("customer_ref")}
              />
              {errors.customer_ref && (
                <p className="text-xs text-rose-600" data-testid="error-customer">
                  {errors.customer_ref.message}
                </p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="amount">Amount</Label>
              <Input
                id="amount"
                inputMode="decimal"
                placeholder="1000.00"
                className="tabular-nums"
                data-testid="pay-amount"
                {...register("amount")}
              />
              {errors.amount && (
                <p className="text-xs text-rose-600" data-testid="error-amount">
                  {errors.amount.message}
                </p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="transaction_ref">
                Transaction reference <span className="text-muted-foreground">(optional)</span>
              </Label>
              <Input
                id="transaction_ref"
                placeholder="auto-generated if left blank"
                className="font-mono"
                data-testid="pay-ref"
                {...register("transaction_ref")}
              />
              {errors.transaction_ref && (
                <p className="text-xs text-rose-600">{errors.transaction_ref.message}</p>
              )}
              <p className="text-xs text-muted-foreground">
                Reusing a reference with the same payload replays the original (idempotent).
              </p>
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={createPayment.isPending}
              data-testid="pay-submit"
            >
              {createPayment.isPending ? "Creating..." : "Create payment"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
