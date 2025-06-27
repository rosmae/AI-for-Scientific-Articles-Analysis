from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

from app.core.config import settings
from app.core.ml import initialize_models
from app.db.database import get_db, Database

# Import routers
from app.api.routers import articles, keywords, scoring, search, database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("prime-time-api")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    A comprehensive API for analyzing medical research opportunities using PubMed data and machine learning.
    
    ## Key Features
    
    - Keyword Generation: Extract relevant keywords from research ideas using PubMedBERT
    - PubMed Search: Search PubMed with automatic MeSH term expansion
    - Article Management: Store and retrieve articles with full metadata
    - Opportunity Scoring: Compute novelty, citation velocity, and recency scores
    - Background Analysis: Clustering and forecasting for research trends
    """,
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search.router, prefix=settings.API_V1_STR)
app.include_router(articles.router, prefix=settings.API_V1_STR)
app.include_router(scoring.router, prefix=settings.API_V1_STR)
app.include_router(keywords.router, prefix=settings.API_V1_STR)
app.include_router(database.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Initialize models and database on startup"""
    try:
        # Initialize ML models
        initialize_models()
        logger.info("ML models initialized successfully")
        
        # Initialize database
        db = Database()
        if db.connect():
            logger.info(f"Connected to database {settings.DATABASE_NAME}")
        else:
            logger.error("Failed to connect to database")
    except Exception as e:
        logger.error(f"Error during startup: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "description": "API for analyzing scientific research opportunities in medical literature"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )