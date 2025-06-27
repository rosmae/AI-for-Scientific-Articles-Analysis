import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path
from fastapi import Depends
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.core.config import settings

# Add the src directory to sys.path
src_path = Path(__file__).parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

# Try to import the database manager from src, or create a dummy implementation
try:
    from db_manager import DatabaseManager as SourceDatabaseManager
    
    class Database:
        def __init__(self):
            self.conn = None
            self.connected = False
            self.db_manager = None
        
        def connect(self):
            """Connect to the PostgreSQL database"""
            try:
                from app.core.config import settings
                
                self.db_manager = SourceDatabaseManager(
                    dbname=settings.DATABASE_NAME,
                    user=settings.DATABASE_USERNAME,
                    password=settings.DATABASE_PASSWORD,
                    host=settings.DATABASE_HOST,
                    port=settings.DATABASE_PORT
                )
                
                self.connected = self.db_manager.connect()
                return self.connected
            except Exception as e:
                print(f"Database connection error: {e}")
                self.connected = False
                return False
        
        def initialize_database(self):
            """Initialize database schema"""
            if not self.connected and not self.connect():
                return False
            
            return self.db_manager.initialize_database()
        
        def close(self):
            """Close the database connection"""
            if self.db_manager:
                self.db_manager.close()
                self.connected = False
        
        def get_cursor(self):
            """Get a database cursor"""
            if not self.connected and not self.connect():
                raise Exception("Not connected to database")
            return self.db_manager.conn.cursor()
except ImportError:
    class Database:
        def __init__(self):
            self.conn = None
            self.connected = False
        
        def connect(self):
            """Connect to the PostgreSQL database"""
            print("Using dummy database connection")
            self.connected = True
            return True
        
        def initialize_database(self):
            """Initialize database schema"""
            print("Using dummy database initialization")
            return True
        
        def close(self):
            """Close the database connection"""
            self.connected = False
        
        def get_cursor(self):
            """Get a database cursor"""
            class DummyCursor:
                def execute(self, *args, **kwargs):
                    pass
                
                def fetchone(self):
                    return {"id": 1, "name": "dummy"}
                
                def fetchall(self):
                    return [{"id": 1, "name": "dummy"}]
                
                def __enter__(self):
                    return self
                
                def __exit__(self, exc_type, exc_val, exc_tb):
                    pass
            
            return DummyCursor()

    # Dummy implementation for testing
    class Database:
        def __init__(self):
            self.conn = None
            self.connected = False
        
        def connect(self):
            """Connect to the PostgreSQL database"""
            print("Using dummy database connection")
            self.connected = True
            return True
        
        def initialize_database(self):
            """Initialize database schema"""
            print("Using dummy database initialization")
            return True
        
        def close(self):
            """Close the database connection"""
            self.connected = False
        
        def get_cursor(self):
            """Get a database cursor"""
            class DummyCursor:
                def execute(self, *args, **kwargs):
                    pass
                
                def fetchone(self):
                    return {"id": 1, "name": "dummy"}
                
                def fetchall(self):
                    return [{"id": 1, "name": "dummy"}]
                
                def __enter__(self):
                    return self
                
                def __exit__(self, exc_type, exc_val, exc_tb):
                    pass
            
            return DummyCursor()

# Database instance
db = Database()

def get_db():
    """Dependency for FastAPI endpoints to get database connection"""
    if not db.connected:
        db.connect()
    return db

def get_value(row, key, index=0):
    """Get value from a row that could be either a dict or tuple"""
    if isinstance(row, dict):
        return row.get(key)
    elif isinstance(row, tuple):
        return row[index] if len(row) > index else None
    return None

class Database:
    def __init__(self):
        self.conn = None
        self.connected = False
    
    def connect(self):
        """Connect to the PostgreSQL database"""
        try:
            # Close existing connection if in a failed state
            if self.conn:
                try:
                    # Check if connection is in a failed transaction
                    with self.conn.cursor() as cur:
                        cur.execute("SELECT 1")
                except psycopg2.errors.InFailedSqlTransaction:
                    # If in a failed transaction, rollback and close
                    self.conn.rollback()
                    self.conn.close()
                    self.conn = None
                except Exception:
                    # Other errors, close connection
                    try:
                        self.conn.close()
                    except:
                        pass
                    self.conn = None
            
            # Create a new connection if needed
            if not self.conn:
                self.conn = psycopg2.connect(
                    dbname=settings.DATABASE_NAME,
                    user=settings.DATABASE_USERNAME,
                    password=settings.DATABASE_PASSWORD,
                    host=settings.DATABASE_HOST,
                    port=int(settings.DATABASE_PORT)
                )
            
            self.conn.autocommit = False  # We'll handle transactions explicitly
            self.connected = True
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            self.connected = False
            return False
    
    def get_cursor(self, dict_cursor=True):
        """Get a database cursor with transaction handling
        
        Args:
            dict_cursor: If True, use RealDictCursor which returns dict results
                         If False, use standard cursor which returns tuple results
        """
        if not self.connected and not self.connect():
            raise Exception("Not connected to database")
        
        class ManagedCursor:
            def __init__(self, conn, use_dict_cursor):
                self.conn = conn
                self.cursor = None
                self.use_dict_cursor = use_dict_cursor
            
            def __enter__(self):
                if self.use_dict_cursor:
                    self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
                else:
                    self.cursor = self.conn.cursor()
                return self.cursor
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    # An exception occurred - rollback
                    try:
                        self.conn.rollback()
                    except Exception as e:
                        print(f"Error during rollback: {e}")
                else:
                    # No exception - commit
                    try:
                        self.conn.commit()
                    except Exception as e:
                        print(f"Error during commit: {e}")
                        try:
                            self.conn.rollback()
                        except:
                            pass
                
                # Always close the cursor
                if self.cursor:
                    self.cursor.close()
        
        return ManagedCursor(self.conn, dict_cursor)
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
            self.conn = None
            self.connected = False
    
    def verify_connection(self):
        """Verify the database connection is healthy"""
        try:
            if not self.connected:
                return self.connect()
                
            # Try a simple query to verify connection
            with self.get_cursor() as cur:
                cur.execute("SELECT 1 as test")
                result = cur.fetchone()
                return result is not None
        except Exception as e:
            print(f"Connection verification failed: {e}")
            # Try to reconnect
            try:
                self.close()
                return self.connect()
            except:
                return False

# Database instance
db = Database()

def get_db():
    """Dependency for FastAPI endpoints to get database connection"""
    if not db.connected:
        db.connect()
    return db

def get_value(row, key, index=0):
    """Get value from a row that could be either a dict or tuple"""
    if isinstance(row, dict):
        return row.get(key)
    elif isinstance(row, tuple):
        return row[index] if len(row) > index else None
    return None

class Database:
    def __init__(self):
        self.conn = None
        self.connected = False
    
    def connect(self):
        """Connect to the PostgreSQL database"""
        try:
            # Close existing connection if in a failed state
            if self.conn:
                try:
                    # Check if connection is in a failed transaction
                    with self.conn.cursor() as cur:
                        cur.execute("SELECT 1")
                except psycopg2.errors.InFailedSqlTransaction:
                    # If in a failed transaction, rollback and close
                    self.conn.rollback()
                    self.conn.close()
                    self.conn = None
                except Exception:
                    # Other errors, close connection
                    try:
                        self.conn.close()
                    except:
                        pass
                    self.conn = None
            
            # Create a new connection if needed
            if not self.conn:
                self.conn = psycopg2.connect(
                    dbname=settings.DATABASE_NAME,
                    user=settings.DATABASE_USERNAME,
                    password=settings.DATABASE_PASSWORD,
                    host=settings.DATABASE_HOST,
                    port=int(settings.DATABASE_PORT),
                    cursor_factory=RealDictCursor  # Use RealDictCursor to return results as dictionaries
                )
            
            self.conn.autocommit = False  # We'll handle transactions explicitly
            self.connected = True
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            self.connected = False
            return False
    
    def initialize_database(self):
        """Initialize database schema"""
        try:
            if not self.connected and not self.connect():
                return False
            
            # Get the SQL file path
            sql_file_path = Path(__file__).parent / "schema.sql"
            
            with open(sql_file_path, 'r') as f:
                sql_commands = f.read()
            
            with self.conn.cursor() as cur:
                cur.execute(sql_commands)
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error initializing database: {e}")
            return False
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
            self.conn = None
            self.connected = False
    
    def get_cursor(self):
        """Get a database cursor with transaction handling"""
        if not self.connected and not self.connect():
            raise Exception("Not connected to database")
        
        class ManagedCursor:
            def __init__(self, conn):
                self.conn = conn
                self.cursor = None
            
            def __enter__(self):
                self.cursor = self.conn.cursor()
                return self.cursor
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    # An exception occurred - rollback
                    try:
                        self.conn.rollback()
                        print(f"Transaction rolled back due to: {exc_val}")
                    except Exception as e:
                        print(f"Error during rollback: {e}")
                else:
                    # No exception - commit
                    try:
                        self.conn.commit()
                    except Exception as e:
                        print(f"Error during commit: {e}")
                        self.conn.rollback()
                
                # Always close the cursor
                if self.cursor:
                    self.cursor.close()
        
        return ManagedCursor(self.conn)
    
    def execute_query(self, query, params=None):
        """Execute a query with proper transaction handling"""
        try:
            with self.get_cursor() as cur:
                cur.execute(query, params or ())
                if query.strip().upper().startswith(('SELECT', 'SHOW')):
                    return cur.fetchall()
                return True
        except Exception as e:
            print(f"Query execution error: {e}")
            return None
            
    def safe_fetch_one(self, cursor, key=None, index=0, default=None):
        """Safely fetch one result, handling both dict and tuple results"""
        result = cursor.fetchone()
        if not result:
            return default
            
        if key is not None:
            return get_value(result, key, index)
        return result
    
    # Article operations
    def insert_article(self, article):
        """Insert article into database"""
        try:
            with self.get_cursor() as cur:
                # Convert pub_date from string to date
                pub_date = None
                if article.get("PubDate"):
                    try:
                        pub_date = datetime.strptime(article["PubDate"], "%Y %b %d").date()
                    except ValueError:
                        try:
                            pub_date = datetime.strptime(article["PubDate"], "%Y %b").date()
                        except ValueError:
                            try:
                                pub_date = datetime.strptime(article["PubDate"], "%Y").date()
                            except ValueError:
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
                
                # Insert authors
                for author in article.get("Authors", []):
                    # Check if author exists
                    cur.execute("SELECT id FROM authors WHERE full_name = %s", (author,))
                    result = cur.fetchone()
                    
                    if result:
                        author_id = result["id"]
                    else:
                        cur.execute(
                            "INSERT INTO authors (full_name) VALUES (%s) RETURNING id",
                            (author,)
                        )
                        author_id = cur.fetchone()["id"]
                    
                    # Link author to article
                    cur.execute(
                        """
                        INSERT INTO articles_authors (article_id, authord_id)
                        VALUES (%s, %s) ON CONFLICT DO NOTHING
                        """,
                        (article_id, author_id)
                    )
                
                self.conn.commit()
                return article_id
        except Exception as e:
            self.conn.rollback()
            print(f"Error inserting article: {e}")
            return None
    
    def article_exists(self, pmid):
        """Check if article exists in database"""
        try:
            with self.get_cursor() as cur:
                cur.execute("SELECT id FROM articles WHERE pmid = %s", (pmid,))
                return cur.fetchone() is not None
        except Exception as e:
            print(f"Error checking if article exists: {e}")
            return False
    
    def get_all_articles(self, limit=100, offset=0):
        """Get all articles from database"""
        try:
            with self.get_cursor() as cur:
                cur.execute(
                    """
                    SELECT a.id, a.pmid, a.title, a.abstract, a.doi, a.journal, a.pub_date, c.count as citation_count,
                    (SELECT array_agg(au.full_name) FROM articles_authors aa JOIN authors au ON aa.author_id = au.id WHERE aa.article_id = a.id) as authors
                    FROM articles a
                    LEFT JOIN citations c ON a.id = c.article_id
                    ORDER BY c.count DESC NULLS LAST
                    LIMIT %s OFFSET %s
                    """,
                    (limit, offset)
                )
                return cur.fetchall()
        except Exception as e:
            print(f"Error fetching articles: {e}")
            return []
    
    def get_article_by_pmid(self, pmid):
        """Get article by PMID"""
        try:
            with self.get_cursor() as cur:
                cur.execute(
                    """
                    SELECT a.id, a.pmid, a.title, a.abstract, a.doi, a.journal, a.pub_date, c.count as citation_count,
                    (SELECT array_agg(au.full_name) FROM articles_authors aa JOIN authors au ON aa.author_id = au.id WHERE aa.article_id = a.id) as authors
                    FROM articles a
                    LEFT JOIN citations c ON a.id = c.article_id
                    WHERE a.pmid = %s
                    """,
                    (pmid,)
                )
                return cur.fetchone()
        except Exception as e:
            print(f"Error fetching article by PMID: {e}")
            return None
    
    # Search operations
    def insert_search(self, idea_text, keyword_text, max_results):
        """Insert search into database"""
        try:
            with self.get_cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO searches (idea_text, keyword_text, max_results, timestamp)
                    VALUES (%s, %s, %s, %s) RETURNING search_id
                    """,
                    (idea_text, keyword_text, max_results, datetime.now())
                )
                search_id = cur.fetchone()["search_id"]
                self.conn.commit()
                return search_id
        except Exception as e:
            self.conn.rollback()
            print(f"Error inserting search: {e}")
            return None
    
    def link_article_to_search(self, article_id, search_id):
        """Link article to search"""
        try:
            with self.get_cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO search_articles (search_id, article_id)
                    VALUES (%s, %s) ON CONFLICT DO NOTHING
                    """,
                    (search_id, article_id)
                )
                self.conn.commit()
                return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error linking article to search: {e}")
            return False
    
    def get_all_searches(self):
        """Get all searches"""
        try:
            with self.get_cursor() as cur:
                cur.execute("SELECT * FROM searches ORDER BY timestamp DESC")
                return cur.fetchall()
        except Exception as e:
            print(f"Error fetching searches: {e}")
            return []
    
    def get_search_by_id(self, search_id):
        """Get search by ID"""
        try:
            with self.get_cursor() as cur:
                cur.execute("SELECT * FROM searches WHERE search_id = %s", (search_id,))
                return cur.fetchone()
        except Exception as e:
            print(f"Error fetching search by ID: {e}")
            return None
    
    # Opportunity score operations
    def insert_opportunity_score(self, search_id, novelty, citation, recency, overall):
        """Insert opportunity score into database"""
        try:
            with self.get_cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO opportunity_scores (search_id, novelty_score, citation_velocity_score, recency_score, overall_score, computed_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (search_id, novelty, citation, recency, overall, datetime.now())
                )
                self.conn.commit()
                return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error inserting opportunity score: {e}")
            return False
    
    def get_opportunity_scores_by_search(self, search_id):
        """Get opportunity scores by search ID"""
        try:
            with self.get_cursor() as cur:
                cur.execute(
                    """
                    SELECT * FROM opportunity_scores
                    WHERE search_id = %s
                    ORDER BY computed_at DESC
                    """,
                    (search_id,)
                )
                return cur.fetchall()
        except Exception as e:
            print(f"Error fetching opportunity scores: {e}")
            return []
    
    # Vector operations
    def insert_article_vector(self, article_id, vector):
        """Insert article vector into database"""
        try:
            with self.get_cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO article_vectors (article_id, vector)
                    VALUES (%s, %s)
                    """,
                    (article_id, vector)
                )
                self.conn.commit()
                return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error inserting article vector: {e}")
            return False
    
    # Export operations
    def export_to_csv(self, filepath):
        """Export articles to CSV"""
        try:
            with self.get_cursor() as cur:
                cur.execute(
                    """
                    SELECT a.pmid, a.title, a.abstract, a.doi, a.journal, a.pub_date, c.count as citation_count,
                    (SELECT string_agg(au.full_name, '; ') FROM articles_authors aa JOIN authors au ON aa.author_id = au.id WHERE aa.article_id = a.id) as authors
                    FROM articles a
                    LEFT JOIN citations c ON a.id = c.article_id
                    ORDER BY c.count DESC NULLS LAST
                    """
                )
                rows = cur.fetchall()
            
            import csv
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['PMID', 'Title', 'Journal', 'Publication Date', 'Authors', 'Citations', 'DOI', 'Abstract'])
                
                for row in rows:
                    writer.writerow([
                        row["pmid"],
                        row["title"],
                        row["journal"],
                        row["pub_date"].strftime("%Y-%m-%d") if row["pub_date"] else "",
                        row["authors"] or "",
                        row["citation_count"] or 0,
                        row["doi"] or "",
                        row["abstract"] or ""
                    ])
                
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    # Search history operations
    def insert_search_history(self, search_id, novelty_raw, citation_raw, recency_raw):
        """Insert search history for normalization"""
        try:
            with self.get_cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO search_history (search_id, novelty_raw, citation_raw, recency_raw)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (search_id, novelty_raw, citation_raw, recency_raw)
                )
                self.conn.commit()
                return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error inserting search history: {e}")
            return False
    
    def get_all_search_history(self):
        """Get all search history for normalization"""
        try:
            with self.get_cursor() as cur:
                cur.execute("SELECT * FROM search_history")
                return cur.fetchall()
        except Exception as e:
            print(f"Error fetching search history: {e}")
            return []
    
    def get_articles_by_search(self, search_id):
        """Get articles by search ID"""
        try:
            with self.get_cursor() as cur:
                cur.execute(
                    """
                    SELECT a.id, a.pmid, a.title, a.abstract, a.doi, a.journal, a.pub_date, c.count as citation_count,
                    (SELECT array_agg(au.full_name) FROM articles_authors aa JOIN authors au ON aa.author_id = au.id WHERE aa.article_id = a.id) as authors
                    FROM articles a
                    JOIN search_articles sa ON a.id = sa.article_id
                    LEFT JOIN citations c ON a.id = c.article_id
                    WHERE sa.search_id = %s
                    """,
                    (search_id,)
                )
                return cur.fetchall()
        except Exception as e:
            print(f"Error fetching articles by search: {e}")
            return []