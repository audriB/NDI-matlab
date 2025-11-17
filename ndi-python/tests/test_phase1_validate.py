"""
Tests for Phase 1 Validation Framework.

Tests ndi.validate module and validator functions.
"""

import pytest
import pandas as pd
from ndi.validate import Validate
from ndi.validators import must_have_required_columns


class TestMustHaveRequiredColumns:
    """Tests for must_have_required_columns validator."""

    def test_dataframe_with_required_columns(self):
        """Test DataFrame with all required columns passes."""
        df = pd.DataFrame({
            'name': ['a', 'b'],
            'value': [1, 2],
            'type': ['x', 'y']
        })
        # Should not raise
        must_have_required_columns(df, ['name', 'value'])

    def test_dataframe_missing_column_raises(self):
        """Test DataFrame missing required column raises ValueError."""
        df = pd.DataFrame({
            'name': ['a', 'b'],
            'value': [1, 2]
        })
        with pytest.raises(ValueError, match="missing required column"):
            must_have_required_columns(df, ['name', 'value', 'missing'])

    def test_dict_with_required_columns(self):
        """Test dict with required keys passes."""
        data = {'name': 'test', 'value': 123, 'type': 'x'}
        # Should not raise
        must_have_required_columns(data, ['name', 'value'])

    def test_dict_missing_key_raises(self):
        """Test dict missing required key raises ValueError."""
        data = {'name': 'test', 'value': 123}
        with pytest.raises(ValueError, match="missing required column"):
            must_have_required_columns(data, ['name', 'value', 'missing'])

    def test_single_required_column_string(self):
        """Test single required column as string."""
        df = pd.DataFrame({'name': ['a', 'b']})
        # Should not raise
        must_have_required_columns(df, 'name')

    def test_invalid_type_raises(self):
        """Test invalid table type raises TypeError."""
        with pytest.raises(TypeError):
            must_have_required_columns("not a table", ['name'])


class TestValidate:
    """Tests for Validate class."""

    def test_validate_creation_without_args(self):
        """Test creating Validate without arguments."""
        v = Validate()
        assert v is not None

    def test_validate_requires_jsonschema(self):
        """Test that jsonschema module is available."""
        import jsonschema
        assert jsonschema is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
