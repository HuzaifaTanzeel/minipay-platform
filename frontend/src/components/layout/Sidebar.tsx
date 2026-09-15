import { LayoutDashboard, CreditCard, Users, PlusCircle } from "lucide-react";
import { NavLink } from "react-router-dom";

import { cn } from "@/lib/utils";

const NAV = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true, testId: "nav-dashboard" },
  { to: "/payments", label: "Payments", icon: CreditCard, testId: "nav-payments" },
  { to: "/customers", label: "Customers", icon: Users, testId: "nav-customers" },
  { to: "/payments/new", label: "New payment", icon: PlusCircle, testId: "nav-new-payment" },
];

export function Sidebar() {
  return (
    <aside className="hidden w-60 shrink-0 border-r bg-card md:block">
      <div className="flex h-16 items-center gap-2 border-b px-6 font-bold text-primary">
        <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          M
        </span>
        MiniPay
      </div>
      <nav className="space-y-1 p-3">
        {NAV.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            data-testid={item.testId}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground"
              )
            }
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
