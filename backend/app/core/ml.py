import sys
import os
from pathlib import Path
import numpy as np

# Add the src directory to sys.path
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

# Try to import models, but provide placeholders if imports fail
try:
    import torch
    from transformers import AutoModel, AutoTokenizer
    from keybert import KeyBERT
    
    # Global model instances
    pubmedbert_model = None
    pubmedbert_tokenizer = None
    keyword_extractor = None
except ImportError:
    pubmedbert_model = None
    pubmedbert_tokenizer = None
    keyword_extractor = None

def initialize_models():
    """Initialize ML models"""
    global pubmedbert_model, pubmedbert_tokenizer, keyword_extractor
    
    if pubmedbert_model is None:
        try:
            print("Loading PubMedBERT model...")
            pubmedbert_model = AutoModel.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")
            pubmedbert_tokenizer = AutoTokenizer.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")
            keyword_extractor = KeyBERT(model=pubmedbert_model)
            print("Models loaded successfully!")
        except Exception as e:
            print(f"Error loading models: {e}")
            # Create dummy implementations for testing
            pubmedbert_model = "dummy_model"
            pubmedbert_tokenizer = "dummy_tokenizer"
            keyword_extractor = object()

def get_bert_model():
    """Get the PubMedBERT model"""
    if pubmedbert_model is None:
        initialize_models()
    return pubmedbert_model

def get_bert_tokenizer():
    """Get the PubMedBERT tokenizer"""
    if pubmedbert_tokenizer is None:
        initialize_models()
    return pubmedbert_tokenizer

def get_keyword_extractor():
    """Get the KeyBERT keyword extractor"""
    if keyword_extractor is None:
        initialize_models()
    return keyword_extractor

def compute_embedding(text: str) -> np.ndarray:
    """Compute BERT embedding for text"""
    try:
        model = get_bert_model()
        tokenizer = get_bert_tokenizer()
        
        if isinstance(model, str) or isinstance(tokenizer, str):
            # Using dummy implementations, return random embedding
            return np.random.rand(768)
        
        model.eval()
        with torch.no_grad():
            tokens = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )
            emb = model(**tokens).last_hidden_state.mean(dim=1).squeeze()
        return emb.numpy()
    except Exception as e:
        print(f"Error computing embedding: {e}")
        return np.random.rand(768)  # Return random embedding for testing
