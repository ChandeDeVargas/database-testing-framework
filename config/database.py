"""
Database Connection Configuration
Supports: SQLite, PostgreSQL, MySQL
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base for ORM models
Base = declarative_base()

class DatabaseConfig:
    """
    Database configuration manager.
    
    Usage:
        db = DatabaseConfig('sqlite')
        session = db.get_session()
    """
    
    def __init__(self, db_type='sqlite'):
        """
        Initialize database connection.
        
        Args:
            db_type: 'sqlite', 'postgresql', or 'mysql'
        """
        self.db_type = db_type
        self.engine = None
        self.Session = None
        self._setup_connection()
    
    
    def _setup_connection(self):
        """Setup database connection based on type"""
        
        if self.db_type == 'sqlite':
            # SQLite - Local file database (for development)
            db_path = os.getenv('SQLITE_DB_PATH', os.path.join('db', 'test_database.db'))
            connection_string = f'sqlite:///{db_path}'
            
        elif self.db_type == 'postgresql':
            # PostgreSQL - Production-like database
            db_user = os.getenv('DB_USER', 'postgres')
            db_password = os.getenv('DB_PASSWORD', 'postgres')
            db_host = os.getenv('DB_HOST', 'localhost')
            db_port = os.getenv('DB_PORT', '5432')
            db_name = os.getenv('DB_NAME', 'testdb')
            
            connection_string = (
                f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
            )
            
        elif self.db_type == 'mysql':
            # MySQL - Another production option
            db_user = os.getenv('DB_USER', 'root')
            db_password = os.getenv('DB_PASSWORD', 'password')
            db_host = os.getenv('DB_HOST', 'localhost')
            db_port = os.getenv('DB_PORT', '3306')
            db_name = os.getenv('DB_NAME', 'testdb')
            
            connection_string = (
                f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
            )
        
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
        
        # Create engine
        self.engine = create_engine(
            connection_string,
            echo=False,  # Set to True for SQL query logging
            pool_pre_ping=True  # Verify connections before using
        )
        
        # Create session factory
        self.Session = sessionmaker(bind=self.engine)
    
    
    def get_session(self):
        """Get a new database session"""
        return self.Session()
    
    
    def execute_query(self, query):
        """
        Execute raw SQL query and return results.
        
        Args:
            query: SQL query string
            
        Returns:
            List of result rows
        """
        with self.engine.connect() as connection:
            result = connection.execute(query)
            return result.fetchall()
    
    
    def execute_query_df(self, query):
        """
        Execute query and return results as Pandas DataFrame.
        Useful for data analysis and validation.
        
        Args:
            query: SQL query string
            
        Returns:
            Pandas DataFrame
        """
        import pandas as pd
        with self.engine.connect() as connection:
            return pd.read_sql(query, connection)
    
    
    def create_tables(self):
        """Create all tables defined in models"""
        Base.metadata.create_all(self.engine)
    
    
    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(self.engine)
    
    
    def close(self):
        """Close all connections"""
        if self.engine:
            self.engine.dispose()


# Convenience function for quick access
def get_db(db_type='sqlite'):
    """
    Quick access to database connection.
    
    Usage:
        db = get_db('sqlite')
    """
    return DatabaseConfig(db_type)