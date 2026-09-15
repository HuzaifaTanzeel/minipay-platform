SELECT
  AVG(completed_at - created_at) AS avg_duration,
  percentile_cont(0.95) WITHIN GROUP (ORDER BY completed_at - created_at) AS p95_duration
FROM transactions
WHERE completed_at IS NOT NULL;
