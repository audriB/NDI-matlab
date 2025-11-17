"""
Integration Tests for Phase 1 & 2 - NDI Python Port.

Tests complete workflows combining multiple components from Phase 1 and Phase 2.

Phase 1 components tested:
    - File utilities (temp files)
    - Validators (input validation)
    - File navigator (epoch organization)

Phase 2 components tested:
    - Calculators (spike rate, tuning curves, cross-correlation)
    - Probe specializations (electrode, multi-electrode, optical)
"""

import pytest
import numpy as np
from pathlib import Path


class TestPhase1Integration:
    """Integration tests for Phase 1 components working together."""

    def test_file_operations_with_validation(self):
        """Test file utilities with input validation."""
        from ndi.file import create_temp_filename
        from ndi.validators import must_be_text_like

        # Create temp filename and validate
        temp_filename = create_temp_filename()
        assert temp_filename is not None
        must_be_text_like(temp_filename)

        # Test with actual data
        test_data = np.random.rand(100, 10)
        temp_file = temp_filename + '.npy'

        # Save and load
        np.save(temp_file, test_data)
        loaded_data = np.load(temp_file)
        np.testing.assert_array_equal(loaded_data, test_data)

        # Cleanup
        Path(temp_file).unlink()

    def test_epoch_navigator_integration(self, tmp_path):
        """Test file navigator with epoch organization."""
        from ndi.file.navigator import EpochDir
        from ndi.validators import must_be_text_like
        from unittest.mock import MagicMock

        # Create mock session
        session = MagicMock()
        session_path = str(tmp_path / 'test_session')
        Path(session_path).mkdir()
        session.path.return_value = session_path

        # Create epoch directories
        epochs = ['t00001', 't00002', 't00003']
        for epoch_id in epochs:
            epoch_dir = Path(session_path) / epoch_id
            epoch_dir.mkdir()
            (epoch_dir / 'data.dat').write_text('test data')

        # Create navigator
        navigator = EpochDir(session, {'filematch': ['*.dat']})

        # Get file groups
        file_groups = navigator.selectfilegroups_disk()

        # Validate results
        assert len(file_groups) == 3
        for i, expected_id in enumerate(epochs, start=1):
            epoch_id = navigator.epochid(i, file_groups[i - 1])
            must_be_text_like(epoch_id)
            assert epoch_id == expected_id

    def test_validation_workflow(self):
        """Test validators working together."""
        from ndi.validators import must_be_text_like, must_be_epoch_input
        from ndi.ido import IDO

        # Validate text
        text_values = ["hello", "world", "test"]
        for text in text_values:
            must_be_text_like(text)

        # Validate epoch inputs (single values and 'all')
        must_be_epoch_input(1)  # integer
        must_be_epoch_input('all')  # string 'all'


class TestPhase2Integration:
    """Integration tests for Phase 2 components working together."""

    def test_spike_analysis_workflow(self):
        """Test complete spike analysis workflow."""
        from ndi.calc import SpikeRateCalculator

        # Generate synthetic spike data
        num_trials = 10
        trial_duration = 2.0
        spike_rate = 20  # Hz

        spike_data = []
        for trial in range(num_trials):
            num_spikes = np.random.poisson(spike_rate * trial_duration)
            spike_times = np.sort(np.random.uniform(0, trial_duration, num_spikes))
            spike_data.append(spike_times)

        # Calculate spike rates
        rate_calc = SpikeRateCalculator()
        spike_rates = []

        for spikes in spike_data:
            rate = rate_calc.calculate_mean_rate(spikes, trial_duration)
            spike_rates.append(rate)

        # Validate rates
        assert len(spike_rates) == num_trials
        assert all(rate >= 0 for rate in spike_rates)

    def test_multi_probe_recording(self):
        """Test multi-probe recording scenario."""
        from ndi.probe import ElectrodeProbe, MultiElectrodeProbe, OpticalProbe
        from unittest.mock import MagicMock

        session = MagicMock()

        # 1. Single electrode for LFP
        lfp_electrode = ElectrodeProbe(
            session,
            name='lfp1',
            reference=1,
            subject_id='mouse001',
            impedance=500e3,
            material='tungsten'
        )

        assert lfp_electrode.name == 'lfp1'
        assert lfp_electrode.impedance == 500e3

        # 2. Tetrode for spike sorting
        tetrode_geometry = np.array([[0, 0], [25, 0], [0, 25], [25, 25]])

        tetrode = MultiElectrodeProbe(
            session,
            name='tetrode1',
            reference=1,
            subject_id='mouse001',
            num_channels=4,
            probe_type='tetrode',
            geometry=tetrode_geometry
        )

        assert tetrode.num_channels == 4
        dist = tetrode.get_channel_distance(0, 1)
        assert np.isclose(dist, 25.0)

        # 3. Two-photon microscope
        microscope = OpticalProbe(
            session,
            name='2p_scope',
            reference=1,
            subject_id='mouse001',
            imaging_type='two-photon',
            wavelength=920,
            resolution=0.5,
            field_of_view=(512, 512),
            frame_rate=30
        )

        assert microscope.is_imaging()
        assert not microscope.is_stimulation()

        # Verify all probes have same subject
        assert lfp_electrode.subject_id == tetrode.subject_id == microscope.subject_id

    def test_cross_correlation_workflow(self):
        """Test cross-correlation analysis."""
        from ndi.calc import CrossCorrelationCalculator

        # Generate two correlated spike trains
        num_spikes = 100
        signal1 = np.sort(np.random.uniform(0, 10, num_spikes))
        shift = 0.02  # 20ms
        signal2 = signal1 + shift + np.random.normal(0, 0.005, num_spikes)

        # Calculate cross-correlation
        xcorr_calc = CrossCorrelationCalculator()
        result = xcorr_calc.calculate_cross_correlogram(
            signal1,
            signal2,
            bin_size=0.001,
            max_lag=0.1
        )

        # Validate results - the actual keys from calculate_cross_correlogram
        assert 'lags' in result
        assert 'counts' in result  # Not 'correlation', it's 'counts'
        assert len(result['lags']) == len(result['counts'])


class TestPhase1Phase2Combined:
    """Integration tests combining Phase 1 and Phase 2 components."""

    def test_complete_experiment_workflow(self):
        """Test complete workflow from setup to analysis."""
        from ndi.file import create_temp_filename
        from ndi.calc import SpikeRateCalculator
        from ndi.probe import ElectrodeProbe
        from unittest.mock import MagicMock

        # Step 1: Set up experiment
        session = MagicMock()
        electrode = ElectrodeProbe(
            session,
            name='electrode1',
            reference=1,
            subject_id='subject001',
            impedance=1e6
        )

        # Step 2: Generate spike data
        num_epochs = 3
        epoch_durations = [2.0, 2.0, 2.0]
        spike_data_files = []

        for epoch_idx in range(num_epochs):
            num_spikes = np.random.poisson(20 * epoch_durations[epoch_idx])
            spike_times = np.sort(np.random.uniform(0, epoch_durations[epoch_idx], num_spikes))

            # Save to temp file
            temp_file = create_temp_filename() + f'_epoch{epoch_idx}.npy'
            np.save(temp_file, spike_times)
            spike_data_files.append(temp_file)

        # Step 3: Analyze each epoch
        calc = SpikeRateCalculator()
        spike_rates = []

        for epoch_idx, spike_file in enumerate(spike_data_files):
            spike_times = np.load(spike_file)
            rate = calc.calculate_mean_rate(spike_times, epoch_durations[epoch_idx])
            spike_rates.append(rate)

        # Step 4: Validate results
        assert len(spike_rates) == num_epochs
        assert all(rate >= 0 for rate in spike_rates)

        # Cleanup
        for temp_file in spike_data_files:
            Path(temp_file).unlink()

    def test_multi_probe_data_organization(self, tmp_path):
        """Test organizing data from multiple probes."""
        from ndi.file.navigator import EpochDir
        from ndi.probe import MultiElectrodeProbe
        from ndi.validators import must_be_text_like
        from unittest.mock import MagicMock

        # Create session
        session_path = tmp_path / 'multi_probe_session'
        session_path.mkdir()

        session = MagicMock()
        session.path.return_value = str(session_path)

        # Create probes
        probe1 = MultiElectrodeProbe(
            session,
            name='tetrode1',
            reference=1,
            subject_id='rat001',
            num_channels=4,
            probe_type='tetrode'
        )

        probe2 = MultiElectrodeProbe(
            session,
            name='tetrode2',
            reference=2,
            subject_id='rat001',
            num_channels=4,
            probe_type='tetrode'
        )

        # Create epoch directories
        epochs = ['t00001', 't00002']
        for epoch_id in epochs:
            epoch_dir = session_path / epoch_id
            epoch_dir.mkdir()

            for probe in [probe1, probe2]:
                data_file = epoch_dir / f'{probe.name}_data.dat'
                data_file.write_text(f'Data from {probe.name}')

        # Create navigators
        nav1 = EpochDir(session, {'filematch': [f'{probe1.name}_*.dat']})
        nav2 = EpochDir(session, {'filematch': [f'{probe2.name}_*.dat']})

        # Get file groups
        files1 = nav1.selectfilegroups_disk()
        files2 = nav2.selectfilegroups_disk()

        # Validate
        assert len(files1) == 2
        assert len(files2) == 2

        # Verify epoch IDs match
        for i in range(len(epochs)):
            epoch_id_1 = nav1.epochid(i + 1, files1[i])
            epoch_id_2 = nav2.epochid(i + 1, files2[i])

            must_be_text_like(epoch_id_1)
            must_be_text_like(epoch_id_2)

            assert epoch_id_1 == epoch_id_2 == epochs[i]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
