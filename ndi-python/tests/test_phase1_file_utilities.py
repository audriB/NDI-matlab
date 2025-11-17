"""
Tests for Phase 1 File Utilities.

Tests ndi.file.utilities module functions.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from ndi.file.utilities import temp_name, temp_fid


class TestTempName:
    """Tests for temp_name function."""

    def test_temp_name_returns_string(self):
        """Test that temp_name returns a string."""
        name = temp_name()
        assert isinstance(name, str)

    def test_temp_name_is_unique(self):
        """Test that temp_name returns unique names."""
        name1 = temp_name()
        name2 = temp_name()
        assert name1 != name2

    def test_temp_name_in_temp_directory(self):
        """Test that temp_name returns path in temp directory."""
        name = temp_name()
        # Should be in system temp or ndi_temp subdirectory
        assert 'tmp' in name.lower() or 'temp' in name.lower()


class TestTempFid:
    """Tests for temp_fid function."""

    def test_temp_fid_returns_file_and_path(self):
        """Test that temp_fid returns file object and path."""
        f, path = temp_fid()
        assert f is not None
        assert isinstance(path, str)
        f.close()

    def test_temp_fid_file_is_writable(self):
        """Test that temp_fid file can be written to."""
        f, path = temp_fid()
        try:
            f.write(b'test data')
            f.flush()
            assert Path(path).stat().st_size > 0
        finally:
            f.close()
            # Clean up
            try:
                Path(path).unlink()
            except:
                pass

    def test_temp_fid_creates_unique_files(self):
        """Test that temp_fid creates unique files."""
        f1, path1 = temp_fid()
        f2, path2 = temp_fid()
        try:
            assert path1 != path2
        finally:
            f1.close()
            f2.close()
            # Clean up
            for p in [path1, path2]:
                try:
                    Path(p).unlink()
                except:
                    pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
