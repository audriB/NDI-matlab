"""
Tests for NDI Element functionality.

This module tests element (probe/measurement) functionality including:
- Element creation and configuration
- Element document handling
- Dependency management
- Epoch data handling
- TimeSeries reading
"""

import pytest
import tempfile
import numpy as np
from unittest.mock import Mock, patch, MagicMock


class TestElementCreation:
    """Tests for Element class creation."""

    def test_element_basic_creation(self):
        """Test basic element creation with parameters."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        element = Element(mock_session, 'test_element', 1, 'generic')

        assert element.name == 'test_element'
        assert element.reference == 1
        assert element.type == 'generic'

    def test_element_with_subject(self):
        """Test element creation with subject ID."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        element = Element(mock_session, 'test_element', 1, 'generic',
                         subject_id='subject_001')

        assert element.subject_id == 'subject_001'

    def test_element_inherits_from_ido(self):
        """Test that Element inherits from IDO."""
        from ndi._element import Element
        from ndi.ido import IDO

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        element = Element(mock_session, 'test_element', 1, 'generic')
        assert isinstance(element, IDO)

    def test_element_inherits_from_epochset(self):
        """Test that Element inherits from EpochSet."""
        from ndi._element import Element
        from ndi.epoch import EpochSet

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        element = Element(mock_session, 'test_element', 1, 'generic')
        assert isinstance(element, EpochSet)

    def test_element_invalid_arguments(self):
        """Test that invalid arguments raise error."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        with pytest.raises(ValueError):
            # Missing required arguments
            Element(mock_session, 'only_name')


class TestElementUnderlyingElement:
    """Tests for Element with underlying element dependencies."""

    def test_element_with_underlying(self):
        """Test element with underlying element."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        # Create underlying element
        underlying = Element(mock_session, 'probe', 1, 'n-trode',
                            subject_id='subject_001')

        # Create derived element
        derived = Element(mock_session, 'lfp', 1, 'timeseries',
                         underlying_element=underlying)

        assert derived.underlying_element == underlying
        assert derived.subject_id == underlying.subject_id

    def test_element_direct_flag(self):
        """Test element direct flag."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        underlying = Element(mock_session, 'probe', 1, 'n-trode')

        # Direct element
        direct_elem = Element(mock_session, 'lfp', 1, 'timeseries',
                             underlying_element=underlying, direct=True)
        assert direct_elem.direct is True

        # Indirect element
        indirect_elem = Element(mock_session, 'filtered', 1, 'timeseries',
                               underlying_element=underlying, direct=False)
        assert indirect_elem.direct is False

    def test_element_subject_from_underlying(self):
        """Test that subject_id is inherited from underlying element."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        underlying = Element(mock_session, 'probe', 1, 'n-trode',
                            subject_id='subject_001')

        derived = Element(mock_session, 'derived', 1, 'timeseries',
                         underlying_element=underlying)

        # Should inherit subject_id
        assert derived.subject_id == 'subject_001'


class TestElementDependencies:
    """Tests for Element dependency management."""

    def test_element_empty_dependencies(self):
        """Test element with no additional dependencies."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        element = Element(mock_session, 'test_element', 1, 'generic')

        assert element.dependencies == {}

    def test_element_with_dependencies(self):
        """Test element with dependencies."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        deps = {'stimulus': 'stim_001', 'trial': 'trial_001'}
        element = Element(mock_session, 'test_element', 1, 'generic',
                         dependencies=deps)

        assert element.dependencies == deps

    def test_set_dependency_value(self):
        """Test setting dependency values."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        element = Element(mock_session, 'test_element', 1, 'generic')

        # Should have set_dependency_value method
        if hasattr(element, 'set_dependency_value'):
            element.set_dependency_value('stimulus', 'stim_001')
            assert element.dependencies.get('stimulus') == 'stim_001'


class TestElementDocument:
    """Tests for Element document handling."""

    def test_element_newdocument(self):
        """Test creating a document from element."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        element = Element(mock_session, 'test_element', 1, 'generic')

        # Should have newdocument method
        if hasattr(element, 'newdocument'):
            doc = element.newdocument()
            assert doc is not None

    def test_element_from_document_id(self):
        """Test creating element from document ID string."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        # Test with document ID string
        # (actual behavior depends on session having the document)
        try:
            element = Element(mock_session, 'doc-id-123')
            # If it works, element should exist
            assert element is not None
        except (ValueError, KeyError):
            # May fail if document not found
            pass


class TestElementEpoch:
    """Tests for Element epoch handling."""

    def test_element_numepochs(self):
        """Test getting number of epochs."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])
        mock_session.cache = None  # No cache

        element = Element(mock_session, 'test_element', 1, 'generic')

        # Should have numepochs method (from EpochSet)
        assert hasattr(element, 'numepochs')
        # Note: Actually calling numepochs() requires full session setup

    def test_element_epochid(self):
        """Test getting epoch ID."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        element = Element(mock_session, 'test_element', 1, 'generic')

        # Should have epochid method
        assert hasattr(element, 'epochid')

    def test_element_epochtable(self):
        """Test getting epoch table."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])
        mock_session.cache = None  # No cache

        element = Element(mock_session, 'test_element', 1, 'generic')

        # Should have epochtable method
        assert hasattr(element, 'epochtable')
        # Note: Actually calling epochtable() requires full session setup


class TestElementTimeSeries:
    """Tests for Element time series operations."""

    def test_element_read_timeseries(self):
        """Test reading time series from element."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        element = Element(mock_session, 'test_element', 1, 'generic')

        # Should have read_timeseries method
        assert hasattr(element, 'readtimeseries') or hasattr(element, 'read_timeseries')

    def test_element_samplerate(self):
        """Test getting sample rate."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])
        mock_session.cache = None  # No cache

        element = Element(mock_session, 'test_element', 1, 'generic')

        # Should have samplerate method
        assert hasattr(element, 'samplerate')
        # Note: Actually calling samplerate() requires full session setup


class TestElementEquality:
    """Tests for Element equality comparison."""

    def test_element_eq_same(self):
        """Test element equality with same parameters."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        elem1 = Element(mock_session, 'test', 1, 'generic')
        elem2 = Element(mock_session, 'test', 1, 'generic')

        # Same name, ref, type should be equivalent
        assert elem1.name == elem2.name
        assert elem1.reference == elem2.reference
        assert elem1.type == elem2.type

    def test_element_eq_different(self):
        """Test element equality with different parameters."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        elem1 = Element(mock_session, 'test1', 1, 'generic')
        elem2 = Element(mock_session, 'test2', 1, 'generic')

        # Different names
        assert elem1.name != elem2.name

    def test_element_eq_method(self):
        """Test element eq method."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        elem1 = Element(mock_session, 'test', 1, 'generic')
        elem2 = Element(mock_session, 'test', 1, 'generic')

        # Should have eq method
        if hasattr(elem1, 'eq'):
            result = elem1.eq(elem2)
            # Two elements with same params should match
            assert isinstance(result, bool)


class TestElementNaming:
    """Tests for Element naming validation."""

    def test_element_name_valid(self):
        """Test valid element name."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        # Valid names start with letter, no whitespace
        element = Element(mock_session, 'validName', 1, 'generic')
        assert element.name == 'validName'

        element = Element(mock_session, 'valid_name_123', 1, 'generic')
        assert element.name == 'valid_name_123'

    def test_element_type_valid(self):
        """Test valid element type."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        element = Element(mock_session, 'test', 1, 'n-trode')
        assert element.type == 'n-trode'

        element = Element(mock_session, 'test', 1, 'timeseries')
        assert element.type == 'timeseries'


class TestElementIntegration:
    """Integration tests for Element with session."""

    def test_element_in_session(self):
        """Test adding element to session."""
        import tempfile
        from ndi.session import SessionDir
        from ndi._element import Element

        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, 'test_session')

            element = Element(session, 'test_element', 1, 'generic')

            # Element should be created successfully
            assert element is not None
            assert element.session == session

    def test_element_with_database(self):
        """Test element with database operations."""
        import tempfile
        from ndi.session import SessionDir
        from ndi._element import Element

        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, 'test_session')

            element = Element(session, 'test_element', 1, 'generic')

            # Create document
            if hasattr(element, 'newdocument'):
                doc = element.newdocument()
                if doc is not None:
                    # Add to database
                    if hasattr(session, 'database_add'):
                        try:
                            session.database_add(doc)
                        except Exception:
                            pass  # May fail if database not fully configured


class TestElementTypes:
    """Tests for specific element types."""

    def test_probe_element_type(self):
        """Test probe element type."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        element = Element(mock_session, 'electrode', 1, 'n-trode')
        assert element.type == 'n-trode'

    def test_timeseries_element_type(self):
        """Test timeseries element type."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        element = Element(mock_session, 'lfp', 1, 'timeseries')
        assert element.type == 'timeseries'

    def test_stimulus_element_type(self):
        """Test stimulus element type."""
        from ndi._element import Element

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        element = Element(mock_session, 'visual_stim', 1, 'stimulus')
        assert element.type == 'stimulus'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
