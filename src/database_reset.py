import os
import psycopg2
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables (go up one level to find .env)
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

DB_PARAMS = {
    "dbname": os.getenv("DATABASE_NAME"),
    "user": os.getenv("DATABASE_USERNAME"),
    "password": os.getenv("DATABASE_PASSWORD"),
    "host": os.getenv("DATABASE_HOST"),
    "port": os.getenv("DATABASE_PORT"),
}

def reset_database():
    """Drop all tables and recreate the database schema"""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        conn.autocommit = True
        
        with conn.cursor() as cur:
            print("🗑️  Dropping existing tables...")
            
            # Drop tables in reverse dependency order
            tables_to_drop = [
                "opportunity_scores",
                "search_articles", 
                "citations",
                "article_authors",
                "searches",
                "articles",
                "authors"
            ]
            
            for table in tables_to_drop:
                cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
                print(f"   ✓ Dropped {table}")
            
            print("\n📋 Creating fresh database schema...")
            
            # Read and execute the init_db.sql file (same directory)
            with open('init_db.sql', 'r') as f:
                sql_commands = f.read()
            cur.execute(sql_commands)
            print("   ✓ Database schema created successfully!")
            
        conn.close()
        print("\n🎉 Database reset complete! Ready for fresh data.")
        return True
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        return False

if __name__ == "__main__":
    reset_database()
