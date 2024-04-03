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
    name TEXT NOT NULL,
    label TEXT,
    term TEXT NOT NULL,
    is_alias INTEGER,
    UNIQUE(name, label, term),
    FOREIGN KEY (name, label) REFERENCES entities(name, label)
    ON DELETE CASCADE
);

-- Full Text Search
CREATE VIRTUAL TABLE IF NOT EXISTS fts_terms USING fts5(
    name,
    label,
    term,
    content='terms',
    content_rowid='rowid',
    tokenize='unicode61'
);

-- Create a VSS virtual table for term embeddings
CREATE VIRTUAL TABLE IF NOT EXISTS vss_terms USING vss0(
    term_embedding(:vss_dimensions) factory="IVF4096,Flat,IDMap2"
);
