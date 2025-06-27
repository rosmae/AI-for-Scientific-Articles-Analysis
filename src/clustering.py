import os
import psycopg2
import numpy as np
import hdbscan

try:
    import umap.umap_ as umap
    UMAP_AVAILABLE = True
except ImportError:
    print("Warning: UMAP not available. Clustering visualization will be skipped.")
    UMAP_AVAILABLE = False

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

from dotenv import load_dotenv
from datetime import datetime
from forecast import compute_article_velocity  

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
    clusterer = hdbscan.HDBSCAN(min_cluster_size=2)
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

def generate_umap_visualization(article_ids, vectors, labels, keyword_embedding=None):
    if not UMAP_AVAILABLE:
        return
    reducer = umap.UMAP(n_neighbors=10, min_dist=0.1, metric='cosine')
    embedding = reducer.fit_transform(vectors)

    plt.figure(figsize=(10, 8))
    unique_labels = np.unique(labels)

    for label in unique_labels:
        if label == -1:
            continue
        indices = [i for i, l in enumerate(labels) if l == label]
        cluster_embedding = embedding[indices]
        plt.scatter(cluster_embedding[:, 0], cluster_embedding[:, 1], label=f"Cluster {label +1}", s=20)

    if keyword_embedding is not None:
        keyword_2d = reducer.transform(keyword_embedding.reshape(1, -1))
        plt.scatter(keyword_2d[0, 0], keyword_2d[0, 1], color='red', s=150, marker='X', label='User Keyword')

    plt.title("UMAP Projection of Clusters")
    plt.legend()
    plt.show()

def run_clustering_pipeline(keyword_embedding=None):
    article_ids, vectors = load_vectors()
    labels = run_hdbscan(vectors)
    update_article_labels(article_ids, labels)
    compute_clusters(article_ids, vectors, labels)
    generate_umap_visualization(article_ids, vectors, labels, keyword_embedding)