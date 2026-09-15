SELECT
  created_at::date AS day,
  status,
  COUNT(*) AS txn_count,
  SUM(amount) AS total_value
FROM transactions
GROUP BY day, status
ORDER BY day, status;
