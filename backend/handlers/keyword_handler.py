import os
import sys
import json
import logging
from transformers import AutoTokenizer, AutoModel
from keybert import KeyBERT
import torch

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.mesh_expander import expand_with_mesh

logger = logging.getLogger("medicalai-api.keywords")

# Initialize PubMedBERT model (load only once)
try:
    tokenizer = AutoTokenizer.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")
    model = AutoModel.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")
    keyword_extractor = KeyBERT(model=model)
    logger.info("PubMedBERT model loaded successfully")
except Exception as e:
    logger.error(f"Error loading PubMedBERT model: {e}")
    tokenizer = None
    model = None
    keyword_extractor = None

class KeywordHandler:
    @staticmethod
    def extract_keywords(request, params):
        """Extract keywords from research idea text"""
        try:
            if not keyword_extractor:
                return {"detail": "Keyword extractor not initialized", "keywords": []}

            idea_text = params.get("text", "")
            if not idea_text:
                return {"detail": "No text provided", "keywords": []}

            # Extract keywords using MMR (diverse and relevant)
            keywords = keyword_extractor.extract_keywords(
                idea_text,
                keyphrase_ngram_range=(1, 4),
                stop_words='english',
                use_mmr=True,
                diversity=0.7,
                nr_candidates=100,
                top_n=7
            )

            # Filter: keep those with score ≥ threshold
            keywords = [(phrase, score) for phrase, score in keywords if score >= 0.7]
            
            logger.info(f"Extracted {len(keywords)} keywords from text")
            return {"keywords": [kw[0] for kw in keywords]}
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return {"detail": f"Keyword extraction failed: {str(e)}", "keywords": []}

    @staticmethod
    def expand_mesh_terms(request, params):
        """Expand a term with MeSH vocabulary"""
        try:
            term = params.get("term", "")
            if not term:
                return []

            expanded = expand_with_mesh(term)
            logger.info(f"Expanded term '{term}' to {len(expanded)} MeSH terms")
            return expanded
            
        except Exception as e:
            logger.error(f"MeSH expansion failed: {e}")
            return []
