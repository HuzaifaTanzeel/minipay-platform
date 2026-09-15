# 05 – Web Services & API Test Automation

Provide a small REST API or use the MiniPay implementation you create. It should support equivalent operations to:

```text
POST /api/customers
POST /api/payments
GET  /api/payments/{id}
GET  /api/customers/{id}/payments
GET  /health
```

Demonstrate appropriate use of HTTP methods, status codes, JSON, headers, validation and error responses.

Create automated API tests covering at least:
- successful requests;
- invalid/missing fields;
- unknown resources;
- authentication or access-control behavior (a simple mechanism is acceptable);
- duplicate/idempotent payment submission;
- server/API error behavior where practical;
- response schema/content assertions; and
- one basic response-time assertion with a reasonable threshold.

Use pytest, Postman/Newman or another reproducible framework. Document one command that executes the complete API suite.

In `tests/api/NOTES.md`, briefly explain how you would handle client/server timeouts, retries, idempotency and HTTP 4xx versus 5xx errors in a payment integration.
