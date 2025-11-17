"""
Tests for Spike Rate Calculator.

Tests all spike rate calculation methods.
"""

import pytest
import numpy as np
from ndi.calc.spike_rate import SpikeRateCalculator


class TestSpikeRateCalculator:
    """Tests for SpikeRateCalculator class."""

    @pytest.fixture
    def calc(self):
        """Create calculator instance."""
        return SpikeRateCalculator(session=None)

    def test_calculator_creation(self, calc):
        """Test creating calculator."""
        assert calc is not None
        assert calc.name == 'SpikeRateCalculator'

    def test_mean_rate_simple(self, calc):
        """Test mean rate calculation."""
        spike_times = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        duration = 1.0
        rate = calc.calculate_mean_rate(spike_times, duration)
        assert rate == 5.0

    def test_mean_rate_empty(self, calc):
        """Test mean rate with no spikes."""
        spike_times = np.array([])
        duration = 1.0
        rate = calc.calculate_mean_rate(spike_times, duration)
        assert rate == 0.0

    def test_mean_rate_invalid_duration(self, calc):
        """Test mean rate with invalid duration."""
        spike_times = np.array([0.1, 0.2])
        with pytest.raises(ValueError, match="Duration must be positive"):
            calc.calculate_mean_rate(spike_times, 0.0)

    def test_instantaneous_rate_isi(self, calc):
        """Test instantaneous rate calculation."""
        # ISIs: 0.1, 0.05, 0.1
        spike_times = np.array([0.0, 0.1, 0.15, 0.25])
        rates = calc.calculate_instantaneous_rate(spike_times, method='isi')

        assert len(rates) == 3
        assert rates[0] == pytest.approx(10.0)  # 1/0.1
        assert rates[1] == pytest.approx(20.0)  # 1/0.05
        assert rates[2] == pytest.approx(10.0)  # 1/0.1

    def test_instantaneous_rate_few_spikes(self, calc):
        """Test instantaneous rate with too few spikes."""
        spike_times = np.array([0.1])
        rates = calc.calculate_instantaneous_rate(spike_times)
        assert len(rates) == 0

    def test_instantaneous_rate_unsorted(self, calc):
        """Test instantaneous rate with unsorted spikes."""
        spike_times = np.array([0.2, 0.1, 0.3])
        with pytest.raises(ValueError, match="must be sorted"):
            calc.calculate_instantaneous_rate(spike_times)

    def test_instantaneous_rate_kernel_not_implemented(self, calc):
        """Test that kernel method raises NotImplementedError."""
        spike_times = np.array([0.0, 0.1, 0.2])
        with pytest.raises(NotImplementedError):
            calc.calculate_instantaneous_rate(spike_times, method='kernel')

    def test_time_varying_rate(self, calc):
        """Test time-varying rate calculation."""
        # 5 spikes: 2 in first bin, 2 in second, 1 in third
        spike_times = np.array([0.05, 0.15, 0.25, 0.35, 0.55])
        time_bins = np.array([0.0, 0.2, 0.4, 0.6])

        centers, rates = calc.calculate_time_varying_rate(spike_times, time_bins)

        assert len(centers) == 3
        assert len(rates) == 3

        # Each bin is 0.2s wide
        assert rates[0] == pytest.approx(10.0)  # 2 spikes / 0.2s
        assert rates[1] == pytest.approx(10.0)  # 2 spikes / 0.2s
        assert rates[2] == pytest.approx(5.0)   # 1 spike / 0.2s

        # Check bin centers
        assert centers[0] == pytest.approx(0.1)
        assert centers[1] == pytest.approx(0.3)
        assert centers[2] == pytest.approx(0.5)

    def test_time_varying_rate_invalid_bins(self, calc):
        """Test time-varying rate with invalid bins."""
        spike_times = np.array([0.1, 0.2])
        time_bins = np.array([0.0])
        with pytest.raises(ValueError, match="at least 2 elements"):
            calc.calculate_time_varying_rate(spike_times, time_bins)

    def test_isi_statistics(self, calc):
        """Test ISI statistics calculation."""
        # ISIs: 0.1, 0.1, 0.15
        spike_times = np.array([0.0, 0.1, 0.2, 0.35])
        stats = calc.calculate_isi_statistics(spike_times)

        assert 'mean_isi' in stats
        assert 'std_isi' in stats
        assert 'cv_isi' in stats
        assert 'median_isi' in stats
        assert 'min_isi' in stats
        assert 'max_isi' in stats

        assert stats['mean_isi'] == pytest.approx(0.11666666, rel=1e-5)
        assert stats['median_isi'] == pytest.approx(0.1)
        assert stats['min_isi'] == pytest.approx(0.1)
        assert stats['max_isi'] == pytest.approx(0.15)

    def test_isi_statistics_few_spikes(self, calc):
        """Test ISI statistics with too few spikes."""
        spike_times = np.array([0.1])
        with pytest.raises(ValueError, match="at least 2 spikes"):
            calc.calculate_isi_statistics(spike_times)

    def test_burst_statistics(self, calc):
        """Test burst detection."""
        # Two bursts: [0.0, 0.005, 0.01] and [0.5, 0.505, 0.51]
        # Isolated: none
        spike_times = np.array([0.0, 0.005, 0.01, 0.5, 0.505, 0.51])
        stats = calc.calculate_burst_statistics(spike_times, max_isi_in_burst=0.02)

        assert stats['num_bursts'] == 2
        assert stats['burst_spikes'] == 6
        assert stats['isolated_spikes'] == 0
        assert stats['mean_burst_length'] == pytest.approx(3.0)
        assert stats['burst_fraction'] == pytest.approx(1.0)

    def test_burst_statistics_no_bursts(self, calc):
        """Test burst detection with no bursts."""
        # All ISIs > threshold
        spike_times = np.array([0.0, 0.1, 0.2, 0.3])
        stats = calc.calculate_burst_statistics(spike_times, max_isi_in_burst=0.01)

        assert stats['num_bursts'] == 0
        assert stats['burst_spikes'] == 0
        assert stats['isolated_spikes'] == 4
        assert stats['burst_fraction'] == 0.0

    def test_burst_statistics_one_spike(self, calc):
        """Test burst detection with one spike."""
        spike_times = np.array([0.1])
        stats = calc.calculate_burst_statistics(spike_times)

        assert stats['num_bursts'] == 0
        assert stats['burst_spikes'] == 0
        assert stats['isolated_spikes'] == 1

    def test_calculate_integration(self, calc):
        """Test full calculate method."""
        spike_times = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        params = {
            'spike_times': spike_times,
            'duration': 1.0,
            'methods': ['mean_rate', 'isi_stats']
        }

        results = calc.calculate(params)

        assert 'mean_rate' in results
        assert 'isi_stats' in results
        assert results['mean_rate'] == 5.0
        assert results['isi_stats']['mean_isi'] == pytest.approx(0.1)

    def test_calculate_all_methods(self, calc):
        """Test calculate with all methods."""
        spike_times = np.array([0.0, 0.005, 0.01, 0.5, 0.505, 0.51])
        params = {
            'spike_times': spike_times,
            'duration': 1.0,
            'methods': ['mean_rate', 'instantaneous_rate', 'isi_stats', 'burst_stats'],
            'max_isi_in_burst': 0.02
        }

        results = calc.calculate(params)

        assert 'mean_rate' in results
        assert 'instantaneous_rate' in results
        assert 'isi_stats' in results
        assert 'burst_stats' in results


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
