import { Search } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function Header() {
  const [ref, setRef] = useState("");
  const navigate = useNavigate();

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = ref.trim().toUpperCase();
    if (trimmed) navigate(`/payments/${trimmed}`);
  }

  return (
    <header className="sticky top-0 z-10 flex h-16 items-center gap-4 border-b bg-background/80 px-4 backdrop-blur sm:px-6">
      <form
        onSubmit={onSubmit}
        className="flex w-full max-w-lg items-center gap-2"
        data-testid="search-form"
      >
        <div className="relative min-w-0 flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={ref}
            onChange={(e) => setRef(e.target.value.toUpperCase())}
            placeholder="Search by transaction reference, e.g. TXN00000001"
            className="pl-9"
            aria-label="Search by transaction reference"
            data-testid="search-input"
          />
        </div>
        <Button type="submit" data-testid="search-submit">
          Search
        </Button>
      </form>
      <div className="ml-auto hidden text-sm text-muted-foreground sm:block">
        Operations console
      </div>
    </header>
  );
}
