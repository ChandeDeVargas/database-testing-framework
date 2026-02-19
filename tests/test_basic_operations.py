"""
Basic Database Operations Tests
Verify database connectivity and CRUD operations
"""
import pytest
from config.models import User, Product


class TestDatabaseConnectivity:
    """Test basic database connectivity"""
    
    def test_database_connection(self, db_engine):
        """
        Test: Database connection is established
        
        Purpose: Verify we can connect to database
        """
        assert db_engine.engine is not None
        print("\n✅ Database connection successful")
    
    
    def test_tables_exist(self, db_engine):
        """
        Test: All required tables exist
        
        Purpose: Verify schema was created correctly
        """
        inspector = db_engine.engine.dialect.get_table_names(
            db_engine.engine.connect()
        )
        
        required_tables = ['users', 'products', 'orders', 'order_items']
        
        for table in required_tables:
            assert table in inspector, f"Table '{table}' not found"
        
        print(f"\n✅ All {len(required_tables)} tables exist")


class TestCRUDOperations:
    """Test Create, Read, Update, Delete operations"""
    
    def test_create_user(self, db_session):
        """
        Test: Create a new user
        
        Purpose: Verify INSERT operation works
        """
        user = User(
            name="John Doe",
            email="john@example.com",
            age=30
        )
        
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        print(f"\n✅ User created with ID: {user.id}")
    
    
    def test_read_user(self, db_session, sample_users):
        """
        Test: Read user from database
        
        Purpose: Verify SELECT operation works
        """
        # Get first user
        user = db_session.query(User).first()
        
        assert user is not None
        assert user.name is not None
        assert user.email is not None
        
        print(f"\n✅ User read: {user.name} ({user.email})")
    
    
    def test_update_user(self, db_session, sample_users):
        """
        Test: Update user information
        
        Purpose: Verify UPDATE operation works
        """
        user = sample_users[0]
        original_name = user.name
        
        # Update name
        user.name = "Updated Name"
        db_session.commit()
        
        # Verify update
        updated_user = db_session.query(User).filter_by(
            id=user.id
        ).first()
        
        assert updated_user.name == "Updated Name"
        assert updated_user.name != original_name
        
        print(f"\n✅ User updated: '{original_name}' → '{updated_user.name}'")
    
    
    def test_delete_user(self, db_session):
        """
        Test: Delete user from database
        
        Purpose: Verify DELETE operation works
        """
        # Create user
        user = User(name="To Delete", email="delete@example.com", age=25)
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        
        # Delete user
        db_session.delete(user)
        db_session.commit()
        
        # Verify deletion
        deleted_user = db_session.query(User).filter_by(
            id=user_id
        ).first()
        
        assert deleted_user is None
        print(f"\n✅ User deleted (ID: {user_id})")
    
    
    def test_query_with_filter(self, db_session, sample_users):
        """
        Test: Query with WHERE clause
        
        Purpose: Verify filtering works
        """
        # Filter active users
        active_users = db_session.query(User).filter(
            User.is_active == True
        ).all()
        
        assert len(active_users) > 0
        assert all(u.is_active for u in active_users)
        
        print(f"\n✅ Found {len(active_users)} active users")
    
    
    def test_count_records(self, db_session, sample_products):
        """
        Test: Count records in table
        
        Purpose: Verify COUNT operation works
        """
        count = db_session.query(Product).count()
        
        assert count == len(sample_products)
        print(f"\n✅ Product count: {count}")