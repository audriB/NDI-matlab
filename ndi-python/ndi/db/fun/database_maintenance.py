"""
NDI Database Maintenance - Utilities for database cleanup and optimization.

This module provides utilities for maintaining NDI databases, including
cleanup of orphaned documents, performance monitoring, and optimization.

MATLAB Equivalent: Various database maintenance patterns in NDI-MATLAB
"""

from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime
import os


class DatabaseCleaner:
    """
    Clean up orphaned documents and files in NDI databases.

    Provides utilities for finding and removing documents that are no longer
    referenced, duplicate documents, and orphaned binary files.

    Examples:
        >>> cleaner = DatabaseCleaner(session)
        >>> orphaned = cleaner.find_orphaned_documents()
        >>> cleaner.remove_orphaned_files()
    """

    def __init__(self, session: Any):
        """
        Initialize database cleaner.

        Args:
            session: NDI session object to clean
        """
        self.session = session

    def find_orphaned_documents(self) -> List[Any]:
        """
        Find documents that have broken dependencies.

        Returns documents that reference non-existent dependencies.

        Returns:
            List of orphaned documents

        Examples:
            >>> cleaner = DatabaseCleaner(session)
            >>> orphaned = cleaner.find_orphaned_documents()
            >>> len(orphaned)
            0
        """
        from .finddocs_missing_dependencies import finddocs_missing_dependencies

        try:
            orphaned = finddocs_missing_dependencies(self.session)
            return orphaned if orphaned else []
        except Exception as e:
            print(f"Error finding orphaned documents: {e}")
            return []

    def find_duplicate_documents(self) -> List[Tuple[Any, Any]]:
        """
        Find documents that appear to be duplicates.

        Identifies documents with identical content but different IDs.

        Returns:
            List of (doc1, doc2) tuples representing duplicates

        Examples:
            >>> duplicates = cleaner.find_duplicate_documents()
        """
        all_docs = self.session.database.search({})
        duplicates = []

        # Group documents by their core properties
        seen_hashes = {}

        for doc in all_docs:
            doc_hash = self._document_hash(doc)
            if doc_hash in seen_hashes:
                duplicates.append((seen_hashes[doc_hash], doc))
            else:
                seen_hashes[doc_hash] = doc

        return duplicates

    def _document_hash(self, doc: Any) -> str:
        """
        Generate a hash of document content (excluding ID and timestamps).

        Args:
            doc: Document to hash

        Returns:
            Hash string
        """
        import json
        import hashlib

        try:
            # Get document properties as dict
            props = doc.document_properties.to_dict() if hasattr(
                doc.document_properties, 'to_dict'
            ) else str(doc.document_properties)

            # Remove fields that should differ (id, created, etc.)
            if isinstance(props, dict):
                props_copy = props.copy()
                if 'base' in props_copy:
                    base = props_copy['base'].copy() if isinstance(
                        props_copy['base'], dict
                    ) else props_copy['base']
                    if isinstance(base, dict):
                        base.pop('id', None)
                        base.pop('created', None)
                        props_copy['base'] = base

                content = json.dumps(props_copy, sort_keys=True)
            else:
                content = str(props)

            return hashlib.md5(content.encode()).hexdigest()

        except Exception:
            # If we can't hash it, return a random value so it won't match
            import uuid
            return str(uuid.uuid4())

    def find_orphaned_files(self) -> List[str]:
        """
        Find binary files that are not referenced by any document.

        Returns:
            List of orphaned file paths

        Examples:
            >>> orphaned_files = cleaner.find_orphaned_files()
        """
        # Get all documents
        all_docs = self.session.database.search({})

        # Collect all file references from documents
        referenced_files = set()
        for doc in all_docs:
            files = self._get_document_files(doc)
            referenced_files.update(files)

        # Get all files in the database directory
        db_path = self.session.path
        all_files = set()

        # Look for binary files (common extensions)
        binary_extensions = ['.bin', '.dat', '.raw', '.h5', '.hdf5', '.mat']

        for root, dirs, files in os.walk(db_path):
            for file in files:
                if any(file.endswith(ext) for ext in binary_extensions):
                    full_path = os.path.join(root, file)
                    all_files.add(full_path)

        # Find orphaned files
        orphaned = all_files - referenced_files

        return list(orphaned)

    def _get_document_files(self, doc: Any) -> Set[str]:
        """
        Get all file references from a document.

        Args:
            doc: Document to extract file references from

        Returns:
            Set of file paths
        """
        files = set()

        # Check for file references in document
        try:
            if hasattr(doc, 'files'):
                doc_files = doc.files() if callable(doc.files) else doc.files
                if doc_files:
                    files.update(str(f) for f in doc_files)
        except Exception:
            pass

        return files

    def remove_orphaned_files(self, dry_run: bool = True) -> List[str]:
        """
        Remove orphaned binary files from the database.

        Args:
            dry_run: If True, only report files that would be deleted

        Returns:
            List of files removed (or would be removed if dry_run=True)

        Examples:
            >>> # Check what would be deleted
            >>> would_delete = cleaner.remove_orphaned_files(dry_run=True)
            >>> # Actually delete
            >>> deleted = cleaner.remove_orphaned_files(dry_run=False)
        """
        orphaned = self.find_orphaned_files()

        if not dry_run:
            for file_path in orphaned:
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error removing {file_path}: {e}")

        return orphaned

    def compact_database(self) -> Dict[str, Any]:
        """
        Compact the database to reclaim space.

        Performs database-specific compaction operations.

        Returns:
            Dictionary with compaction statistics

        Examples:
            >>> stats = cleaner.compact_database()
            >>> stats['space_saved']
            1024000
        """
        stats = {
            'before_size': 0,
            'after_size': 0,
            'space_saved': 0,
            'documents_removed': 0
        }

        # Get database path
        db_path = self.session.path

        # Calculate size before
        stats['before_size'] = self._get_directory_size(db_path)

        # Database-specific compaction
        if hasattr(self.session.database, 'compact'):
            try:
                self.session.database.compact()
            except Exception as e:
                print(f"Error compacting database: {e}")

        # Calculate size after
        stats['after_size'] = self._get_directory_size(db_path)
        stats['space_saved'] = stats['before_size'] - stats['after_size']

        return stats

    def _get_directory_size(self, path: str) -> int:
        """
        Get total size of a directory in bytes.

        Args:
            path: Directory path

        Returns:
            Size in bytes
        """
        total_size = 0
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
        return total_size


class PerformanceMonitor:
    """
    Monitor database performance and provide optimization suggestions.

    Tracks query performance, database size, and provides recommendations
    for optimization.

    Examples:
        >>> monitor = PerformanceMonitor(session)
        >>> stats = monitor.collect_statistics()
        >>> recommendations = monitor.get_recommendations()
    """

    def __init__(self, session: Any):
        """
        Initialize performance monitor.

        Args:
            session: NDI session object to monitor
        """
        self.session = session
        self.query_times: List[float] = []

    def collect_statistics(self) -> Dict[str, Any]:
        """
        Collect database statistics.

        Returns:
            Dictionary of statistics

        Examples:
            >>> stats = monitor.collect_statistics()
            >>> stats['total_documents']
            42
        """
        stats = {
            'total_documents': 0,
            'documents_by_type': {},
            'database_size': 0,
            'average_query_time': 0,
        }

        # Count documents
        all_docs = self.session.database.search({})
        stats['total_documents'] = len(all_docs)

        # Count by type
        doc_types = {}
        for doc in all_docs:
            try:
                doc_type = doc.document_properties.document_class.definition
                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            except AttributeError:
                doc_types['unknown'] = doc_types.get('unknown', 0) + 1

        stats['documents_by_type'] = doc_types

        # Database size
        db_path = self.session.path
        stats['database_size'] = self._get_directory_size(db_path)

        # Average query time
        if self.query_times:
            stats['average_query_time'] = sum(self.query_times) / len(self.query_times)

        return stats

    def _get_directory_size(self, path: str) -> int:
        """Get directory size in bytes."""
        total_size = 0
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
        return total_size

    def time_query(self, query: Dict[str, Any]) -> Tuple[List[Any], float]:
        """
        Execute a query and measure its time.

        Args:
            query: Query to execute

        Returns:
            Tuple of (results, execution_time_seconds)

        Examples:
            >>> results, time_taken = monitor.time_query({'type': 'probe'})
            >>> print(f"Query took {time_taken:.3f} seconds")
        """
        import time

        start = time.time()
        results = self.session.database.search(query)
        elapsed = time.time() - start

        self.query_times.append(elapsed)

        return results, elapsed

    def get_recommendations(self) -> List[str]:
        """
        Get optimization recommendations based on statistics.

        Returns:
            List of recommendation strings

        Examples:
            >>> recommendations = monitor.get_recommendations()
            >>> for rec in recommendations:
            ...     print(rec)
        """
        recommendations = []
        stats = self.collect_statistics()

        # Large database
        if stats['database_size'] > 1_000_000_000:  # 1 GB
            recommendations.append(
                "Database is large (>1GB). Consider archiving old documents."
            )

        # Many documents
        if stats['total_documents'] > 10000:
            recommendations.append(
                "Large number of documents (>10k). Consider using query caching."
            )

        # Slow queries
        if stats['average_query_time'] > 1.0:
            recommendations.append(
                "Queries are slow (>1s average). Consider database indexing."
            )

        # Unbalanced document types
        if stats['documents_by_type']:
            max_count = max(stats['documents_by_type'].values())
            total = stats['total_documents']
            if max_count > 0.8 * total:
                recommendations.append(
                    "Document types are unbalanced. Consider partitioning by type."
                )

        if not recommendations:
            recommendations.append("Database performance is good. No recommendations.")

        return recommendations

    def reset_statistics(self) -> None:
        """Reset collected statistics."""
        self.query_times.clear()


class IndexManager:
    """
    Manage database indexes for improved query performance.

    Provides utilities for creating, removing, and analyzing database indexes.

    Examples:
        >>> index_mgr = IndexManager(session)
        >>> index_mgr.create_index('element.type')
        >>> indexes = index_mgr.list_indexes()
    """

    def __init__(self, session: Any):
        """
        Initialize index manager.

        Args:
            session: NDI session object
        """
        self.session = session
        self.indexes: Set[str] = set()

    def create_index(self, field: str) -> bool:
        """
        Create an index on a field.

        Args:
            field: Field name to index (dot notation supported)

        Returns:
            True if index was created successfully

        Examples:
            >>> index_mgr.create_index('element.type')
            True
        """
        # Note: This is a placeholder. Actual implementation depends on
        # the database backend (SQLite, TinyDB, etc.)
        self.indexes.add(field)
        return True

    def remove_index(self, field: str) -> bool:
        """
        Remove an index.

        Args:
            field: Field name

        Returns:
            True if index was removed successfully

        Examples:
            >>> index_mgr.remove_index('element.type')
            True
        """
        if field in self.indexes:
            self.indexes.remove(field)
            return True
        return False

    def list_indexes(self) -> List[str]:
        """
        List all current indexes.

        Returns:
            List of indexed field names

        Examples:
            >>> indexes = index_mgr.list_indexes()
            >>> 'element.type' in indexes
            True
        """
        return list(self.indexes)

    def suggest_indexes(self) -> List[str]:
        """
        Suggest fields that should be indexed based on usage.

        Returns:
            List of recommended field names to index

        Examples:
            >>> suggestions = index_mgr.suggest_indexes()
        """
        # Common fields that benefit from indexing
        common_fields = [
            'base.id',
            'base.session_id',
            'base.type',
            'element.type',
            'element.subject_id',
            'app.name',
        ]

        # Filter out already indexed fields
        suggestions = [f for f in common_fields if f not in self.indexes]

        return suggestions
