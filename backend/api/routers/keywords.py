from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.keyword_service import KeywordService
from app.core.ml import get_keyword_extractor

router = APIRouter(prefix="/keywords", tags=["keywords"])

class KeywordRequest(BaseModel):
    text: str

class KeywordResponse(BaseModel):
    keywords: list[str]

@router.post("/extract", response_model=KeywordResponse)
async def extract_keywords(
    request: KeywordRequest, 
    keyword_service: KeywordService = Depends(lambda: KeywordService(get_keyword_extractor()))
):
    """Extract keywords from research idea text"""
    try:
        keywords = keyword_service.extract_keywords(request.text)
        return KeywordResponse(keywords=keywords)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Keyword extraction failed: {str(e)}")

@router.post("/expand", response_model=list[str])
async def expand_mesh_terms(term: str):
    """Expand a term with MeSH vocabulary"""
    from app.services.mesh_service import expand_with_mesh
    try:
        expanded = expand_with_mesh(term)
        return expanded
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MeSH expansion failed: {str(e)}")