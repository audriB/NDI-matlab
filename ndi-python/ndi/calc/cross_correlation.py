"""
Cross-Correlation Calculator - Analyze temporal relationships between spike trains.

Computes cross-correlograms to analyze spike timing relationships between neurons.

MATLAB equivalent: Custom cross-correlation analysis
"""

from typing import Dict, Any, Optional, Tuple
import numpy as np


class CrossCorrelationCalculator:
    """
    Calculate cross-correlations between spike trains.

    Analyzes temporal relationships between neurons by computing
    cross-correlograms showing spike timing dependencies.

    Examples:
        >>> calc = CrossCorrelationCalculator()
        >>> spikes1 = np.array([0.1, 0.3, 0.5])
        >>> spikes2 = np.array([0.15, 0.35, 0.55])
        >>> ccg = calc.calculate_cross_correlogram(spikes1, spikes2, max_lag=0.1, bin_size=0.01)
    """

    def __init__(self, session: Optional[Any] = None):
        """
        Create a CrossCorrelationCalculator.

        Args:
            session: Optional NDI Session object

        Examples:
            >>> calc = CrossCorrelationCalculator()
            >>> calc.name
            'CrossCorrelationCalculator'
        """
        self.session = session
        self.name = 'CrossCorrelationCalculator'

    def calculate_cross_correlogram(self,
                                   spike_times1: np.ndarray,
                                   spike_times2: np.ndarray,
                                   max_lag: float = 0.05,
                                   bin_size: float = 0.001) -> Dict[str, Any]:
        """
        Calculate cross-correlogram between two spike trains.

        Args:
            spike_times1: First spike train (reference)
            spike_times2: Second spike train (target)
            max_lag: Maximum lag to compute (seconds)
            bin_size: Bin size for histogram (seconds)

        Returns:
            Dict with:
            - 'lags': Array of lag values (seconds)
            - 'counts': Cross-correlogram counts
            - 'normalized_counts': Counts normalized by bin size and duration

        Examples:
            >>> spikes1 = np.array([0.1, 0.2, 0.3])
            >>> spikes2 = np.array([0.15, 0.25, 0.35])
            >>> ccg = calc.calculate_cross_correlogram(spikes1, spikes2)
            >>> 'lags' in ccg and 'counts' in ccg
            True
        """
        if len(spike_times1) == 0 or len(spike_times2) == 0:
            n_bins = int(2 * max_lag / bin_size) + 1
            lags = np.linspace(-max_lag, max_lag, n_bins)
            return {
                'lags': lags,
                'counts': np.zeros(len(lags)),
                'normalized_counts': np.zeros(len(lags))
            }

        # Compute all pairwise time differences
        differences = []
        for t1 in spike_times1:
            diffs = spike_times2 - t1
            # Only keep differences within max_lag
            valid_diffs = diffs[(diffs >= -max_lag) & (diffs <= max_lag)]
            differences.extend(valid_diffs)

        differences = np.array(differences)

        # Create histogram bins
        n_bins = int(2 * max_lag / bin_size) + 1
        bins = np.linspace(-max_lag, max_lag, n_bins + 1)
        lags = (bins[:-1] + bins[1:]) / 2

        # Histogram the differences
        counts, _ = np.histogram(differences, bins=bins)

        # Normalize by bin size and number of reference spikes
        duration = max(np.max(spike_times1), np.max(spike_times2)) - \
                  min(np.min(spike_times1), np.min(spike_times2))
        normalized_counts = counts / (bin_size * len(spike_times1)) if duration > 0 else counts

        return {
            'lags': lags,
            'counts': counts.astype(float),
            'normalized_counts': normalized_counts
        }

    def find_peak_correlation(self, ccg: Dict[str, Any]) -> Tuple[float, float]:
        """
        Find peak of cross-correlogram.

        Args:
            ccg: Output from calculate_cross_correlogram()

        Returns:
            Tuple of (peak_lag, peak_count)

        Examples:
            >>> ccg = {'lags': np.array([-0.01, 0, 0.01]),
            ...        'counts': np.array([5, 15, 8])}
            >>> lag, count = calc.find_peak_correlation(ccg)
            >>> lag
            0.0
            >>> count
            15.0
        """
        if len(ccg['counts']) == 0:
            return np.nan, np.nan

        peak_idx = np.argmax(ccg['counts'])
        return float(ccg['lags'][peak_idx]), float(ccg['counts'][peak_idx])

    def calculate_synchrony_index(self,
                                 spike_times1: np.ndarray,
                                 spike_times2: np.ndarray,
                                 window: float = 0.005) -> float:
        """
        Calculate synchrony index (fraction of coincident spikes).

        Args:
            spike_times1: First spike train
            spike_times2: Second spike train
            window: Time window for coincidence (seconds)

        Returns:
            Synchrony index (0 to 1)

        Examples:
            >>> spikes1 = np.array([0.1, 0.2, 0.3])
            >>> spikes2 = np.array([0.101, 0.25, 0.35])
            >>> si = calc.calculate_synchrony_index(spikes1, spikes2, window=0.01)
            >>> 0 <= si <= 1
            True
        """
        if len(spike_times1) == 0 or len(spike_times2) == 0:
            return 0.0

        # Count coincident spikes (spikes in train2 within window of train1)
        coincident = 0
        for t1 in spike_times1:
            if np.any(np.abs(spike_times2 - t1) <= window / 2):
                coincident += 1

        return coincident / len(spike_times1)

    def calculate(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive cross-correlation analysis.

        Args:
            parameters: Dict with:
                - 'spike_times1': First spike train
                - 'spike_times2': Second spike train
                - 'max_lag': Maximum lag (default: 0.05)
                - 'bin_size': Bin size (default: 0.001)
                - 'analysis_types': List of analyses

        Returns:
            Dict with requested analyses

        Examples:
            >>> params = {
            ...     'spike_times1': np.array([0.1, 0.2, 0.3]),
            ...     'spike_times2': np.array([0.15, 0.25, 0.35]),
            ...     'analysis_types': ['ccg', 'peak', 'synchrony']
            ... }
            >>> results = calc.calculate(params)
            >>> 'ccg' in results
            True
        """
        spike_times1 = parameters.get('spike_times1', np.array([]))
        spike_times2 = parameters.get('spike_times2', np.array([]))
        max_lag = parameters.get('max_lag', 0.05)
        bin_size = parameters.get('bin_size', 0.001)
        analysis_types = parameters.get('analysis_types', ['ccg'])

        results = {}

        if 'ccg' in analysis_types:
            ccg = self.calculate_cross_correlogram(
                spike_times1, spike_times2, max_lag, bin_size
            )
            results['ccg'] = ccg

            if 'peak' in analysis_types:
                peak_lag, peak_count = self.find_peak_correlation(ccg)
                results['peak_lag'] = peak_lag
                results['peak_count'] = peak_count

        if 'synchrony' in analysis_types:
            window = parameters.get('synchrony_window', 0.005)
            results['synchrony_index'] = self.calculate_synchrony_index(
                spike_times1, spike_times2, window
            )

        return results
