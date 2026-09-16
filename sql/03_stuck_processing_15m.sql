SELECT
  id,
  transaction_ref,
  customer_id,
  amount,
  created_at
FROM transactions
WHERE status = 'PROCESSING'
  AND created_at < now() - INTERVAL '15 minutes'
ORDER BY created_at
LIMIT 20;
