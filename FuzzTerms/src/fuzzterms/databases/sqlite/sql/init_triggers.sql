-- name: init_triggers#

CREATE TRIGGER insert_terms_trigger AFTER INSERT ON terms
BEGIN
    INSERT INTO fts_terms (rowid, term)
    VALUES (NEW.rowid, NEW.term);

    INSERT INTO vss_terms (rowid, vector)
    VALUES (NEW.rowid, NEW.vector);
END;

CREATE TRIGGER update_terms_trigger AFTER UPDATE ON terms
BEGIN
    UPDATE fts_terms
       SET term = NEW.term
     WHERE rowid = OLD.rowid;

    UPDATE vss_terms
       SET vector = NEW.vector
     WHERE rowid = OLD.rowid;
END;

CREATE TRIGGER delete_terms_trigger AFTER DELETE ON terms
BEGIN
    DELETE FROM fts_terms
     WHERE rowid = OLD.rowid;

    DELETE FROM vss_terms
     WHERE rowid = OLD.rowid;
END;
