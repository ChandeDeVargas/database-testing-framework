"""
Database Connection Configuration
Supports: SQLite, PostgreSQL, MySQL
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
import os

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
            db_path = os.path.join('db', 'test_database.db')
            connection_string = f'sqlite:///{db_path}'
            
        elif self.db_type == 'postgresql':
            # PostgreSQL - Production-like database
            # Change these to your actual PostgreSQL credentials
            connection_string = (
                'postgresql://postgres:postgres@localhost:5432/testdb'
            )
            
        elif self.db_type == 'mysql':
            # MySQL - Another production option
            connection_string = (
                'mysql+pymysql://root:password@localhost:3306/testdb'
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