import os
import sys
import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModel
import torch
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Load environment variables
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")

DB_PARAMS = {
    "dbname": os.getenv("DATABASE_NAME"),
    "user": os.getenv("DATABASE_USERNAME"),
    "password": os.getenv("DATABASE_PASSWORD"),
    "host": os.getenv("DATABASE_HOST"),
    "port": os.getenv("DATABASE_PORT"),
}

# Load PubMedBERT
print("Loading PubMedBERT model...")
tokenizer = AutoTokenizer.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")
model = AutoModel.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")
model.eval()

def compute_embedding(text):
    with torch.no_grad():
        tokens = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        embedding = model(**tokens).last_hidden_state.mean(dim=1).squeeze()
    return embedding.numpy()

def fetch_training_data():
    print("Connecting to database...")
    try:
        conn = psycopg2.connect(**DB_PARAMS)
    except Exception as e:
        print("❌ Failed to connect to database:", e)
        sys.exit(1)

    with conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT s.search_id, s.keyword_text, 
                       os.overall_score,
                       a.title, a.abstract, c.count AS citation_count, a.pub_date
                FROM searches s
                JOIN opportunity_scores os ON s.search_id = os.search_id
                JOIN search_articles sa ON s.search_id = sa.search_id
                JOIN articles a ON sa.article_id = a.id
                LEFT JOIN citations c ON a.id = c.article_id
                WHERE c.count IS NOT NULL AND c.count >= 0
            """)
            rows = cur.fetchall()
    
    return rows

def prepare_training_samples(rows):
    grouped = defaultdict(list)

    # Group article rows by search_id
    for row in rows:
        grouped[row["search_id"]].append(row)

    samples = []

    for search_id, entries in grouped.items():
        keyword_text = entries[0]["keyword_text"]
        opportunity_score = entries[0]["overall_score"]

        try:
            keyword_vec = compute_embedding(keyword_text)

            article_vecs = []
            citation_counts = []
            pub_years = []

            for entry in entries:
                text = (entry["title"] or "") + " " + (entry["abstract"] or "")
                article_vecs.append(compute_embedding(text))

                if entry["citation_count"] is not None:
                    citation_counts.append(entry["citation_count"])

                if entry["pub_date"] is not None:
                    pub_years.append(entry["pub_date"].year)

            if not article_vecs:
                continue

            article_vec_avg = np.mean(article_vecs, axis=0)
            avg_citations = np.mean(citation_counts) if citation_counts else 0
            avg_pub_year = np.mean(pub_years) if pub_years else datetime.now().year

            sample = {
                "keyword_vector": keyword_vec,
                "article_vector": article_vec_avg,
                "avg_citations": avg_citations,
                "avg_pub_year": avg_pub_year,
                "opportunity_score": opportunity_score
            }
            samples.append(sample)

        except Exception as e:
            print(f"Skipping search_id {search_id} due to error: {e}")

    return samples

def save_samples_to_npz(samples, output_path="training_data.npz"):
    keyword_vecs = np.array([s["keyword_vector"] for s in samples])
    article_vecs = np.array([s["article_vector"] for s in samples])
    citations = np.array([s["avg_citations"] for s in samples]).reshape(-1, 1)
    pub_years = np.array([s["avg_pub_year"] for s in samples]).reshape(-1, 1)
    targets = np.array([s["opportunity_score"] for s in samples])

    np.savez(output_path,
             keyword_vecs=keyword_vecs,
             article_vecs=article_vecs,
             avg_citations=citations,
             avg_pub_years=pub_years,
             opportunity_scores=targets)
    
    print(f"Saved {len(samples)} samples to {output_path}")

if __name__ == "__main__":
    rows = fetch_training_data()
    samples = prepare_training_samples(rows)
    if samples:
        save_samples_to_npz(samples, output_path="src/model/training_data.npz")
    else:
        print("No samples generated.")
