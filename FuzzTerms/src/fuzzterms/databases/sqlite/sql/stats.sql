-- name: stats^
SELECT
  SUM(CASE WHEN source = 'entities' THEN count ELSE 0 END) AS entities,
  SUM(CASE WHEN source = 'terms' THEN count ELSE 0 END) AS terms
FROM (
  SELECT 'entities' AS source, COUNT(*) AS count FROM entities
  UNION ALL
  SELECT 'terms', COUNT(*) FROM terms
) AS counts;
