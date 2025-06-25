import os
import psycopg2
import numpy as np

from dotenv import load_dotenv
from statsmodels.tsa.arima.model import ARIMA

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
    counts_sorted = np.cumsum([c for _, c in sorted(zip(years, counts))]).tolist()

    try:
        model_arima = ARIMA(counts_sorted, order=(1,1,0))
        model_fit = model_arima.fit()
        forecast = model_fit.forecast(steps=forecast_horizon)
        velocity = np.mean([(f - current_total) / current_total for f in forecast])
        return float(velocity)
    except:
        return 0.0
