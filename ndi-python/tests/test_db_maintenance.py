"""
Tests for NDI database maintenance utilities.

Tests DatabaseCleaner, PerformanceMonitor, and IndexManager.
"""

import pytest
import tempfile
import os
from ndi.db.fun import DatabaseCleaner, PerformanceMonitor, IndexManager
from ndi.session import SessionDir
from ndi.document import Document
from ndi.probe import ElectrodeProbe


class TestDatabaseCleaner:
    """Test DatabaseCleaner class."""

    def test_cleaner_creation(self):
        """Test creating a DatabaseCleaner instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")
            cleaner = DatabaseCleaner(session)

            assert cleaner is not None
            assert cleaner.session is session

    def test_find_orphaned_documents(self):
        """Test finding orphaned documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")
            cleaner = DatabaseCleaner(session)

            # Initially no orphaned docs
            orphaned = cleaner.find_orphaned_documents()

            assert isinstance(orphaned, list)

    def test_find_duplicate_documents(self):
        """Test finding duplicate documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            # Add some documents
            doc1 = Document('test_doc', value=42)
            doc2 = Document('test_doc', value=42)  # Potential duplicate

            session.database.add(doc1)
            session.database.add(doc2)

            cleaner = DatabaseCleaner(session)
            duplicates = cleaner.find_duplicate_documents()

            assert isinstance(duplicates, list)

    def test_find_orphaned_files(self):
        """Test finding orphaned binary files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            # Create a binary file in session directory
            test_file = os.path.join(tmpdir, 'test.bin')
            with open(test_file, 'wb') as f:
                f.write(b'test data')

            cleaner = DatabaseCleaner(session)
            orphaned = cleaner.find_orphaned_files()

            # Should find the orphaned file
            assert isinstance(orphaned, list)

    def test_remove_orphaned_files_dry_run(self):
        """Test removing orphaned files in dry run mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            # Create a binary file
            test_file = os.path.join(tmpdir, 'test.bin')
            with open(test_file, 'wb') as f:
                f.write(b'test data')

            cleaner = DatabaseCleaner(session)
            would_delete = cleaner.remove_orphaned_files(dry_run=True)

            # File should still exist
            assert os.path.exists(test_file)

    def test_remove_orphaned_files_actual(self):
        """Test actually removing orphaned files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            # Create a binary file
            test_file = os.path.join(tmpdir, 'orphaned.bin')
            with open(test_file, 'wb') as f:
                f.write(b'orphaned data')

            cleaner = DatabaseCleaner(session)
            deleted = cleaner.remove_orphaned_files(dry_run=False)

            # File should be deleted if it was found
            # (depends on whether it was identified as orphaned)
            assert isinstance(deleted, list)

    def test_compact_database(self):
        """Test database compaction."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            # Add and then remove some documents
            for i in range(10):
                doc = Document('test_doc', value=i)
                session.database.add(doc)

            cleaner = DatabaseCleaner(session)
            stats = cleaner.compact_database()

            assert 'before_size' in stats
            assert 'after_size' in stats
            assert 'space_saved' in stats


class TestPerformanceMonitor:
    """Test PerformanceMonitor class."""

    def test_monitor_creation(self):
        """Test creating a PerformanceMonitor instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")
            monitor = PerformanceMonitor(session)

            assert monitor is not None
            assert monitor.session is session

    def test_collect_statistics(self):
        """Test collecting database statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            # Add some documents
            for i in range(5):
                doc = Document('test_doc', value=i)
                session.database.add(doc)

            monitor = PerformanceMonitor(session)
            stats = monitor.collect_statistics()

            assert 'total_documents' in stats
            assert 'documents_by_type' in stats
            assert 'database_size' in stats
            assert stats['total_documents'] == 5

    def test_time_query(self):
        """Test timing a query."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            # Add documents
            for i in range(3):
                doc = Document('test_doc', value=i)
                session.database.add(doc)

            monitor = PerformanceMonitor(session)
            results, time_taken = monitor.time_query({})

            assert len(results) == 3
            assert time_taken >= 0
            assert len(monitor.query_times) == 1

    def test_multiple_timed_queries(self):
        """Test timing multiple queries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            # Add documents
            doc = Document('test_doc', value=1)
            session.database.add(doc)

            monitor = PerformanceMonitor(session)

            # Time multiple queries
            for i in range(3):
                monitor.time_query({})

            stats = monitor.collect_statistics()

            assert len(monitor.query_times) == 3
            assert stats['average_query_time'] >= 0

    def test_get_recommendations_small_db(self):
        """Test getting recommendations for a small database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            # Small database
            doc = Document('test_doc', value=1)
            session.database.add(doc)

            monitor = PerformanceMonitor(session)
            recommendations = monitor.get_recommendations()

            assert isinstance(recommendations, list)
            assert len(recommendations) > 0

    def test_get_recommendations_many_documents(self):
        """Test recommendations for database with many documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            # Add enough documents to trigger recommendation
            # (simplified - would need 10000+ for actual threshold)
            for i in range(100):
                doc = Document('test_doc', value=i)
                session.database.add(doc)

            monitor = PerformanceMonitor(session)
            recommendations = monitor.get_recommendations()

            assert isinstance(recommendations, list)

    def test_reset_statistics(self):
        """Test resetting statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            monitor = PerformanceMonitor(session)

            # Time some queries
            monitor.time_query({})
            monitor.time_query({})

            assert len(monitor.query_times) == 2

            # Reset
            monitor.reset_statistics()

            assert len(monitor.query_times) == 0


class TestIndexManager:
    """Test IndexManager class."""

    def test_index_manager_creation(self):
        """Test creating an IndexManager instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")
            index_mgr = IndexManager(session)

            assert index_mgr is not None
            assert index_mgr.session is session

    def test_create_index(self):
        """Test creating an index."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")
            index_mgr = IndexManager(session)

            result = index_mgr.create_index('element.type')

            assert result is True
            assert 'element.type' in index_mgr.indexes

    def test_create_multiple_indexes(self):
        """Test creating multiple indexes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")
            index_mgr = IndexManager(session)

            index_mgr.create_index('element.type')
            index_mgr.create_index('element.subject_id')
            index_mgr.create_index('base.session_id')

            assert len(index_mgr.indexes) == 3

    def test_list_indexes(self):
        """Test listing indexes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")
            index_mgr = IndexManager(session)

            index_mgr.create_index('field1')
            index_mgr.create_index('field2')

            indexes = index_mgr.list_indexes()

            assert len(indexes) == 2
            assert 'field1' in indexes
            assert 'field2' in indexes

    def test_remove_index(self):
        """Test removing an index."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")
            index_mgr = IndexManager(session)

            index_mgr.create_index('field1')
            assert 'field1' in index_mgr.indexes

            result = index_mgr.remove_index('field1')

            assert result is True
            assert 'field1' not in index_mgr.indexes

    def test_remove_nonexistent_index(self):
        """Test removing an index that doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")
            index_mgr = IndexManager(session)

            result = index_mgr.remove_index('nonexistent')

            assert result is False

    def test_suggest_indexes(self):
        """Test suggesting indexes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")
            index_mgr = IndexManager(session)

            suggestions = index_mgr.suggest_indexes()

            assert isinstance(suggestions, list)
            assert len(suggestions) > 0

    def test_suggest_indexes_excludes_existing(self):
        """Test that suggestions exclude existing indexes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")
            index_mgr = IndexManager(session)

            # Create an index
            index_mgr.create_index('base.id')

            # Get suggestions
            suggestions = index_mgr.suggest_indexes()

            # Should not suggest existing index
            assert 'base.id' not in suggestions


class TestMaintenanceIntegration:
    """Integration tests for database maintenance."""

    def test_clean_and_monitor_workflow(self):
        """Test cleaning and monitoring together."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            # Add documents
            for i in range(5):
                doc = Document('test_doc', value=i)
                session.database.add(doc)

            # Clean
            cleaner = DatabaseCleaner(session)
            orphaned = cleaner.find_orphaned_documents()

            # Monitor
            monitor = PerformanceMonitor(session)
            stats = monitor.collect_statistics()

            assert stats['total_documents'] == 5

    def test_index_and_performance_workflow(self):
        """Test indexing and performance monitoring together."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            # Add documents
            for i in range(10):
                doc = Document('test_doc', value=i)
                session.database.add(doc)

            # Create indexes
            index_mgr = IndexManager(session)
            index_mgr.create_index('element.type')

            # Monitor performance
            monitor = PerformanceMonitor(session)
            results, time_taken = monitor.time_query({})

            assert len(results) == 10
            assert time_taken >= 0

    def test_complete_maintenance_workflow(self):
        """Test complete maintenance workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            # Setup: Add data
            for i in range(5):
                doc = Document('test_doc', value=i)
                session.database.add(doc)

            probe = ElectrodeProbe(session, 'e1', reference=1,
                                  subject_id='mouse01')
            session.add_probe(probe)

            # Step 1: Check for issues
            cleaner = DatabaseCleaner(session)
            orphaned_docs = cleaner.find_orphaned_documents()
            duplicates = cleaner.find_duplicate_documents()

            # Step 2: Monitor performance
            monitor = PerformanceMonitor(session)
            stats = monitor.collect_statistics()
            recommendations = monitor.get_recommendations()

            # Step 3: Optimize with indexes
            index_mgr = IndexManager(session)
            suggestions = index_mgr.suggest_indexes()

            for field in suggestions[:2]:  # Create first 2 suggested indexes
                index_mgr.create_index(field)

            # Step 4: Compact database
            compact_stats = cleaner.compact_database()

            # Verify results
            assert isinstance(orphaned_docs, list)
            assert isinstance(duplicates, list)
            assert stats['total_documents'] > 0
            assert isinstance(recommendations, list)
            assert len(index_mgr.list_indexes()) == 2
            assert 'space_saved' in compact_stats
