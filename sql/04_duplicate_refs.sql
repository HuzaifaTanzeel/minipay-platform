SELECT
  transaction_ref,
  COUNT(*) AS occurrences
FROM transactions
GROUP BY transaction_ref
HAVING COUNT(*) > 1
ORDER BY transaction_ref;
