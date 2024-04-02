-- name: initialize#

CREATE TABLE IF NOT EXISTS entities (
    name TEXT NOT NULL,
    label TEXT,
    priority INTEGER DEFAULT 0,
    meta TEXT, -- storing JSON as text
    PRIMARY KEY (name, label)
);

CREATE TABLE IF NOT EXISTS aliases (
    name TEXT NOT NULL,
    label TEXT,
    alias TEXT NOT NULL,
    UNIQUE(name, label, alias),
    FOREIGN KEY (name, label) REFERENCES entities(name, label)
    ON DELETE CASCADE
);

