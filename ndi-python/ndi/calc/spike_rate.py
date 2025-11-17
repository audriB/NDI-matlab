"""
Spike Rate Calculator - Calculate firing rates from spike data.

This calculator computes various spike rate metrics from neural spike data,
including mean firing rate, instantaneous firing rate, and time-varying rates.

MATLAB equivalent: Similar to spike analysis in various MATLAB toolboxes
"""

from typing import Optional, Dict, Any, List, Tuple
import numpy as np
from pathlib import Path


class SpikeRateCalculator:
    """
    Calculate spike rates from neural data.

    Computes firing rate metrics from spike times, including:
    - Mean firing rate
    - Instantaneous firing rate
    - Time-varying firing rate (PSTH-style)
    - Inter-spike interval (ISI) statistics

    This is a standalone calculator that doesn't require NDI session infrastructure.
    For full NDI integration, use as a mixin or wrap in Calculator class.

    MATLAB equivalent: Custom spike rate calculations

    Examples:
        >>> calc = SpikeRateCalculator()
        >>> spike_times = np.array([0.1, 0.2, 0.3])
        >>> rate = calc.calculate_mean_rate(spike_times, 1.0)
        >>> rate
        3.0
    """

    def __init__(self, session: Optional[Any] = None):
        """
        Create a SpikeRateCalculator.

        Args:
            session: Optional NDI Session object (for future NDI integration)

        Examples:
            >>> calc = SpikeRateCalculator()
            >>> calc.name
            'SpikeRateCalculator'
        """
        self.session = session
        self.name = 'SpikeRateCalculator'

    def calculate_mean_rate(self,
                           spike_times: np.ndarray,
                           duration: float) -> float:
        """
        Calculate mean firing rate.

        Args:
            spike_times: Array of spike times (seconds)
            duration: Total duration of recording (seconds)

        Returns:
            Mean firing rate in Hz

        Raises:
            ValueError: If duration <= 0

        Examples:
            >>> spike_times = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
            >>> duration = 1.0
            >>> rate = calc.calculate_mean_rate(spike_times, duration)
            >>> rate
            5.0
        """
        if duration <= 0:
            raise ValueError("Duration must be positive")

        if len(spike_times) == 0:
            return 0.0

        return len(spike_times) / duration

    def calculate_instantaneous_rate(self,
                                    spike_times: np.ndarray,
                                    method: str = 'isi') -> np.ndarray:
        """
        Calculate instantaneous firing rate.

        Args:
            spike_times: Array of spike times (seconds), must be sorted
            method: Method for calculation:
                - 'isi': 1 / ISI (inter-spike interval)
                - 'kernel': Gaussian kernel smoothing (not yet implemented)

        Returns:
            Array of instantaneous rates (Hz) at each spike time

        Raises:
            ValueError: If spike_times not sorted or invalid method

        Examples:
            >>> spike_times = np.array([0.0, 0.1, 0.15, 0.25])
            >>> rates = calc.calculate_instantaneous_rate(spike_times)
            >>> # Returns rates based on ISIs: [10.0, 20.0, 10.0]
        """
        if len(spike_times) < 2:
            return np.array([])

        # Verify sorted
        if not np.all(np.diff(spike_times) >= 0):
            raise ValueError("spike_times must be sorted")

        if method == 'isi':
            # Calculate ISIs
            isis = np.diff(spike_times)

            # Instantaneous rate is 1 / ISI
            # Return rates at spike times (excluding first spike)
            rates = 1.0 / isis
            return rates

        elif method == 'kernel':
            raise NotImplementedError(
                "Kernel smoothing not yet implemented. "
                "Use method='isi' for now."
            )
        else:
            raise ValueError(f"Unknown method: {method}")

    def calculate_time_varying_rate(self,
                                   spike_times: np.ndarray,
                                   time_bins: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate time-varying firing rate (PSTH-style).

        Bins spikes into time windows and calculates rate in each bin.

        Args:
            spike_times: Array of spike times (seconds)
            time_bins: Array of bin edges (seconds), length N+1 for N bins

        Returns:
            Tuple of (bin_centers, rates):
            - bin_centers: Center time of each bin
            - rates: Firing rate in each bin (Hz)

        Examples:
            >>> spike_times = np.array([0.05, 0.15, 0.25, 0.35, 0.45])
            >>> time_bins = np.array([0.0, 0.2, 0.4, 0.6])
            >>> centers, rates = calc.calculate_time_varying_rate(spike_times, time_bins)
            >>> # Returns rates in each 0.2s bin
        """
        if len(time_bins) < 2:
            raise ValueError("time_bins must have at least 2 elements")

        # Count spikes in each bin
        spike_counts, _ = np.histogram(spike_times, bins=time_bins)

        # Calculate bin widths
        bin_widths = np.diff(time_bins)

        # Calculate rates (counts / width)
        rates = spike_counts / bin_widths

        # Calculate bin centers
        bin_centers = time_bins[:-1] + bin_widths / 2

        return bin_centers, rates

    def calculate_isi_statistics(self,
                                spike_times: np.ndarray) -> Dict[str, float]:
        """
        Calculate inter-spike interval (ISI) statistics.

        Args:
            spike_times: Array of spike times (seconds), must be sorted

        Returns:
            Dict with ISI statistics:
            - 'mean_isi': Mean ISI (seconds)
            - 'std_isi': Standard deviation of ISI (seconds)
            - 'cv_isi': Coefficient of variation (std / mean)
            - 'median_isi': Median ISI (seconds)
            - 'min_isi': Minimum ISI (seconds)
            - 'max_isi': Maximum ISI (seconds)

        Raises:
            ValueError: If fewer than 2 spikes

        Examples:
            >>> spike_times = np.array([0.0, 0.1, 0.2, 0.35])
            >>> stats = calc.calculate_isi_statistics(spike_times)
            >>> stats['mean_isi']  # doctest: +SKIP
            0.11666...
        """
        if len(spike_times) < 2:
            raise ValueError("Need at least 2 spikes to calculate ISI")

        # Verify sorted
        if not np.all(np.diff(spike_times) >= 0):
            raise ValueError("spike_times must be sorted")

        # Calculate ISIs
        isis = np.diff(spike_times)

        return {
            'mean_isi': float(np.mean(isis)),
            'std_isi': float(np.std(isis)),
            'cv_isi': float(np.std(isis) / np.mean(isis)) if np.mean(isis) > 0 else 0.0,
            'median_isi': float(np.median(isis)),
            'min_isi': float(np.min(isis)),
            'max_isi': float(np.max(isis))
        }

    def calculate_burst_statistics(self,
                                  spike_times: np.ndarray,
                                  max_isi_in_burst: float = 0.01) -> Dict[str, Any]:
        """
        Detect and analyze burst firing.

        A burst is defined as a sequence of spikes with ISI < max_isi_in_burst.

        Args:
            spike_times: Array of spike times (seconds), must be sorted
            max_isi_in_burst: Maximum ISI to be considered within a burst (seconds)

        Returns:
            Dict with burst statistics:
            - 'num_bursts': Number of bursts detected
            - 'burst_spikes': Total spikes in bursts
            - 'isolated_spikes': Spikes not in bursts
            - 'mean_burst_length': Mean number of spikes per burst
            - 'burst_fraction': Fraction of spikes in bursts

        Examples:
            >>> # Spikes with bursts at start and end
            >>> spike_times = np.array([0.0, 0.005, 0.01, 0.5, 0.505, 0.51])
            >>> stats = calc.calculate_burst_statistics(spike_times, max_isi_in_burst=0.02)
            >>> stats['num_bursts']
            2
        """
        if len(spike_times) < 2:
            return {
                'num_bursts': 0,
                'burst_spikes': 0,
                'isolated_spikes': len(spike_times),
                'mean_burst_length': 0.0,
                'burst_fraction': 0.0
            }

        # Calculate ISIs
        isis = np.diff(spike_times)

        # Use a simple state machine to detect bursts
        # A burst starts with a short ISI and ends when we see a long ISI
        burst_lengths = []
        current_burst_length = 1  # Start with first spike

        for i, isi in enumerate(isis):
            if isi < max_isi_in_burst:
                # Continue/start burst
                current_burst_length += 1
            else:
                # End of burst (if we had one)
                if current_burst_length >= 2:  # Only count as burst if >= 2 spikes
                    burst_lengths.append(current_burst_length)
                current_burst_length = 1  # Reset for next potential burst

        # Don't forget the last burst if we ended in one
        if current_burst_length >= 2:
            burst_lengths.append(current_burst_length)

        num_bursts = len(burst_lengths)
        burst_spikes = sum(burst_lengths)
        isolated_spikes = len(spike_times) - burst_spikes

        return {
            'num_bursts': num_bursts,
            'burst_spikes': burst_spikes,
            'isolated_spikes': isolated_spikes,
            'mean_burst_length': float(np.mean(burst_lengths)) if burst_lengths else 0.0,
            'burst_fraction': burst_spikes / len(spike_times) if len(spike_times) > 0 else 0.0
        }


    def calculate(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform spike rate calculation with given parameters.

        Args:
            parameters: Calculation parameters including:
                - 'spike_times': Spike times array
                - 'duration': Recording duration
                - 'methods': List of methods to run

        Returns:
            Dict with calculation results

        Examples:
            >>> params = {
            ...     'spike_times': np.array([0.1, 0.2, 0.3]),
            ...     'duration': 1.0,
            ...     'methods': ['mean_rate', 'isi_stats']
            ... }
            >>> results = calc.calculate(params)
            >>> 'mean_rate' in results
            True
        """
        spike_times = parameters.get('spike_times', np.array([]))
        duration = parameters.get('duration', 1.0)
        methods = parameters.get('methods', ['mean_rate'])

        results = {}

        if 'mean_rate' in methods:
            results['mean_rate'] = self.calculate_mean_rate(spike_times, duration)

        if 'instantaneous_rate' in methods and len(spike_times) >= 2:
            results['instantaneous_rate'] = self.calculate_instantaneous_rate(spike_times)

        if 'isi_stats' in methods and len(spike_times) >= 2:
            results['isi_stats'] = self.calculate_isi_statistics(spike_times)

        if 'burst_stats' in methods and len(spike_times) >= 2:
            max_isi = parameters.get('max_isi_in_burst', 0.01)
            results['burst_stats'] = self.calculate_burst_statistics(spike_times, max_isi)

        return results
