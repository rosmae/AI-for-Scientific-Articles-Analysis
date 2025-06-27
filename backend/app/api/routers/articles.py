from fastapi import APIRouter, Depends, HTTPException, Response
from typing import List, Optional
from pydantic import BaseModel
import csv
import io
from datetime import datetime
import traceback

from app.db.database import get_db

router = APIRouter(prefix="/articles", tags=["articles"])

class ArticleResponse(BaseModel):
    id: int
    pmid: str
    title: str
    journal: Optional[str] = None
    pub_date: Optional[datetime] = None
    abstract: Optional[str] = None
    doi: Optional[str] = None
    citation_count: Optional[int] = None
    authors: List[str] = []

@router.get("/", response_model=List[ArticleResponse])
async def get_articles(
    search_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    db = Depends(get_db)
):
    """Get articles, optionally filtered by search_id"""
    try:
        # Check if table exists first
        with db.get_cursor() as cur:
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'articles')")
            table_exists = cur.fetchone()
            
            if not table_exists or not table_exists.get('exists', False):
                return []  # Return empty list if table doesn't exist
            
            # Use a simple query for debugging
            if search_id:
                cur.execute("""
                    SELECT a.id, a.pmid, a.title, a.abstract, a.doi, a.journal, a.pub_date
                    FROM articles a
                    JOIN search_articles sa ON a.id = sa.article_id
                    WHERE sa.search_id = %s
                    LIMIT %s OFFSET %s
                """, (search_id, limit, offset))
            else:
                cur.execute("""
                    SELECT id, pmid, title, abstract, doi, journal, pub_date
                    FROM articles
                    LIMIT %s OFFSET %s
                """, (limit, offset))
            
            rows = cur.fetchall()
            
            # Simple transformation to response model
            articles = []
            for row in rows:
                articles.append(ArticleResponse(
                    id=row["id"],
                    pmid=row["pmid"] or "",
                    title=row["title"] or "",
                    journal=row["journal"],
                    pub_date=row["pub_date"],
                    abstract=row["abstract"],
                    doi=row["doi"],
                    citation_count=0,  # Default value for now
                    authors=[]  # Default empty authors for now
                ))
            
            return articles
    except Exception as e:
        print(f"Error fetching articles: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch articles: {str(e)}")

@router.get("/{pmid}", response_model=ArticleResponse)
async def get_article(pmid: str, db = Depends(get_db)):
    """Get article by PMID"""
    try:
        with db.get_cursor() as cur:
            cur.execute("""
                SELECT a.id, a.pmid, a.title, a.abstract, a.doi, a.journal, a.pub_date, c.count as citation_count,
                (SELECT string_agg(full_name, ';') FROM articles_authors aa JOIN authors au ON aa.author_id = au.id WHERE aa.article_id = a.id) as authors
                FROM articles a
                LEFT JOIN citations c ON a.id = c.article_id
                WHERE a.pmid = %s
            """, (pmid,))
            
            row = cur.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Article not found")
            
            authors = row["authors"].split(';') if row["authors"] else []
            return ArticleResponse(
                id=row["id"],
                pmid=row["pmid"],
                title=row["title"],
                journal=row["journal"],
                pub_date=row["pub_date"],
                abstract=row["abstract"],
                doi=row["doi"],
                citation_count=row["citation_count"],
                authors=authors
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch article: {str(e)}")

@router.get("/export/csv")
async def export_csv(db = Depends(get_db)):
    """Export articles to CSV"""
    try:
        # Create a StringIO object to store CSV data
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header row
        writer.writerow(['PMID', 'Title', 'Journal', 'Publication Date', 'Authors', 'Citations', 'DOI', 'Abstract'])
        
        # Get all articles
        with db.get_cursor() as cur:
            cur.execute("""
                SELECT a.pmid, a.title, a.abstract, a.doi, a.journal, a.pub_date, c.count as citation_count,
                (SELECT string_agg(full_name, '; ') FROM articles_authors aa JOIN authors au ON aa.authord_id = au.id WHERE aa.article_id = a.id) as authors
                FROM articles a
                LEFT JOIN citations c ON a.id = c.article_id
                ORDER BY c.count DESC NULLS LAST
            """)
            articles = cur.fetchall()
        
        # Write data rows
        for article in articles:
            writer.writerow([
                article.get("pmid", ""),
                article.get("title", ""),
                article.get("journal", ""),
                article.get("pub_date").strftime("%Y-%m-%d") if article.get("pub_date") else "",
                article.get("authors", ""),
                article.get("citation_count", 0),
                article.get("doi", ""),
                article.get("abstract", "")
            ])
        
        # Return CSV as attachment
        output.seek(0)
        content = output.getvalue()
        
        headers = {
            'Content-Disposition': 'attachment; filename="articles.csv"',
            'Content-Type': 'text/csv'
        }
        
        return Response(content=content, headers=headers)
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to export articles: {str(e)}")
