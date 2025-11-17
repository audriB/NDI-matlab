"""
NDI File - File navigation and management utilities.
"""

# Import base classes first (from the _navigator.py file, not navigator/ package)
from ._navigator import Navigator

# Import utilities
from .utilities import (
    temp_name,
    temp_fid,
    pfilemirror,
    create_temp_file,
    create_temp_filename,
    mirror_directory
)

# Delayed import of navigator types to avoid circular dependency
# Don't import at module level - let users import explicitly if needed
# from .navigator.epochdir import EpochDir

# Import file types
from .type.mfdaq_epoch_channel import MFDAQEpochChannel

__all__ = [
    # Base classes
    'Navigator',
    # File types
    'MFDAQEpochChannel',
    # Utilities
    'temp_name',
    'temp_fid',
    'pfilemirror',
    'create_temp_file',
    'create_temp_filename',
    'mirror_directory'
]

# Add lazy-loaded exports
def __getattr__(name):
    """Lazy load navigator types to avoid circular imports."""
    if name == 'EpochDir':
        from .navigator.epochdir import EpochDir
        return EpochDir
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
