#!/usr/bin/env python
import sys
import os
import asyncio
import threading
from datetime import datetime
from typing import List, Optional, Dict, Any
import torch
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import uvicorn

from db_manager import DatabaseManager
from pubmed_fetcher import search_pubmed, fetch_summaries
from mesh_expander import expand_with_mesh
from opportunity_score import compute_novelty_score, compute_citation_velocity_score, compute_recency_score, compute_opportunity_score
from transformers import AutoModel, AutoTokenizer
from keybert import KeyBERT
from sklearn.metrics.pairwise import cosine_similarity
from clustering import run_clustering_pipeline
from forecast import run_forecast_pipeline

# Load environment variables
ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)
DB_HOST = os.getenv("DATABASE_HOST")
DB_PORT = os.getenv("DATABASE_PORT")
DB_NAME = os.getenv("DATABASE_NAME")
DB_USER = os.getenv("DATABASE_USERNAME")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD")

# Pydantic models for API requests/responses
class ResearchIdeaRequest(BaseModel):
    idea: str = Field(
        ..., 
        description="Research idea text",
        example="machine learning applications in cancer diagnosis and treatment",
        min_length=10,
        max_length=1000
    )

class KeywordGenerationResponse(BaseModel):
    keywords: List[str] = Field(
        ..., 
        description="Generated keywords from the research idea",
        example=["machine learning", "cancer diagnosis", "medical imaging", "artificial intelligence", "oncology"]
    )
    scores: List[float] = Field(
        ..., 
        description="Relevance scores for each keyword (0.0 to 1.0)",
        example=[0.95, 0.92, 0.88, 0.85, 0.82]
    )

class SearchRequest(BaseModel):
    keywords: str = Field(
        ..., 
        description="Semicolon-separated keywords for PubMed search",
        example="machine learning; cancer diagnosis; medical imaging",
        min_length=3
    )
    idea_text: str = Field(
        ..., 
        description="Original research idea that generated the keywords",
        example="machine learning applications in cancer diagnosis and treatment",
        min_length=10
    )
    max_results: int = Field(
        default=10, 
        ge=1, 
        le=1000, 
        description="Maximum number of articles to retrieve from PubMed",
        example=20
    )
    start_date: Optional[str] = Field(
        None, 
        description="Start date for search filter (YYYY-MM-DD format)",
        example="2020-01-01"
    )
    end_date: Optional[str] = Field(
        None, 
        description="End date for search filter (YYYY-MM-DD format)",
        example="2024-01-01"
    )

class SearchResponse(BaseModel):
    search_id: int = Field(
        ..., 
        description="Unique identifier for this search",
        example=123
    )
    articles_found: int = Field(
        ..., 
        description="Total number of articles found in PubMed",
        example=45
    )
    articles_added: int = Field(
        ..., 
        description="Number of new articles added to the database",
        example=15
    )
    message: str = Field(
        ..., 
        description="Status message describing the search results",
        example="Found 45 articles, added 15 new articles"
    )

class ArticleResponse(BaseModel):
    pmid: str = Field(
        ..., 
        description="PubMed ID (unique identifier)",
        example="12345678"
    )
    title: str = Field(
        ..., 
        description="Article title",
        example="Machine Learning in Cancer Diagnosis: A Systematic Review"
    )
    journal: Optional[str] = Field(
        None, 
        description="Journal name",
        example="Nature Medicine"
    )
    pub_date: Optional[str] = Field(
        None, 
        description="Publication date (YYYY-MM-DD format)",
        example="2023-06-15"
    )
    authors: List[str] = Field(
        default_factory=list, 
        description="List of author names",
        example=["Smith, John", "Doe, Jane", "Johnson, Bob"]
    )
    citation_count: Optional[int] = Field(
        None, 
        description="Number of citations",
        example=150
    )
    doi: Optional[str] = Field(
        None, 
        description="Digital Object Identifier",
        example="10.1038/s41591-023-02345-6"
    )
    abstract: Optional[str] = Field(
        None, 
        description="Article abstract",
        example="This study presents a comprehensive review of machine learning applications..."
    )

class ArticleDetailResponse(BaseModel):
    pmid: str = Field(
        ..., 
        description="PubMed ID (unique identifier)",
        example="12345678"
    )
    title: str = Field(
        ..., 
        description="Article title",
        example="Machine Learning in Cancer Diagnosis: A Systematic Review"
    )
    journal: Optional[str] = Field(
        None, 
        description="Journal name",
        example="Nature Medicine"
    )
    pub_date: Optional[str] = Field(
        None, 
        description="Publication date (YYYY-MM-DD format)",
        example="2023-06-15"
    )
    authors: List[str] = Field(
        default_factory=list, 
        description="List of author names",
        example=["Smith, John", "Doe, Jane", "Johnson, Bob"]
    )
    citation_count: Optional[int] = Field(
        None, 
        description="Number of citations",
        example=150
    )
    doi: Optional[str] = Field(
        None, 
        description="Digital Object Identifier",
        example="10.1038/s41591-023-02345-6"
    )
    abstract: Optional[str] = Field(
        None, 
        description="Article abstract",
        example="This study presents a comprehensive review of machine learning applications in cancer diagnosis. The research demonstrates significant improvements in diagnostic accuracy when using deep learning algorithms compared to traditional methods..."
    )

class OpportunityScoreResponse(BaseModel):
    search_id: int = Field(
        ..., 
        description="Search ID that these scores belong to",
        example=123
    )
    novelty_score: float = Field(
        ..., 
        description="Novelty score (0.0 to 1.0) - measures how unique the research topic is",
        example=0.75,
        ge=0.0,
        le=1.0
    )
    citation_score: float = Field(
        ..., 
        description="Citation velocity score (0.0 to 1.0) - measures citation growth rate",
        example=0.82,
        ge=0.0,
        le=1.0
    )
    recency_score: float = Field(
        ..., 
        description="Recency score (0.0 to 1.0) - measures how recent the research is",
        example=0.68,
        ge=0.0,
        le=1.0
    )
    overall_score: float = Field(
        ..., 
        description="Overall opportunity score (0.0 to 1.0) - combined metric",
        example=0.75,
        ge=0.0,
        le=1.0
    )
    recommendation: str = Field(
        ..., 
        description="Text recommendation based on the scores",
        example="High opportunity score indicates this is a promising research area with good citation velocity and novelty"
    )

class DatabaseConfig(BaseModel):
    host: str = Field(
        default=DB_HOST, 
        description="Database host address",
        example="localhost"
    )
    port: str = Field(
        default=DB_PORT, 
        description="Database port number",
        example="5432"
    )
    database: str = Field(
        default=DB_NAME, 
        description="Database name",
        example="prime_time_db"
    )
    username: str = Field(
        default=DB_USER, 
        description="Database username",
        example="postgres"
    )
    password: str = Field(
        default=DB_PASSWORD, 
        description="Database password",
        example="your_password"
    )

class DatabaseStatusResponse(BaseModel):
    connected: bool = Field(
        ..., 
        description="Whether the database connection is active",
        example=True
    )
    message: str = Field(
        ..., 
        description="Status message describing the connection state",
        example="Connected to database prime_time_db"
    )

# Initialize FastAPI app
app = FastAPI(
    title="Prime Time Medical Research Opportunities API",
    version="1.0.0",
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    tags=[
        {
            "name": "keywords",
            "description": "Keyword generation from research ideas using BERT models"
        },
        {
            "name": "search",
            "description": "PubMed search and article management"
        },
        {
            "name": "articles",
            "description": "Article retrieval and details"
        },
        {
            "name": "analysis",
            "description": "Opportunity scoring and research analysis"
        },
        {
            "name": "database",
            "description": "Database connection and management"
        },
        {
            "name": "export",
            "description": "Data export functionality"
        }
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for ML models
keyword_extractor = None
bert_model = None
bert_tokenizer = None
db_manager = None

def initialize_models():
    """Initialize ML models globally"""
    global keyword_extractor, bert_model, bert_tokenizer
    
    if keyword_extractor is None:
        print("Loading PubMedBERT model...")
        pubmedbert_model = AutoModel.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")
        pubmedbert_tokenizer = AutoTokenizer.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")
        keyword_extractor = KeyBERT(model=pubmedbert_model)
        bert_model = pubmedbert_model
        bert_tokenizer = pubmedbert_tokenizer
        print("Models loaded successfully!")

def initialize_database():
    """Initialize database connection"""
    global db_manager
    
    if db_manager is None:
        db_manager = DatabaseManager(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        
        if not db_manager.connect():
            raise HTTPException(status_code=500, detail="Failed to connect to database")

def compute_embedding(text: str) -> np.ndarray:
    """Compute BERT embedding for text"""
    if bert_model is None or bert_tokenizer is None:
        initialize_models()
    
    bert_model.eval()
    with torch.no_grad():
        tokens = bert_tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )
        emb = bert_model(**tokens).last_hidden_state.mean(dim=1).squeeze()
    return emb.numpy()

@app.on_event("startup")
async def startup_event():
    """Initialize models and database on startup"""
    try:
        initialize_models()
        initialize_database()
        print("API startup completed successfully!")
    except Exception as e:
        print(f"Error during startup: {e}")
        raise

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {"message": "Prime Time Medical Research Opportunities API", "version": "1.0.0"}

@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/database/status", response_model=DatabaseStatusResponse, tags=["database"])
async def get_database_status():
    """Check database connection status"""
    try:
        initialize_database()
        if db_manager and db_manager.connected:
            return DatabaseStatusResponse(
                connected=True,
                message=f"Connected to database {DB_NAME}"
            )
        else:
            return DatabaseStatusResponse(
                connected=False,
                message="Not connected to database"
            )
    except Exception as e:
        return DatabaseStatusResponse(
            connected=False,
            message=f"Database connection error: {str(e)}"
        )

@app.post("/database/connect", response_model=DatabaseStatusResponse, tags=["database"])
async def connect_database(config: DatabaseConfig):
    """Connect to database with custom configuration"""
    global db_manager
    
    try:
        # Close existing connection if any
        if db_manager:
            db_manager.close()
        
        # Create new connection
        db_manager = DatabaseManager(
            dbname=config.database,
            user=config.username,
            password=config.password,
            host=config.host,
            port=config.port
        )
        
        if db_manager.connect():
            return DatabaseStatusResponse(
                connected=True,
                message=f"Connected to database {config.database}"
            )
        else:
            return DatabaseStatusResponse(
                connected=False,
                message="Failed to connect to database"
            )
    except Exception as e:
        return DatabaseStatusResponse(
            connected=False,
            message=f"Connection error: {str(e)}"
        )

@app.post("/database/initialize", tags=["database"])
async def initialize_database_schema():
    """Initialize database schema"""
    try:
        initialize_database()
        result = db_manager.initialize_database()
        if result:
            return {
                "success": True,
                "message": "Database initialized successfully",
                "details": "All tables created or already exist"
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail="Failed to initialize database. Check server logs for details."
            )
    except Exception as e:
        # Check if it's a "relation already exists" error
        if "already exists" in str(e).lower():
            return {
                "success": True,
                "message": "Database already initialized",
                "details": "All required tables already exist in the database"
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Database initialization error: {str(e)}"
            )

@app.post("/keywords/generate", response_model=KeywordGenerationResponse, tags=["keywords"])
async def generate_keywords(request: ResearchIdeaRequest):
    """
    Generate relevant keywords from a research idea using BERT-based keyword extraction.
    
    This endpoint uses the PubMedBERT model to extract the most relevant keywords from your research idea.
    The keywords are generated using MMR (Maximal Marginal Relevance) to ensure diversity and relevance.
    
    **Process:**
    1. Analyzes the research idea using PubMedBERT embeddings
    2. Extracts candidate keywords using KeyBERT
    3. Applies MMR algorithm for diversity (diversity=0.7)
    4. Filters keywords with relevance score ≥ 0.7
    5. Returns top 7 most relevant keywords
    
    **Example Usage:**
    ```json
    {
        "idea": "machine learning applications in cancer diagnosis and treatment"
    }
    ```
    
    **Response:**
    ```json
    {
        "keywords": ["machine learning", "cancer diagnosis", "medical imaging", "artificial intelligence", "oncology"],
        "scores": [0.95, 0.92, 0.88, 0.85, 0.82]
    }
    ```
    """
    try:
        if not request.idea.strip():
            raise HTTPException(status_code=400, detail="Research idea cannot be empty")
        
        initialize_models()
        
        # Extract keywords using MMR (diverse and relevant)
        keywords = keyword_extractor.extract_keywords(
            request.idea,
            keyphrase_ngram_range=(1, 4),
            stop_words='english',
            use_mmr=True,
            diversity=0.7,
            nr_candidates=100,
            top_n=7
        )
        
        # Filter: keep those with score >= threshold
        filtered_keywords = [(phrase, score) for phrase, score in keywords if score >= 0.7]
        
        return KeywordGenerationResponse(
            keywords=[kw[0] for kw in filtered_keywords],
            scores=[kw[1] for kw in filtered_keywords]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Keyword generation failed: {str(e)}")

@app.post("/search/pubmed", response_model=SearchResponse, tags=["search"])
async def search_pubmed_articles(request: SearchRequest, background_tasks: BackgroundTasks):
    """
    Search PubMed and store articles in the database.
    
    This endpoint performs a comprehensive PubMed search using the provided keywords, with automatic
    MeSH term expansion for better search coverage. Articles are stored in the database and linked
    to the search for future analysis.
    
    **Process:**
    1. Expands keywords using MeSH (Medical Subject Headings) terms
    2. Constructs PubMed query with expanded terms
    3. Searches PubMed for articles within date range (if specified)
    4. Fetches detailed article information (title, abstract, authors, etc.)
    5. Stores articles in database with semantic vectors
    6. Runs background analysis (clustering, forecasting, opportunity scoring)
    
    **Keyword Format:**
    - Use semicolons to separate multiple keywords
    - Example: "machine learning; cancer diagnosis; medical imaging"
    
    **Date Format:**
    - Use YYYY-MM-DD format (e.g., "2020-01-01")
    - Both start_date and end_date are optional
    
    **Example Request:**
    ```json
    {
        "keywords": "machine learning; cancer diagnosis; medical imaging",
        "idea_text": "machine learning applications in cancer diagnosis and treatment",
        "max_results": 20,
        "start_date": "2020-01-01",
        "end_date": "2024-01-01"
    }
    ```
    
    **Response:**
    ```json
    {
        "search_id": 123,
        "articles_found": 45,
        "articles_added": 15,
        "message": "Found 45 articles, added 15 new articles"
    }
    ```
    
    **Background Processing:**
    After the search completes, the following analysis runs in the background:
    - **Clustering**: Groups similar articles using HDBSCAN
    - **Forecasting**: Predicts citation growth trends
    - **Opportunity Scoring**: Computes novelty, citation velocity, and recency scores
    """
    try:
        initialize_database()
        
        # Parse keywords
        keyword_list = [kw.strip() for kw in request.keywords.split(";") if kw.strip()]
        query_groups = []
        
        for kw in keyword_list:
            expanded = expand_with_mesh(kw)
            if expanded:
                group = "(" + " OR ".join(expanded) + ")"
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
        search_id = db_manager.insert_search(
            idea_text=request.idea_text,
            keyword_text=request.keywords,
            max_results=request.max_results
        )
        
        if not search_id:
            raise HTTPException(status_code=500, detail="Failed to insert search metadata")
        
        # Fetch and store articles
        articles = fetch_summaries(pmids)
        count_added = 0
        
        for article in articles:
            if not db_manager.article_exists(article["PMID"]):
                article_id = db_manager.insert_article(article)
                if article_id:
                    db_manager.link_article_to_search(article_id, search_id)
                    
                    # Compute semantic vector for title + abstract
                    text = (article["Title"] or "") + " " + (article["Abstract"] or "")
                    vector = compute_embedding(text)
                    
                    # Insert vector into database
                    db_manager.insert_article_vector(article_id, vector.tolist())
                    
                    count_added += 1
        
        # Add background tasks for clustering, forecasting, and scoring
        background_tasks.add_task(run_background_analysis, search_id, request.keywords)
        
        return SearchResponse(
            search_id=search_id,
            articles_found=count_found,
            articles_added=count_added,
            message=f"Found {count_found} articles, added {count_added} new articles"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

async def run_background_analysis(search_id: int, keywords: str):
    """Run clustering, forecasting, and scoring in background"""
    try:
        # Compute clustering and visualization
        keyword_vector = compute_embedding(keywords)
        run_clustering_pipeline(keyword_embedding=keyword_vector)
        run_forecast_pipeline(search_id)
        
        # Compute opportunity scores
        await compute_opportunity_scores_async(search_id, keywords)
        
    except Exception as e:
        print(f"Background analysis error: {e}")

async def compute_opportunity_scores_async(search_id: int, keywords: str):
    """Compute opportunity scores asynchronously"""
    try:
        # Fetch article metadata for this search
        articles = db_manager.get_articles_by_search(search_id)
        valid_articles = [a for a in articles if a.get("citation_count") is not None and a.get("citation_count") >= 0]
        
        if len(valid_articles) == 0:
            return
        
        # Compute embeddings
        keywords_vec = compute_embedding(keywords)
        article_vecs = [compute_embedding(a["title"] + " " + (a["abstract"] or "")) for a in valid_articles]
        
        similarities = cosine_similarity([keywords_vec], article_vecs)[0]
        avg_sim = float(np.mean(similarities))
        
        # Build raw scores from history
        history = db_manager.get_all_search_history()
        novelty_raws = []
        citation_raws = []
        recency_raws = []
        
        for h in history:
            if h["search_id"] == search_id:
                continue
            novelty_raws.append(h["novelty_raw"])
            citation_raws.append(h["citation_raw"])
            recency_raws.append(h["recency_raw"])
        
        num_articles = len(valid_articles)
        pub_dates = [a["pub_date"] for a in valid_articles]
        citation_counts = [a["citation_count"] for a in valid_articles]
        
        novelty = compute_novelty_score(avg_sim, num_articles, novelty_raws)
        citation = compute_citation_velocity_score(citation_counts, pub_dates, citation_raws)
        recency = compute_recency_score(pub_dates, recency_raws)
        score = compute_opportunity_score(novelty, citation, recency)
        
        db_manager.insert_opportunity_score(search_id, novelty, citation, recency, score)
        
    except Exception as e:
        print(f"Error computing opportunity score: {e}")

@app.get("/articles", response_model=List[ArticleResponse], tags=["articles"])
async def get_articles():
    """Get all articles from database"""
    try:
        initialize_database()
        articles = db_manager.get_all_articles()
        
        response_articles = []
        for article in articles:
            authors = ", ".join(article["authors"]) if article["authors"] and article["authors"][0] else ""
            pub_date = article["pub_date"].strftime("%Y-%m-%d") if article["pub_date"] else None
            
            response_articles.append(ArticleResponse(
                pmid=article["pmid"],
                title=article["title"],
                journal=article["journal"],
                pub_date=pub_date,
                authors=authors.split(", ") if authors else [],
                citation_count=article["citation_count"],
                doi=article["doi"],
                abstract=article["abstract"]
            ))
        
        return response_articles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch articles: {str(e)}")

@app.get("/articles/{pmid}", response_model=ArticleDetailResponse, tags=["articles"])
async def get_article_detail(pmid: str):
    """Get detailed information about a specific article"""
    try:
        initialize_database()
        article = db_manager.get_article_by_pmid(pmid)
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        authors = ", ".join(article["authors"]) if article["authors"] and article["authors"][0] else ""
        pub_date = article["pub_date"].strftime("%Y-%m-%d") if article["pub_date"] else None
        
        return ArticleDetailResponse(
            pmid=article["pmid"],
            title=article["title"],
            journal=article["journal"],
            pub_date=pub_date,
            authors=authors.split(", ") if authors else [],
            citation_count=article["citation_count"],
            doi=article["doi"],
            abstract=article["abstract"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch article: {str(e)}")

@app.get("/search/{search_id}/scores", response_model=OpportunityScoreResponse, tags=["analysis"])
async def get_opportunity_scores(search_id: int):
    """Get opportunity scores for a specific search"""
    try:
        initialize_database()
        
        # Get the latest opportunity score for this search
        scores = db_manager.get_opportunity_scores_by_search(search_id)
        
        if not scores:
            raise HTTPException(status_code=404, detail="No opportunity scores found for this search")
        
        # Get the most recent score
        latest_score = scores[-1]
        
        return OpportunityScoreResponse(
            search_id=search_id,
            novelty_score=latest_score["novelty_score"],
            citation_score=latest_score["citation_score"],
            recency_score=latest_score["recency_score"],
            overall_score=latest_score["overall_score"],
            recommendation="Score based on current search analysis"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch opportunity scores: {str(e)}")

@app.get("/export/csv", tags=["export"])
async def export_articles_csv():
    """Export all articles to CSV"""
    try:
        initialize_database()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"prime_time_export_{timestamp}.csv"
        filepath = f"/tmp/{filename}"  # Use /tmp for temporary files
        
        success = db_manager.export_to_csv(filepath)
        
        if success:
            return FileResponse(
                path=filepath,
                filename=filename,
                media_type="text/csv"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to export articles to CSV")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.get("/searches", response_model=List[Dict[str, Any]], tags=["analysis"])
async def get_search_history():
    """Get search history"""
    try:
        initialize_database()
        searches = db_manager.get_all_searches()
        return searches
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch search history: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 