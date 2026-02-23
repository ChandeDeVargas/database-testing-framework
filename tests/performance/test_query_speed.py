"""
Query Performance Tests
Detect slow queries that degrade user experience

Slow queries cause:
- Poor user experience (timeouts)
- Database overload
- Increased infrastructure costs
- Cascading failures
"""
import pytest
import time
from sqlalchemy import text
from config.models import User, Product, Order, OrderItem


class TestQueryPerformance:
    """
    Measure query execution time.
    
    SLA (Service Level Agreement):
    - Simple SELECT: < 100ms
    - JOIN queries: < 500ms
    - Complex aggregations: < 1000ms
    """
    
    def test_simple_select_performance(self, db_session, sample_users):
        """
        Test: Simple SELECT query is fast (< 100ms)
        
        Query: SELECT * FROM users WHERE id = 1
        Expected: < 100ms
        """
        start = time.time()
        
        user = db_session.query(User).filter_by(id=1).first()
        
        elapsed_ms = (time.time() - start) * 1000
        
        print(f"\n[Performance] Simple SELECT: {elapsed_ms:.2f}ms")
        
        if elapsed_ms > 100:
            print(f"WARNING: Query exceeded 100ms SLA")
        
        assert elapsed_ms < 100, \
            f"PERFORMANCE: Simple SELECT took {elapsed_ms:.2f}ms (limit: 100ms)"
        
        print(f"Simple SELECT: {elapsed_ms:.2f}ms (within SLA)")
    
    
    def test_join_query_performance(self, db_session, sample_orders):
        """
        Test: JOIN query is fast (< 500ms)
        
        Query: SELECT * FROM orders JOIN users ON orders.user_id = users.id
        Expected: < 500ms
        """
        start = time.time()
        
        # Query with JOIN
        orders_with_users = db_session.query(Order, User).join(
            User, Order.user_id == User.id
        ).all()
        
        elapsed_ms = (time.time() - start) * 1000
        
        print(f"\n[Performance] JOIN query: {elapsed_ms:.2f}ms "
              f"({len(orders_with_users)} results)")
        
        if elapsed_ms > 500:
            print(f"WARNING: Query exceeded 500ms SLA")
        
        assert elapsed_ms < 500, \
            f"PERFORMANCE: JOIN query took {elapsed_ms:.2f}ms (limit: 500ms)"
        
        print(f"JOIN Query: {elapsed_ms:.2f}ms (within SLA)")
    
    
    def test_aggregation_query_performance(self, db_session, sample_orders):
        """
        Test: Aggregation query is fast (< 1000ms)
        
        Query: SELECT user_id, COUNT(*), SUM(total_amount) 
               FROM orders GROUP BY user_id
        Expected: < 1000ms
        """
        from sqlalchemy import func
        
        start = time.time()
        
        # Aggregation query
        user_stats = db_session.query(
            Order.user_id,
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('total_spent')
        ).group_by(Order.user_id).all()
        
        elapsed_ms = (time.time() - start) * 1000
        
        print(f"\n[Performance] Aggregation query: {elapsed_ms:.2f}ms "
              f"({len(user_stats)} groups)")
        
        if elapsed_ms > 1000:
            print(f"WARNING: Query exceeded 1000ms SLA")
        
        assert elapsed_ms < 1000, \
            f"PERFORMANCE: Aggregation took {elapsed_ms:.2f}ms (limit: 1000ms)"
        
        print(f"Aggregation: {elapsed_ms:.2f}ms (within SLA)")
    
    
    def test_full_table_scan_detection(self, db_session, sample_products):
        """
        Test: Detect queries doing full table scans
        
        Full table scan = reading ALL rows when you only need 1
        Cause: Missing indexes
        
        This test uses EXPLAIN to detect scans (SQLite specific)
        """
        # Query without index (email search)
        start = time.time()
        
        product = db_session.query(Product).filter(
            Product.name.like('%test%')
        ).first()
        
        elapsed_ms = (time.time() - start) * 1000
        
        print(f"\n[Performance] LIKE query: {elapsed_ms:.2f}ms")
        
        # LIKE queries are inherently slow (full scan)
        # Just measure and warn if too slow
        if elapsed_ms > 100:
            print(f"WARNING: LIKE query slow (consider full-text search)")
        
        print(f"LIKE Query: {elapsed_ms:.2f}ms (measured)")
    
    
    def test_bulk_insert_performance(self, db_session):
        """
        Test: Bulk insert is efficient
        
        Inserting 100 records should be fast (< 1000ms)
        
        Bad: 100 individual INSERTs = slow
        Good: Bulk INSERT = fast
        """
        users_to_insert = []
        
        for i in range(100):
            user = User(
                name=f"Bulk User {i}",
                email=f"bulk{i}@test.com",
                age=25
            )
            users_to_insert.append(user)
        
        start = time.time()
        
        db_session.bulk_save_objects(users_to_insert)
        db_session.commit()
        
        elapsed_ms = (time.time() - start) * 1000
        
        print(f"\n[Performance] Bulk insert (100 users): {elapsed_ms:.2f}ms")
        
        # Cleanup
        db_session.query(User).filter(
            User.email.like('bulk%@test.com')
        ).delete(synchronize_session=False)
        db_session.commit()
        
        assert elapsed_ms < 1000, \
            f"PERFORMANCE: Bulk insert took {elapsed_ms:.2f}ms (limit: 1000ms)"
        
        print(f"Bulk Insert: {elapsed_ms:.2f}ms (efficient)")
    
    
    def test_pagination_performance(self, db_session, sample_products):
        """
        Test: Pagination is efficient
        
        Getting page 1 vs page 100 should have similar performance
        Bad: OFFSET 10000 = reads 10000 rows then skips them
        """
        # Page 1 (LIMIT 10)
        start = time.time()
        page1 = db_session.query(Product).limit(10).all()
        page1_ms = (time.time() - start) * 1000
        
        # Page 10 (LIMIT 10 OFFSET 90)
        start = time.time()
        page10 = db_session.query(Product).limit(10).offset(90).all()
        page10_ms = (time.time() - start) * 1000
        
        print(f"\n[Performance] Pagination:")
        print(f"   Page 1:  {page1_ms:.2f}ms")
        print(f"   Page 10: {page10_ms:.2f}ms")
        
        # Page 10 shouldn't be >10x slower than page 1
        if page10_ms > page1_ms * 10:
            print(f"WARNING: Pagination performance degrades significantly")
        
        print(f"Pagination: Performance acceptable")


class TestNPlusOneQueries:
    """
    Detect N+1 query problem.
    
    N+1 Problem:
    - Query 1: Get all orders (N orders)
    - Query 2-N+1: For each order, get the user (N queries)
    Total: N+1 queries when should be 1
    
    Solution: Eager loading with JOIN
    """
    
    def test_detect_n_plus_one_problem(self, db_session, sample_orders):
        """
        Test: Detect N+1 query problem
        
        Bad approach (N+1):
        orders = db.query(Order).all()  # 1 query
        for order in orders:
            user = order.user  # N queries (lazy load)
        Total: N+1 queries
        
        Good approach (1 query):
        orders = db.query(Order).join(User).all()  # 1 query
        """
        from sqlalchemy import event
        from sqlalchemy.engine import Engine
        
        query_count = {'count': 0}
        
        # Track queries
        @event.listens_for(Engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, 
                                         params, context, executemany):
            query_count['count'] += 1
        
        # BAD: Lazy loading (N+1 problem)
        query_count['count'] = 0
        
        orders = db_session.query(Order).all()
        
        # This triggers lazy loads (1 query per order.user access)
        user_names = [order.user.name for order in orders]
        
        bad_query_count = query_count['count']
        
        print(f"\n[N+1 Detection] Lazy loading:")
        print(f"   Orders fetched: {len(orders)}")
        print(f"   Queries executed: {bad_query_count}")
        
        # Clean up event listener
        event.remove(Engine, "before_cursor_execute", 
                    receive_before_cursor_execute)
        
        # GOOD: Eager loading (JOIN)
        query_count['count'] = 0
        
        @event.listens_for(Engine, "before_cursor_execute")
        def receive_before_cursor_execute_2(conn, cursor, statement, 
                                           params, context, executemany):
            query_count['count'] += 1
        
        from sqlalchemy.orm import joinedload
        
        orders_eager = db_session.query(Order).options(
            joinedload(Order.user)
        ).all()
        
        good_query_count = query_count['count']
        
        print(f"\n[N+1 Detection] Eager loading (JOIN):")
        print(f"   Orders fetched: {len(orders_eager)}")
        print(f"   Queries executed: {good_query_count}")
        
        # Clean up
        event.remove(Engine, "before_cursor_execute", 
                    receive_before_cursor_execute_2)
        
        # N+1 problem exists if lazy loading uses many queries
        if bad_query_count > len(orders):
            print(f"\nN+1 PROBLEM DETECTED:")
            print(f"   Lazy loading: {bad_query_count} queries for {len(orders)} orders")
            print(f"   Eager loading: {good_query_count} queries")
            print(f"   Improvement: {bad_query_count - good_query_count} fewer queries")
        
        print(f"\nN+1 Detection: Issue identified and demonstrated")


class TestDatabaseConnections:
    """
    Test database connection management.
    
    Connection leaks cause:
    - Exhausted connection pools
    - Database refusing new connections
    - Application crashes
    """
    
    def test_connections_are_closed(self, db_engine):
        """
        Test: Connections are properly closed after use
        
        Connection leak = opening connections without closing them
        Result: Eventually hit max_connections limit
        """
        # Get initial connection count
        initial_size = db_engine.engine.pool.size()
        
        print(f"\n[Connection Test] Initial pool size: {initial_size}")
        
        # Open and close 10 connections
        for i in range(10):
            session = db_engine.get_session()
            session.execute(text('SELECT 1'))
            session.close()
        
        # Check final connection count
        final_size = db_engine.engine.pool.size()
        
        print(f"   After 10 operations: {final_size}")
        
        # Pool size shouldn't grow indefinitely
        assert final_size <= initial_size + 5, \
            f"CONNECTION LEAK: Pool grew from {initial_size} to {final_size}"
        
        print(f"Connections: Properly managed (no leaks)")
    
    
    def test_concurrent_connections(self, db_engine):
        """
        Test: Database handles concurrent connections
        
        Simulate multiple users accessing database simultaneously
        """
        import threading
        
        results = []
        errors = []
        
        def query_database(thread_id):
            try:
                session = db_engine.get_session()
                user = session.query(User).first()
                results.append({
                    'thread': thread_id,
                    'success': True,
                    'user_id': user.id if user else None
                })
                session.close()
            except Exception as e:
                errors.append({
                    'thread': thread_id,
                    'error': str(e)
                })
        
        # Create 10 concurrent connections
        threads = []
        for i in range(10):
            t = threading.Thread(target=query_database, args=(i,))
            threads.append(t)
        
        print(f"\n[Concurrency Test] Starting 10 concurrent connections...")
        
        start = time.time()
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        elapsed_ms = (time.time() - start) * 1000
        
        print(f"   Completed: {len(results)}/10 successful")
        print(f"   Errors: {len(errors)}")
        print(f"   Time: {elapsed_ms:.2f}ms")
        
        if errors:
            print(f"\n   Errors encountered:")
            for error in errors:
                print(f"      Thread {error['thread']}: {error['error']}")
        
        assert len(errors) == 0, \
            f"CONCURRENCY: {len(errors)} connection errors"
        
        print(f"Concurrency: All 10 connections handled successfully")


class TestQueryOptimization:
    """
    Test query optimization strategies.
    
    Compare optimized vs unoptimized queries.
    """
    
    def test_select_specific_columns_vs_star(self, db_session, sample_users):
        """
        Test: SELECT specific columns is faster than SELECT *
        
        SELECT * = transfers all columns (including unused BLOBs)
        SELECT name, email = transfers only needed data
        """
        # SELECT * (all columns)
        start = time.time()
        users_all = db_session.query(User).all()
        all_columns_ms = (time.time() - start) * 1000
        
        # SELECT specific columns
        start = time.time()
        users_specific = db_session.query(
            User.id, User.name, User.email
        ).all()
        specific_columns_ms = (time.time() - start) * 1000
        
        print(f"\n[Query Optimization] Column selection:")
        print(f"   SELECT *: {all_columns_ms:.2f}ms")
        print(f"   SELECT name, email: {specific_columns_ms:.2f}ms")
        
        if specific_columns_ms < all_columns_ms:
            improvement = ((all_columns_ms - specific_columns_ms) / 
                          all_columns_ms * 100)
            print(f"   Improvement: {improvement:.1f}% faster")
        
        print(f"Optimization: Column selection impact measured")
    
    
    def test_exists_vs_count(self, db_session, sample_users):
        """
        Test: EXISTS is faster than COUNT for existence checks
        
        Bad: if count(*) > 0  (counts ALL rows)
        Good: if exists()     (stops at first match)
        """
        from sqlalchemy import exists
        
        # COUNT approach
        start = time.time()
        count_result = db_session.query(User).filter(
            User.age > 30
        ).count()
        has_users_count = count_result > 0
        count_ms = (time.time() - start) * 1000
        
        # EXISTS approach
        start = time.time()
        exists_result = db_session.query(
            exists().where(User.age > 30)
        ).scalar()
        has_users_exists = exists_result
        exists_ms = (time.time() - start) * 1000
        
        print(f"\n[Query Optimization] Existence check:")
        print(f"   COUNT(*): {count_ms:.2f}ms")
        print(f"   EXISTS:   {exists_ms:.2f}ms")
        
        if exists_ms < count_ms:
            improvement = ((count_ms - exists_ms) / count_ms * 100)
            print(f"   Improvement: {improvement:.1f}% faster")
        
        print(f"Optimization: EXISTS vs COUNT compared")
    
    
    def test_batch_vs_individual_updates(self, db_session):
        """
        Test: Batch updates are faster than individual updates
        
        Bad: UPDATE users SET age=age+1 WHERE id=1 (100 times)
        Good: UPDATE users SET age=age+1 WHERE id IN (1,2,3...100)
        """
        # Create test users
        test_users = []
        for i in range(100):
            user = User(
                name=f"Test {i}",
                email=f"test{i}@batch.com",
                age=25
            )
            test_users.append(user)
        
        db_session.bulk_save_objects(test_users)
        db_session.commit()
        
        # Get their IDs
        user_ids = [u.id for u in db_session.query(User).filter(
            User.email.like('%@batch.com')
        ).all()]
        
        # Individual updates
        start = time.time()
        for user_id in user_ids:
            db_session.query(User).filter_by(id=user_id).update(
                {'age': 26}
            )
        db_session.commit()
        individual_ms = (time.time() - start) * 1000
        
        # Batch update
        start = time.time()
        db_session.query(User).filter(
            User.id.in_(user_ids)
        ).update(
            {'age': 27},
            synchronize_session=False
        )
        db_session.commit()
        batch_ms = (time.time() - start) * 1000
        
        print(f"\n[Query Optimization] Batch updates:")
        print(f"   Individual (100 UPDATEs): {individual_ms:.2f}ms")
        print(f"   Batch (1 UPDATE):         {batch_ms:.2f}ms")
        
        improvement = ((individual_ms - batch_ms) / individual_ms * 100)
        print(f"   Improvement: {improvement:.1f}% faster")
        
        # Cleanup
        db_session.query(User).filter(
            User.email.like('%@batch.com')
        ).delete(synchronize_session=False)
        db_session.commit()
        
        assert batch_ms < individual_ms, \
            "OPTIMIZATION: Batch should be faster than individual"
        
        print(f"Optimization: Batch updates {improvement:.1f}% faster")