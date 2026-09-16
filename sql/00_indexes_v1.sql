-- Extra indexes for search and ops queries. PK/unique on customers.customer_ref already exist.
-- Production: prefer CREATE INDEX CONCURRENTLY outside a transaction to avoid long write locks.

CREATE INDEX IF NOT EXISTS ix_transactions_ref
  ON transactions (transaction_ref);

CREATE INDEX IF NOT EXISTS ix_transactions_customer_created
  ON transactions (customer_id, created_at DESC);

CREATE INDEX IF NOT EXISTS ix_transactions_processing
  ON transactions (created_at)
  WHERE status = 'PROCESSING';

ANALYZE transactions;
ANALYZE callbacks;
