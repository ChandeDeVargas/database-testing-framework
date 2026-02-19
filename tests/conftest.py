"""
Pytest Configuration and Fixtures
Global fixtures for database testing
"""
import pytest
from config.database import DatabaseConfig, Base
from config.models import User, Product, Order, OrderItem
from faker import Faker
import random

fake = Faker()


@pytest.fixture(scope='session')
def db_engine():
    """
    Session-scoped database engine.
    Creates tables once for all tests.
    """
    db = DatabaseConfig('sqlite')
    
    # Create all tables
    Base.metadata.create_all(db.engine)
    
    yield db
    
    # Cleanup after all tests
    Base.metadata.drop_all(db.engine)
    db.close()


@pytest.fixture(scope='function')
def db_session(db_engine):
    """
    Function-scoped database session.
    Creates a fresh session for each test.
    Rolls back after each test to keep DB clean.
    """
    session = db_engine.get_session()
    
    yield session
    
    # Rollback and close after test
    session.rollback()
    session.close()


@pytest.fixture
def sample_users(db_session):
    """
    Create sample users for testing.
    
    Returns:
        List of User objects
    """
    users = []
    for i in range(5):
        user = User(
            name=fake.name(),
            email=fake.email(),
            age=random.randint(18, 80),
            is_active=True
        )
        db_session.add(user)
        users.append(user)
    
    db_session.commit()
    return users


@pytest.fixture
def sample_products(db_session):
    """
    Create sample products for testing.
    
    Returns:
        List of Product objects
    """
    products = []
    for i in range(10):
        product = Product(
            name=fake.catch_phrase(),
            sku=f"SKU-{fake.random_number(digits=6)}",
            price=round(random.uniform(10.0, 500.0), 2),
            stock=random.randint(0, 100),
            description=fake.text(max_nb_chars=200)
        )
        db_session.add(product)
        products.append(product)
    
    db_session.commit()
    return products


@pytest.fixture
def sample_orders(db_session, sample_users, sample_products):
    """
    Create sample orders with items for testing.
    
    Returns:
        List of Order objects
    """
    orders = []
    
    for user in sample_users[:3]:  # Create orders for first 3 users
        # Create 1-3 orders per user
        for _ in range(random.randint(1, 3)):
            order = Order(
                user_id=user.id,
                status=random.choice(['pending', 'completed', 'cancelled']),
                total_amount=0  # Will calculate below
            )
            db_session.add(order)
            db_session.flush()  # Get order ID
            
            # Add 1-3 items per order
            total = 0
            for _ in range(random.randint(1, 3)):
                product = random.choice(sample_products)
                quantity = random.randint(1, 5)
                price = product.price
                
                item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    price=price
                )
                db_session.add(item)
                total += price * quantity
            
            # Update order total
            order.total_amount = round(total, 2)
            orders.append(order)
    
    db_session.commit()
    return orders


@pytest.fixture
def empty_database(db_session):
    """
    Provides a completely empty database for testing.
    Useful for negative tests.
    """
    # Delete all existing data
    db_session.query(OrderItem).delete()
    db_session.query(Order).delete()
    db_session.query(Product).delete()
    db_session.query(User).delete()
    db_session.commit()
    
    return db_session