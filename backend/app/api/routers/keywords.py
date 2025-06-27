from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

# Import MeSH expansion functionality from src
import sys
import os
from pathlib import Path

# Add the src directory to sys.path
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

try:
    from mesh_expander import expand_with_mesh
except ImportError:
    # Fallback implementation if import fails
    def expand_with_mesh(term: str) -> List[str]:
        return [term]

router = APIRouter(prefix="/keywords", tags=["keywords"])

class KeywordRequest(BaseModel):
    text: str

class KeywordResponse(BaseModel):
    keywords: List[str]

@router.post("/extract", response_model=KeywordResponse)
async def extract_keywords(request: KeywordRequest):
    """Extract keywords from research idea text"""
    try:
        # Placeholder implementation
        # In a real implementation, you would use KeyBERT
        keywords = request.text.split()[:5]  # Just split the text and take first 5 words as an example
        return KeywordResponse(keywords=keywords)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Keyword extraction failed: {str(e)}")

@router.post("/expand", response_model=List[str])
async def expand_mesh_terms(term: str):
    """Expand a term with MeSH vocabulary"""
    try:
        expanded = expand_with_mesh(term)
        return expanded
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MeSH expansion failed: {str(e)}")
