-- name: init_tables#

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

CREATE INDEX IF NOT EXISTS idx_terms_name_label ON terms (name, label);
CREATE INDEX IF NOT EXISTS idx_terms_term ON terms (term);

-- Note: VSS processed in Python code due to limit of aiosql (no variables in executable scripts)
