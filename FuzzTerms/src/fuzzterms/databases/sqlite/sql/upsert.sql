-- name: upsert-entities*!
-- Upserts entities into the entities table
INSERT OR REPLACE INTO entities
        (name, label, priority, meta)
     VALUES
        (:name, :label, :priority, :meta)
;

-- name: upsert-terms*!
-- Upserts terms into the terms table
INSERT OR REPLACE INTO terms
        (name, label, term, is_alias, vector)
    VALUES
        (:name, :label, :term, :is_alias, :vector)
;