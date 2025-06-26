import os
import psycopg2
import numpy as np
import matplotlib.pyplot as plt

from dotenv import load_dotenv
from statsmodels.tsa.arima.model import ARIMA

import warnings
warnings.filterwarnings("ignore")

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

def generate_forecast_visualization(search_id):
    conn = connect_db()
    with conn.cursor() as cur:
        cur.execute("SELECT article_id FROM search_articles WHERE search_id = %s", (search_id,))
        article_ids = [row[0] for row in cur.fetchall()]
    conn.close()

    if not article_ids:
        print("No articles for this search.")
        return

    all_years = {}
    for article_id in article_ids:
        history = get_citation_history(article_id)
        if not history:
            continue
        years, counts = history
        cumulative = np.cumsum(counts)
        for year, value in zip(years, cumulative):
            all_years.setdefault(year, []).append(value)

    if not all_years:
        print("No citation history found.")
        return

    sorted_years = sorted(all_years.keys())
    avg_cumulative = [np.mean(all_years[year]) for year in sorted_years]

    try:
        model = ARIMA(avg_cumulative, order=(1, 1, 0))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=3)
        forecast_years = [sorted_years[-1] + i for i in range(1, 4)]

        plt.figure(figsize=(10, 5))
        plt.plot(sorted_years, avg_cumulative, label="Avg. Cumulative Citations")
        plt.plot([sorted_years[-1], forecast_years[0]], 
            [avg_cumulative[-1], forecast[0]], 
            linestyle='dashed', color='orange')

        plt.plot(forecast_years, forecast.tolist(), linestyle='dashed', label="Forecast")
        plt.title("Topic Citation Growth Forecast")
        plt.xlabel("Year")
        plt.ylabel("Cumulative Citations")
        plt.legend()
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print("Forecast failed:", str(e))
    
def run_forecast_pipeline(search_id):
    generate_forecast_visualization(search_id)
