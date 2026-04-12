CREATE TABLE IF NOT EXISTS rule (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT    NOT NULL,
    rule_type TEXT    NOT NULL,
    threshold REAL,
    target    TEXT,
    active    INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS portfolio (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    uploaded_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS holding (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL REFERENCES portfolio(id),
    ticker       TEXT    NOT NULL,
    isin         TEXT,
    sector       TEXT,
    country      TEXT,
    weight       REAL    NOT NULL
);
