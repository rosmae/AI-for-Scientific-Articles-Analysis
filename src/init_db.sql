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