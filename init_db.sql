CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    pmid TEXT UNIQUE,
    title TEXT,
    abstract TEXT,
    doi TEXT,
    journal TEXT,
    pub_date DATE
);

CREATE TABLE authors (
    id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL
);

CREATE TABLE articles_authors (
    article_id INTEGER NOT NULL,
    authord_id INTEGER NOT NULL,
    PRIMARY KEY (article_id, authord_id),
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (authord_id) REFERENCES authors(id) ON DELETE CASCADE
);

CREATE TABLE citations (
    id SERIAL PRIMARY KEY,
    article_id INTEGER,
    source TEXT NOT NULL,
    count INTEGER,
    last_update DATE,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);

CREATE TABLE affiliations (
    id SERIAL PRIMARY KEY,
    author_id INTEGER,
    institution TEXT,
    country TEXT,
    city TEXT,
    full_address TEXT,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
);
