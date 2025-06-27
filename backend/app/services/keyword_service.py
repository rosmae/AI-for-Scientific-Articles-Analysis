from typing import List
from keybert import KeyBERT

class KeywordService:
    def __init__(self, keyword_extractor: KeyBERT):
        self.keyword_extractor = keyword_extractor
    
    def extract_keywords(self, idea_text: str) -> List[str]:
        """Extract keywords from research idea using KeyBERT"""
        if not idea_text.strip():
            return []
            
        # Extract keywords using MMR (diverse and relevant)
        keywords = self.keyword_extractor.extract_keywords(
            idea_text,
            keyphrase_ngram_range=(1, 4),
            stop_words='english',
            use_mmr=True,
            diversity=0.7,
            nr_candidates=100,
            top_n=7
        )
        
        # Filter keywords with score >= threshold
        threshold = 0.7
        filtered_keywords = [phrase for phrase, score in keywords if score >= threshold]
        
        return filtered_keywords
