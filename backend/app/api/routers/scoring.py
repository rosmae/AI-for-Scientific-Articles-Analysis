from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from app.db.database import get_db
from app.services.scoring_service import ScoringService

router = APIRouter(prefix="/scoring", tags=["scoring"])

class OpportunityScoreResponse(BaseModel):
    search_id: int
    novelty_score: float = Field(..., ge=0.0, le=1.0)
    citation_score: float = Field(..., ge=0.0, le=1.0)
    recency_score: float = Field(..., ge=0.0, le=1.0)
    overall_score: float = Field(..., ge=0.0, le=1.0)
    recommendation: str

@router.get("/{search_id}", response_model=OpportunityScoreResponse)
async def get_opportunity_score(search_id: int, db = Depends(get_db)):
    """Get opportunity scores for a search"""
    try:
        # First check if the search exists
        with db.get_cursor() as cur:
            cur.execute("SELECT * FROM searches WHERE search_id = %s", (search_id,))
            search = cur.fetchone()
            
        if not search:
            raise HTTPException(status_code=404, detail="Search not found")
        
        # Get opportunity scores
        with db.get_cursor() as cur:
            cur.execute("""
                SELECT * FROM opportunity_scores 
                WHERE search_id = %s
                ORDER BY computed_at DESC
                LIMIT 1
            """, (search_id,))
            
            score = cur.fetchone()
            
        if not score:
            # If no scores are found, try to compute them
            scoring_service = ScoringService(db)
            score = scoring_service.compute_scores_for_search(search_id)
            
            if not score:
                raise HTTPException(
                    status_code=404, 
                    detail="No opportunity scores found for this search and could not compute them"
                )
        
        # Generate recommendation based on scores
        recommendation = generate_recommendation(
            score["novelty_score"],
            # Use citation_rate_score instead of citation_velocity_score to match DB schema
            score["citation_rate_score"],
            score["recency_score"],
            score["overall_score"]
        )
        
        return OpportunityScoreResponse(
            search_id=search_id,
            novelty_score=score["novelty_score"],
            # Map citation_rate_score to citation_score in response
            citation_score=score["citation_rate_score"],
            recency_score=score["recency_score"],
            overall_score=score["overall_score"],
            recommendation=recommendation
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch opportunity scores: {str(e)}")

def generate_recommendation(novelty: float, citation: float, recency: float, overall: float) -> str:
    """Generate a recommendation based on opportunity scores"""
    if overall >= 0.8:
        return "Very high opportunity - This research area shows excellent potential with high novelty and impact."
    elif overall >= 0.6:
        return "High opportunity - This research area shows good potential for impactful work."
    elif overall >= 0.4:
        return "Moderate opportunity - Consider focusing on specific aspects to increase potential."
    elif overall >= 0.2:
        return "Limited opportunity - This area may be saturated or has limited growth potential."
    else:
        return "Low opportunity - Consider pivoting to more promising research areas."
