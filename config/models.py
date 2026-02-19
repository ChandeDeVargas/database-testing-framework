"""
Database Models (ORM)
Example schema for testing
"""
from email.policy import default
from sqlalchemy import (
    Column, Integer, String, Float,
    ForeignKey, DateTime, Boolean, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from config.database import Base

class User(Base):
    """
    Users table.

    Tests to write:
    - Email format validation
    - Unique email constraint
    - Required fields (name, email)
    - Orphaned records detection
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key = True)
    name = Column(String(100), nullable = False)
    email = Column(String(100), unique = True, nullable = False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default = True)
    age = Column(Integer)

    # Relationships
    orders = relationship('Order', back_populates = 'user')

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"

class Product(Base):
    """
    Products table.

    Tests to write:
    - Price validation (> 0)
    - Stock validation (>= 0)
    - Required fields
    - Duplicate SKU detection
    """
    __tablename__ = 'products'

    id = Column(Integer, primary_key = True)
    name = Column(String(200), nullable = False)
    sku = Column(String(50), unique = True, nullable = False)
    price = Column(Float, nullable = False)
    stock = Column(Integer, default = 0)
    description = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    order_items = relationship('OrderItem', back_populates = 'product')

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', sku='{self.sku}')>"

class Order(Base):
    """
    Orders table.
    
    Tests to write:
    - Foreign key integrity (user_id exists)
    - Status validation (pending, completed, cancelled)
    - Total amount validation (matches sum of items)
    - Orphaned orders detection
    """
    __tablename__ = 'orders'

    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable = False)
    status = Column(String(20), default = 'pending') # pending, completed, cancelled
    total_amount = Column(Float, nullable =False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship('User', back_populates = 'orders')
    items = relationship('OrderItem', back_populates = 'order')

    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, total={self.total_amount})>"

class OrderItem(Base):
    """
    Order Items table (junction table).
    
    Tests to write:
    - Foreign key integrity (order_id, product_id)
    - Quantity validation (> 0)
    - Price consistency (matches product price)
    - Orphaned items detection
    """
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)  # Price at time of order
    
    # Relationships
    order = relationship('Order', back_populates='items')
    product = relationship('Product', back_populates='order_items')
    
    def __repr__(self):
        return f"<OrderItem(order_id={self.order_id}, product_id={self.product_id}, qty={self.quantity})>"