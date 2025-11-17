"""NDI File Navigators - Specific file navigation strategies."""

# Don't import at module level to avoid circular dependency
# Users should import directly: from ndi.file.navigator.epochdir import EpochDir

__all__ = []

# Lazy loading to avoid circular imports
def __getattr__(name):
    if name == 'EpochDir':
        from .epochdir import EpochDir
        return EpochDir
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
