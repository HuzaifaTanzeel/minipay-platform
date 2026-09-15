SELECT
  COUNT(*) AS success_count,
  SUM(amount) AS success_value,
  COUNT(*) FILTER (WHERE has_success_callback) AS callback_success_count,
  SUM(amount) FILTER (WHERE has_success_callback) AS callback_success_value
FROM (
  SELECT
    t.amount,
    EXISTS (
      SELECT 1
      FROM callbacks c
      WHERE c.transaction_id = t.id
        AND c.callback_status = 'SUCCESS'
    ) AS has_success_callback
  FROM transactions t
  WHERE t.status = 'SUCCESS'
) s;
