"""
Tests for Probe Specializations.

Tests electrode, multi-electrode, and optical probe implementations.
"""

import pytest
import numpy as np
from unittest.mock import Mock


class TestElectrodeProbe:
    """Tests for ElectrodeProbe class."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return Mock()

    def test_electrode_creation(self, mock_session):
        """Test creating an electrode probe."""
        from ndi.probe import ElectrodeProbe

        electrode = ElectrodeProbe(
            mock_session,
            name='electrode1',
            reference=1,
            subject_id='mouse001',
            impedance=1e6,
            material='tungsten'
        )

        assert electrode.name == 'electrode1'
        assert electrode.reference == 1
        assert electrode.impedance == 1e6
        assert electrode.material == 'tungsten'

    def test_electrode_properties(self, mock_session):
        """Test getting electrode properties."""
        from ndi.probe import ElectrodeProbe

        electrode = ElectrodeProbe(
            mock_session,
            name='test_electrode',
            reference=1,
            subject_id='rat01',
            impedance=2e6,
            material='platinum',
            tip_diameter=0.5
        )

        props = electrode.get_properties()

        assert props['name'] == 'test_electrode'
        assert props['material'] == 'platinum'
        assert props['impedance'] == 2e6
        assert props['tip_diameter'] == 0.5


class TestMultiElectrodeProbe:
    """Tests for MultiElectrodeProbe class."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return Mock()

    def test_tetrode_creation(self, mock_session):
        """Test creating a tetrode."""
        from ndi.probe import MultiElectrodeProbe

        tetrode = MultiElectrodeProbe(
            mock_session,
            name='tetrode1',
            reference=1,
            subject_id='mouse001',
            num_channels=4,
            probe_type='tetrode'
        )

        assert tetrode.name == 'tetrode1'
        assert tetrode.num_channels == 4
        assert tetrode.probe_type == 'tetrode'
        assert len(tetrode.channel_map) == 4

    def test_multielectrode_with_geometry(self, mock_session):
        """Test multi-electrode probe with geometry."""
        from ndi.probe import MultiElectrodeProbe

        # Create linear probe with 16 channels, 25um spacing
        geometry = np.array([[0, i*25] for i in range(16)])

        probe = MultiElectrodeProbe(
            mock_session,
            name='linear16',
            reference=1,
            subject_id='mouse01',
            num_channels=16,
            probe_type='linear_array',
            geometry=geometry
        )

        assert probe.num_channels == 16
        assert probe.geometry.shape == (16, 2)

    def test_channel_geometry(self, mock_session):
        """Test getting channel geometry."""
        from ndi.probe import MultiElectrodeProbe

        geometry = np.array([[0, 0], [0, 25], [0, 50], [0, 75]])

        probe = MultiElectrodeProbe(
            mock_session,
            name='probe1',
            reference=1,
            subject_id='test',
            num_channels=4,
            geometry=geometry
        )

        loc = probe.get_channel_geometry(2)
        assert loc == (0.0, 50.0)

    def test_channel_distance(self, mock_session):
        """Test calculating distance between channels."""
        from ndi.probe import MultiElectrodeProbe

        geometry = np.array([[0, 0], [0, 100], [100, 0], [100, 100]])

        probe = MultiElectrodeProbe(
            mock_session,
            name='probe1',
            reference=1,
            subject_id='test',
            num_channels=4,
            geometry=geometry
        )

        # Distance between (0, 0) and (0, 100) should be 100
        dist = probe.get_channel_distance(0, 1)
        assert dist == pytest.approx(100.0)

        # Distance between (0, 0) and (100, 100) should be ~141.4
        dist = probe.get_channel_distance(0, 3)
        assert dist == pytest.approx(141.421, rel=1e-3)


class TestOpticalProbe:
    """Tests for OpticalProbe class."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return Mock()

    def test_microscope_creation(self, mock_session):
        """Test creating a microscope probe."""
        from ndi.probe import OpticalProbe

        microscope = OpticalProbe(
            mock_session,
            name='2p_scope',
            reference=1,
            subject_id='mouse001',
            imaging_type='two_photon',
            wavelength=920,
            resolution=0.5,
            frame_rate=30.0
        )

        assert microscope.name == '2p_scope'
        assert microscope.imaging_type == 'two_photon'
        assert microscope.wavelengths == [920]
        assert microscope.resolution == 0.5
        assert microscope.frame_rate == 30.0

    def test_optogenetic_led(self, mock_session):
        """Test creating an optogenetic LED."""
        from ndi.probe import OpticalProbe

        led = OpticalProbe(
            mock_session,
            name='blue_led',
            reference=1,
            subject_id='mouse001',
            imaging_type='optogenetic_stim',
            wavelength=473,
            power=10.0
        )

        assert led.name == 'blue_led'
        assert led.imaging_type == 'optogenetic_stim'
        assert led.wavelengths == [473]
        assert led.power == 10.0

    def test_is_imaging_vs_stimulation(self, mock_session):
        """Test distinguishing imaging from stimulation."""
        from ndi.probe import OpticalProbe

        camera = OpticalProbe(
            mock_session,
            name='camera',
            reference=1,
            subject_id='test',
            imaging_type='widefield'
        )

        led = OpticalProbe(
            mock_session,
            name='led',
            reference=1,
            subject_id='test',
            imaging_type='optogenetic_stim'
        )

        assert camera.is_imaging() is True
        assert camera.is_stimulation() is False

        assert led.is_imaging() is False
        assert led.is_stimulation() is True

    def test_multi_wavelength(self, mock_session):
        """Test multi-wavelength optical probe."""
        from ndi.probe import OpticalProbe

        fiber = OpticalProbe(
            mock_session,
            name='fiber_photometry',
            reference=1,
            subject_id='mouse01',
            imaging_type='fiber_photometry',
            wavelengths=[470, 405],
            frame_rate=100.0
        )

        assert fiber.wavelengths == [470, 405]
        props = fiber.get_properties()
        assert 'wavelengths' in props
        assert props['wavelengths'] == [470, 405]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
