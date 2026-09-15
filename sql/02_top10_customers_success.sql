SELECT
  c.customer_ref,
  c.name,
  SUM(t.amount) AS success_value
FROM transactions t
JOIN customers c ON c.id = t.customer_id
WHERE t.status = 'SUCCESS'
GROUP BY c.customer_ref, c.name
ORDER BY success_value DESC
LIMIT 10;
