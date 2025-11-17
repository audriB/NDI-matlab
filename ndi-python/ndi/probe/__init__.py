"""
NDI Probe - Base probe class and specialized probe types.

This module provides the base Probe class and concrete probe implementations
for common neuroscience measurement and stimulation devices.
"""

# Import base Probe class first
from ._probe import Probe

# Import specialized probe types
from .electrode import ElectrodeProbe
from .multielectrode import MultiElectrodeProbe
from .optical import OpticalProbe

__all__ = [
    'Probe',
    'ElectrodeProbe',
    'MultiElectrodeProbe',
    'OpticalProbe',
]
