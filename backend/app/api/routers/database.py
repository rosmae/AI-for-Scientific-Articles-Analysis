from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import traceback
import os
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED

from app.db.database import get_db
from app.core.config import settings

router = APIRouter(prefix="/database", tags=["database"])

class DatabaseResponse(BaseModel):
    success: bool
    message: str
    details: str = ""

class DatabaseVerificationResponse(BaseModel):
    healthy: bool
    details: str
    sql_command: str = ""

@router.post("/initialize", response_model=DatabaseResponse)
async def initialize_database(db = Depends(get_db)):
    """Initialize the database schema with required tables"""
    try:
        # Get the SQL file path
        sql_file_path = Path(__file__).parent.parent.parent / "db" / "schema.sql"
        
        if not sql_file_path.exists():
            raise HTTPException(status_code=404, detail="Schema file not found")
        
        with open(sql_file_path, 'r') as f:
            sql_commands = f.read()
        
        # Explicitly use non-dict cursor for DDL statements
        with db.get_cursor(dict_cursor=False) as cur:
            cur.execute(sql_commands)
        
        return DatabaseResponse(
            success=True,
            message="Database schema initialized successfully",
            details="All tables have been created or updated"
        )
    except Exception as e:
        print(f"Database initialization error: {e}")
        traceback.print_exc()
        
        # Check if it's a "relation already exists" error
        if "already exists" in str(e).lower():
            return DatabaseResponse(
                success=True,
                message="Database already initialized",
                details="Tables already exist in the database"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Database initialization failed: {str(e)}"
            )

@router.get("/tables")
async def list_database_tables(db = Depends(get_db)):
    """List all tables in the database"""
    try:
        import psycopg2
        from app.core.config import settings
        
        # Clear any problematic environment variables that might affect PostgreSQL
        env_backup = {}
        problematic_vars = ['PGOPTIONS', 'PGCLIENTENCODING', 'PGISOLATION']
        for var in problematic_vars:
            if var in os.environ:
                env_backup[var] = os.environ[var]
                del os.environ[var]
        
        try:
            # Create connection with minimal parameters to avoid issues
            conn = psycopg2.connect(
                dbname=settings.DATABASE_NAME,
                user=settings.DATABASE_USERNAME,
                password=settings.DATABASE_PASSWORD,
                host=settings.DATABASE_HOST,
                port=int(settings.DATABASE_PORT)
            )
            conn.autocommit = True  # This ensures no transaction is started
            
            tables = []
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                tables = [row[0] for row in cur.fetchall()]
            
            # Always close the connection
            conn.close()
            
            return {
                "tables": tables,
                "count": len(tables),
                "database": settings.DATABASE_NAME,
                "connection_status": "Fresh connection"
            }
        finally:
            # Restore environment variables
            for var, value in env_backup.items():
                os.environ[var] = value
    except Exception as e:
        print(f"Error listing database tables: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/verify", response_model=DatabaseVerificationResponse)
async def verify_database(db = Depends(get_db)):
    """Verify database connection health with transaction handling"""
    try:
        # Test with a simple query
        with db.get_cursor() as cur:
            cur.execute("SELECT 1 as test")
            result = cur.fetchone()
        
        return DatabaseVerificationResponse(
            healthy=True,
            details="Database connection is healthy",
            sql_command="SELECT 1 as test -- Run this in psql to verify your connection"
        )
    except Exception as e:
        print(f"Database verification error: {e}")
        traceback.print_exc()
        
        # Create helpful SQL for manual verification
        sql_command = """
-- Run these commands in psql to check transaction status
SELECT * FROM pg_stat_activity 
WHERE datname = 'prime_time' 
AND state = 'idle in transaction';

-- If any transactions are stuck, you can terminate them with:
-- (Replace PID with the actual process ID from the query above)
SELECT pg_terminate_backend(PID);
"""
        
        return DatabaseVerificationResponse(
            healthy=False,
            details=f"Database connection error: {str(e)}",
            sql_command=sql_command
        )
        # Test with a simple query
        with db.get_cursor() as cur:
            cur.execute("SELECT 1 as test")
            result = cur.fetchone()
        
        return DatabaseVerificationResponse(
            healthy=True,
            details="Database connection is healthy",
            sql_command="SELECT 1 as test -- Run this in psql to verify your connection"
        )
    except Exception as e:
        print(f"Database verification error: {e}")
        traceback.print_exc()
        
        # Create helpful SQL for manual verification
        sql_command = """
-- Run these commands in psql to check transaction status
SELECT * FROM pg_stat_activity 
WHERE datname = 'prime_time' 
AND state = 'idle in transaction';

-- If any transactions are stuck, you can terminate them with:
-- (Replace PID with the actual process ID from the query above)
SELECT pg_terminate_backend(PID);
"""
        
        return DatabaseVerificationResponse(
            healthy=False,
            details=f"Database connection error: {str(e)}",
            sql_command=sql_command
        )