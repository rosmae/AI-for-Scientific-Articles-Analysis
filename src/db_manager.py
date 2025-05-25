import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import os
import sys
import csv
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller --onefile bundles."""
    base_path = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
    return os.path.join(base_path, relative_path)

class DatabaseManager:
    def __init__(self, dbname=None, user=None, password=None, host=None, port=None):
        self.connection_params = {
            "dbname": dbname or os.getenv("DATABASE_NAME"),
            "user": user or os.getenv("DATABASE_USERNAME"),
            "password": password or os.getenv("DATABASE_PASSWORD"),
            "host": host or os.getenv("DATABASE_HOST"),
            "port": port or os.getenv("DATABASE_PORT")
        }
        self.conn = None
        self.connected = False

    
    def connect(self):
        """Connect to the PostgreSQL database server"""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.connected = True
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error: {error}")
            self.connected = False
            return False
            
    def initialize_database(self):
        """Create tables if they don't exist"""
        if not self.connected and not self.connect():
            return False
            
        try:
            # Read schema from SQL file
            schema_file = resource_path("init_db.sql")
            with open(schema_file, "r") as f:
                sql_schema = f.read()
                
            # Execute schema creation
            with self.conn.cursor() as cur:
                cur.execute(sql_schema)
            self.conn.commit()
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error initializing database: {error}")
            self.conn.rollback()
            return False
    
    def article_exists(self, pmid):
        """Check if an article with the given PMID already exists"""
        if not self.connected and not self.connect():
            return False
            
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT id FROM articles WHERE pmid = %s", (pmid,))
                return cur.fetchone() is not None
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error checking article existence: {error}")
            return False
    
    def insert_article(self, article_data, article_vector=None, keyword_vector=None):
        """Insert a new article and related data"""
        if not self.connected and not self.connect():
            return False
            
        try:
            # Begin transaction
            with self.conn.cursor() as cur:
                # Insert article
                cur.execute(
                    """
                    INSERT INTO articles (pmid, title, abstract, doi, journal, pub_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        article_data["PMID"],
                        article_data["Title"],
                        article_data["Abstract"],
                        article_data["DOI"],
                        article_data["Journal"],
                        self._parse_date(article_data["PubDate"])
                    )
                )
                article_id = cur.fetchone()[0]
                
                # Insert authors
                for author_name in article_data["Authors"]:
                    # Check if author exists
                    cur.execute("SELECT id FROM authors WHERE full_name = %s", (author_name,))
                    result = cur.fetchone()
                    
                    if result:
                        author_id = result[0]
                    else:
                        # Insert new author
                        cur.execute(
                            "INSERT INTO authors (full_name) VALUES (%s) RETURNING id",
                            (author_name,)
                        )
                        author_id = cur.fetchone()[0]
                    
                    # Create article-author relationship
                    cur.execute(
                        "INSERT INTO articles_authors (article_id, authord_id) VALUES (%s, %s)",
                        (article_id, author_id)
                    )
                
                # Insert citation count
                citation_count = article_data.get("CitationCount", 0)

                cur.execute(
                """
                INSERT INTO citations (article_id, source, count, last_update)
                VALUES (%s, %s, %s, %s)
                """,
                (article_id, "crossref", citation_count, datetime.now().date())
                )

                # Insert semantics_vector
                if article_vector is not None and keyword_vector is not None:
                    cur.execute(
                        """
                        INSERT INTO semantic_vectors (article_id, article_vector, keyword_vector)
                        VALUES (%s, %s, %s)
                        """,
                        (article_id, article_vector.tolist(), keyword_vector.tolist())
                    )


            self.conn.commit()
            return article_id
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error inserting article: {error}")
            self.conn.rollback()
            return None

    def get_all_articles(self):
        """Retrieve all articles with their authors"""
        if not self.connected and not self.connect():
            return []
            
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT a.*, 
                           array_agg(au.full_name) as authors,
                           c.count as citation_count
                    FROM articles a
                    LEFT JOIN articles_authors aa ON a.id = aa.article_id
                    LEFT JOIN authors au ON aa.authord_id = au.id
                    LEFT JOIN citations c ON a.id = c.article_id
                    GROUP BY a.id, c.count
                    ORDER BY a.id DESC
                """)
                return cur.fetchall()
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error retrieving articles: {error}")
            return []
    
    def get_article_by_pmid(self, pmid):
        """Retrieve a specific article by PMID"""
        if not self.connected and not self.connect():
            return None
            
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT a.*, 
                           array_agg(au.full_name) as authors,
                           c.count as citation_count
                    FROM articles a
                    LEFT JOIN articles_authors aa ON a.id = aa.article_id
                    LEFT JOIN authors au ON aa.authord_id = au.id
                    LEFT JOIN citations c ON a.id = c.article_id
                    WHERE a.pmid = %s
                    GROUP BY a.id, c.count
                """, (pmid,))
                return cur.fetchone()
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error retrieving article: {error}")
            return None
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.connected = False
    
    def _parse_date(self, date_str):
        """Parse publication date string to a datetime object"""
        try:
            # Handle various date formats from PubMed
            formats = [
                "%Y %b %d",
                "%Y %b",
                "%Y",
                "%Y-%m-%d"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            
            # If all formats fail, default to current date
            return datetime.now().date()
        except Exception:
            return datetime.now().date()

    def export_to_csv(self, output_path):
        """Export all articles with semantic vectors to a CSV file"""
        if not self.connected and not self.connect():
            return False

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        a.pmid,
                        a.title,
                        a.journal,
                        a.pub_date,
                        array_agg(au.full_name) as authors,
                        c.count as citation_count,
                        sv.article_vector,
                        sv.keyword_vector
                    FROM articles a
                    LEFT JOIN articles_authors aa ON a.id = aa.article_id
                    LEFT JOIN authors au ON aa.authord_id = au.id
                    LEFT JOIN citations c ON a.id = c.article_id
                    LEFT JOIN semantic_vectors sv ON a.id = sv.article_id
                    GROUP BY a.id, c.count, sv.article_vector, sv.keyword_vector
                    ORDER BY a.id DESC
                """)
                articles = cur.fetchall()

            if not articles:
                return False

            with open(output_path, mode="w", newline='', encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([
                    "PMID", "Title", "Journal", "Publication Date", "Authors",
                    "Citation Count", "Article Vector", "Keyword Vector"
                ])
                for article in articles:
                    writer.writerow([
                        article["pmid"],
                        article["title"],
                        article["journal"],
                        article["pub_date"].strftime("%Y-%m-%d") if article["pub_date"] else "",
                        ", ".join(article["authors"]) if article["authors"] else "",
                        article["citation_count"],
                        str(article["article_vector"]) if article["article_vector"] else "",
                        str(article["keyword_vector"]) if article["keyword_vector"] else ""
                    ])
            return True
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            return False
