"""
NDI Element package - Base Element class and specializations.

This package contains the base Element class (re-exported from _element module)
and specialized element types like TimeSeriesElement.
"""

# Import base Element class from _element module
from .._element import Element

# These imports will work once the parent ndi module is fully loaded
# They are deferred to avoid circular imports during initial load

__all__ = [
    'Element',
    'TimeSeriesElement',
    'OneEpoch',
    'Downsample',
    'MissingEpochs',
    'SpikesForProbe',
    'spikes_for_probe',
    'missingepochs'
]


def __getattr__(name):
    """Lazy import to avoid circular dependencies."""
    if name == 'TimeSeriesElement':
        from .timeseries import TimeSeriesElement
        return TimeSeriesElement
    elif name == 'OneEpoch':
        from .oneepoch import OneEpoch
        return OneEpoch
    elif name == 'Downsample':
        from .downsample import Downsample
        return Downsample
    elif name == 'MissingEpochs':
        from .missingepochs import MissingEpochs
        return MissingEpochs
    elif name == 'SpikesForProbe':
        from .spikes_for_probe import SpikesForProbe
        return SpikesForProbe
    elif name == 'spikes_for_probe':
        from .spikes_for_probe import spikes_for_probe
        return spikes_for_probe
    elif name == 'missingepochs':
        from .missingepochs import missingepochs
        return missingepochs
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
