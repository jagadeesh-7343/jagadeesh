import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import sql
import os
from pathlib import Path

class DatabaseManager:
    """
    Production-ready PostgreSQL database manager for Citizen Bridge
    """
    
    def __init__(self, dbname='citizen_bridge', user='postgres', password='nsrit', 
                 host='localhost', port=5432):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            print(f"✓ Connected to database: {self.dbname}")
            return self.connection
        except psycopg2.Error as e:
            print(f"✗ Database connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✓ Database connection closed")
    
    def create_database(self):
        """Create the citizen_bridge database if it doesn't exist"""
        try:
            # Connect to default postgres DB to create new database
            conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            # Check if database exists first
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (self.dbname,))
            exists = cursor.fetchone()
            if not exists:
                    cursor.execute(sql.SQL("CREATE DATABASE {};").format(sql.Identifier(self.dbname)))
                    print(f"✓ Database '{self.dbname}' created")
            else:
                print(f"✓ Database '{self.dbname}' already exists")
            cursor.close()
            conn.close()
        except psycopg2.Error as e:
                # If we failed to connect to the 'postgres' database (often due to auth),
                # attempt a best-effort fallback: try connecting directly to the target
                # database. This helps in environments where the user cannot connect to
                # the default 'postgres' DB but the target DB already exists.
                print(f"✗ Error creating database: {e}")
                try:
                    fallback_conn = psycopg2.connect(
                        dbname=self.dbname,
                        user=self.user,
                        password=self.password,
                        host=self.host,
                        port=self.port
                    )
                    fallback_conn.close()
                    print(f"✓ Connected to target database '{self.dbname}' (create skipped)")
                    return
                except Exception:
                    print("✗ Could not connect to the target database either.")
                    print("Ensure your DB credentials are correct or set environment variables:")
                    print("  DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT")
                    raise
    
    def execute_sql_file(self, filepath):
        """Execute SQL queries from a file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            cursor = self.connection.cursor()
            cursor.execute(sql_content)
            self.connection.commit()
            cursor.close()
            print(f"✓ SQL file executed successfully: {filepath}")
        except FileNotFoundError:
            print(f"✗ SQL file not found: {filepath}")
            raise
        except psycopg2.Error as e:
            self.connection.rollback()
            print(f"✗ Error executing SQL file: {e}")
            raise
    
    def initialize_schema(self):
        """Initialize database schema"""
        try:
            # Path to the database.sql file
            sql_file = Path(__file__).parent / 'database.sql'
            
            if not sql_file.exists():
                print(f"✗ Schema file not found: {sql_file}")
                return False
            
            print("Initializing database schema...")
            self.execute_sql_file(str(sql_file))
            print("✓ Database schema initialized successfully")
            return True
        except Exception as e:
            print(f"✗ Schema initialization failed: {e}")
            raise
    
    def health_check(self):
        """Check database health and connectivity"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1;")
            cursor.close()
            print("✓ Database health check passed")
            return True
        except Exception as e:
            print(f"✗ Database health check failed: {e}")
            return False


def initialize_database(db_config=None):
    """
    Main initialization function for database setup
    
    Args:
        db_config: Dictionary with database configuration
                  Default uses environment variables or hardcoded values
    """
    if db_config is None:
        db_config = {
            'dbname': os.getenv('DB_NAME', 'citizen_bridge'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'nsrit'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432))
        }
    
    db_manager = DatabaseManager(**db_config)
    
    try:
        # Create database
        db_manager.create_database()
        
        # Connect to database
        db_manager.connect()
        
        # Initialize schema
        db_manager.initialize_schema()
        
        # Health check
        db_manager.health_check()
        
        return db_manager
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    # Test database initialization
    try:
        db_manager = initialize_database()
        print("\n✓ All database operations completed successfully!")
        db_manager.disconnect()
    except Exception as e:
        print(f"\n✗ Failed to initialize database: {e}")