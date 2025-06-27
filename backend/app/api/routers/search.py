from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import traceback

from app.db.database import get_db
from app.services.mesh_service import expand_with_mesh
from app.services.pubmed_service import search_pubmed, fetch_summaries
from app.core.ml import compute_embedding

router = APIRouter(prefix="/search", tags=["search"])

class SearchRequest(BaseModel):
    keywords: str = Field(
        ..., 
        description="Semicolon-separated keywords for PubMed search",
        example="machine learning; cancer diagnosis; medical imaging"
    )
    idea_text: str = Field(
        ..., 
        description="Original research idea that generated the keywords",
        example="machine learning applications in cancer diagnosis and treatment"
    )
    max_results: int = Field(
        default=10, 
        ge=1, 
        le=1000, 
        description="Maximum number of articles to retrieve from PubMed"
    )
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class SearchResponse(BaseModel):
    search_id: int
    articles_found: int
    articles_added: int
    message: str

@router.post("/pubmed", response_model=SearchResponse)
async def search_pubmed_articles(
    request: SearchRequest,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Search PubMed and store articles in the database"""
    try:
        # Parse keywords
        keyword_list = [kw.strip() for kw in request.keywords.split(";") if kw.strip()]
        query_groups = []
        
        for kw in keyword_list:
            expanded = expand_with_mesh(kw)
            if expanded:
                group = "(" + " OR ".join([term.replace("'", "''") for term in expanded]) + ")"
                query_groups.append(group)
        
        query = " AND ".join(query_groups)
        
        if not query:
            raise HTTPException(status_code=400, detail="No valid search terms provided")
        
        # Search PubMed
        pmids = search_pubmed(
            query, 
            request.max_results, 
            start_date=request.start_date, 
            end_date=request.end_date
        )
        
        count_found = len(pmids) if pmids else 0
        
        if count_found == 0:
            return SearchResponse(
                search_id=0,
                articles_found=0,
                articles_added=0,
                message="No articles found"
            )
        
        # Insert search metadata
        search_id = None
        try:
            with db.get_cursor() as cur:
                cur.execute(
                    "INSERT INTO searches (idea_text, keyword_text, max_results, timestamp) VALUES (%s, %s, %s, %s) RETURNING search_id",
                    (request.idea_text, request.keywords, request.max_results, datetime.now())
                )
                result = cur.fetchone()
                if result:
                    # Handle both tuple and dictionary access
                    search_id = result[0] if isinstance(result, tuple) else result["search_id"]
        except Exception as e:
            print(f"Database error inserting search: {e}")
            traceback.print_exc()
            # Return with error but still provide the search results
            return SearchResponse(
                search_id=0,
                articles_found=count_found,
                articles_added=0,
                message=f"Found {count_found} articles but couldn't save to database: {str(e)}"
            )
        
        if not search_id:
            return SearchResponse(
                search_id=0,
                articles_found=count_found,
                articles_added=0,
                message=f"Found {count_found} articles but couldn't store search metadata"
            )
        
        # Fetch and store articles
        articles = fetch_summaries(pmids)
        count_added = 0
        
        for article in articles:
            try:
                with db.get_cursor() as cur:
                    # Check if article exists
                    cur.execute("SELECT id FROM articles WHERE pmid = %s", (article["PMID"],))
                    existing = cur.fetchone()
                    
                    article_id = None
                    
                    if not existing:
                        # Parse pub_date from various formats
                        pub_date = None
                        try:
                            from dateutil import parser
                            pub_date = parser.parse(article["PubDate"]).strftime("%Y-%m-%d") if article["PubDate"] else None
                        except:
                            try:
                                pub_date = datetime.strptime(article["PubDate"], "%Y %b %d").strftime("%Y-%m-%d") if article["PubDate"] else None
                            except:
                                try:
                                    pub_date = datetime.strptime(article["PubDate"], "%Y %b").strftime("%Y-%m-%d") if article["PubDate"] else None
                                except:
                                    try:
                                        pub_date = datetime.strptime(article["PubDate"], "%Y").strftime("%Y-%m-%d") if article["PubDate"] else None
                                    except:
                                        pub_date = None
                        
                        # Insert article
                        cur.execute(
                            """
                            INSERT INTO articles (pmid, title, abstract, doi, journal, pub_date)
                            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                            """,
                            (
                                article["PMID"],
                                article["Title"],
                                article["Abstract"],
                                article["DOI"],
                                article["Journal"],
                                pub_date
                            )
                        )
                        article_id = cur.fetchone()["id"]
                        
                        # Insert citation information
                        cur.execute(
                            """
                            INSERT INTO citations (article_id, source, count, last_update)
                            VALUES (%s, %s, %s, %s)
                            """,
                            (article_id, "CrossRef", article["CitationCount"], datetime.now())
                        )
                        
                        # Insert citation history
                        for year, count in article["CitationHistory"].items():
                            cur.execute(
                                """
                                INSERT INTO citations_per_year (article_id, year, citation_count)
                                VALUES (%s, %s, %s)
                                """,
                                (article_id, year, count)
                            )
                        
                        # Compute semantic vector for title + abstract
                        text = (article["Title"] or "") + " " + (article["Abstract"] or "")
                        vector = compute_embedding(text)
                        
                        # Insert vector into database
                        cur.execute(
                            """
                            INSERT INTO article_vectors (article_id, vector)
                            VALUES (%s, %s)
                            """,
                            (article_id, vector.tolist())
                        )
                        
                        count_added += 1
                    else:
                        # Use existing article ID
                        article_id = existing["id"]
                    
                    # Link to search
                    if article_id and search_id:
                        cur.execute(
                            """
                            INSERT INTO search_articles (search_id, article_id)
                            VALUES (%s, %s) ON CONFLICT DO NOTHING
                            """,
                            (search_id, article_id)
                        )
            except Exception as e:
                print(f"Error processing article {article['PMID']}: {e}")
                traceback.print_exc()
                # Continue with next article
        
        # Add background tasks for analysis (only if we have a valid search ID)
        if search_id > 0:
            try:
                background_tasks.add_task(run_background_analysis, db, search_id, request.keywords)
            except Exception as e:
                print(f"Error scheduling background task: {e}")
        
        return SearchResponse(
            search_id=search_id if search_id else 0,
            articles_found=count_found,
            articles_added=count_added,
            message=f"Found {count_found} articles, added {count_added} new articles"
        )
        
    except Exception as e:
        print(f"Search error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/")
async def get_searches(db = Depends(get_db)):
    """Get all searches"""
    try:
        with db.get_cursor() as cur:
            cur.execute("SELECT * FROM searches ORDER BY timestamp DESC")
            searches = cur.fetchall()
            
        return searches
    except Exception as e:
        print(f"Failed to fetch searches: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch searches: {str(e)}")

@router.get("/{search_id}")
async def get_search(search_id: int, db = Depends(get_db)):
    """Get search details"""
    try:
        with db.get_cursor() as cur:
            cur.execute("SELECT * FROM searches WHERE search_id = %s", (search_id,))
            search = cur.fetchone()
            
        if not search:
            raise HTTPException(status_code=404, detail="Search not found")
            
        return search
    except HTTPException:
        raise
    except Exception as e:
        print(f"Failed to fetch search: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch search: {str(e)}")

async def run_background_analysis(db, search_id: int, keywords: str):
    """Run background tasks for clustering, forecasting and scoring"""
    try:
        # Get keyword embedding
        keyword_embedding = None
        try:
            keyword_embedding = compute_embedding(keywords)
        except Exception as e:
            print(f"Error computing keyword embedding: {e}")
        
        # These are imported locally to avoid circular imports
        try:
            from src.clustering import run_clustering_pipeline
            if keyword_embedding is not None:
                run_clustering_pipeline(keyword_embedding=keyword_embedding)
        except Exception as e:
            print(f"Error running clustering: {e}")
        
        try:
            from src.forecast import run_forecast_pipeline
            run_forecast_pipeline(search_id)
        except Exception as e:
            print(f"Error running forecasting: {e}")
        
        # Note: opportunity scores would typically be computed here too
        try:
            from app.services.scoring_service import ScoringService
            scoring_service = ScoringService(db)
            scoring_service.compute_scores_for_search(search_id)
        except Exception as e:
            print(f"Error computing opportunity scores: {e}")
        
    except Exception as e:
        print(f"Background analysis error: {e}")
