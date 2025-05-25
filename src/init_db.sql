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

-- Semantic Vectors table
CREATE TABLE IF NOT EXISTS semantic_vectors (
    article_id INTEGER PRIMARY KEY,
    article_vector FLOAT8[],
    keyword_vector FLOAT8[],
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);

