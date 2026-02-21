"""
Value Range Validation Tests
Detect values outside acceptable business ranges

Out-of-range values indicate:
- Data entry errors
- System bugs
- Data corruption
- Fraud attempts
"""
import pytest
from datetime import datetime, timedelta, timezone
from config.models import User, Product, Order


class TestValueRanges:
    """
    Validate that data values are within acceptable ranges.
    
    Business rules encoded as data validation.
    """
    
    def test_age_in_valid_range(self, db_session, sample_users):
        """
        Test: User ages are realistic (0-120 years)
        
        Valid range: 0-120
        Suspicious: <13 (child accounts - may violate TOS)
        Invalid: >120 (data error), negative (impossible)
        """
        invalid_ages = []
        suspicious_ages = []
        
        for user in sample_users:
            age = user.age
            
            if age is None:
                continue
            
            if age < 0 or age > 120:
                invalid_ages.append({
                    'user_id': user.id,
                    'name': user.name,
                    'age': age,
                    'issue': 'Age outside valid range (0-120)'
                })
            elif age < 13:
                suspicious_ages.append({
                    'user_id': user.id,
                    'name': user.name,
                    'age': age,
                    'issue': 'Minor account (<13) - may violate TOS'
                })
        
        if invalid_ages:
            print(f"\nCRITICAL: Found {len(invalid_ages)} users with invalid ages!")
            for item in invalid_ages:
                print(f"   User {item['user_id']} ({item['name']}): "
                      f"Age = {item['age']}")
        
        if suspicious_ages:
            print(f"\nWARNING: Found {len(suspicious_ages)} minor accounts!")
            for item in suspicious_ages[:5]:
                print(f"   User {item['user_id']}: Age = {item['age']}")
        
        assert len(invalid_ages) == 0, \
            f"DATA QUALITY: {len(invalid_ages)} users with impossible ages"
        
        print(f"\nAge Validation: All ages within valid range (0-120)")
    
    
    def test_price_in_valid_range(self, db_session, sample_products):
        """
        Test: Product prices are reasonable
        
        Valid range: $0.01 - $1,000,000
        Invalid: Negative, zero (unless intentional), > $1M
        """
        invalid_prices = []
        
        for product in sample_products:
            price = product.price
            
            if price < 0:
                invalid_prices.append({
                    'product_id': product.id,
                    'name': product.name,
                    'price': price,
                    'issue': 'Negative price'
                })
            elif price == 0:
                invalid_prices.append({
                    'product_id': product.id,
                    'name': product.name,
                    'price': price,
                    'issue': 'Zero price (verify intentional)'
                })
            elif price > 1000000:
                invalid_prices.append({
                    'product_id': product.id,
                    'name': product.name,
                    'price': price,
                    'issue': 'Price > $1M (verify legitimate)'
                })
        
        if invalid_prices:
            print(f"\nCRITICAL: Found {len(invalid_prices)} products with invalid prices!")
            for item in invalid_prices:
                print(f"   Product {item['product_id']} ({item['name']}): "
                      f"${item['price']:.2f} - {item['issue']}")
        
        assert len(invalid_prices) == 0, \
            f"DATA QUALITY: {len(invalid_prices)} products with invalid prices"
        
        print(f"\nPrice Validation: All prices in valid range")
    
    
    def test_stock_in_valid_range(self, db_session, sample_products):
        """
        Test: Stock quantities are realistic
        
        Valid range: 0-100,000
        Warning: 0 (out of stock - business issue)
        Invalid: Negative, > 100,000 (warehouse capacity)
        """
        invalid_stock = []
        out_of_stock = []
        
        for product in sample_products:
            stock = product.stock
            
            if stock < 0:
                invalid_stock.append({
                    'product_id': product.id,
                    'name': product.name,
                    'stock': stock,
                    'issue': 'Negative stock (impossible)'
                })
            elif stock > 100000:
                invalid_stock.append({
                    'product_id': product.id,
                    'name': product.name,
                    'stock': stock,
                    'issue': 'Stock > 100k (verify warehouse capacity)'
                })
            elif stock == 0:
                out_of_stock.append({
                    'product_id': product.id,
                    'name': product.name
                })
        
        if invalid_stock:
            print(f"\nCRITICAL: Found {len(invalid_stock)} products with invalid stock!")
            for item in invalid_stock:
                print(f"   Product {item['product_id']} ({item['name']}): "
                      f"Stock = {item['stock']} - {item['issue']}")
        
        if out_of_stock:
            print(f"\nBUSINESS WARNING: {len(out_of_stock)} products out of stock")
        
        assert len(invalid_stock) == 0, \
            f"DATA QUALITY: {len(invalid_stock)} products with invalid stock"
        
        print(f"\nStock Validation: All stock levels valid")
    
    
    def test_order_total_in_valid_range(self, db_session, sample_orders):
        """
        Test: Order totals are reasonable
        
        Valid range: $0.01 - $100,000
        Invalid: Zero (empty order?), Negative, > $100k (fraud risk)
        """
        invalid_totals = []
        
        for order in sample_orders:
            total = order.total_amount
            
            if total <= 0:
                invalid_totals.append({
                    'order_id': order.id,
                    'total': total,
                    'issue': 'Zero or negative total'
                })
            elif total > 100000:
                invalid_totals.append({
                    'order_id': order.id,
                    'total': total,
                    'issue': 'Total > $100k (fraud risk - review)'
                })
        
        if invalid_totals:
            print(f"\nCRITICAL: Found {len(invalid_totals)} orders with invalid totals!")
            for item in invalid_totals:
                print(f"   Order {item['order_id']}: "
                      f"${item['total']:.2f} - {item['issue']}")
        
        assert len(invalid_totals) == 0, \
            f"DATA QUALITY: {len(invalid_totals)} orders with invalid totals"
        
        print(f"\nOrder Total Validation: All totals in valid range")
    
    
    def test_created_dates_not_in_future(self, db_session):
        """
        Test: Record creation dates are not in the future
        
        Invalid: created_at > NOW
        Common cause: System clock issues, timezone bugs
        """
        now = datetime.now(timezone.utc)
        
        # Check users
        future_users = db_session.query(User).filter(
            User.created_at > now
        ).all()
        
        # Check products
        future_products = db_session.query(Product).filter(
            Product.created_at > now
        ).all()
        
        # Check orders
        future_orders = db_session.query(Order).filter(
            Order.created_at > now
        ).all()
        
        issues = []
        
        if future_users:
            for user in future_users:
                issues.append(f"User {user.id}: created_at = {user.created_at}")
        
        if future_products:
            for product in future_products:
                issues.append(f"Product {product.id}: created_at = {product.created_at}")
        
        if future_orders:
            for order in future_orders:
                issues.append(f"Order {order.id}: created_at = {order.created_at}")
        
        if issues:
            print(f"\nCRITICAL: Found {len(issues)} records with future timestamps!")
            for issue in issues:
                print(f"   {issue}")
        
        assert len(issues) == 0, \
            f"DATA QUALITY: {len(issues)} records created in the future"
        
        print(f"\nTimestamp Validation: All creation dates are valid")
    
    
    def test_order_status_values(self, db_session, sample_orders):
        """
        Test: Order status contains only valid values
        
        Valid: 'pending', 'completed', 'cancelled'
        Invalid: Anything else (typos, old values, null)
        """
        valid_statuses = ['pending', 'completed', 'cancelled']
        invalid_statuses = []
        
        for order in sample_orders:
            status = order.status
            
            if status not in valid_statuses:
                invalid_statuses.append({
                    'order_id': order.id,
                    'status': status,
                    'issue': f"Invalid status (not in {valid_statuses})"
                })
        
        if invalid_statuses:
            print(f"\nCRITICAL: Found {len(invalid_statuses)} orders with invalid status!")
            for item in invalid_statuses:
                print(f"   Order {item['order_id']}: "
                      f"Status = '{item['status']}'")
        
        assert len(invalid_statuses) == 0, \
            f"DATA QUALITY: {len(invalid_statuses)} orders with invalid status"
        
        print(f"\nStatus Validation: All order statuses are valid")