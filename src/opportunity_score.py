import numpy as np
from datetime import datetime

# --- Normalization utility ---
def normalize_score(value, all_values):
    all_vals = list(all_values) + [value]  
    min_val  = min(all_vals)
    max_val  = max(all_vals)
    if max_val == min_val:                  
        return 1.0                          
    return (value - min_val) / (max_val - min_val)

# --- Novelty Score ---
def compute_novelty_score(avg_cosine_similarity, num_articles, all_novelty_raw_scores):
    raw_score = avg_cosine_similarity / (num_articles + 1)
    return normalize_score(raw_score, all_novelty_raw_scores)

# --- Citation Rate Score ---
def compute_citation_velocity_score(citation_counts, pub_dates, all_raw_rates):
    rates = []
    for count, pub_date in zip(citation_counts, pub_dates):
        months = max((datetime.now().year - pub_date.year) * 12 + (datetime.now().month - pub_date.month), 1)
        rates.append(count / months)
    raw_score = np.mean(rates) if rates else 0
    return normalize_score(raw_score, all_raw_rates)

# --- Recency Score ---
def compute_recency_score(pub_dates, all_recency_raw_scores):
    now = datetime.now()
    recent_count = 0
    for date in pub_dates:
        delta = (now.year - date.year) * 12 + (now.month - date.month)
        if delta <= 12:
            recent_count += 1
    raw_score = recent_count / (len(pub_dates) + 1)
    return normalize_score(raw_score, all_recency_raw_scores)

# --- Final Opportunity Score ---
def compute_opportunity_score(normalized_novelty, normalized_citation_velocity, normalized_recency):
    return round((normalized_novelty + normalized_citation_velocity + normalized_recency) / 3, 3)
