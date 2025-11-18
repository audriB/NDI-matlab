"""
Tests for NDI database query builder utilities.

Tests the QueryBuilder, QueryCache, and query optimization functions.
"""

import pytest
from ndi.db.fun import QueryBuilder, QueryCache, combine_queries, optimize_query


class TestQueryBuilder:
    """Test QueryBuilder class."""

    def test_builder_creation(self):
        """Test creating a QueryBuilder instance."""
        qb = QueryBuilder()
        assert qb is not None
        assert qb.conditions == []

    def test_simple_where_clause(self):
        """Test building a simple WHERE clause."""
        qb = QueryBuilder()
        query = qb.where('type', '==', 'stimulus').build()

        assert query == {'type': 'stimulus'}

    def test_multiple_where_clauses(self):
        """Test building multiple AND WHERE clauses."""
        qb = QueryBuilder()
        query = qb.where('type', '==', 'stimulus') \
                  .where('session_id', '==', 'abc123') \
                  .build()

        assert query == {'type': 'stimulus', 'session_id': 'abc123'}

    def test_or_where_clause(self):
        """Test building OR WHERE clauses."""
        qb = QueryBuilder()
        query = qb.where('type', '==', 'A') \
                  .or_where('type', '==', 'B') \
                  .build()

        # Should create OR structure
        assert '$or' in query or '$and' in query

    def test_comparison_operators(self):
        """Test various comparison operators."""
        qb = QueryBuilder()

        # Greater than
        query = qb.where('value', '>', 10).build()
        # Complex operators create nested structure
        assert query is not None
        assert isinstance(query, dict)

        # Less than or equal
        qb = QueryBuilder()
        query = qb.where('value', '<=', 100).build()
        assert query is not None

        # In operator
        qb = QueryBuilder()
        query = qb.where('type', 'in', ['A', 'B', 'C']).build()
        assert query is not None

    def test_select_fields(self):
        """Test field selection."""
        qb = QueryBuilder()
        query = qb.where('type', '==', 'probe') \
                  .select('id', 'name', 'type') \
                  .build()

        assert '$fields' in query
        assert query['$fields'] == ['id', 'name', 'type']

    def test_limit(self):
        """Test result limiting."""
        qb = QueryBuilder()
        query = qb.where('type', '==', 'stimulus') \
                  .limit(10) \
                  .build()

        assert '$limit' in query
        assert query['$limit'] == 10

    def test_order_by(self):
        """Test result ordering."""
        qb = QueryBuilder()
        query = qb.where('type', '==', 'probe') \
                  .order_by('created', 'desc') \
                  .build()

        assert '$sort' in query
        assert query['$sort'] == {'created': -1}

        # Test ascending order
        qb = QueryBuilder()
        query = qb.where('type', '==', 'probe') \
                  .order_by('created', 'asc') \
                  .build()

        assert query['$sort'] == {'created': 1}

    def test_complex_query(self):
        """Test building a complex query with multiple features."""
        qb = QueryBuilder()
        query = qb.where('type', '==', 'stimulus') \
                  .where('value', '>', 10) \
                  .select('id', 'value', 'type') \
                  .order_by('value', 'desc') \
                  .limit(5) \
                  .build()

        # Should have various components
        assert query is not None
        assert isinstance(query, dict)

    def test_empty_query(self):
        """Test building an empty query."""
        qb = QueryBuilder()
        query = qb.build()

        assert query == {}

    def test_invalid_operator(self):
        """Test that invalid operators raise errors."""
        qb = QueryBuilder()

        with pytest.raises(ValueError):
            qb.where('field', 'invalid_op', 'value').build()

    def test_method_chaining(self):
        """Test that methods return self for chaining."""
        qb = QueryBuilder()

        result = qb.where('a', '==', 1)
        assert result is qb

        result = qb.select('a', 'b')
        assert result is qb

        result = qb.limit(10)
        assert result is qb

        result = qb.order_by('a')
        assert result is qb


class TestQueryCache:
    """Test QueryCache class."""

    def test_cache_creation(self):
        """Test creating a QueryCache instance."""
        cache = QueryCache()
        assert cache is not None
        assert cache.size() == 0

    def test_cache_set_and_get(self):
        """Test setting and getting cached values."""
        cache = QueryCache()

        query = {'type': 'stimulus'}
        results = [1, 2, 3]

        cache.set(query, results)

        cached = cache.get(query)
        assert cached == results

    def test_cache_miss(self):
        """Test getting a value that's not in cache."""
        cache = QueryCache()

        query = {'type': 'stimulus'}
        cached = cache.get(query)

        assert cached is None

    def test_cache_different_queries(self):
        """Test that different queries are cached separately."""
        cache = QueryCache()

        query1 = {'type': 'A'}
        query2 = {'type': 'B'}

        cache.set(query1, [1, 2, 3])
        cache.set(query2, [4, 5, 6])

        assert cache.get(query1) == [1, 2, 3]
        assert cache.get(query2) == [4, 5, 6]

    def test_cache_same_query_different_order(self):
        """Test that query key order doesn't matter."""
        cache = QueryCache()

        query1 = {'type': 'A', 'value': 1}
        query2 = {'value': 1, 'type': 'A'}  # Same but different order

        cache.set(query1, [1, 2, 3])

        # Should get same results for query2
        cached = cache.get(query2)
        assert cached == [1, 2, 3]

    def test_cache_size(self):
        """Test cache size tracking."""
        cache = QueryCache()

        assert cache.size() == 0

        cache.set({'a': 1}, [1])
        assert cache.size() == 1

        cache.set({'b': 2}, [2])
        assert cache.size() == 2

    def test_cache_clear(self):
        """Test clearing the cache."""
        cache = QueryCache()

        cache.set({'a': 1}, [1])
        cache.set({'b': 2}, [2])

        assert cache.size() == 2

        cache.clear()

        assert cache.size() == 0
        assert cache.get({'a': 1}) is None

    def test_cache_max_size(self):
        """Test that cache respects max size."""
        cache = QueryCache(max_size=3)

        # Add 3 items
        for i in range(3):
            cache.set({'id': i}, [i])

        assert cache.size() == 3

        # Add one more (should evict oldest)
        cache.set({'id': 3}, [3])

        assert cache.size() == 3


class TestCombineQueries:
    """Test combine_queries function."""

    def test_combine_empty(self):
        """Test combining no queries."""
        result = combine_queries()
        assert result == {}

    def test_combine_single_query(self):
        """Test combining a single query."""
        q1 = {'type': 'A'}
        result = combine_queries(q1)

        assert result == q1

    def test_combine_two_queries_and(self):
        """Test combining two queries with AND."""
        q1 = {'type': 'A'}
        q2 = {'value': 10}

        result = combine_queries(q1, q2, logic='AND')

        assert result == {'type': 'A', 'value': 10}

    def test_combine_two_queries_or(self):
        """Test combining two queries with OR."""
        q1 = {'type': 'A'}
        q2 = {'type': 'B'}

        result = combine_queries(q1, q2, logic='OR')

        assert '$or' in result
        assert len(result['$or']) == 2

    def test_combine_multiple_queries_and(self):
        """Test combining multiple queries with AND."""
        q1 = {'a': 1}
        q2 = {'b': 2}
        q3 = {'c': 3}

        result = combine_queries(q1, q2, q3, logic='AND')

        assert result == {'a': 1, 'b': 2, 'c': 3}

    def test_combine_invalid_logic(self):
        """Test that invalid logic raises error."""
        with pytest.raises(ValueError):
            combine_queries({'a': 1}, {'b': 2}, logic='XOR')


class TestOptimizeQuery:
    """Test optimize_query function."""

    def test_optimize_simple_query(self):
        """Test optimizing a simple query (no change)."""
        query = {'type': 'stimulus'}
        optimized = optimize_query(query)

        assert optimized == query

    def test_optimize_unwrap_single_and(self):
        """Test unwrapping $and with single element."""
        query = {'$and': [{'type': 'A'}]}
        optimized = optimize_query(query)

        assert optimized == {'type': 'A'}

    def test_optimize_unwrap_single_or(self):
        """Test unwrapping $or with single element."""
        query = {'$or': [{'type': 'A'}]}
        optimized = optimize_query(query)

        assert optimized == {'type': 'A'}

    def test_optimize_remove_duplicate_and_conditions(self):
        """Test removing duplicate conditions in $and."""
        query = {'$and': [
            {'type': 'A'},
            {'value': 10},
            {'type': 'A'}  # Duplicate
        ]}

        optimized = optimize_query(query)

        # Should have only 2 conditions
        assert len(optimized['$and']) == 2

    def test_optimize_remove_duplicate_or_conditions(self):
        """Test removing duplicate conditions in $or."""
        query = {'$or': [
            {'type': 'A'},
            {'type': 'B'},
            {'type': 'A'}  # Duplicate
        ]}

        optimized = optimize_query(query)

        # Should have only 2 conditions
        assert len(optimized['$or']) == 2

    def test_optimize_complex_query(self):
        """Test optimizing a complex query."""
        query = {'$and': [
            {'$and': [{'type': 'A'}]},  # Nested single $and
        ]}

        optimized = optimize_query(query)

        # Should unwrap nested structure
        assert optimized == {'type': 'A'}


class TestQueryBuilderIntegration:
    """Integration tests for query builder components."""

    def test_build_cache_and_optimize(self):
        """Test building, caching, and optimizing a query."""
        # Build a query
        qb = QueryBuilder()
        query = qb.where('type', '==', 'stimulus') \
                  .where('value', '>', 10) \
                  .build()

        # Optimize it
        optimized = optimize_query(query)

        # Cache it
        cache = QueryCache()
        cache.set(optimized, [1, 2, 3])

        # Retrieve from cache
        cached = cache.get(optimized)
        assert cached == [1, 2, 3]

    def test_combine_and_optimize(self):
        """Test combining and optimizing queries."""
        q1 = {'type': 'A'}
        q2 = {'value': 10}

        combined = combine_queries(q1, q2, logic='AND')
        optimized = optimize_query(combined)

        assert optimized == {'type': 'A', 'value': 10}
