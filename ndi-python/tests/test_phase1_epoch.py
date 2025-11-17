"""
Tests for Phase 1 Epoch Management.

Tests ndi.epoch module classes and functions.
"""

import pytest
import numpy as np
from ndi.epoch import Epoch, EpochSet, EpochProbeMap, findepochnode, epochrange
from ndi.epoch.epochprobemap_daqsystem import EpochProbeMapDAQSystem
from ndi.time import ClockType


class TestEpoch:
    """Tests for Epoch dataclass."""

    def test_epoch_creation(self):
        """Test creating an Epoch."""
        epoch = Epoch(
            epoch_number=1,
            epoch_id='t00001',
            epoch_session_id='session_123',
            epoch_clock=[ClockType('dev_local_time')],
            t0_t1=[[0.0, 10.0]]
        )
        assert epoch.epoch_number == 1
        assert epoch.epoch_id == 't00001'
        assert len(epoch.epoch_clock) == 1

    def test_epoch_validation_negative_number(self):
        """Test that negative epoch_number raises error."""
        with pytest.raises(ValueError, match="non-negative"):
            epoch = Epoch(epoch_number=-1)

    def test_epoch_repr(self):
        """Test Epoch string representation."""
        epoch = Epoch(epoch_number=1, epoch_id='t00001')
        repr_str = repr(epoch)
        assert 'Epoch' in repr_str
        assert 'number=1' in repr_str


class TestEpochSet:
    """Tests for EpochSet base class."""

    def test_epochset_creation(self):
        """Test creating an EpochSet."""
        es = EpochSet()
        assert es is not None

    def test_numepochs_empty(self):
        """Test numepochs on empty epochset."""
        es = EpochSet()
        assert es.numepochs() == 0

    def test_epochtable_empty(self):
        """Test epochtable on empty epochset."""
        es = EpochSet()
        et, hashvalue = es.epochtable()
        assert et == []
        assert hashvalue is not None

    def test_epochsetname_default(self):
        """Test epochsetname returns 'unknown' by default."""
        es = EpochSet()
        assert es.epochsetname() == 'unknown'

    def test_issyncgraphroot_default(self):
        """Test issyncgraphroot returns True by default."""
        es = EpochSet()
        assert es.issyncgraphroot() is True

    def test_epoch2str_int(self):
        """Test epoch2str with integer."""
        es = EpochSet()
        assert es.epoch2str(5) == '5'

    def test_epoch2str_string(self):
        """Test epoch2str with string."""
        es = EpochSet()
        assert es.epoch2str('t00001') == 't00001'

    def test_epoch2str_list(self):
        """Test epoch2str with list."""
        es = EpochSet()
        result = es.epoch2str(['t00001', 't00002'])
        assert 't00001' in result
        assert 't00002' in result


class TestEpochProbeMapDAQSystem:
    """Tests for EpochProbeMapDAQSystem."""

    def test_creation_with_defaults(self):
        """Test creating with default arguments."""
        epm = EpochProbeMapDAQSystem()
        assert epm.name == 'a'
        assert epm.reference == 0

    def test_creation_with_args(self):
        """Test creating with specific arguments."""
        epm = EpochProbeMapDAQSystem(
            name='lfp1',
            reference=1,
            type='ephys',
            devicestring='dev1;ai0:7',
            subjectstring='subject_001'
        )
        assert epm.name == 'lfp1'
        assert epm.reference == 1
        assert epm.type == 'ephys'
        assert epm.devicestring == 'dev1;ai0:7'

    def test_invalid_name_raises(self):
        """Test that invalid name raises ValueError."""
        with pytest.raises(ValueError, match="must start with letter"):
            EpochProbeMapDAQSystem(name='123invalid')

    def test_invalid_reference_raises(self):
        """Test that negative reference raises ValueError."""
        with pytest.raises(ValueError, match="non-negative integer"):
            EpochProbeMapDAQSystem(reference=-1)

    def test_serialize(self):
        """Test serialization to string."""
        epm = EpochProbeMapDAQSystem(
            name='lfp1',
            reference=1,
            type='ephys',
            devicestring='dev1;ai0',
            subjectstring='subj1'
        )
        s = epm.serialize()
        assert isinstance(s, str)
        assert 'lfp1' in s
        assert '1' in s
        assert 'ephys' in s

    def test_decode(self):
        """Test decoding from string."""
        s = "name\treference\ttype\tdevicestring\tsubjectstring\n"
        s += "lfp1\t1\tephys\tdev1;ai0\tsubj1\n"
        result = EpochProbeMapDAQSystem.decode(s)
        assert len(result) == 1
        assert result[0]['name'] == 'lfp1'
        assert result[0]['reference'] == 1

    def test_from_string(self):
        """Test creating from serialized string."""
        s = "name\treference\ttype\tdevicestring\tsubjectstring\n"
        s += "lfp1\t1\tephys\tdev1;ai0\tsubj1\n"
        epm = EpochProbeMapDAQSystem.from_string(s)
        assert epm.name == 'lfp1'
        assert epm.reference == 1

    def test_equality(self):
        """Test equality comparison."""
        epm1 = EpochProbeMapDAQSystem(
            name='lfp1', reference=1, type='ephys',
            devicestring='dev1', subjectstring='subj1'
        )
        epm2 = EpochProbeMapDAQSystem(
            name='lfp1', reference=1, type='ephys',
            devicestring='dev1', subjectstring='subj1'
        )
        assert epm1 == epm2


class TestFindEpochNode:
    """Tests for findepochnode function."""

    def test_find_by_epoch_id(self):
        """Test finding node by epoch_id."""
        node = {'epoch_id': 'abc123', 'objectname': 'mydaq'}
        nodes = [
            {'epoch_id': 'abc123', 'objectname': 'mydaq'},
            {'epoch_id': 'def456', 'objectname': 'mydaq'},
        ]
        indices = findepochnode(node, nodes)
        assert indices == [0]

    def test_find_by_objectname(self):
        """Test finding nodes by objectname."""
        node = {'objectname': 'mydaq'}
        nodes = [
            {'epoch_id': 'abc123', 'objectname': 'mydaq'},
            {'epoch_id': 'def456', 'objectname': 'mydaq'},
            {'epoch_id': 'ghi789', 'objectname': 'otherdaq'},
        ]
        indices = findepochnode(node, nodes)
        assert len(indices) == 2
        assert 0 in indices
        assert 1 in indices

    def test_find_no_match(self):
        """Test finding with no matches."""
        node = {'epoch_id': 'notfound'}
        nodes = [
            {'epoch_id': 'abc123'},
            {'epoch_id': 'def456'},
        ]
        indices = findepochnode(node, nodes)
        assert indices == []

    def test_empty_node_array(self):
        """Test with empty node array."""
        node = {'epoch_id': 'abc123'}
        nodes = []
        indices = findepochnode(node, nodes)
        assert indices == []


class TestEpochRange:
    """Tests for epochrange function."""

    def test_epochrange_basic(self):
        """Test basic epoch range functionality."""
        # Create a mock epochset
        class MockEpochSet(EpochSet):
            def buildepochtable(self):
                return [
                    {
                        'epoch_number': 0,
                        'epoch_id': 't00001',
                        'epoch_clock': [ClockType('dev_local_time')],
                        't0_t1': [[0.0, 10.0]]
                    },
                    {
                        'epoch_number': 1,
                        'epoch_id': 't00002',
                        'epoch_clock': [ClockType('dev_local_time')],
                        't0_t1': [[10.0, 20.0]]
                    },
                    {
                        'epoch_number': 2,
                        'epoch_id': 't00003',
                        'epoch_clock': [ClockType('dev_local_time')],
                        't0_t1': [[20.0, 30.0]]
                    },
                ]

        es = MockEpochSet()
        er, et, t0_t1 = epochrange(es, ClockType('dev_local_time'), 0, 2)

        assert len(er) == 3
        assert er[0] == 't00001'
        assert er[2] == 't00003'
        assert t0_t1.shape == (3, 2)
        assert t0_t1[0, 0] == 0.0
        assert t0_t1[2, 1] == 30.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
