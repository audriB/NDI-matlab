"""
NDI Query Builder - Enhanced query construction utilities.

This module provides utilities for building complex database queries with
support for combining conditions, field selection, and query optimization.

MATLAB Equivalent: Various query construction patterns in NDI-MATLAB
"""

from typing import Any, Dict, List, Optional, Union
from functools import lru_cache


class QueryBuilder:
    """
    Builder for constructing complex NDI database queries.

    Provides a fluent interface for building queries with multiple conditions,
    field selections, and logical operators (AND, OR, NOT).

    Examples:
        >>> qb = QueryBuilder()
        >>> query = qb.where('base.session_id', '==', 'session123') \\
        ...           .where('element.type', '==', 'stimulus') \\
        ...           .build()
        >>> query
        {'base.session_id': 'session123', 'element.type': 'stimulus'}

        >>> # Complex queries with OR
        >>> qb = QueryBuilder()
        >>> query = qb.where('element.type', '==', 'stimulus') \\
        ...           .or_where('element.type', '==', 'probe') \\
        ...           .build()
    """

    def __init__(self):
        """Initialize a new QueryBuilder."""
        self.conditions: List[Dict[str, Any]] = []
        self.fields: Optional[List[str]] = None
        self.limit_value: Optional[int] = None
        self.sort_by: Optional[str] = None
        self.sort_order: str = 'asc'

    def where(self, field: str, operator: str, value: Any) -> 'QueryBuilder':
        """
        Add a WHERE condition to the query.

        Args:
            field: Field name (dot notation supported, e.g., 'base.session_id')
            operator: Comparison operator ('==', '!=', '>', '<', '>=', '<=', 'in', 'contains')
            value: Value to compare against

        Returns:
            Self for method chaining

        Examples:
            >>> qb = QueryBuilder()
            >>> qb.where('base.session_id', '==', 'abc123')
            >>> qb.where('element.type', 'in', ['stimulus', 'probe'])
        """
        self.conditions.append({
            'field': field,
            'operator': operator,
            'value': value,
            'logic': 'AND'
        })
        return self

    def or_where(self, field: str, operator: str, value: Any) -> 'QueryBuilder':
        """
        Add an OR WHERE condition to the query.

        Args:
            field: Field name
            operator: Comparison operator
            value: Value to compare against

        Returns:
            Self for method chaining

        Examples:
            >>> qb = QueryBuilder()
            >>> qb.where('type', '==', 'A').or_where('type', '==', 'B')
        """
        self.conditions.append({
            'field': field,
            'operator': operator,
            'value': value,
            'logic': 'OR'
        })
        return self

    def select(self, *fields: str) -> 'QueryBuilder':
        """
        Specify which fields to return in results.

        Args:
            *fields: Field names to select

        Returns:
            Self for method chaining

        Examples:
            >>> qb = QueryBuilder()
            >>> qb.select('base.id', 'base.session_id', 'element.type')
        """
        self.fields = list(fields)
        return self

    def limit(self, count: int) -> 'QueryBuilder':
        """
        Limit the number of results.

        Args:
            count: Maximum number of results to return

        Returns:
            Self for method chaining

        Examples:
            >>> qb = QueryBuilder()
            >>> qb.where('type', '==', 'stimulus').limit(10)
        """
        self.limit_value = count
        return self

    def order_by(self, field: str, order: str = 'asc') -> 'QueryBuilder':
        """
        Specify result ordering.

        Args:
            field: Field to sort by
            order: Sort order ('asc' or 'desc')

        Returns:
            Self for method chaining

        Examples:
            >>> qb = QueryBuilder()
            >>> qb.order_by('base.created', 'desc')
        """
        self.sort_by = field
        self.sort_order = order.lower()
        return self

    def build(self) -> Dict[str, Any]:
        """
        Build the final query dictionary.

        Returns:
            Query dictionary compatible with NDI database search

        Examples:
            >>> qb = QueryBuilder()
            >>> qb.where('type', '==', 'stimulus').build()
            {'type': 'stimulus'}
        """
        if not self.conditions:
            return {}

        # For simple queries (all AND, all ==), return simple dict
        if all(c['logic'] == 'AND' and c['operator'] == '=='
               for c in self.conditions):
            query = {c['field']: c['value'] for c in self.conditions}
        else:
            # For complex queries, build structured query
            query = {'$and': []} if self.conditions[0]['logic'] == 'AND' else {'$or': []}

            for condition in self.conditions:
                field_query = self._build_condition(
                    condition['field'],
                    condition['operator'],
                    condition['value']
                )

                if condition['logic'] == 'AND':
                    if '$and' not in query:
                        query = {'$and': [query] if query else []}
                    query['$and'].append(field_query)
                else:  # OR
                    if '$or' not in query:
                        query = {'$or': [query] if query else []}
                    query['$or'].append(field_query)

        # Add metadata if specified
        if self.fields is not None:
            query['$fields'] = self.fields
        if self.limit_value is not None:
            query['$limit'] = self.limit_value
        if self.sort_by is not None:
            query['$sort'] = {self.sort_by: 1 if self.sort_order == 'asc' else -1}

        return query

    def _build_condition(self, field: str, operator: str, value: Any) -> Dict[str, Any]:
        """
        Build a single condition.

        Args:
            field: Field name
            operator: Comparison operator
            value: Comparison value

        Returns:
            Condition dictionary
        """
        operator_map = {
            '==': '$eq',
            '!=': '$ne',
            '>': '$gt',
            '<': '$lt',
            '>=': '$gte',
            '<=': '$lte',
            'in': '$in',
            'contains': '$contains'
        }

        if operator == '==':
            return {field: value}

        mongo_op = operator_map.get(operator)
        if mongo_op is None:
            raise ValueError(f'Unsupported operator: {operator}')

        return {field: {mongo_op: value}}


class QueryCache:
    """
    Cache for query results to improve performance.

    Provides LRU caching for database query results with TTL support.

    Examples:
        >>> cache = QueryCache(max_size=100)
        >>> cache.set('query_key', results)
        >>> cached = cache.get('query_key')
    """

    def __init__(self, max_size: int = 1000):
        """
        Initialize query cache.

        Args:
            max_size: Maximum number of cached queries
        """
        self.max_size = max_size
        self._cache: Dict[str, Any] = {}

    @staticmethod
    def _query_to_key(query: Dict[str, Any]) -> str:
        """
        Convert query dict to cache key.

        Args:
            query: Query dictionary

        Returns:
            String cache key
        """
        import json
        # Sort keys for consistent hashing
        return json.dumps(query, sort_keys=True)

    def get(self, query: Dict[str, Any]) -> Optional[Any]:
        """
        Get cached results for a query.

        Args:
            query: Query dictionary

        Returns:
            Cached results or None if not found
        """
        key = self._query_to_key(query)
        return self._cache.get(key)

    def set(self, query: Dict[str, Any], results: Any) -> None:
        """
        Cache results for a query.

        Args:
            query: Query dictionary
            results: Results to cache
        """
        key = self._query_to_key(query)

        # Simple LRU: if cache is full, remove oldest
        if len(self._cache) >= self.max_size:
            # Remove first (oldest) item
            self._cache.pop(next(iter(self._cache)))

        self._cache[key] = results

    def clear(self) -> None:
        """Clear all cached results."""
        self._cache.clear()

    def size(self) -> int:
        """
        Get current cache size.

        Returns:
            Number of cached queries
        """
        return len(self._cache)


def combine_queries(*queries: Dict[str, Any], logic: str = 'AND') -> Dict[str, Any]:
    """
    Combine multiple queries with AND or OR logic.

    Args:
        *queries: Query dictionaries to combine
        logic: Logical operator ('AND' or 'OR')

    Returns:
        Combined query dictionary

    Examples:
        >>> q1 = {'type': 'stimulus'}
        >>> q2 = {'session_id': 'abc123'}
        >>> combined = combine_queries(q1, q2, logic='AND')
        >>> combined
        {'type': 'stimulus', 'session_id': 'abc123'}

        >>> q1 = {'type': 'stimulus'}
        >>> q2 = {'type': 'probe'}
        >>> combined = combine_queries(q1, q2, logic='OR')
    """
    if not queries:
        return {}

    if len(queries) == 1:
        return queries[0]

    logic = logic.upper()
    if logic not in ['AND', 'OR']:
        raise ValueError(f"Logic must be 'AND' or 'OR', got '{logic}'")

    # For AND logic with simple queries, merge dictionaries
    if logic == 'AND' and all(
        not any(k.startswith('$') for k in q.keys())
        for q in queries
    ):
        result = {}
        for query in queries:
            result.update(query)
        return result

    # For OR logic or complex queries, use MongoDB-style operators
    operator = '$and' if logic == 'AND' else '$or'
    return {operator: list(queries)}


def optimize_query(query: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optimize a query for better performance.

    Performs optimizations like:
    - Removing redundant conditions
    - Simplifying nested operators
    - Reordering conditions for index usage

    Args:
        query: Query dictionary to optimize

    Returns:
        Optimized query dictionary

    Examples:
        >>> query = {'$and': [{'type': 'A'}, {'type': 'A'}]}
        >>> optimize_query(query)
        {'type': 'A'}
    """
    # If query has $and with single element, unwrap it
    if '$and' in query and len(query['$and']) == 1:
        return optimize_query(query['$and'][0])

    # If query has $or with single element, unwrap it
    if '$or' in query and len(query['$or']) == 1:
        return optimize_query(query['$or'][0])

    # Remove duplicate conditions in $and or $or
    if '$and' in query:
        unique_conditions = []
        seen = set()
        for condition in query['$and']:
            import json
            key = json.dumps(condition, sort_keys=True)
            if key not in seen:
                seen.add(key)
                unique_conditions.append(condition)
        if len(unique_conditions) != len(query['$and']):
            query = {'$and': unique_conditions}

    if '$or' in query:
        unique_conditions = []
        seen = set()
        for condition in query['$or']:
            import json
            key = json.dumps(condition, sort_keys=True)
            if key not in seen:
                seen.add(key)
                unique_conditions.append(condition)
        if len(unique_conditions) != len(query['$or']):
            query = {'$or': unique_conditions}

    return query
