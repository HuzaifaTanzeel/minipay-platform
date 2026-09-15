import { createBrowserRouter } from "react-router-dom";

import { AppShell } from "@/components/layout/AppShell";
import { CustomerDetailPage } from "@/pages/CustomerDetailPage";
import { CustomersPage } from "@/pages/CustomersPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { NewPaymentPage } from "@/pages/NewPaymentPage";
import { NotFoundPage } from "@/pages/NotFoundPage";
import { PaymentDetailPage } from "@/pages/PaymentDetailPage";
import { PaymentsPage } from "@/pages/PaymentsPage";

export const router = createBrowserRouter([
  {
    element: <AppShell />,
    children: [
      { path: "/", element: <DashboardPage /> },
      { path: "/payments", element: <PaymentsPage /> },
      { path: "/payments/new", element: <NewPaymentPage /> },
      { path: "/payments/:ref", element: <PaymentDetailPage /> },
      { path: "/customers", element: <CustomersPage /> },
      { path: "/customers/:id", element: <CustomerDetailPage /> },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);
