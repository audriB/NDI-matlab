"""
NDI Epoch Package - Utilities for epoch management and probe mapping.

This package contains concrete implementations of epoch-related classes
and utility functions.

MATLAB equivalent: +ndi/+epoch/ package
"""

from .epochprobemap_daqsystem import EpochProbeMapDAQSystem

__all__ = [
    'EpochProbeMapDAQSystem',
]
