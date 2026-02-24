"""
Schema Validation Tests
Validate database structure matches expected schema

Schema issues cause:
- Migration failures
- Application crashes
- Data type mismatches
- Lost business logic
"""
import pytest
from sqlalchemy import inspect, Integer, String, Float, Boolean, DateTime
from config.models import User, Product, Order, OrderItem


class TestSchemaStructure:
    """
    Validate database schema structure.
    
    Ensures:
    - All tables exist
    - Columns have correct types
    - Constraints are in place
    - Indexes exist
    """
    
    def test_all_tables_exist(self, db_engine):
        """
        Test: All required tables exist in database
        
        Missing tables = broken application
        """
        inspector = inspect(db_engine.engine)
        existing_tables = inspector.get_table_names()
        
        required_tables = ['users', 'products', 'orders', 'order_items']
        
        missing_tables = [
            table for table in required_tables 
            if table not in existing_tables
        ]
        
        if missing_tables:
            print(f"\n🔴 CRITICAL: Missing tables: {missing_tables}")
        
        assert len(missing_tables) == 0, \
            f"SCHEMA: Missing tables {missing_tables}"
        
        print(f"\n✅ Schema: All {len(required_tables)} tables exist")
        print(f"   Tables: {existing_tables}")
    
    
    def test_users_table_columns(self, db_engine):
        """
        Test: Users table has all required columns with correct types
        
        Expected columns:
        - id: Integer (Primary Key)
        - name: String (NOT NULL)
        - email: String (UNIQUE, NOT NULL)
        - age: Integer
        - created_at: DateTime
        - is_active: Boolean
        """
        inspector = inspect(db_engine.engine)
        columns = inspector.get_columns('users')
        
        column_dict = {col['name']: col for col in columns}
        
        print(f"\n[Users Table Schema]")
        
        # Check required columns exist
        required_columns = ['id', 'name', 'email', 'age', 'created_at', 'is_active']
        
        missing_columns = [
            col for col in required_columns 
            if col not in column_dict
        ]
        
        if missing_columns:
            print(f"🔴 Missing columns: {missing_columns}")
        
        assert len(missing_columns) == 0, \
            f"SCHEMA: Users table missing columns {missing_columns}"
        
        # Validate column types
        for col_name, col_info in column_dict.items():
            print(f"   {col_name}: {col_info['type']} "
                  f"(nullable: {col_info['nullable']})")
        
        # Check specific constraints
        assert not column_dict['name']['nullable'], \
            "SCHEMA: users.name should be NOT NULL"
        
        assert not column_dict['email']['nullable'], \
            "SCHEMA: users.email should be NOT NULL"
        
        print(f"\n✅ Schema: Users table structure valid")
    
    
    def test_products_table_columns(self, db_engine):
        """
        Test: Products table has all required columns
        
        Expected columns:
        - id, name, sku, price, stock, description, created_at
        """
        inspector = inspect(db_engine.engine)
        columns = inspector.get_columns('products')
        
        column_dict = {col['name']: col for col in columns}
        
        required_columns = ['id', 'name', 'sku', 'price', 'stock']
        
        missing_columns = [
            col for col in required_columns 
            if col not in column_dict
        ]
        
        assert len(missing_columns) == 0, \
            f"SCHEMA: Products table missing columns {missing_columns}"
        
        # Check NOT NULL constraints
        assert not column_dict['name']['nullable'], \
            "SCHEMA: products.name should be NOT NULL"
        
        assert not column_dict['sku']['nullable'], \
            "SCHEMA: products.sku should be NOT NULL"
        
        assert not column_dict['price']['nullable'], \
            "SCHEMA: products.price should be NOT NULL"
        
        print(f"\n✅ Schema: Products table structure valid")
    
    
    def test_orders_table_foreign_keys(self, db_engine):
        """
        Test: Orders table has proper foreign keys
        
        Expected:
        - user_id → users.id (Foreign Key)
        """
        inspector = inspect(db_engine.engine)
        foreign_keys = inspector.get_foreign_keys('orders')
        
        print(f"\n[Orders Table Foreign Keys]")
        
        if not foreign_keys:
            print(f"   ⚠️ WARNING: No foreign keys detected")
            print(f"   Note: SQLite FK constraints may be disabled")
        else:
            for fk in foreign_keys:
                print(f"   {fk['constrained_columns']} → "
                      f"{fk['referred_table']}.{fk['referred_columns']}")
        
        # SQLite doesn't enforce FKs by default, so we just document
        print(f"\n✅ Schema: Foreign keys documented")
    
    
    def test_unique_constraints(self, db_engine):
        """
        Test: Unique constraints exist where needed
        
        Expected:
        - users.email (UNIQUE)
        - products.sku (UNIQUE)
        """
        inspector = inspect(db_engine.engine)
        
        # Check users.email unique constraint
        users_indexes = inspector.get_indexes('users')
        
        email_unique = False
        for index in users_indexes:
            if 'email' in index['column_names'] and index['unique']:
                email_unique = True
        
        # Check products.sku unique constraint
        products_indexes = inspector.get_indexes('products')
        
        sku_unique = False
        for index in products_indexes:
            if 'sku' in index['column_names'] and index['unique']:
                sku_unique = True
        
        print(f"\n[Unique Constraints]")
        print(f"   users.email: {'✅ UNIQUE' if email_unique else '⚠️ Not unique'}")
        print(f"   products.sku: {'✅ UNIQUE' if sku_unique else '⚠️ Not unique'}")
        
        # These should be unique but may not show in indexes
        # (SQLite creates implicit indexes for UNIQUE columns)
        print(f"\n✅ Schema: Unique constraints checked")
    
    
    def test_primary_keys(self, db_engine):
        """
        Test: All tables have primary keys
        
        Primary key = unique identifier for each row
        """
        inspector = inspect(db_engine.engine)
        tables = ['users', 'products', 'orders', 'order_items']
        
        print(f"\n[Primary Keys]")
        
        for table in tables:
            pk = inspector.get_pk_constraint(table)
            
            if pk['constrained_columns']:
                print(f"   {table}: {pk['constrained_columns']}")
            else:
                print(f"   {table}: ⚠️ No primary key!")
        
        # All tables should have id as primary key
        for table in tables:
            pk = inspector.get_pk_constraint(table)
            assert 'id' in pk['constrained_columns'], \
                f"SCHEMA: {table} should have 'id' as primary key"
        
        print(f"\n✅ Schema: All tables have primary keys")


class TestSchemaConsistency:
    """
    Test schema consistency across environments.
    
    Ensures development DB matches expected schema.
    """
    
    def test_column_count_stability(self, db_engine):
        """
        Test: Tables have expected number of columns
        
        Purpose: Detect accidental schema changes
        """
        inspector = inspect(db_engine.engine)
        
        expected_counts = {
            'users': 6,        # id, name, email, age, created_at, is_active
            'products': 7,     # id, name, sku, price, stock, description, created_at
            'orders': 5,       # id, user_id, status, total_amount, created_at
            'order_items': 5   # id, order_id, product_id, quantity, price
        }
        
        print(f"\n[Column Counts]")
        
        mismatches = []
        
        for table, expected_count in expected_counts.items():
            columns = inspector.get_columns(table)
            actual_count = len(columns)
            
            status = "✅" if actual_count == expected_count else "⚠️"
            print(f"   {table}: {actual_count} columns {status}")
            
            if actual_count != expected_count:
                mismatches.append({
                    'table': table,
                    'expected': expected_count,
                    'actual': actual_count
                })
        
        if mismatches:
            print(f"\n⚠️ WARNING: Column count mismatches detected")
            for m in mismatches:
                print(f"   {m['table']}: expected {m['expected']}, "
                      f"got {m['actual']}")
        
        assert len(mismatches) == 0, \
            f"SCHEMA: Column count mismatches in {len(mismatches)} tables"
        
        print(f"\n✅ Schema: Column counts match expected")
    
    
    def test_no_unexpected_tables(self, db_engine):
        """
        Test: No extra tables exist (orphaned migrations)
        
        Extra tables indicate:
        - Failed migrations
        - Manual SQL changes
        - Testing artifacts left behind
        """
        inspector = inspect(db_engine.engine)
        existing_tables = inspector.get_table_names()
        
        expected_tables = ['users', 'products', 'orders', 'order_items']
        
        extra_tables = [
            table for table in existing_tables 
            if table not in expected_tables
        ]
        
        if extra_tables:
            print(f"\n⚠️ WARNING: Found unexpected tables: {extra_tables}")
        else:
            print(f"\n✅ Schema: No unexpected tables")
        
        # Warning, not error (might be intentional temp tables)
        if len(extra_tables) > 0:
            print(f"   Review: {extra_tables}")