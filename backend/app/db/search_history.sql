-- Create the search history table for storing raw scores used in normalization
CREATE TABLE IF NOT EXISTS search_history (
    id SERIAL PRIMARY KEY,
    search_id INTEGER REFERENCES searches(search_id) ON DELETE CASCADE,
    novelty_raw REAL,
    citation_raw REAL,
    recency_raw REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
