"""
Tests for NDI synchronization rules.

Tests FileFind, FileMatch, and CommonTriggers sync rules.
"""

import pytest
import tempfile
import os
import numpy as np

from ndi.time.syncrules import FileFind, FileMatch, CommonTriggers
from ndi.time.timemapping import TimeMapping


class TestFileFind:
    """Test FileFind sync rule."""

    def test_filefind_creation(self):
        """Test creating a FileFind rule."""
        rule = FileFind()
        assert rule is not None
        assert rule.parameters['syncfilename'] == 'syncfile.txt'

    def test_filefind_with_parameters(self):
        """Test FileFind with custom parameters."""
        params = {
            'number_fullpath_matches': 2,
            'syncfilename': 'custom_sync.txt',
            'daqsystem1': 'intan',
            'daqsystem2': 'stimulus'
        }
        rule = FileFind(params)

        assert rule.parameters['number_fullpath_matches'] == 2
        assert rule.parameters['syncfilename'] == 'custom_sync.txt'
        assert rule.parameters['daqsystem1'] == 'intan'
        assert rule.parameters['daqsystem2'] == 'stimulus'

    def test_validate_parameters_valid(self):
        """Test parameter validation with valid parameters."""
        rule = FileFind()
        params = {
            'number_fullpath_matches': 1,
            'syncfilename': 'sync.txt',
            'daqsystem1': 'daq1',
            'daqsystem2': 'daq2'
        }

        valid, msg = rule.isvalidparameters(params)
        assert valid is True
        assert msg == ""

    def test_validate_parameters_missing_field(self):
        """Test parameter validation with missing field."""
        rule = FileFind()
        params = {
            'number_fullpath_matches': 1,
            'syncfilename': 'sync.txt'
            # Missing daqsystem1, daqsystem2
        }

        valid, msg = rule.isvalidparameters(params)
        assert valid is False
        assert 'daqsystem1' in msg

    def test_validate_parameters_invalid_type(self):
        """Test parameter validation with invalid types."""
        rule = FileFind()
        params = {
            'number_fullpath_matches': 'not_a_number',  # Should be int
            'syncfilename': 'sync.txt',
            'daqsystem1': 'daq1',
            'daqsystem2': 'daq2'
        }

        valid, msg = rule.isvalidparameters(params)
        assert valid is False
        assert 'integer' in msg

    def test_eligible_epochsets(self):
        """Test eligible epoch sets."""
        rule = FileFind()
        eligible = rule.eligible_epochsets()

        assert 'ndi.daq.system' in eligible

    def test_ineligible_epochsets(self):
        """Test ineligible epoch sets."""
        rule = FileFind()
        ineligible = rule.ineligible_epochsets()

        assert 'ndi.epoch.epochset' in ineligible
        assert 'ndi.file.navigator' in ineligible

    def test_load_sync_file_forward(self):
        """Test loading sync file for forward mapping."""
        rule = FileFind()

        # Create a temporary sync file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write('10.5\n')  # shift
            f.write('2.0\n')   # scale
            sync_file = f.name

        try:
            mapping = rule._load_sync_file(sync_file, reverse=False)

            # Forward: t_out = shift + scale * t_in = 10.5 + 2.0 * t_in
            assert mapping is not None
            assert abs(mapping.map(0.0) - 10.5) < 1e-10
            assert abs(mapping.map(1.0) - 12.5) < 1e-10
            assert abs(mapping.map(10.0) - 30.5) < 1e-10
        finally:
            os.unlink(sync_file)

    def test_load_sync_file_reverse(self):
        """Test loading sync file for reverse mapping."""
        rule = FileFind()

        # Create a temporary sync file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write('10.0\n')  # shift
            f.write('2.0\n')   # scale
            sync_file = f.name

        try:
            mapping = rule._load_sync_file(sync_file, reverse=True)

            # Reverse: t_in = (t_out - shift) / scale
            #                = (t_out - 10.0) / 2.0
            #                = -5.0 + 0.5 * t_out
            assert mapping is not None
            assert abs(mapping.map(10.0) - 0.0) < 1e-10  # (10-10)/2 = 0
            assert abs(mapping.map(12.0) - 1.0) < 1e-10  # (12-10)/2 = 1
            assert abs(mapping.map(30.0) - 10.0) < 1e-10  # (30-10)/2 = 10
        finally:
            os.unlink(sync_file)


class TestFileMatch:
    """Test FileMatch sync rule."""

    def test_filematch_creation(self):
        """Test creating a FileMatch rule."""
        rule = FileMatch()
        assert rule is not None
        assert rule.parameters['number_fullpath_matches'] == 2

    def test_filematch_with_parameters(self):
        """Test FileMatch with custom parameters."""
        params = {'number_fullpath_matches': 3}
        rule = FileMatch(params)

        assert rule.parameters['number_fullpath_matches'] == 3

    def test_validate_parameters_valid(self):
        """Test parameter validation with valid parameters."""
        rule = FileMatch()
        params = {'number_fullpath_matches': 1}

        valid, msg = rule.isvalidparameters(params)
        assert valid is True
        assert msg == ""

    def test_validate_parameters_missing_field(self):
        """Test parameter validation with missing field."""
        rule = FileMatch()
        params = {}

        valid, msg = rule.isvalidparameters(params)
        assert valid is False
        assert 'number_fullpath_matches' in msg

    def test_validate_parameters_invalid_value(self):
        """Test parameter validation with invalid value."""
        rule = FileMatch()
        params = {'number_fullpath_matches': 0}  # Must be >= 1

        valid, msg = rule.isvalidparameters(params)
        assert valid is False

    def test_eligible_epochsets(self):
        """Test eligible epoch sets."""
        rule = FileMatch()
        eligible = rule.eligible_epochsets()

        assert 'ndi.daq.system' in eligible

    def test_ineligible_epochsets(self):
        """Test ineligible epoch sets."""
        rule = FileMatch()
        ineligible = rule.ineligible_epochsets()

        assert 'ndi.epoch.epochset' in ineligible
        assert 'ndi.file.navigator' in ineligible

    def test_apply_with_common_files(self):
        """Test apply() with common files (success case)."""
        rule = FileMatch({'number_fullpath_matches': 1})

        # Create mock epoch nodes with common files
        epochnode_a = {
            'objectclass': 'ndi.daq.system',
            'objectname': 'daq1',
            'underlying_epochs': {
                'underlying': ['/path/file1.dat', '/path/file2.dat']
            }
        }

        epochnode_b = {
            'objectclass': 'ndi.daq.system',
            'objectname': 'daq2',
            'underlying_epochs': {
                'underlying': ['/path/file1.dat', '/path/file3.dat']
            }
        }

        cost, mapping = rule.apply(epochnode_a, epochnode_b)

        assert cost == 1.0
        assert mapping is not None
        # Should be identity mapping
        assert abs(mapping.map(10.0) - 10.0) < 1e-10

    def test_apply_insufficient_common_files(self):
        """Test apply() with insufficient common files (failure case)."""
        rule = FileMatch({'number_fullpath_matches': 2})

        # Create mock epoch nodes with only 1 common file
        epochnode_a = {
            'objectclass': 'ndi.daq.system',
            'objectname': 'daq1',
            'underlying_epochs': {
                'underlying': ['/path/file1.dat', '/path/file2.dat']
            }
        }

        epochnode_b = {
            'objectclass': 'ndi.daq.system',
            'objectname': 'daq2',
            'underlying_epochs': {
                'underlying': ['/path/file1.dat', '/path/file3.dat']
            }
        }

        cost, mapping = rule.apply(epochnode_a, epochnode_b)

        assert cost is None
        assert mapping is None


class TestCommonTriggers:
    """Test CommonTriggers sync rule."""

    def test_commontriggers_creation(self):
        """Test creating a CommonTriggers rule."""
        # Should show warning about placeholder
        with pytest.warns(UserWarning, match="placeholder"):
            rule = CommonTriggers()

        assert rule is not None
        assert rule.parameters['number_fullpath_matches'] == 2

    def test_commontriggers_with_parameters(self):
        """Test CommonTriggers with custom parameters."""
        params = {
            'daqsystem1': 'intan',
            'channel_daq1': 'di0',
            'daqsystem2': 'stimulus',
            'channel_daq2': 'trigger_out',
            'number_fullpath_matches': 1
        }

        with pytest.warns(UserWarning):
            rule = CommonTriggers(params)

        assert rule.parameters['daqsystem1'] == 'intan'
        assert rule.parameters['channel_daq1'] == 'di0'

    def test_validate_parameters_valid(self):
        """Test parameter validation with valid parameters."""
        with pytest.warns(UserWarning):
            rule = CommonTriggers()

        params = {
            'daqsystem1': 'daq1',
            'channel_daq1': 'ai0',
            'daqsystem2': 'daq2',
            'channel_daq2': 'di0',
            'number_fullpath_matches': 1
        }

        valid, msg = rule.isvalidparameters(params)
        assert valid is True
        assert msg == ""

    def test_validate_parameters_missing_field(self):
        """Test parameter validation with missing field."""
        with pytest.warns(UserWarning):
            rule = CommonTriggers()

        params = {
            'daqsystem1': 'daq1',
            'channel_daq1': 'ai0'
            # Missing other fields
        }

        valid, msg = rule.isvalidparameters(params)
        assert valid is False

    def test_eligible_epochsets(self):
        """Test eligible epoch sets."""
        with pytest.warns(UserWarning):
            rule = CommonTriggers()

        eligible = rule.eligible_epochsets()
        assert 'ndi.daq.system' in eligible

    def test_ineligible_epochsets(self):
        """Test ineligible epoch sets."""
        with pytest.warns(UserWarning):
            rule = CommonTriggers()

        ineligible = rule.ineligible_epochsets()
        assert 'ndi.epoch.epochset' in ineligible
        assert 'ndi.file.navigator' in ineligible

    def test_apply_placeholder_behavior(self):
        """Test apply() with placeholder behavior."""
        with pytest.warns(UserWarning):
            rule = CommonTriggers({'number_fullpath_matches': 1})

        # Create mock epoch nodes
        epochnode_a = {
            'objectclass': 'ndi.daq.system',
            'objectname': 'daq1',
            'underlying_epochs': {
                'underlying': ['/path/file1.dat']
            }
        }

        epochnode_b = {
            'objectclass': 'ndi.daq.system',
            'objectname': 'daq2',
            'underlying_epochs': {
                'underlying': ['/path/file1.dat']
            }
        }

        cost, mapping = rule.apply(epochnode_a, epochnode_b)

        # Placeholder should behave like FileMatch
        assert cost == 1.0
        assert mapping is not None
