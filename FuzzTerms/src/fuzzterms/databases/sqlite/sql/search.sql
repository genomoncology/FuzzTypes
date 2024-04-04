-- name: fts_search^
SELECT
    rowid,
    term,
    bm25(fts_terms) AS fts_score
FROM fts_terms
WHERE fts_terms MATCH :query
ORDER BY bm25(fts_terms)
LIMIT :limit
;

-- name: search
WITH
    vss_results AS (
        SELECT
            t.name,
            t.label,
            t.term,
            vss.distance AS vss_score
        FROM vss_terms vss
        JOIN terms t ON t.rowid = vss.rowid
        WHERE vss_search(vss.term_embedding, :vector)
        ORDER BY vss.distance
        LIMIT :limit
    ),
    fts_results AS (
        SELECT
            name,
            label,
            term,
            bm25(fts_terms) AS fts_score
        FROM fts_terms
        WHERE fts_terms MATCH 'zeus'
        ORDER BY bm25(fts_terms)
        LIMIT :limit
    )
SELECT
    COALESCE(vss.name, fts.name) AS name,
    COALESCE(vss.label, fts.label) AS label,
    COALESCE(vss.term, fts.term) AS term,
    COALESCE(vss.vss_score, 0) AS vss_score,
    COALESCE(fts.fts_score, 0) AS fts_score
FROM vss_results vss
FULL OUTER JOIN fts_results fts ON vss.name = fts.name AND vss.label = fts.label
ORDER BY vss_score, fts_score DESC
LIMIT :limit;