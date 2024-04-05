-- name: fts_search
SELECT
    rowid,
    term,
    bm25(fts_terms) AS fts_score
FROM fts_terms
WHERE fts_terms MATCH :query
ORDER BY bm25(fts_terms)
LIMIT :limit
;

-- name: vss_search
with vss_scores AS (
    select rowid, distance as vss_distance
    from vss_terms
    where vss_search(vector, :vector)
    limit :limit
)
select vss_distance,
       rank() OVER (ORDER BY vss_distance) as vss_rank,
       terms.term,
       terms.name,
       terms.label
  from vss_scores
  join terms
    on terms.rowid = vss_scores.rowid
;

-- name: hybrid_search
WITH
vss_scores AS (
   SELECT rowid, distance AS vss_distance
   FROM vss_terms
   WHERE vss_search(vector, :vector)
   LIMIT :limit
),
vss_results AS (
   SELECT
      vs.rowid,
      vs.vss_distance,
      rank() OVER (ORDER BY vss_distance) AS vss_rank
   FROM vss_scores vs
),
fts_scores AS (
   SELECT
      rowid,
      bm25(fts_terms) AS fts_distance
   FROM fts_terms
   WHERE fts_terms MATCH :query
   LIMIT :limit
),
fts_results AS (
   SELECT
      fs.rowid,
      fs.fts_distance,
      rank() OVER (ORDER BY fts_distance) AS fts_rank
   FROM fts_scores fs
),
ranked_results AS (
   SELECT
      t.name,
      t.label,
      t.term,
      COALESCE(vr.vss_distance, 999999) AS vss_distance,
      COALESCE(vr.vss_rank, 999999) AS vss_rank,
      COALESCE(fr.fts_distance, 999999) AS fts_distance,
      COALESCE(fr.fts_rank, 999999) AS fts_rank
   FROM terms t
   LEFT JOIN vss_results vr ON t.rowid = vr.rowid
   LEFT JOIN fts_results fr ON t.rowid = fr.rowid
   WHERE vr.rowid IS NOT NULL OR fr.rowid IS NOT NULL
),
best_terms AS (
   SELECT
      name,
      label,
      MIN(vss_rank) AS min_vss_rank,
      MIN(fts_rank) AS min_fts_rank
   FROM ranked_results
   GROUP BY name, label
),
consolidated_results AS (
SELECT
   rr.name,
   rr.label,
   rr.term,
   rr.vss_distance,
   rr.vss_rank,
   rr.fts_distance,
      rr.fts_rank,
      ROW_NUMBER() OVER (
         PARTITION BY rr.name, rr.label
         ORDER BY rr.vss_rank, rr.fts_rank
      ) AS rn
FROM ranked_results rr
JOIN best_terms bt ON rr.name = bt.name AND rr.label = bt.label
WHERE (rr.vss_rank = bt.min_vss_rank OR rr.fts_rank = bt.min_fts_rank)
)
SELECT
   cr.name,
   cr.label,
   e.priority,
   e.meta,
   (SELECT json_group_array(term) FROM terms WHERE name = cr.name AND label = cr.label AND is_alias = 1) AS aliases,
   cr.term,
   cr.vss_distance,
   cr.vss_rank,
   cr.fts_distance,
   cr.fts_rank
FROM consolidated_results cr
JOIN entities e ON cr.name = e.name AND cr.label = e.label
WHERE cr.rn = 1
ORDER BY
   cr.vss_rank,
   cr.fts_rank,
   e.priority DESC NULLS LAST
LIMIT :limit;