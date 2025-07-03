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

# --- Citation Velocity Score ---
def compute_citation_velocity_score(citation_counts, pub_dates, all_raw_rates):
    """
    Compute citation velocity based on citations per months since publication.
    This measures how quickly articles are gaining citations over time.
    """
    if not citation_counts or not pub_dates:
        return 0.0
    
    rates = []
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    for count, pub_date in zip(citation_counts, pub_dates):

        # Calculate months since publication (minimum 1 to avoid division by zero)
        months = max((current_year-pub_date.year) * 12 + (current_month-pub_date.month) , 1)

        # Citations per month (velocity)
        citation_velocity = count / months

        rates.append(citation_velocity)
    
    # Use median instead of mean to reduce impact of outliers
    # raw_score = np.median(rates) if rates else 0
    # ORIGINAL: 
    raw_score = np.mean(rates) if rates else 0

    # Normalize against all other searches
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
