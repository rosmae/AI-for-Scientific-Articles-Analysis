import os
import sys
import psycopg2
import numpy as np
import hdbscan
import umap
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime

load_dotenv()

DB_PARAMS = {
    "dbname": os.getenv("DATABASE_NAME"),
    "user": os.getenv("DATABASE_USERNAME"),
    "password": os.getenv("DATABASE_PASSWORD"),
    "host": os.getenv("DATABASE_HOST"),
    "port": os.getenv("DATABASE_PORT")
}

def connect_db():
    return psycopg2.connect(**DB_PARAMS)

def load_vectors():
    conn = connect_db()
    with conn.cursor() as cur:
        cur.execute("SELECT article_id, vector FROM article_vectors")
        rows = cur.fetchall()
    conn.close()

    article_ids = [row[0] for row in rows]
    vectors = np.array([row[1] for row in rows])
    return article_ids, vectors

def run_hdbscan(vectors):
    clusterer = hdbscan.HDBSCAN(min_cluster_size=5)
    labels = clusterer.fit_predict(vectors)
    return labels

def update_article_labels(article_ids, labels):
    conn = connect_db()
    with conn.cursor() as cur:
        for article_id, label in zip(article_ids, labels):
            cur.execute(
                "UPDATE article_vectors SET cluster_label = %s WHERE article_id = %s",
                (int(label), int(article_id))
            )
    conn.commit()
    conn.close()

def compute_centroid(vectors):
    return np.mean(vectors, axis=0)

def get_citation_history(article_id):
    conn = connect_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT year, citation_count FROM citations_per_year 
            WHERE article_id = %s ORDER BY year
        """, (article_id,))
        rows = cur.fetchall()
    conn.close()
    if not rows:
        return None
    years, counts = zip(*rows)
    return list(years), list(counts)

def get_current_citations(article_id):
    conn = connect_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT count FROM citations WHERE article_id = %s
        """, (article_id,))
        row = cur.fetchone()
    conn.close()
    return row[0] if row else None

def compute_article_velocity(article_id, forecast_horizon=3):
    data = get_citation_history(article_id)
    current_total = get_current_citations(article_id)
    if data is None or current_total is None or current_total == 0:
        return 0.0

    years, counts = data
    years_sorted = sorted(years)
    counts_sorted = [c for _, c in sorted(zip(years, counts))]

    try:
        model = ARIMA(counts_sorted, order=(1,1,0))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=forecast_horizon)
        velocity = np.mean([(f - current_total) / current_total for f in forecast])
        return float(velocity)
    except:
        return 0.0

def compute_clusters(article_ids, vectors, labels):
    conn = connect_db()
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE clusters")
        cluster_labels = set(label for label in labels if label != -1)

        for cluster_label in cluster_labels:
            indices = [i for i, l in enumerate(labels) if l == cluster_label]
            cluster_vectors = vectors[indices]
            centroid = compute_centroid(cluster_vectors)

            article_velocities = []
            for i in indices:
                article_id = article_ids[i]
                vel = compute_article_velocity(article_id)
                article_velocities.append(vel)

            avg_velocity = np.mean(article_velocities)
            cur.execute("""
                INSERT INTO clusters (cluster_label, centroid, size, velocity, last_updated)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                int(cluster_label),
                centroid.tolist(),
                len(indices),
                float(avg_velocity),
                datetime.now()
            ))
    conn.commit()
    conn.close()

def generate_umap_visualization(article_ids, vectors, labels):
    reducer = umap.UMAP()
    embedding = reducer.fit_transform(vectors)

    plt.figure(figsize=(10, 8))
    unique_labels = np.unique(labels)

    for label in unique_labels:
        indices = [i for i, l in enumerate(labels) if l == label]
        cluster_embedding = embedding[indices]
        plt.scatter(cluster_embedding[:,0], cluster_embedding[:,1], label=f"Cluster {label}", s=20)

    plt.title("UMAP Projection of Clusters")
    plt.legend()
    plt.savefig("cluster_umap.png")
    plt.close()

def main():
    article_ids, vectors = load_vectors()
    labels = run_hdbscan(vectors)
    update_article_labels(article_ids, labels)
    compute_clusters(article_ids, vectors, labels)
    generate_umap_visualization(article_ids, vectors, labels)
    print("Clustering pipeline completed.")

if __name__ == "__main__":
    main()
