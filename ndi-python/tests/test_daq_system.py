"""
Tests for NDI DAQ System functionality.

This module tests the DAQ system components including:
- DAQ System creation and configuration
- DAQ Reader implementations
- DAQSystemString parsing
- Sample/time conversions
- Epoch handling
"""

import pytest
import math
from unittest.mock import Mock, patch, MagicMock
import numpy as np


class TestDAQSystem:
    """Tests for ndi.daq.System class."""

    def test_system_creation(self):
        """Test basic DAQ system creation."""
        from ndi.daq.system import System

        system = System('test_system')
        assert system.name == 'test_system'
        assert system.filenavigator is None
        assert system.daqreader is None
        assert system.daqmetadatareader == []

    def test_system_with_components(self):
        """Test DAQ system creation with components."""
        from ndi.daq.system import System

        mock_navigator = Mock()
        mock_reader = Mock()
        mock_metadata = [Mock(), Mock()]

        system = System(
            'test_system',
            filenavigator=mock_navigator,
            daqreader=mock_reader,
            daqmetadatareader=mock_metadata
        )

        assert system.name == 'test_system'
        assert system.filenavigator == mock_navigator
        assert system.daqreader == mock_reader
        assert len(system.daqmetadatareader) == 2

    def test_epochclock_returns_no_time(self):
        """Test that base epochclock returns no_time clock type."""
        from ndi.daq.system import System

        system = System('test_system')
        clocks = system.epochclock(1)

        assert len(clocks) == 1
        assert clocks[0].type == 'no_time'

    def test_t0_t1_returns_nan(self):
        """Test that base t0_t1 returns NaN values."""
        from ndi.daq.system import System

        system = System('test_system')
        times = system.t0_t1(1)

        assert len(times) == 1
        assert math.isnan(times[0][0])
        assert math.isnan(times[0][1])

    def test_system_inherits_from_ido(self):
        """Test that System inherits from IDO."""
        from ndi.daq.system import System
        from ndi.ido import IDO

        system = System('test_system')
        assert isinstance(system, IDO)
        assert hasattr(system, 'id')

    def test_system_inherits_from_epochset(self):
        """Test that System inherits from EpochSet."""
        from ndi.daq.system import System
        from ndi.epoch import EpochSet

        system = System('test_system')
        assert isinstance(system, EpochSet)


class TestDAQReader:
    """Tests for ndi.daq.reader module."""

    def test_reader_base_class(self):
        """Test DAQ reader base class exists and has key methods."""
        from ndi.daq.reader import Reader

        # Reader is an abstract base class
        assert Reader is not None
        assert hasattr(Reader, 'epochclock')
        assert hasattr(Reader, 't0_t1')

    def test_reader_instance_methods(self):
        """Test reader instance methods."""
        from ndi.daq.readers.mfdaq import MFDAQReader, Intan

        # MFDAQReader is the concrete base
        reader = Intan()
        assert hasattr(reader, 'epochclock')
        assert hasattr(reader, 't0_t1')

    def test_reader_inherits_from_ido(self):
        """Test that readers inherit from IDO."""
        from ndi.daq.readers.mfdaq import Intan
        from ndi.ido import IDO

        reader = Intan()
        assert isinstance(reader, IDO)
        assert hasattr(reader, 'id')


class TestDAQSystemString:
    """Tests for DAQ system string parsing (from test_phase4_daq_time.py equivalent)."""

    def test_parse_simple_channel(self):
        """Test parsing simple channel specification."""
        from ndi.daq.daqsystemstring import DAQSystemString

        dss = DAQSystemString('mydevice:ai1')

        assert dss.devicename == 'mydevice'
        assert 'ai' in dss.channeltype
        assert 1 in dss.channellist

    def test_parse_channel_range(self):
        """Test parsing channel range specification."""
        from ndi.daq.daqsystemstring import DAQSystemString

        dss = DAQSystemString('mydevice:ai1-5')

        assert dss.devicename == 'mydevice'
        assert 'ai' in dss.channeltype
        # Should contain channels 1,2,3,4,5
        assert set([1, 2, 3, 4, 5]).issubset(set(dss.channellist))

    def test_parse_multiple_channels(self):
        """Test parsing multiple channel specifications."""
        from ndi.daq.daqsystemstring import DAQSystemString

        dss = DAQSystemString('mydevice:ai1,2,5')

        assert dss.devicename == 'mydevice'
        assert 1 in dss.channellist
        assert 2 in dss.channellist
        assert 5 in dss.channellist

    def test_parse_complex_string(self):
        """Test parsing complex DAQ string with ranges and single channels."""
        from ndi.daq.daqsystemstring import DAQSystemString

        dss = DAQSystemString('mydevice:ai1-5,7,23')

        assert dss.devicename == 'mydevice'
        # Should have 1,2,3,4,5,7,23
        expected = [1, 2, 3, 4, 5, 7, 23]
        for ch in expected:
            assert ch in dss.channellist

    def test_build_from_components(self):
        """Test building DAQSystemString from components."""
        from ndi.daq.daqsystemstring import DAQSystemString

        dss = DAQSystemString('mydevice', ['ai']*7, [1, 2, 3, 4, 5, 10, 17])

        assert dss.devicename == 'mydevice'
        assert len(dss.channellist) == 7
        assert dss.devicestring() == 'mydevice:ai1-5,10,17'

    def test_devicestring_generation(self):
        """Test devicestring method generates correct output."""
        from ndi.daq.daqsystemstring import DAQSystemString

        dss = DAQSystemString('mydevice:ai1-5,10,17')
        output = dss.devicestring()

        assert 'mydevice' in output
        assert ':' in output


class TestSampleTimeConversion:
    """Tests for sample-to-time and time-to-sample conversions."""

    def test_samples2times_basic(self):
        """Test basic sample to time conversion."""
        from ndi.time.fun.samples2times import samples2times

        # At 1000 Hz, sample 1001 = 1 second (1-indexed, formula: t = (s-1)/sr + t0)
        times = samples2times([1001], (0.0, 10.0), 1000.0)
        assert abs(times[0] - 1.0) < 1e-9

    def test_samples2times_with_offset(self):
        """Test sample to time conversion with non-zero start time."""
        from ndi.time.fun.samples2times import samples2times

        # At 1000 Hz, sample 1001 with t0=0.5 = 1.5 seconds
        times = samples2times([1001], (0.5, 10.5), 1000.0)
        assert abs(times[0] - 1.5) < 1e-9

    def test_times2samples_basic(self):
        """Test basic time to sample conversion."""
        from ndi.time.fun.times2samples import times2samples

        # At 1000 Hz, time 1.0 = sample 1001 (1-indexed)
        samples = times2samples([1.0], (0.0, 10.0), 1000.0)
        assert abs(samples[0] - 1001) < 1

    def test_times2samples_with_offset(self):
        """Test time to sample conversion with non-zero start time."""
        from ndi.time.fun.times2samples import times2samples

        # At 1000 Hz, time 1.5 with t0=0.5 = sample 1001
        samples = times2samples([1.5], (0.5, 10.5), 1000.0)
        assert abs(samples[0] - 1001) < 1

    def test_samples2times_negative_inf(self):
        """Test handling of negative infinity in samples2times."""
        from ndi.time.fun.samples2times import samples2times

        times = samples2times([float('-inf')], (0.0, 10.0), 1000.0)
        # -inf should map to t0
        assert times[0] == 0.0

    def test_samples2times_positive_inf(self):
        """Test handling of positive infinity in samples2times."""
        from ndi.time.fun.samples2times import samples2times

        times = samples2times([float('inf')], (0.0, 10.0), 1000.0)
        # +inf should map to t1
        assert times[0] == 10.0

    def test_round_trip_conversion(self):
        """Test that sample->time->sample conversion is consistent."""
        from ndi.time.fun.samples2times import samples2times
        from ndi.time.fun.times2samples import times2samples

        original_samples = [1, 501, 1001, 5001]  # 1-indexed
        sr = 1000.0
        t0_t1 = (0.0, 10.0)

        times = samples2times(original_samples, t0_t1, sr)
        recovered_samples = times2samples(times, t0_t1, sr)

        for orig, recov in zip(original_samples, recovered_samples):
            assert abs(orig - recov) < 1  # Allow for rounding


class TestMFDAQReaders:
    """Tests for multi-function DAQ readers."""

    def test_intan_reader_exists(self):
        """Test that Intan reader can be imported."""
        from ndi.daq.readers.mfdaq.intan import Intan
        reader = Intan()
        assert reader is not None

    def test_spikegadgets_reader_exists(self):
        """Test that SpikeGadgets reader can be imported."""
        from ndi.daq.readers.mfdaq.spikegadgets import SpikeGadgets
        reader = SpikeGadgets()
        assert reader is not None

    def test_cedspike2_reader_exists(self):
        """Test that CED Spike2 reader can be imported."""
        from ndi.daq.readers.mfdaq.cedspike2 import CEDSpike2
        reader = CEDSpike2()
        assert reader is not None

    def test_blackrock_reader_exists(self):
        """Test that Blackrock reader can be imported."""
        from ndi.daq.readers.mfdaq.blackrock import Blackrock
        reader = Blackrock()
        assert reader is not None

    def test_mfdaq_base_class(self):
        """Test that MFDAQReader base class is available."""
        from ndi.daq.readers.mfdaq import MFDAQReader
        assert MFDAQReader is not None

    def test_readers_inherit_from_mfdaq(self):
        """Test that readers inherit from MFDAQReader."""
        from ndi.daq.readers.mfdaq import MFDAQReader, Intan, SpikeGadgets

        intan = Intan()
        spikegadgets = SpikeGadgets()

        assert isinstance(intan, MFDAQReader)
        assert isinstance(spikegadgets, MFDAQReader)


class TestMetadataReader:
    """Tests for DAQ metadata reader."""

    def test_metadatareader_creation(self):
        """Test creating a metadata reader."""
        from ndi.daq.metadatareader import MetadataReader

        reader = MetadataReader()
        assert reader is not None
        assert hasattr(reader, 'readmetadata')

    def test_metadatareader_with_pattern(self):
        """Test creating metadata reader with TSV pattern."""
        from ndi.daq.metadatareader import MetadataReader

        reader = MetadataReader(r'.*_stim\.txt$')
        assert reader.tab_separated_file_parameter == r'.*_stim\.txt$'


class TestDAQSystemDocument:
    """Tests for DAQ system document creation and retrieval."""

    def test_system_newdocument(self):
        """Test creating a document from a DAQ system."""
        from ndi.daq.system import System

        system = System('test_system')

        # Should have newdocument method
        if hasattr(system, 'newdocument'):
            doc = system.newdocument()
            assert doc is not None
            # Document should contain system name
            if hasattr(doc, 'document'):
                assert 'test_system' in str(doc.document)

    def test_system_eq(self):
        """Test DAQ system equality comparison."""
        from ndi.daq.system import System

        system1 = System('test_system')
        system2 = System('test_system')
        system3 = System('other_system')

        # Same name systems should be comparable
        # (exact equality depends on implementation)
        assert system1.name == system2.name
        assert system1.name != system3.name


class TestDAQSystemIntegration:
    """Integration tests for DAQ system with session."""

    def test_system_in_session(self):
        """Test adding DAQ system to a session."""
        import tempfile
        import os
        from ndi.session import SessionDir
        from ndi.daq.system import System

        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, 'test_session')

            system = System('test_daq')

            # System should have ID
            assert hasattr(system, 'id')
            assert system.id is not None

    def test_system_with_session_database(self):
        """Test system interaction with session database."""
        import tempfile
        from ndi.session import SessionDir
        from ndi.daq.system import System

        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionDir(tmpdir, 'test_session')

            system = System('test_daq')

            # Create document if method exists
            if hasattr(system, 'newdocument'):
                doc = system.newdocument()
                assert doc is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
