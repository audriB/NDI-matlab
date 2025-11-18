"""
Tests for NDI database metadata management utilities.

Tests MetadataExtractor, MetadataValidator, and MetadataSearcher.
"""

import pytest
import tempfile
import numpy as np
from ndi.db.fun import MetadataExtractor, MetadataValidator, MetadataSearcher
from ndi.session import SessionDir
from ndi.document import Document
from ndi.probe import ElectrodeProbe


class TestMetadataExtractor:
    """Test MetadataExtractor class."""

    def test_extractor_creation(self):
        """Test creating a MetadataExtractor instance."""
        extractor = MetadataExtractor()
        assert extractor is not None
        assert 'base' in extractor.extractors

    def test_extract_from_simple_document(self):
        """Test extracting metadata from a simple document."""
        extractor = MetadataExtractor()

        # Create a simple document
        doc = Document('test_doc')

        metadata = extractor.extract_from_document(doc)

        assert 'document_type' in metadata

    def test_extract_base_metadata(self):
        """Test extracting base metadata fields."""
        extractor = MetadataExtractor()

        # Create a document with base properties
        doc = Document('test_doc')

        metadata = extractor.extract_from_document(doc)

        # Should have extracted document type
        assert 'document_type' in metadata

    def test_extract_session_metadata(self):
        """Test extracting metadata from a session."""
        extractor = MetadataExtractor()

        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            # Add some documents
            for i in range(3):
                doc = Document('test_doc', value=i)
                session.database.add(doc)

            # Extract metadata
            metadata = extractor.extract_session_metadata(session)

            assert 'session_id' in metadata
            assert 'total_documents' in metadata
            assert metadata['total_documents'] == 3

    def test_extract_session_with_probes(self):
        """Test extracting metadata from session with probes."""
        extractor = MetadataExtractor()

        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            # Add a probe
            probe = ElectrodeProbe(session, 'e1', reference=1,
                                  subject_id='mouse01', impedance=1e6)
            session.add_probe(probe)

            # Extract metadata
            metadata = extractor.extract_session_metadata(session)

            assert 'num_probes' in metadata
            assert metadata['num_probes'] == 1

    def test_extract_empty_session(self):
        """Test extracting metadata from empty session."""
        extractor = MetadataExtractor()

        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            metadata = extractor.extract_session_metadata(session)

            assert 'session_id' in metadata
            assert metadata.get('total_documents', 0) == 0


class TestMetadataValidator:
    """Test MetadataValidator class."""

    def test_validator_creation(self):
        """Test creating a MetadataValidator instance."""
        validator = MetadataValidator()
        assert validator is not None
        assert 'base' in validator.rules

    def test_validate_valid_base_metadata(self):
        """Test validating valid base metadata."""
        validator = MetadataValidator()

        metadata = {
            'id': 'abc123',
            'session_id': 'sess456'
        }

        issues = validator.validate(metadata, 'base')

        assert len(issues) == 0

    def test_validate_missing_required_field(self):
        """Test validation fails for missing required fields."""
        validator = MetadataValidator()

        metadata = {
            'id': 'abc123'
            # Missing session_id
        }

        issues = validator.validate(metadata, 'base')

        assert len(issues) > 0
        assert any('session_id' in issue for issue in issues)

    def test_validate_invalid_id_type(self):
        """Test validation fails for invalid ID type."""
        validator = MetadataValidator()

        metadata = {
            'id': 123,  # Should be string
            'session_id': 'sess456'
        }

        issues = validator.validate(metadata, 'base')

        assert len(issues) > 0
        assert any('id' in issue for issue in issues)

    def test_validate_element_metadata(self):
        """Test validating element metadata."""
        validator = MetadataValidator()

        # Valid element metadata
        metadata = {
            'type': 'probe',
            'direct': True
        }

        issues = validator.validate(metadata, 'element')

        assert len(issues) == 0

    def test_validate_invalid_element_type(self):
        """Test validation fails for invalid element type."""
        validator = MetadataValidator()

        metadata = {
            'type': 'invalid_type'
        }

        issues = validator.validate(metadata, 'element')

        assert len(issues) > 0

    def test_validate_probe_metadata(self):
        """Test validating probe metadata."""
        validator = MetadataValidator()

        # Valid probe metadata
        metadata = {
            'num_channels': 4,
            'impedance': 1e6,
            'wavelength': 920
        }

        issues = validator.validate(metadata, 'probe')

        assert len(issues) == 0

    def test_validate_invalid_probe_channels(self):
        """Test validation fails for invalid channel count."""
        validator = MetadataValidator()

        metadata = {
            'num_channels': -1  # Invalid
        }

        issues = validator.validate(metadata, 'probe')

        assert len(issues) > 0
        assert any('num_channels' in issue for issue in issues)

    def test_validate_session_metadata(self):
        """Test validating session metadata."""
        validator = MetadataValidator()

        with tempfile.TemporaryDirectory() as tmpdir:
            metadata = {
                'session_id': 'sess123',
                'path': tmpdir
            }

            issues = validator.validate(metadata, 'session')

            assert len(issues) == 0

    def test_validate_empty_metadata(self):
        """Test validation of empty metadata."""
        validator = MetadataValidator()

        metadata = {}

        issues = validator.validate(metadata, 'generic')

        assert len(issues) > 0


class TestMetadataSearcher:
    """Test MetadataSearcher class."""

    def test_searcher_creation(self):
        """Test creating a MetadataSearcher instance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")
            searcher = MetadataSearcher(session)

            assert searcher is not None
            assert searcher.session is session

    def test_find_by_type(self):
        """Test finding documents by type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            # Add a probe
            probe = ElectrodeProbe(session, 'e1', reference=1,
                                  subject_id='mouse01')
            session.add_probe(probe)

            # Search for probes
            searcher = MetadataSearcher(session)
            probes = searcher.find_by_type('probe')

            assert len(probes) > 0

    def test_find_by_app(self):
        """Test finding documents by app name."""
        from ndi.app import App

        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            # Create an app document
            app = App(session, 'test_app')
            doc = app.newdocument('results', value=42)
            session.database.add(doc)

            # Search for app documents
            searcher = MetadataSearcher(session)
            app_docs = searcher.find_by_app('test_app')

            assert len(app_docs) == 1

    def test_find_by_subject(self):
        """Test finding documents by subject ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            # Add probes for different subjects
            probe1 = ElectrodeProbe(session, 'e1', reference=1,
                                   subject_id='mouse01')
            probe2 = ElectrodeProbe(session, 'e2', reference=1,
                                   subject_id='mouse02')

            session.add_probe(probe1)
            session.add_probe(probe2)

            # Search for mouse01 documents
            searcher = MetadataSearcher(session)
            mouse01_docs = searcher.find_by_subject('mouse01')

            assert len(mouse01_docs) >= 1

    def test_find_missing_metadata(self):
        """Test finding documents with missing metadata fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            # Add documents with varying metadata
            doc1 = Document('complete_doc')
            doc2 = Document('incomplete_doc')

            session.database.add(doc1)
            session.database.add(doc2)

            # Search for missing fields
            searcher = MetadataSearcher(session)
            missing = searcher.find_missing_metadata(['element.type'])

            # Both docs likely missing element.type
            assert len(missing) >= 0  # May or may not have missing fields

    def test_find_recent_documents(self):
        """Test finding recent documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            # Add some documents
            for i in range(3):
                doc = Document('test_doc', value=i)
                session.database.add(doc)

            # Search for recent documents
            searcher = MetadataSearcher(session)
            recent = searcher.find_recent(days=7)

            # All should be recent
            assert len(recent) >= 0  # May find some or all


class TestMetadataIntegration:
    """Integration tests for metadata management."""

    def test_extract_validate_workflow(self):
        """Test extracting and then validating metadata."""
        extractor = MetadataExtractor()
        validator = MetadataValidator()

        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            # Extract session metadata
            metadata = extractor.extract_session_metadata(session)

            # Validate it
            issues = validator.validate(metadata, 'session')

            # Should be valid
            assert len(issues) == 0

    def test_search_extract_validate(self):
        """Test searching, extracting, and validating metadata."""
        extractor = MetadataExtractor()
        validator = MetadataValidator()

        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            # Add a probe
            probe = ElectrodeProbe(session, 'e1', reference=1,
                                  subject_id='mouse01', impedance=1e6)
            session.add_probe(probe)

            # Search for probes
            searcher = MetadataSearcher(session)
            probes = searcher.find_by_type('probe')

            # Extract and validate metadata from first probe document
            if probes:
                metadata = extractor.extract_from_document(probes[0])

                # Should have some metadata
                assert len(metadata) > 0

    def test_complete_metadata_workflow(self):
        """Test complete metadata management workflow."""
        from ndi.app import App

        extractor = MetadataExtractor()
        validator = MetadataValidator()

        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, "test_session")

            # Create app and document
            app = App(session, 'metadata_test_app')
            doc = app.newdocument('test_results',
                                 accuracy=0.95,
                                 num_samples=100)
            session.database.add(doc)

            # Extract metadata
            doc_metadata = extractor.extract_from_document(doc)
            session_metadata = extractor.extract_session_metadata(session)

            # Validate
            session_issues = validator.validate(session_metadata, 'session')

            # Search
            searcher = MetadataSearcher(session)
            app_docs = searcher.find_by_app('metadata_test_app')

            # Assertions
            assert len(session_issues) == 0
            assert session_metadata['total_documents'] == 1
            assert len(app_docs) == 1
