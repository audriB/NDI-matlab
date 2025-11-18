"""
NDI Time Synchronization Rules - Concrete implementations.

This package provides concrete sync rule implementations for matching and
synchronizing epochs across different DAQ systems.

Available Rules:
- FileFind: Matches epochs by finding sync files with time mappings
- FileMatch: Matches epochs based on file characteristics
- CommonTriggers: Matches epochs based on common trigger signals
"""

from .filefind import FileFind
from .filematch import FileMatch
from .commontriggers import CommonTriggers

__all__ = [
    'FileFind',
    'FileMatch',
    'CommonTriggers',
]
