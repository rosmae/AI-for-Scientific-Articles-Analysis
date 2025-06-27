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
-- Note: "authord_id" column has a typo but is kept for compatibility
CREATE TABLE IF NOT EXISTS articles_authors (
    article_id INTEGER NOT NULL,
    authord_id INTEGER NOT NULL,  -- Intentional spelling (matches existing DB)
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

-- Create the searches table
CREATE TABLE IF NOT EXISTS searches (
    search_id SERIAL PRIMARY KEY,
    idea_text TEXT,
    keyword_text TEXT,
    max_results INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the search_articles table (many-to-many mapping)
CREATE TABLE IF NOT EXISTS search_articles (
    search_id INTEGER REFERENCES searches(search_id) ON DELETE CASCADE,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    PRIMARY KEY (search_id, article_id)
);

-- Create the opportunity score and subscores table
CREATE TABLE IF NOT EXISTS opportunity_scores (
    search_id INTEGER PRIMARY KEY REFERENCES searches(search_id) ON DELETE CASCADE,
    novelty_score REAL,
    citation_velocity_score REAL,
    recency_score REAL,
    overall_score REAL,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the title + abstract semantic vectors table
CREATE TABLE IF NOT EXISTS article_vectors (
    article_id INTEGER PRIMARY KEY REFERENCES articles(id) ON DELETE CASCADE,
    vector FLOAT8[],
    cluster_label INTEGER
);

-- Create the citation history table
CREATE TABLE IF NOT EXISTS citations_per_year (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    citation_count INTEGER
);

-- Create clusters table
CREATE TABLE IF NOT EXISTS clusters (
    cluster_label INTEGER PRIMARY KEY,
    centroid FLOAT8[],
    size INTEGER,
    velocity REAL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create search history table for scoring normalization
CREATE TABLE IF NOT EXISTS search_history (
    id SERIAL PRIMARY KEY,
    search_id INTEGER REFERENCES searches(search_id) ON DELETE CASCADE,
    novelty_raw REAL,
    citation_raw REAL,
    recency_raw REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
