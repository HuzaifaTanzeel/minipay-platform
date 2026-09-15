SELECT
  created_at::date AS day,
  ROUND(
    100.0 * COUNT(*) FILTER (WHERE status = 'SUCCESS') / COUNT(*),
    2
  ) AS success_rate_pct
FROM transactions
GROUP BY day
ORDER BY day;
