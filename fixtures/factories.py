"""
Test Data Factories
Professional test data generation with realistic constraints

Factories provide:
- Consistent test data
- Realistic relationships
- Easy customization
- Better than Faker alone
"""
from numpy.random.mtrand import random
from datetime import datetime, timezone
from faker import Faker
import random

fake = Faker()

class UserFactory:
    """
    Create realistic user records.
    
    Usage:
        user = UserFactory.create()
        user = UserFactory.create(age=25, email='test@example.com')
    """
    @staticmethod
    def create(**kwargs):
        """
        Create a user with optional overrides.
        
        Args:
            **kwargs: Override any default values
            
        Returns:
            User object (not saved to DB)
        """
        from config.models import User

        defaults = {
            'name': fake.name(),
            'email': fake.email(),
            'age': random.randint(18, 80),
            'is_active': True,
            'created_at': datetime.now(timezone.utc),
        }

        # Override defaults with any kwargs
        defaults.update(kwargs)

        return User(**defaults)

    @staticmethod
    def create_batch(count, **kwargs):
        """
        Create multiple users.
        
        Args:
            count: Number of users to create
            **kwargs: Common attributes for all users
            
        Returns:
            List of User objects
        """
        return [UserFactory.create(**kwargs) for _ in range(count)]
    
    @staticmethod
    def create_inactive(**kwargs):
        """Create an inactive user (specific scenario)"""
        kwargs['is_active'] = False
        return UserFactory.create(**kwargs)

    @staticmethod
    def create_minor(**kwargs):
        """Create a minor user (age < 18)"""
        kwargs['age'] = random.randint(13, 17)
        return UserFactory.create(**kwargs)

    @staticmethod
    def create_senior(**kwargs):
        """Create a senior user (age > 65)"""
        kwargs['age'] = random.randint(65, 90)
        return UserFactory.create(**kwargs)

class ProductFactory:
    """
    Create realistic product records.
    
    Usage:
        product = ProductFactory.create()
        product = ProductFactory.create(price=99.99, stock=0)
    """
    @staticmethod
    def create(**kwargs):
        """Create a product with optional overrides"""
        from config.models import Product

        defaults = {
            'name': fake.catch_phrase(),
            'sku': f"SKU-{fake.random_number(digits=8)}",
            'price': round(random.uniform(10.0, 500.0), 2),
            'stock': random.randint(0, 100),
            'description': fake.text(max_nb_chars=200),
            'created_at': datetime.now(timezone.utc),
        }

        defaults.update(kwargs)

        return Product(**defaults)

    @staticmethod
    def create_batch(count, **kwargs):
        """Create multiple products."""
        return [ProductFactory.create(**kwargs) for _ in range(count)]

    @staticmethod
    def create_out_of_stock(**kwargs):
        """Create a product with zero stock (specific scenario)"""
        kwargs['stock'] = 0
        return ProductFactory.create(**kwargs)

    @staticmethod
    def create_expensive(**kwargs):
        """Create an expensive product (> $1000)"""
        kwargs['price'] = round(random.uniform(1000.0, 5000.0), 2)
        return ProductFactory.create(**kwargs)

    @staticmethod
    def create_cheap(**kwargs):
        """Create a cheap product (< $10)"""
        kwargs['price'] = round(random.uniform(1.0, 9.99), 2)
        return ProductFactory.create(**kwargs)

class OrderFactory:
    """
    Create realistic order records.
    
    Usage:
        order = OrderFactory.create(user_id=1)
        order = OrderFactory.create_with_items(user_id=1, num_items=3)
    """
    @staticmethod
    def create(user_id, **kwargs):
        """
        Create an order.
        
        Args:
            user_id: ID of the user placing the order (required)
            **kwargs: Override defaults
        """
        from config.models import Order

        defaults = {
            'user_id': user_id,
            'status': random.choice(['pending', 'completed', 'cancelled']),
            'total_amount': round(random.uniform(10.0, 500.0), 2),
            'created_at': datetime.now(timezone.utc)
        }

        defaults.update(kwargs)

        return Order(**defaults)

    @staticmethod
    def create_batch(user_id, count, **kwargs):
        """Create multiple orders for a user"""
        return [OrderFactory.create(user_id, **kwargs) for _ in range(count)]

    @staticmethod
    def create_pending(user_id, **kwargs):
        """Create pending order"""
        kwargs['status'] = 'pending'
        return OrderFactory.create(user_id, **kwargs)

    @staticmethod
    def create_completed(user_id, **kwargs):
        """Create a completed order"""
        kwargs['status'] = 'completed'
        return OrderFactory.create(user_id, **kwargs)

    @staticmethod
    def create_with_items(db_session, user_id, product_ids=None, num_items=3):
        """
        Create an order WITH order items.
        
        Args:
            db_session: Database session
            user_id: User placing order
            product_ids: List of product IDs (or None to create random)
            num_items: Number of items in order
            
        Returns:
            Order object (with items)
        """ 
        from config.models import Order, OrderItem, Product

        # Get or create products
        if product_ids is None:
            products = db_session.query(Product).limit(num_items).all()
            if len(products) < num_items:
                # Create remaining products if not enough exist
                needed = num_items - len(products)
                new_products = ProductFactory.create_batch(needed)
                for product in new_products:
                    db_session.add(product)
                db_session.flush()
                products.extend(new_products)
        else:
            products = db_session.query(Product).filter(
                Product.id.in_(product_ids)
            ).all()
        
        # Create order
        order = Order(
            user_id=user_id,
            status='pending',
            total_amount=0,
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(order)
        db_session.flush() # Get order.id

        # Create order items and calculate total
        total = 0
        for product in products[:num_items]:
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
            
        order.total_amount = round(total, 2)

        return order

class ScenarioFactory:
    """
    Create complete test scenarios (multiple related objects).
    
    Usage:
        scenario = ScenarioFactory.create_customer_with_orders(db_session)
        # Returns: {user, products, orders}
    """
    @staticmethod
    def create_customer_with_orders(db_session, num_orders=3):
        """
        Create a complete customer scenario:
        - 1 user
        - Multiple products
        - Multiple orders with items
        
        Returns:
            dict: {user, products, orders}
        """
        # Create user
        user = UserFactory.create()
        db_session.add(user)
        db_session.flush()

        # Create products
        products = ProductFactory.create_batch(10)
        for product in products:
            db_session.add(product)
        db_session.flush()

        # Create orders with items
        orders = []
        for _ in range(num_orders):
            order = OrderFactory.create_with_items(
                db_session,
                user_id=user.id,
                num_items=random.randint(1, 3)
            )
            orders.append(order)

        db_session.commit()

        return {
            'user': user,
            'products': products,
            'orders': orders
        }
    
    @staticmethod
    def create_inventory_scenario(db_session):
        """
        Create inventory scenario:
        - Products with varying stock levels
        - Some out of stock
        - Some overstocked
        
        Returns:
            dict: {in_stock, out_of_stock, overstocked}
        """
        in_stock = ProductFactory.create_batch(5, stock=50)
        out_of_stock = ProductFactory.create_batch(3, stock=0)
        overstocked = ProductFactory.create_batch(2, stock=500)

        all_products = in_stock + out_of_stock + overstocked

        for product in all_products:
            db_session.add(product)
        db_session.commit()

        return {
            'in_stock': in_stock,
            'out_of_stock': out_of_stock,
            'overstocked': overstocked
        }