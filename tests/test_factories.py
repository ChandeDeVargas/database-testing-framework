"""
Test Data Factory Tests
Verify factories create valid test data

Tests that test the tests! (Meta-testing)
"""
import pytest
from fixtures.factories import (
    UserFactory, ProductFactory, OrderFactory, ScenarioFactory
)


class TestUserFactory:
    """Test UserFactory creates valid users"""
    
    def test_create_user(self, db_session):
        """Test: Factory creates valid user"""
        user = UserFactory.create()
        
        assert user.name is not None
        assert '@' in user.email
        assert 18 <= user.age <= 80
        assert user.is_active is True
        
        # Save to DB
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        print(f"\n✅ UserFactory: Created user {user.id} - {user.name}")
    
    
    def test_create_user_with_overrides(self, db_session):
        """Test: Factory respects custom values"""
        user = UserFactory.create(
            name="Custom Name",
            age=25,
            is_active=False
        )
        
        assert user.name == "Custom Name"
        assert user.age == 25
        assert user.is_active is False
        
        print(f"\n✅ UserFactory: Overrides working correctly")
    
    
    def test_create_batch(self, db_session):
        """Test: Factory creates multiple users"""
        users = UserFactory.create_batch(10)
        
        assert len(users) == 10
        
        # All should be valid
        for user in users:
            assert user.email is not None
            assert '@' in user.email
        
        print(f"\n✅ UserFactory: Created batch of {len(users)} users")


class TestProductFactory:
    """Test ProductFactory creates valid products"""
    
    def test_create_product(self, db_session):
        """Test: Factory creates valid product"""
        product = ProductFactory.create()
        
        assert product.name is not None
        assert product.sku is not None
        assert product.price > 0
        assert product.stock >= 0
        
        db_session.add(product)
        db_session.commit()
        
        print(f"\n✅ ProductFactory: Created {product.name} (${product.price})")
    
    
    def test_create_out_of_stock_product(self, db_session):
        """Test: Factory creates out-of-stock product"""
        product = ProductFactory.create_out_of_stock()
        
        assert product.stock == 0
        
        print(f"\n✅ ProductFactory: Created out-of-stock product")


class TestOrderFactory:
    """Test OrderFactory creates valid orders"""
    
    def test_create_order(self, db_session):
        """Test: Factory creates valid order"""
        # Create user first
        user = UserFactory.create()
        db_session.add(user)
        db_session.commit()
        
        # Create order
        order = OrderFactory.create(user_id=user.id)
        
        assert order.user_id == user.id
        assert order.status in ['pending', 'completed', 'cancelled']
        assert order.total_amount > 0
        
        db_session.add(order)
        db_session.commit()
        
        print(f"\n✅ OrderFactory: Created order ${order.total_amount}")
    
    
    def test_create_order_with_items(self, db_session):
        """Test: Factory creates order with items"""
        # Create user
        user = UserFactory.create()
        db_session.add(user)
        db_session.commit()
        
        # Create order with items
        order = OrderFactory.create_with_items(
            db_session,
            user_id=user.id,
            num_items=3
        )
        
        assert order.id is not None
        assert len(order.items) == 3
        assert order.total_amount > 0
        
        print(f"\n✅ OrderFactory: Created order with {len(order.items)} items")


class TestScenarioFactory:
    """Test ScenarioFactory creates complete scenarios"""
    
    def test_create_customer_scenario(self, db_session):
        """Test: Factory creates complete customer scenario"""
        scenario = ScenarioFactory.create_customer_with_orders(
            db_session,
            num_orders=3
        )
        
        assert scenario['user'].id is not None
        assert len(scenario['products']) == 10
        assert len(scenario['orders']) == 3
        
        # Verify relationships
        for order in scenario['orders']:
            assert order.user_id == scenario['user'].id
            assert len(order.items) > 0
        
        print(f"\n✅ ScenarioFactory: Created complete customer scenario")
        print(f"   User: {scenario['user'].name}")
        print(f"   Products: {len(scenario['products'])}")
        print(f"   Orders: {len(scenario['orders'])}")