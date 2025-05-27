import psycopg2
from psycopg2.extras import RealDictCursor
import os
import sys
import csv
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

def resource_path(relative_path: str) -> str:
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
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.connected = True
            return True
        except Exception as error:
            print(f"Error: {error}")
            self.connected = False
            return False

    def initialize_database(self):
        if not self.connected and not self.connect():
            return False
        try:
            schema_file = resource_path("init_db.sql")
            with open(schema_file, "r") as f:
                sql_schema = f.read()
            with self.conn.cursor() as cur:
                cur.execute(sql_schema)
            self.conn.commit()
            return True
        except Exception as error:
            print(f"Error initializing database: {error}")
            self.conn.rollback()
            return False

    def article_exists(self, pmid):
        if not self.connected and not self.connect():
            return False
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT id FROM articles WHERE pmid = %s", (pmid,))
                return cur.fetchone() is not None
        except Exception as error:
            print(f"Error checking article existence: {error}")
            return False

    def insert_search(self, idea_text, keyword_text, max_results):
        if not self.connected and not self.connect():
            return None
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO searches (idea_text, keyword_text, max_results)
                    VALUES (%s, %s, %s)
                    RETURNING search_id
                """, (idea_text, keyword_text, max_results))
                search_id = cur.fetchone()[0]
            self.conn.commit()
            return search_id
        except Exception as error:
            print(f"Error inserting search: {error}")
            self.conn.rollback()
            return None

    def link_article_to_search(self, article_id, search_id):
        if not self.connected and not self.connect():
            return False
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO search_articles (search_id, article_id)
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                """, (search_id, article_id))
            self.conn.commit()
            return True
        except Exception as error:
            print(f"Error linking article to search: {error}")
            self.conn.rollback()
            return False

    def insert_article(self, article_data):
        if not self.connected and not self.connect():
            return None
        try:
            with self.conn.cursor() as cur:
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

                for author_name in article_data["Authors"]:
                    cur.execute("SELECT id FROM authors WHERE full_name = %s", (author_name,))
                    result = cur.fetchone()
                    if result:
                        author_id = result[0]
                    else:
                        cur.execute(
                            "INSERT INTO authors (full_name) VALUES (%s) RETURNING id",
                            (author_name,)
                        )
                        author_id = cur.fetchone()[0]

                    cur.execute(
                        "INSERT INTO articles_authors (article_id, authord_id) VALUES (%s, %s)",
                        (article_id, author_id)
                    )

                citation_count = article_data.get("CitationCount", 0)
                cur.execute(
                    """
                    INSERT INTO citations (article_id, source, count, last_update)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (article_id, "crossref", citation_count, datetime.now().date())
                )

            self.conn.commit()
            return article_id
        except Exception as error:
            print(f"Error inserting article: {error}")
            self.conn.rollback()
            return None

    def get_all_articles(self):
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
        except Exception as error:
            print(f"Error retrieving articles: {error}")
            return []

    def get_article_by_pmid(self, pmid):
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
        except Exception as error:
            print(f"Error retrieving article: {error}")
            return None

    def insert_opportunity_score(self, search_id, novelty_score, citation_rate_score, recency_score, overall_score):
        if not self.connected and not self.connect():
            return False
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO opportunity_scores (
                        search_id, novelty_score, citation_rate_score, recency_score, overall_score
                    ) VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (search_id) DO UPDATE SET
                        novelty_score = EXCLUDED.novelty_score,
                        citation_rate_score = EXCLUDED.citation_rate_score,
                        recency_score = EXCLUDED.recency_score,
                        overall_score = EXCLUDED.overall_score,
                        computed_at = CURRENT_TIMESTAMP
                """, (search_id, novelty_score, citation_rate_score, recency_score, overall_score))
            self.conn.commit()
            return True
        except Exception as error:
            print(f"Error inserting opportunity score: {error}")
            self.conn.rollback()
            return False   

    def get_latest_search_id(self):
        if not self.connected and not self.connect():
            return None
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT search_id FROM searches ORDER BY search_id DESC LIMIT 1")
                row = cur.fetchone()
                return row[0] if row else None
        except Exception as error:
            print(f"Error retrieving latest search_id: {error}")
            return None

    def get_total_search_count(self):
        if not self.connected and not self.connect():
            return 0
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM searches")
                return cur.fetchone()[0]
        except Exception as error:
            print(f"Error getting search count: {error}")
            return 0

    def get_articles_by_search(self, search_id):
        if not self.connected and not self.connect():
            return []
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT a.title, a.abstract, a.pub_date, c.count AS citation_count
                    FROM search_articles sa
                    JOIN articles a ON sa.article_id = a.id
                    LEFT JOIN citations c ON a.id = c.article_id
                    WHERE sa.search_id = %s
                """, (search_id,))
                return cur.fetchall()
        except Exception as error:
            print(f"Error retrieving articles by search: {error}")
            return []

        # ---- NEW helper used by the UI scoring function ----
    def get_all_search_history(self):
        """
        Returns a list of dicts with keys that
        compute_and_display_opportunity_scores() expects.
        """
        if not self.connected and not self.connect():
            return []

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT search_id,
                           novelty_score  AS novelty_raw,
                           citation_rate_score AS citation_raw,
                           recency_score AS recency_raw
                    FROM opportunity_scores
                    WHERE novelty_score IS NOT NULL
                """)
                return cur.fetchall()
        except Exception as error:
            print(f"Error retrieving search history: {error}")
            return []
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.connected = False

    def _parse_date(self, date_str):
        try:
            formats = ["%Y %b %d", "%Y %b", "%Y", "%Y-%m-%d"]
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            return datetime.now().date()
        except Exception:
            return datetime.now().date()

    def export_to_csv(self, output_path):
        if not self.connected and not self.connect():
            return False
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        a.pmid,
                        a.title,
                        a.abstract,
                        a.journal,
                        a.pub_date,
                        array_agg(au.full_name) as authors,
                        c.count as citation_count,
                        s.idea_text,
                        s.keyword_text,
                        s.max_results,
                        s.timestamp,
                        o.novelty_score,
                        o.citation_rate_score,
                        o.recency_score,
                        o.overall_score
                    FROM articles a
                    LEFT JOIN articles_authors aa ON a.id = aa.article_id
                    LEFT JOIN authors au ON aa.authord_id = au.id
                    LEFT JOIN citations c ON a.id = c.article_id
                    LEFT JOIN search_articles sa ON a.id = sa.article_id
                    LEFT JOIN searches s ON sa.search_id = s.search_id
                    LEFT JOIN opportunity_scores o ON s.search_id = o.search_id
                    GROUP BY a.id, c.count, s.idea_text, s.keyword_text, s.max_results, s.timestamp, o.novelty_score, o.citation_rate_score, o.recency_score, o.overall_score
                    ORDER BY a.id DESC
                """)
                articles = cur.fetchall()

            if not articles:
                return False

            with open(output_path, mode="w", newline='', encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([
                    "PMID", "Title", "Abstract", "Journal", "Publication Date", "Authors",
                    "Citation Count", "Idea", "Keywords", "Max Results", "Search Timestamp",
                    "Novelty Score", "Citation Rate Score", "Recency Score", "Opportunity Score"
                ])

                for article in articles:
                    writer.writerow([
                        article["pmid"],
                        article["title"],
                        article["abstract"] or "",
                        article["journal"],
                        article["pub_date"].strftime("%Y-%m-%d") if article["pub_date"] else "",
                        ", ".join([a for a in article["authors"] if a]) if article["authors"] else "",
                        article["citation_count"],
                        article["idea_text"] or "",
                        article["keyword_text"] or "",
                        article["max_results"] or "",
                        article["timestamp"].strftime("%Y-%m-%d %H:%M:%S") if article["timestamp"] else "",
                        article["novelty_score"],
                        article["citation_rate_score"],
                        article["recency_score"],
                        article["overall_score"]
                    ])
            return True
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            return False
