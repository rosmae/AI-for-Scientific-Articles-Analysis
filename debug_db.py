#!/usr/bin/env python
"""
Debug script to test PostgreSQL connection and identify isolation level issues
"""
import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_connection():
    """Test database connection with various approaches"""
    print("🔍 Testing PostgreSQL Connection...")
    print("-" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Show current environment variables
    print("📋 Environment Variables:")
    print(f"DATABASE_HOST: {os.getenv('DATABASE_HOST')}")
    print(f"DATABASE_PORT: {os.getenv('DATABASE_PORT')}")
    print(f"DATABASE_NAME: {os.getenv('DATABASE_NAME')}")
    print(f"DATABASE_USERNAME: {os.getenv('DATABASE_USERNAME')}")
    print(f"DATABASE_PASSWORD: {'*' * len(os.getenv('DATABASE_PASSWORD', '')) if os.getenv('DATABASE_PASSWORD') else 'Not set'}")
    print()
    
    # Check for problematic PostgreSQL environment variables
    print("🔍 PostgreSQL Environment Variables:")
    pg_vars = [var for var in os.environ.keys() if var.startswith('PG')]
    if pg_vars:
        for var in pg_vars:
            print(f"{var}: {os.environ[var]}")
    else:
        print("No PostgreSQL environment variables found")
    print()
    
    try:
        import psycopg2
        from app.core.config import settings
        
        print("📝 Configuration Settings:")
        print(f"DATABASE_HOST: {settings.DATABASE_HOST}")
        print(f"DATABASE_PORT: {settings.DATABASE_PORT}")
        print(f"DATABASE_NAME: {settings.DATABASE_NAME}")
        print(f"DATABASE_USERNAME: {settings.DATABASE_USERNAME}")
        print()
        
        # Test 1: Simple connection
        print("🧪 Test 1: Simple Connection")
        try:
            conn = psycopg2.connect(
                dbname=settings.DATABASE_NAME,
                user=settings.DATABASE_USERNAME,
                password=settings.DATABASE_PASSWORD,
                host=settings.DATABASE_HOST,
                port=int(settings.DATABASE_PORT)
            )
            print("✅ Simple connection successful!")
            
            # Test query
            with conn.cursor() as cur:
                cur.execute("SELECT version()")
                version = cur.fetchone()[0]
                print(f"PostgreSQL Version: {version}")
                
                # Check current isolation level
                cur.execute("SHOW default_transaction_isolation")
                isolation = cur.fetchone()[0]
                print(f"Default Transaction Isolation: {isolation}")
                
            conn.close()
            
        except Exception as e:
            print(f"❌ Simple connection failed: {e}")
            print(f"Error type: {type(e).__name__}")
        
        print()
        
        # Test 2: Connection with environment cleanup
        print("🧪 Test 2: Connection with Environment Cleanup")
        try:
            # Clear problematic environment variables
            env_backup = {}
            problematic_vars = ['PGOPTIONS', 'PGCLIENTENCODING', 'PGISOLATION', 'PGAPPNAME']
            for var in problematic_vars:
                if var in os.environ:
                    env_backup[var] = os.environ[var]
                    del os.environ[var]
                    print(f"Cleared {var}: {env_backup[var]}")
            
            conn = psycopg2.connect(
                dbname=settings.DATABASE_NAME,
                user=settings.DATABASE_USERNAME,
                password=settings.DATABASE_PASSWORD,
                host=settings.DATABASE_HOST,
                port=int(settings.DATABASE_PORT)
            )
            print("✅ Connection with cleanup successful!")
            conn.close()
            
            # Restore environment variables
            for var, value in env_backup.items():
                os.environ[var] = value
                
        except Exception as e:
            print(f"❌ Connection with cleanup failed: {e}")
            # Restore environment variables even if connection failed
            for var, value in env_backup.items():
                os.environ[var] = value
        
        print()
        
        # Test 3: Connection string approach
        print("🧪 Test 3: Connection String Approach")
        try:
            connection_string = f"dbname={settings.DATABASE_NAME} user={settings.DATABASE_USERNAME} password={settings.DATABASE_PASSWORD} host={settings.DATABASE_HOST} port={settings.DATABASE_PORT}"
            conn = psycopg2.connect(connection_string)
            print("✅ Connection string approach successful!")
            conn.close()
            
        except Exception as e:
            print(f"❌ Connection string approach failed: {e}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have installed all dependencies:")
        print("pip install -r requirements_api.txt")

if __name__ == "__main__":
    test_connection()
