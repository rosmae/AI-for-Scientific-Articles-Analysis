import numpy as np
from datetime import datetime
from typing import Dict, List, Optional

from app.core.ml import compute_embedding
from sklearn.metrics.pairwise import cosine_similarity

class ScoringService:
    def __init__(self, db):
        self.db = db
    
    def compute_scores_for_search(self, search_id: int) -> Optional[Dict]:
        """Compute opportunity scores for a search"""
        try:
            # Get search details
            with self.db.get_cursor() as cur:
                cur.execute("SELECT * FROM searches WHERE search_id = %s", (search_id,))
                search = cur.fetchone()
                
                if not search:
                    return None
                
                # Get articles for this search
                cur.execute("""
                    SELECT a.id, a.title, a.abstract, a.pub_date, c.count as citation_count
                    FROM articles a
                    JOIN search_articles sa ON a.id = sa.article_id
                    LEFT JOIN citations c ON a.id = c.article_id
                    WHERE sa.search_id = %s
                """, (search_id,))
                
                articles = cur.fetchall()
                
                if not articles:
                    return None
                
                # Filter out articles with no citation data
                valid_articles = [a for a in articles if a["citation_count"] is not None and a["citation_count"] >= 0]
                
                if not valid_articles:
                    return None
                
                # Compute keyword embedding
                keyword_text = search["keyword_text"]
                keyword_embedding = compute_embedding(keyword_text)
                
                # Compute article embeddings
                article_embeddings = []
                for article in valid_articles:
                    text = (article["title"] or "") + " " + (article["abstract"] or "")
                    embedding = compute_embedding(text)
                    article_embeddings.append(embedding)
                
                # Compute similarity
                similarities = cosine_similarity([keyword_embedding], article_embeddings)[0]
                avg_sim = float(np.mean(similarities))
                
                # Get historical data for normalization
                cur.execute("""
                    SELECT novelty_raw, citation_raw, recency_raw
                    FROM search_history
                    WHERE search_id != %s
                """, (search_id,))
                
                history = cur.fetchall()
                
                novelty_raws = [h["novelty_raw"] for h in history]
                citation_raws = [h["citation_raw"] for h in history]
                recency_raws = [h["recency_raw"] for h in history]
                
                # Compute scores
                num_articles = len(valid_articles)
                pub_dates = [a["pub_date"] for a in valid_articles]
                citation_counts = [a["citation_count"] for a in valid_articles]
                
                novelty_raw = avg_sim / (num_articles + 1)
                novelty_score = self._normalize_score(novelty_raw, novelty_raws)
                
                citation_velocity_raw = self._compute_citation_velocity_raw(citation_counts, pub_dates)
                citation_velocity_score = self._normalize_score(citation_velocity_raw, citation_raws)
                
                recency_raw = self._compute_recency_raw(pub_dates)
                recency_score = self._normalize_score(recency_raw, recency_raws)
                
                overall_score = (novelty_score + citation_velocity_score + recency_score) / 3
                
                # Store scores in database - use citation_rate_score to match existing schema
                cur.execute("""
                    INSERT INTO opportunity_scores
                    (search_id, novelty_score, citation_rate_score, recency_score, overall_score, computed_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    search_id,
                    novelty_score,
                    citation_velocity_score,  # rename in code but not DB column
                    recency_score,
                    overall_score,
                    datetime.now()
                ))
                
                self.db.conn.commit()
                
                # Store raw scores for future normalization
                cur.execute("""
                    INSERT INTO search_history
                    (search_id, novelty_raw, citation_raw, recency_raw)
                    VALUES (%s, %s, %s, %s)
                """, (
                    search_id,
                    novelty_raw,
                    citation_velocity_raw,
                    recency_raw
                ))
                
                self.db.conn.commit()
                
                return {
                    "search_id": search_id,
                    "novelty_score": novelty_score,
                    "citation_rate_score": citation_velocity_score,  # use DB column name
                    "recency_score": recency_score,
                    "overall_score": overall_score
                }
                
        except Exception as e:
            print(f"Error computing scores: {e}")
            return None
    
    def _normalize_score(self, value: float, all_values: List[float]) -> float:
        """Normalize a score using min-max scaling"""
        if not all_values:
            return value
        
        all_vals = all_values + [value]
        min_val = min(all_vals)
        max_val = max(all_vals)
        
        if max_val == min_val:
            return 1.0
            
        return (value - min_val) / (max_val - min_val)
    
    def _compute_citation_velocity_raw(self, citation_counts: List[int], pub_dates: List[datetime]) -> float:
        """Compute raw citation velocity score"""
        if not citation_counts or not pub_dates:
            return 0.0
            
        rates = []
        now = datetime.now()
        
        for count, pub_date in zip(citation_counts, pub_dates):
            if not pub_date:
                continue
                
            months = max((now.year - pub_date.year) * 12 + (now.month - pub_date.month), 1)
            rates.append(count / months)
            
        return np.mean(rates) if rates else 0.0
    
    def _compute_recency_raw(self, pub_dates: List[datetime]) -> float:
        """Compute raw recency score"""
        if not pub_dates:
            return 0.0
            
        now = datetime.now()
        recent_count = 0
        
        for date in pub_dates:
            if not date:
                continue
                
            delta = (now.year - date.year) * 12 + (now.month - date.month)
            if delta <= 12:
                recent_count += 1
                
        return recent_count / (len(pub_dates) + 1)
