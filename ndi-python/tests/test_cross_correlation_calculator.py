"""
Tests for Cross-Correlation Calculator.

Tests all cross-correlation analysis methods.
"""

import pytest
import numpy as np
from ndi.calc.cross_correlation import CrossCorrelationCalculator


class TestCrossCorrelationCalculator:
    """Tests for CrossCorrelationCalculator class."""

    @pytest.fixture
    def calc(self):
        """Create calculator instance."""
        return CrossCorrelationCalculator(session=None)

    def test_calculator_creation(self, calc):
        """Test creating calculator."""
        assert calc is not None
        assert calc.name == 'CrossCorrelationCalculator'

    def test_calculate_cross_correlogram_simple(self, calc):
        """Test basic cross-correlogram calculation."""
        # Two spike trains with consistent lag
        spikes1 = np.array([0.1, 0.2, 0.3])
        spikes2 = np.array([0.11, 0.21, 0.31])  # Consistently 10ms after spikes1

        ccg = calc.calculate_cross_correlogram(
            spikes1, spikes2, max_lag=0.05, bin_size=0.01
        )

        assert 'lags' in ccg
        assert 'counts' in ccg
        assert 'normalized_counts' in ccg

        # Should have bins from -0.05 to 0.05
        assert len(ccg['lags']) > 0
        assert ccg['lags'][0] >= -0.05
        assert ccg['lags'][-1] <= 0.05

        # Total counts should be 3 (one for each reference spike)
        assert np.sum(ccg['counts']) == 3

    def test_calculate_cross_correlogram_zero_lag(self, calc):
        """Test cross-correlogram with perfectly synchronous spikes."""
        # Identical spike trains
        spikes1 = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        spikes2 = np.array([0.1, 0.2, 0.3, 0.4, 0.5])

        ccg = calc.calculate_cross_correlogram(
            spikes1, spikes2, max_lag=0.05, bin_size=0.01
        )

        # Peak should be at or near zero lag
        peak_idx = np.argmax(ccg['counts'])
        peak_lag = ccg['lags'][peak_idx]

        assert abs(peak_lag) < 0.01  # Within one bin of zero

    def test_calculate_cross_correlogram_empty_first(self, calc):
        """Test cross-correlogram with empty first spike train."""
        spikes1 = np.array([])
        spikes2 = np.array([0.1, 0.2, 0.3])

        ccg = calc.calculate_cross_correlogram(spikes1, spikes2)

        assert len(ccg['lags']) > 0
        assert np.all(ccg['counts'] == 0)
        assert np.all(ccg['normalized_counts'] == 0)

    def test_calculate_cross_correlogram_empty_second(self, calc):
        """Test cross-correlogram with empty second spike train."""
        spikes1 = np.array([0.1, 0.2, 0.3])
        spikes2 = np.array([])

        ccg = calc.calculate_cross_correlogram(spikes1, spikes2)

        assert len(ccg['lags']) > 0
        assert np.all(ccg['counts'] == 0)
        assert np.all(ccg['normalized_counts'] == 0)

    def test_calculate_cross_correlogram_both_empty(self, calc):
        """Test cross-correlogram with both spike trains empty."""
        spikes1 = np.array([])
        spikes2 = np.array([])

        ccg = calc.calculate_cross_correlogram(spikes1, spikes2)

        assert len(ccg['lags']) > 0
        assert np.all(ccg['counts'] == 0)

    def test_calculate_cross_correlogram_max_lag(self, calc):
        """Test that max_lag is respected."""
        spikes1 = np.array([0.1])
        spikes2 = np.array([0.0, 0.05, 0.1, 0.15, 0.2])

        max_lag = 0.03
        ccg = calc.calculate_cross_correlogram(
            spikes1, spikes2, max_lag=max_lag, bin_size=0.01
        )

        # Only spikes within ±0.03 should be counted
        # spikes2 at 0.05, 0.1, 0.15 are within range
        # 0.05: lag = -0.05 (outside)
        # 0.1: lag = 0 (inside)
        # 0.15: lag = 0.05 (outside)
        # Actually: from spikes1[0]=0.1: 0.05 is -0.05, 0.1 is 0, 0.15 is +0.05
        # Only 0.1 is within ±0.03
        assert np.sum(ccg['counts']) == 1

    def test_calculate_cross_correlogram_bin_size(self, calc):
        """Test that bin_size affects resolution."""
        spikes1 = np.array([0.1, 0.2, 0.3])
        spikes2 = np.array([0.11, 0.21, 0.31])

        # Fine bins
        ccg_fine = calc.calculate_cross_correlogram(
            spikes1, spikes2, max_lag=0.05, bin_size=0.001
        )

        # Coarse bins
        ccg_coarse = calc.calculate_cross_correlogram(
            spikes1, spikes2, max_lag=0.05, bin_size=0.01
        )

        # Fine should have more bins
        assert len(ccg_fine['lags']) > len(ccg_coarse['lags'])

    def test_find_peak_correlation(self, calc):
        """Test finding peak in cross-correlogram."""
        ccg = {
            'lags': np.array([-0.02, -0.01, 0, 0.01, 0.02]),
            'counts': np.array([5.0, 10.0, 20.0, 12.0, 6.0])
        }

        peak_lag, peak_count = calc.find_peak_correlation(ccg)

        assert peak_lag == 0.0
        assert peak_count == 20.0

    def test_find_peak_correlation_negative_lag(self, calc):
        """Test peak at negative lag."""
        ccg = {
            'lags': np.array([-0.02, -0.01, 0, 0.01, 0.02]),
            'counts': np.array([5.0, 25.0, 10.0, 8.0, 6.0])
        }

        peak_lag, peak_count = calc.find_peak_correlation(ccg)

        assert peak_lag == -0.01
        assert peak_count == 25.0

    def test_find_peak_correlation_empty(self, calc):
        """Test finding peak with empty data."""
        ccg = {
            'lags': np.array([]),
            'counts': np.array([])
        }

        peak_lag, peak_count = calc.find_peak_correlation(ccg)

        assert np.isnan(peak_lag)
        assert np.isnan(peak_count)

    def test_calculate_synchrony_index_perfect(self, calc):
        """Test synchrony index with perfect synchrony."""
        # Identical spike trains
        spikes1 = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        spikes2 = np.array([0.1, 0.2, 0.3, 0.4, 0.5])

        si = calc.calculate_synchrony_index(spikes1, spikes2, window=0.01)

        # All spikes should be coincident
        assert si == 1.0

    def test_calculate_synchrony_index_none(self, calc):
        """Test synchrony index with no synchrony."""
        # Completely non-overlapping spike trains
        spikes1 = np.array([0.1, 0.2, 0.3])
        spikes2 = np.array([0.15, 0.25, 0.35])

        si = calc.calculate_synchrony_index(spikes1, spikes2, window=0.001)

        # No spikes should be coincident with such a small window
        assert si == 0.0

    def test_calculate_synchrony_index_partial(self, calc):
        """Test synchrony index with partial synchrony."""
        # Some coincident, some not
        spikes1 = np.array([0.1, 0.2, 0.3, 0.4])
        spikes2 = np.array([0.101, 0.25, 0.301, 0.5])

        si = calc.calculate_synchrony_index(spikes1, spikes2, window=0.01)

        # First and third spikes from spikes1 are coincident
        # 0.1 matches 0.101 (diff = 0.001)
        # 0.3 matches 0.301 (diff = 0.001)
        # 2 out of 4 = 0.5
        assert si == pytest.approx(0.5)

    def test_calculate_synchrony_index_empty_first(self, calc):
        """Test synchrony index with empty first train."""
        spikes1 = np.array([])
        spikes2 = np.array([0.1, 0.2, 0.3])

        si = calc.calculate_synchrony_index(spikes1, spikes2)

        assert si == 0.0

    def test_calculate_synchrony_index_empty_second(self, calc):
        """Test synchrony index with empty second train."""
        spikes1 = np.array([0.1, 0.2, 0.3])
        spikes2 = np.array([])

        si = calc.calculate_synchrony_index(spikes1, spikes2)

        assert si == 0.0

    def test_calculate_synchrony_index_both_empty(self, calc):
        """Test synchrony index with both trains empty."""
        spikes1 = np.array([])
        spikes2 = np.array([])

        si = calc.calculate_synchrony_index(spikes1, spikes2)

        assert si == 0.0

    def test_calculate_integration_ccg_only(self, calc):
        """Test calculate method with CCG only."""
        spikes1 = np.array([0.1, 0.2, 0.3])
        spikes2 = np.array([0.11, 0.21, 0.31])

        params = {
            'spike_times1': spikes1,
            'spike_times2': spikes2,
            'analysis_types': ['ccg']
        }

        results = calc.calculate(params)

        assert 'ccg' in results
        assert 'peak_lag' not in results
        assert 'synchrony_index' not in results

    def test_calculate_integration_ccg_and_peak(self, calc):
        """Test calculate method with CCG and peak."""
        spikes1 = np.array([0.1, 0.2, 0.3])
        spikes2 = np.array([0.11, 0.21, 0.31])

        params = {
            'spike_times1': spikes1,
            'spike_times2': spikes2,
            'analysis_types': ['ccg', 'peak']
        }

        results = calc.calculate(params)

        assert 'ccg' in results
        assert 'peak_lag' in results
        assert 'peak_count' in results

    def test_calculate_integration_all_analyses(self, calc):
        """Test calculate method with all analyses."""
        spikes1 = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        spikes2 = np.array([0.11, 0.21, 0.31, 0.41, 0.51])

        params = {
            'spike_times1': spikes1,
            'spike_times2': spikes2,
            'max_lag': 0.05,
            'bin_size': 0.001,
            'analysis_types': ['ccg', 'peak', 'synchrony'],
            'synchrony_window': 0.03  # Use wider window to avoid edge cases
        }

        results = calc.calculate(params)

        assert 'ccg' in results
        assert 'peak_lag' in results
        assert 'peak_count' in results
        assert 'synchrony_index' in results

        # All spikes should be synchronous with window=0.03 (half-window 0.015 > 0.01 difference)
        assert results['synchrony_index'] == 1.0

    def test_calculate_integration_synchrony_only(self, calc):
        """Test calculate method with synchrony only."""
        spikes1 = np.array([0.1, 0.2, 0.3])
        spikes2 = np.array([0.11, 0.21, 0.31])

        params = {
            'spike_times1': spikes1,
            'spike_times2': spikes2,
            'analysis_types': ['synchrony']
        }

        results = calc.calculate(params)

        assert 'synchrony_index' in results
        assert 'ccg' not in results

    def test_calculate_integration_empty_data(self, calc):
        """Test calculate method with empty data."""
        params = {
            'spike_times1': np.array([]),
            'spike_times2': np.array([]),
            'analysis_types': ['ccg', 'peak', 'synchrony']
        }

        results = calc.calculate(params)

        assert 'ccg' in results
        assert 'peak_lag' in results
        assert 'synchrony_index' in results

        # Should handle empty gracefully
        # Note: peak_lag is valid (first lag bin) even with empty data, peak_count should be 0
        assert results['peak_count'] == 0.0
        assert results['synchrony_index'] == 0.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
