-- Create tables if they don't exist

-- Articles table
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    pmid TEXT UNIQUE,
    title TEXT,
    abstract TEXT,
    doi TEXT,
    journal TEXT,
    pub_date DATE
);

-- Authors table
CREATE TABLE IF NOT EXISTS authors (
    id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL
);

-- Articles-Authors join table
CREATE TABLE IF NOT EXISTS articles_authors (
    article_id INTEGER NOT NULL,
    authord_id INTEGER NOT NULL,
    PRIMARY KEY (article_id, authord_id),
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (authord_id) REFERENCES authors(id) ON DELETE CASCADE
);

-- Citations table
CREATE TABLE IF NOT EXISTS citations (
    id SERIAL PRIMARY KEY,
    article_id INTEGER,
    source TEXT NOT NULL,
    count INTEGER,
    last_update DATE,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);

-- Affiliations table
CREATE TABLE IF NOT EXISTS affiliations (
    id SERIAL PRIMARY KEY,
    author_id INTEGER,
    institution TEXT,
    country TEXT,
    city TEXT,
    full_address TEXT,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
);

-- Subfields table for categorization
CREATE TABLE IF NOT EXISTS subfields (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE,
    description TEXT
);

-- Articles-Subfields join table
CREATE TABLE IF NOT EXISTS articles_subfields (
    article_id INTEGER NOT NULL,
    subfield_id INTEGER NOT NULL,
    PRIMARY KEY (article_id, subfield_id),
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (subfield_id) REFERENCES subfields(id) ON DELETE CASCADE
);

-- Subfield metrics table
CREATE TABLE IF NOT EXISTS subfield_metrics (
    id SERIAL PRIMARY KEY,
    subfield_id INTEGER,
    publication_count INTEGER,
    total_citations INTEGER,
    avg_citations FLOAT,
    opportunity_score FLOAT,
    calculation_date DATE,
    FOREIGN KEY (subfield_id) REFERENCES subfields(id) ON DELETE CASCADE
);