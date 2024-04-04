-- name: initialize#

-- Entities Table
CREATE TABLE IF NOT EXISTS entities (
    name TEXT NOT NULL,
    label TEXT,
    priority INTEGER DEFAULT 0,
    meta TEXT,
    PRIMARY KEY (name, label)
);

-- Terms Table
CREATE TABLE IF NOT EXISTS terms (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    label TEXT,
    term TEXT NOT NULL,
    is_alias INTEGER,
    vector BLOB,
    UNIQUE(name, label, term),
    FOREIGN KEY (name, label) REFERENCES entities(name, label)
    ON DELETE CASCADE
);

-- Full Text Search
CREATE VIRTUAL TABLE IF NOT EXISTS fts_terms USING fts5(
    term,
    content='terms',
    content_rowid='rowid',
    tokenize="trigram case_sensitive 0"
);

CREATE TRIGGER insert_terms_trigger AFTER INSERT ON terms
BEGIN
    INSERT INTO fts_terms (rowid, term)
         VALUES (NEW.rowid, NEW.term);
END;

CREATE TRIGGER update_terms_trigger AFTER UPDATE ON terms
BEGIN
    UPDATE fts_terms
       SET term = NEW.term
     WHERE rowid = OLD.rowid;
END;

CREATE TRIGGER delete_terms_trigger AFTER DELETE ON terms
BEGIN
    DELETE FROM fts_terms
          WHERE rowid = OLD.rowid;
END;
