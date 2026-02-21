"""
Duplicate Detection Tests
Find duplicate records that shouldn't exist

Duplicates cause:
- Data inconsistency
- Business logic errors
- Customer confusion (multiple accounts)
- Analytics inaccuracy
"""
import pytest
from sqlalchemy import func
from config.models import User, Product, Order


class TestDuplicateDetection:
    """
    Detect duplicate records across tables.
    
    Duplicates happen from:
    - Race conditions (concurrent inserts)
    - Failed constraint enforcement
    - Data migration errors
    - Manual SQL inserts
    """
    
    def test_no_duplicate_emails(self, db_session):
        """
        Test: No two users share the same email
        
        Business Rule: One email = One account
        Common Issue: Case sensitivity (User@example.com vs user@example.com)
        """
        # Group by lowercase email and count
        duplicates = db_session.query(
            func.lower(User.email).label('email'),
            func.count(User.id).label('count')
        ).group_by(
            func.lower(User.email)
        ).having(
            func.count(User.id) > 1
        ).all()
        
        if duplicates:
            print(f"\nCRITICAL: Found {len(duplicates)} duplicate emails!")
            for dup in duplicates:
                # Get all users with this email
                users = db_session.query(User).filter(
                    func.lower(User.email) == dup.email
                ).all()
                print(f"\n   Email: {dup.email} ({dup.count} accounts)")
                for user in users:
                    print(f"      User ID {user.id}: {user.email} (original case)")
        
        assert len(duplicates) == 0, \
            f"DATA QUALITY: {len(duplicates)} duplicate emails found"
        
        print(f"\nDuplicate Check: All emails are unique")
    
    
    def test_no_duplicate_skus(self, db_session):
        """
        Test: No two products share the same SKU
        
        Business Rule: SKU = Stock Keeping Unit (must be unique)
        Impact: Inventory chaos, wrong products shipped
        """
        duplicates = db_session.query(
            Product.sku,
            func.count(Product.id).label('count')
        ).group_by(
            Product.sku
        ).having(
            func.count(Product.id) > 1
        ).all()
        
        if duplicates:
            print(f"\nCRITICAL: Found {len(duplicates)} duplicate SKUs!")
            for dup in duplicates:
                products = db_session.query(Product).filter_by(sku=dup.sku).all()
                print(f"\n   SKU: {dup.sku} ({dup.count} products)")
                for product in products:
                    print(f"      Product ID {product.id}: {product.name}")
        
        assert len(duplicates) == 0, \
            f"DATA QUALITY: {len(duplicates)} duplicate SKUs found"
        
        print(f"\nDuplicate Check: All SKUs are unique")
    
    
    def test_no_duplicate_user_names_suspicious(self, db_session):
        """
        Test: Detect suspiciously identical user names
        
        Not necessarily an error, but worth investigating:
        - Multiple "John Smith" accounts
        - Identical full names (might be same person)
        """
        duplicates = db_session.query(
            User.name,
            func.count(User.id).label('count')
        ).group_by(
            User.name
        ).having(
            func.count(User.id) > 1
        ).all()
        
        if duplicates:
            print(f"\nWARNING: Found {len(duplicates)} duplicate names")
            for dup in duplicates[:5]:  # Show first 5
                print(f"   Name: '{dup.name}' appears {dup.count} times")
        
        # This is a warning, not a hard error
        # (legitimate users can have same name)
        if len(duplicates) > 0:
            print(f"\nNote: {len(duplicates)} duplicate names found "
                  f"(may be legitimate)")
        else:
            print(f"\nDuplicate Check: All names are unique")
    
    
    def test_exact_duplicate_orders(self, db_session):
        """
        Test: Detect exact duplicate orders
        
        Same user + same amount + same timestamp = Likely duplicate submission
        
        Common causes:
        - Double-click on "Place Order" button
        - Network retry
        - Race condition
        """
        # Find orders with same user_id, total_amount, and close timestamps
        all_orders = db_session.query(Order).order_by(
            Order.user_id, Order.created_at
        ).all()
        
        duplicates = []
        
        for i in range(len(all_orders) - 1):
            order1 = all_orders[i]
            order2 = all_orders[i + 1]
            
            # Check if orders are suspiciously similar
            if (order1.user_id == order2.user_id and
                order1.total_amount == order2.total_amount and
                abs((order1.created_at - order2.created_at).total_seconds()) < 60):
                duplicates.append({
                    'order1_id': order1.id,
                    'order2_id': order2.id,
                    'user_id': order1.user_id,
                    'amount': order1.total_amount,
                    'time_diff': abs((order1.created_at - order2.created_at).total_seconds())
                })
        
        if duplicates:
            print(f"\nWARNING: Found {len(duplicates)} potential duplicate orders!")
            for dup in duplicates:
                print(f"   Orders {dup['order1_id']} & {dup['order2_id']}: "
                      f"User {dup['user_id']}, ${dup['amount']:.2f}, "
                      f"{dup['time_diff']:.1f}s apart")
        
        # Warning, not hard failure
        if len(duplicates) > 0:
            print(f"\nReview: {len(duplicates)} potential duplicate orders")
        else:
            print(f"\nDuplicate Check: No duplicate orders detected")