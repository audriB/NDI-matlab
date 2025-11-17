"""
Tuning Curve Calculator - Calculate stimulus tuning curves for neurons.

Computes tuning curves showing how neural responses vary with stimulus parameters
like orientation, direction, frequency, etc.

MATLAB equivalent: ndi.calc.stimulus.tuningcurve
"""

from typing import Dict, Any, List, Tuple, Optional, Union
import numpy as np


class TuningCurveCalculator:
    """
    Calculate tuning curves from neural responses to stimuli.

    Analyzes how neurons respond to different stimulus parameters,
    computing mean responses, standard errors, and tuning metrics.

    Examples:
        >>> calc = TuningCurveCalculator()
        >>> stimuli = np.array([0, 45, 90, 135, 180, 225, 270, 315])  # Orientations
        >>> responses = np.array([10, 15, 25, 20, 12, 8, 18, 22])  # Spike counts
        >>> curve = calc.calculate_tuning_curve(stimuli, responses)
    """

    def __init__(self, session: Optional[Any] = None):
        """
        Create a TuningCurveCalculator.

        Args:
            session: Optional NDI Session object

        Examples:
            >>> calc = TuningCurveCalculator()
            >>> calc.name
            'TuningCurveCalculator'
        """
        self.session = session
        self.name = 'TuningCurveCalculator'

    def calculate_tuning_curve(self,
                              stimulus_values: np.ndarray,
                              responses: np.ndarray,
                              stimulus_repeats: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Calculate tuning curve from stimulus-response pairs.

        Args:
            stimulus_values: Array of stimulus parameter values
            responses: Array of response values (same length as stimulus_values)
            stimulus_repeats: Optional array indicating which responses belong
                            to same stimulus (for computing error bars)

        Returns:
            Dict with:
            - 'unique_stimuli': Unique stimulus values (sorted)
            - 'mean_responses': Mean response for each unique stimulus
            - 'std_responses': Standard deviation for each stimulus
            - 'sem_responses': Standard error of mean
            - 'n_trials': Number of trials per stimulus

        Examples:
            >>> stimuli = np.array([0, 45, 90, 0, 45, 90])
            >>> responses = np.array([10, 15, 25, 12, 17, 23])
            >>> curve = calc.calculate_tuning_curve(stimuli, responses)
            >>> curve['unique_stimuli']
            array([ 0, 45, 90])
            >>> curve['mean_responses']  # doctest: +SKIP
            array([11., 16., 24.])
        """
        if len(stimulus_values) != len(responses):
            raise ValueError("stimulus_values and responses must have same length")

        if len(stimulus_values) == 0:
            return {
                'unique_stimuli': np.array([]),
                'mean_responses': np.array([]),
                'std_responses': np.array([]),
                'sem_responses': np.array([]),
                'n_trials': np.array([])
            }

        # Get unique stimuli and sort
        unique_stimuli = np.unique(stimulus_values)

        # Calculate statistics for each unique stimulus
        mean_responses = []
        std_responses = []
        sem_responses = []
        n_trials = []

        for stim in unique_stimuli:
            mask = stimulus_values == stim
            stim_responses = responses[mask]

            mean_responses.append(np.mean(stim_responses))
            std_responses.append(np.std(stim_responses, ddof=1) if len(stim_responses) > 1 else 0.0)
            sem_responses.append(
                np.std(stim_responses, ddof=1) / np.sqrt(len(stim_responses))
                if len(stim_responses) > 1 else 0.0
            )
            n_trials.append(len(stim_responses))

        return {
            'unique_stimuli': unique_stimuli,
            'mean_responses': np.array(mean_responses),
            'std_responses': np.array(std_responses),
            'sem_responses': np.array(sem_responses),
            'n_trials': np.array(n_trials)
        }

    def find_preferred_stimulus(self, tuning_curve: Dict[str, Any]) -> Tuple[float, float]:
        """
        Find the preferred stimulus (maximum response).

        Args:
            tuning_curve: Output from calculate_tuning_curve()

        Returns:
            Tuple of (preferred_stimulus, max_response)

        Examples:
            >>> curve = {'unique_stimuli': np.array([0, 45, 90]),
            ...          'mean_responses': np.array([10, 15, 25])}
            >>> pref_stim, max_resp = calc.find_preferred_stimulus(curve)
            >>> pref_stim
            90.0
            >>> max_resp
            25.0
        """
        if len(tuning_curve['mean_responses']) == 0:
            return np.nan, np.nan

        max_idx = np.argmax(tuning_curve['mean_responses'])
        return (
            float(tuning_curve['unique_stimuli'][max_idx]),
            float(tuning_curve['mean_responses'][max_idx])
        )

    def calculate_selectivity_index(self,
                                   tuning_curve: Dict[str, Any]) -> float:
        """
        Calculate selectivity index (max - min) / (max + min).

        This metric quantifies how selective the neuron is for different stimuli.
        Values range from 0 (no selectivity) to 1 (complete selectivity).

        Args:
            tuning_curve: Output from calculate_tuning_curve()

        Returns:
            Selectivity index (0 to 1)

        Examples:
            >>> curve = {'mean_responses': np.array([10, 15, 25])}
            >>> si = calc.calculate_selectivity_index(curve)
            >>> si  # doctest: +SKIP
            0.428...
        """
        responses = tuning_curve['mean_responses']

        if len(responses) == 0:
            return np.nan

        max_resp = np.max(responses)
        min_resp = np.min(responses)

        if max_resp + min_resp == 0:
            return 0.0

        return (max_resp - min_resp) / (max_resp + min_resp)

    def calculate_circular_variance(self,
                                   tuning_curve: Dict[str, Any],
                                   is_circular: bool = True) -> float:
        """
        Calculate circular variance for circular stimuli (e.g., orientation).

        Circular variance ranges from 0 (very tuned) to 1 (not tuned).

        Args:
            tuning_curve: Output from calculate_tuning_curve()
            is_circular: Whether stimulus is circular (e.g., orientation in degrees)

        Returns:
            Circular variance (0 to 1)

        Examples:
            >>> # Highly tuned neuron
            >>> curve = {
            ...     'unique_stimuli': np.array([0, 90, 180, 270]),
            ...     'mean_responses': np.array([20, 5, 5, 5])
            ... }
            >>> cv = calc.calculate_circular_variance(curve)
            >>> cv < 0.5  # Low variance = high tuning
            True
        """
        if not is_circular:
            raise ValueError("Circular variance only applies to circular stimuli")

        stimuli = tuning_curve['unique_stimuli']
        responses = tuning_curve['mean_responses']

        if len(responses) == 0:
            return np.nan

        # Convert stimuli to radians (assuming degrees)
        theta = np.deg2rad(stimuli)

        # Calculate vector strength
        # Weight each angle by its response
        total_response = np.sum(responses)
        if total_response == 0:
            return 1.0  # No tuning if no responses

        x = np.sum(responses * np.cos(theta)) / total_response
        y = np.sum(responses * np.sin(theta)) / total_response

        # Vector length (ranges from 0 to 1)
        vector_length = np.sqrt(x**2 + y**2)

        # Circular variance is 1 - vector_length
        return 1.0 - vector_length

    def fit_gaussian_tuning(self,
                          tuning_curve: Dict[str, Any]) -> Dict[str, float]:
        """
        Fit a Gaussian function to the tuning curve.

        Gaussian model: A * exp(-((x - mu)^2) / (2 * sigma^2)) + baseline

        Args:
            tuning_curve: Output from calculate_tuning_curve()

        Returns:
            Dict with fitted parameters:
            - 'amplitude': Gaussian amplitude
            - 'mean': Preferred stimulus (Gaussian mean)
            - 'std': Tuning width (Gaussian std)
            - 'baseline': Baseline response
            - 'r_squared': Goodness of fit

        Note:
            This is a simplified implementation using basic curve fitting.
            For production use, consider scipy.optimize.curve_fit.

        Examples:
            >>> curve = {
            ...     'unique_stimuli': np.array([0, 45, 90, 135, 180]),
            ...     'mean_responses': np.array([5, 10, 20, 10, 5])
            ... }
            >>> fit = calc.fit_gaussian_tuning(curve)
            >>> 'amplitude' in fit
            True
        """
        stimuli = tuning_curve['unique_stimuli']
        responses = tuning_curve['mean_responses']

        if len(responses) < 4:
            return {
                'amplitude': np.nan,
                'mean': np.nan,
                'std': np.nan,
                'baseline': np.nan,
                'r_squared': np.nan
            }

        # Simple parameter estimation (not optimal, but functional)
        baseline = np.min(responses)
        amplitude = np.max(responses) - baseline
        mean = stimuli[np.argmax(responses)]

        # Estimate std from half-width at half-maximum
        half_max = baseline + amplitude / 2
        above_half = responses > half_max
        if np.sum(above_half) >= 2:
            indices = np.where(above_half)[0]
            width = stimuli[indices[-1]] - stimuli[indices[0]]
            std = width / 2.355  # FWHM = 2.355 * sigma for Gaussian
        else:
            std = (stimuli[-1] - stimuli[0]) / 4  # Rough estimate

        # Calculate R-squared
        predicted = amplitude * np.exp(-((stimuli - mean)**2) / (2 * std**2)) + baseline
        ss_res = np.sum((responses - predicted)**2)
        ss_tot = np.sum((responses - np.mean(responses))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

        return {
            'amplitude': float(amplitude),
            'mean': float(mean),
            'std': float(std),
            'baseline': float(baseline),
            'r_squared': float(r_squared)
        }

    def calculate(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive tuning curve analysis.

        Args:
            parameters: Dict with:
                - 'stimulus_values': Stimulus parameter values
                - 'responses': Response values
                - 'analysis_types': List of analyses to perform

        Returns:
            Dict with requested analyses

        Examples:
            >>> params = {
            ...     'stimulus_values': np.array([0, 45, 90, 135]),
            ...     'responses': np.array([10, 15, 20, 15]),
            ...     'analysis_types': ['tuning_curve', 'preferred', 'selectivity']
            ... }
            >>> results = calc.calculate(params)
            >>> 'tuning_curve' in results
            True
        """
        stimulus_values = parameters.get('stimulus_values', np.array([]))
        responses = parameters.get('responses', np.array([]))
        analysis_types = parameters.get('analysis_types', ['tuning_curve'])

        results = {}

        # Always calculate tuning curve first
        tuning_curve = self.calculate_tuning_curve(stimulus_values, responses)

        if 'tuning_curve' in analysis_types:
            results['tuning_curve'] = tuning_curve

        if 'preferred' in analysis_types:
            pref_stim, max_resp = self.find_preferred_stimulus(tuning_curve)
            results['preferred_stimulus'] = pref_stim
            results['max_response'] = max_resp

        if 'selectivity' in analysis_types:
            results['selectivity_index'] = self.calculate_selectivity_index(tuning_curve)

        if 'circular_variance' in analysis_types:
            is_circular = parameters.get('is_circular', True)
            results['circular_variance'] = self.calculate_circular_variance(
                tuning_curve, is_circular
            )

        if 'gaussian_fit' in analysis_types:
            results['gaussian_fit'] = self.fit_gaussian_tuning(tuning_curve)

        return results
