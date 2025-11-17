"""
NDI Epoch Package - Core epoch classes and utilities.

This package contains the base epoch classes (re-exported from _epoch module)
and epoch utility implementations like EpochProbeMapDAQSystem.

MATLAB equivalent: +ndi/+epoch/ package
"""

# Import core classes from _epoch module
from .._epoch import Epoch, EpochSet, EpochProbeMap, findepochnode, epochrange

# Use lazy loading for utilities to avoid circular imports
__all__ = [
    'Epoch',
    'EpochSet',
    'EpochProbeMap',
    'findepochnode',
    'epochrange',
    'EpochProbeMapDAQSystem',
]


def __getattr__(name):
    """Lazy import to avoid circular dependencies."""
    if name == 'EpochProbeMapDAQSystem':
        from .epochprobemap_daqsystem import EpochProbeMapDAQSystem
        return EpochProbeMapDAQSystem
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
