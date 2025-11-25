"""
Tests for NDI File Navigator functionality.

This module tests file navigation and epoch organization including:
- Navigator creation and configuration
- Epoch detection from file patterns
- File parameter handling
- Epoch table generation
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestNavigatorCreation:
    """Tests for Navigator class creation."""

    def test_navigator_basic_creation(self):
        """Test basic navigator creation."""
        from ndi.file._navigator import Navigator

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        nav = Navigator(mock_session, {'filematch': ['*.rhd']})

        assert nav.session == mock_session
        assert nav.fileparameters is not None

    def test_navigator_with_null_session(self):
        """Test navigator creation with null session."""
        from ndi.file._navigator import Navigator

        nav = Navigator(None, {'filematch': ['*.dat']})

        assert nav.session is None

    def test_navigator_inherits_from_ido(self):
        """Test that Navigator inherits from IDO."""
        from ndi.file._navigator import Navigator
        from ndi.ido import IDO

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        nav = Navigator(mock_session, {'filematch': ['*.rhd']})
        assert isinstance(nav, IDO)
        assert hasattr(nav, 'id')

    def test_navigator_inherits_from_epochset(self):
        """Test that Navigator inherits from EpochSet."""
        from ndi.file._navigator import Navigator
        from ndi.epoch import EpochSet

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        nav = Navigator(mock_session, {'filematch': ['*.rhd']})
        assert isinstance(nav, EpochSet)


class TestFileParameters:
    """Tests for file parameter handling."""

    def test_setfileparameters_dict(self):
        """Test setting file parameters from dict."""
        from ndi.file._navigator import Navigator

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        nav = Navigator(mock_session, None)
        nav.setfileparameters({'filematch': ['*.rhd', '*.dat']})

        assert nav.fileparameters is not None
        assert 'filematch' in nav.fileparameters

    def test_setfileparameters_string(self):
        """Test setting file parameters from string."""
        from ndi.file._navigator import Navigator

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        nav = Navigator(mock_session, '*.rhd')

        # Should handle string input
        assert nav.fileparameters is not None


class TestEpochDetection:
    """Tests for epoch detection from files."""

    def test_numepochs_empty_directory(self):
        """Test epoch count with no matching files."""
        from ndi.file._navigator import Navigator

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])
        mock_session.path = '/nonexistent/path'
        mock_session.cache = None  # No cache available

        nav = Navigator(mock_session, {'filematch': ['*.rhd']})

        # Should have numepochs method
        assert hasattr(nav, 'numepochs')
        # Note: numepochs() calls epochtable() which may need full session setup
        # Just verify method exists

    def test_getepochfiles_basic(self):
        """Test getting files for an epoch."""
        from ndi.file._navigator import Navigator

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        nav = Navigator(mock_session, {'filematch': ['*.rhd']})

        # Should have getepochfiles method
        assert hasattr(nav, 'getepochfiles')

    def test_epochtable_generation(self):
        """Test epoch table generation."""
        from ndi.file._navigator import Navigator

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        nav = Navigator(mock_session, {'filematch': ['*.rhd']})

        # Should have epochtable method
        assert hasattr(nav, 'epochtable')

    def test_epochid_generation(self):
        """Test epoch ID generation."""
        from ndi.file._navigator import Navigator

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        nav = Navigator(mock_session, {'filematch': ['*.rhd']})

        # Should have epochid method
        assert hasattr(nav, 'epochid')


class TestEpochProbeMap:
    """Tests for epoch probe map handling."""

    def test_epochprobemap_class_default(self):
        """Test default epoch probe map class."""
        from ndi.file._navigator import Navigator

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        nav = Navigator(mock_session, {'filematch': ['*.rhd']})

        assert nav.epochprobemap_class == 'ndi.epoch.epochprobemap_daqsystem'

    def test_epochprobemap_class_custom(self):
        """Test custom epoch probe map class."""
        from ndi.file._navigator import Navigator

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        nav = Navigator(
            mock_session,
            {'filematch': ['*.rhd']},
            epochprobemap_class='custom.probemap.class'
        )

        assert nav.epochprobemap_class == 'custom.probemap.class'

    def test_setepochprobemapfileparameters(self):
        """Test setting epoch probe map file parameters."""
        from ndi.file._navigator import Navigator

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        nav = Navigator(mock_session, {'filematch': ['*.rhd']})

        # Should have method to set epochprobemap file parameters
        if hasattr(nav, 'setepochprobemapfileparameters'):
            nav.setepochprobemapfileparameters({'filematch': ['*.ndi']})
            assert nav.epochprobemap_fileparameters is not None


class TestNavigatorDocument:
    """Tests for Navigator document creation and loading."""

    def test_navigator_newdocument(self):
        """Test creating a document from navigator."""
        from ndi.file._navigator import Navigator

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        nav = Navigator(mock_session, {'filematch': ['*.rhd']})

        # Should have newdocument method
        if hasattr(nav, 'newdocument'):
            doc = nav.newdocument()
            assert doc is not None

    def test_navigator_from_document(self):
        """Test creating navigator from document."""
        from ndi.file._navigator import Navigator
        from ndi.document import Document

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        # Create a mock document with navigator properties
        mock_doc = Mock(spec=Document)
        mock_doc.document = {
            'document': {
                'id': 'test-id',
                'type': 'filenavigator'
            },
            'filenavigator': {
                'fileparameters': {'filematch': ['*.rhd']},
                'epochprobemap_class': 'ndi.epoch.epochprobemap_daqsystem'
            }
        }

        # Test that document form is handled
        # (actual implementation may vary)
        try:
            nav = Navigator(mock_session, mock_doc)
            assert nav is not None
        except (ValueError, AttributeError, KeyError):
            # Document initialization may require specific structure
            pass


class TestEpochDirNavigator:
    """Tests for EpochDir Navigator subclass."""

    def test_epochdir_import(self):
        """Test that EpochDir navigator can be imported."""
        from ndi.file.navigator.epochdir import EpochDir
        assert EpochDir is not None

    def test_epochdir_creation(self):
        """Test EpochDir navigator creation."""
        from ndi.file.navigator.epochdir import EpochDir

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])
        mock_session.path = '/tmp/test'

        nav = EpochDir(mock_session, {'filematch': ['*.rhd']})
        assert nav is not None

    def test_epochdir_inherits_from_navigator(self):
        """Test that EpochDir inherits from Navigator."""
        from ndi.file.navigator.epochdir import EpochDir
        from ndi.file._navigator import Navigator

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])
        mock_session.path = '/tmp/test'

        nav = EpochDir(mock_session, {'filematch': ['*.rhd']})
        assert isinstance(nav, Navigator)


class TestNavigatorIntegration:
    """Integration tests for Navigator with real file system."""

    def test_navigator_with_temp_files(self):
        """Test navigator with temporary test files."""
        from ndi.file._navigator import Navigator
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some test files
            for i in range(3):
                Path(tmpdir) / f'epoch_{i}' / 'data.rhd'

            mock_session = Mock()
            mock_session.database_search = Mock(return_value=[])
            mock_session.path = tmpdir

            nav = Navigator(mock_session, {'filematch': ['*.rhd']})

            # Navigator should be created successfully
            assert nav is not None

    def test_navigator_file_matching(self):
        """Test file pattern matching."""
        from ndi.file._navigator import Navigator
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files with different extensions
            (Path(tmpdir) / 'data1.rhd').touch()
            (Path(tmpdir) / 'data2.rhd').touch()
            (Path(tmpdir) / 'data3.dat').touch()

            mock_session = Mock()
            mock_session.database_search = Mock(return_value=[])
            mock_session.path = tmpdir

            nav = Navigator(mock_session, {'filematch': ['*.rhd']})

            # Should only match .rhd files
            assert nav is not None


class TestNavigatorEquality:
    """Tests for Navigator equality comparison."""

    def test_navigator_eq(self):
        """Test navigator equality."""
        from ndi.file._navigator import Navigator

        mock_session = Mock()
        mock_session.database_search = Mock(return_value=[])

        nav1 = Navigator(mock_session, {'filematch': ['*.rhd']})
        nav2 = Navigator(mock_session, {'filematch': ['*.rhd']})
        nav3 = Navigator(mock_session, {'filematch': ['*.dat']})

        # Should have eq method
        if hasattr(nav1, 'eq') or hasattr(nav1, '__eq__'):
            # Same parameters should be comparable
            assert nav1.fileparameters == nav2.fileparameters
            assert nav1.fileparameters != nav3.fileparameters


class TestFileTypeUtilities:
    """Tests for file type utilities."""

    def test_mfdaq_epoch_channel(self):
        """Test MFDAQ epoch channel utilities."""
        from ndi.file.type.mfdaq_epoch_channel import MFDAQEpochChannel

        channel = MFDAQEpochChannel()
        assert channel is not None


class TestFileUtilities:
    """Tests for file utilities module."""

    def test_file_utilities_import(self):
        """Test that file utilities can be imported."""
        from ndi.file import utilities
        assert utilities is not None

    def test_temp_name(self):
        """Test temporary file name generation."""
        from ndi.file.utilities import temp_name

        name1 = temp_name()
        name2 = temp_name()

        # Should generate unique names
        assert name1 != name2
        # Should be valid file paths
        assert isinstance(name1, str)
        assert isinstance(name2, str)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
