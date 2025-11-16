"""
NDI File Utilities.

Utility functions for file operations in NDI.

MATLAB equivalent: ndi.file package functions
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Tuple, Optional, BinaryIO
import warnings


def temp_name() -> str:
    """
    Return a unique temporary file name.

    Returns the full path of a unique temporary file name that
    can be used by NDI programs. Uses ndi.IDO to generate a unique
    identifier for the filename.

    MATLAB equivalent: ndi.file.temp_name()

    Returns:
        str: Full path to a unique temporary file

    Example:
        >>> fname = temp_name()
        >>> # Use fname for temporary operations
    """
    from ndi.ido import IDO

    # Generate unique ID
    ido_obj = IDO()
    uid = ido_obj.identifier

    # Get system temp directory and create NDI temp folder if needed
    system_temp = tempfile.gettempdir()
    ndi_temp = os.path.join(system_temp, 'ndi_temp')

    # Create directory if it doesn't exist
    os.makedirs(ndi_temp, exist_ok=True)

    # Return full path with unique ID
    return os.path.join(ndi_temp, uid)


def temp_fid() -> Tuple[BinaryIO, str]:
    """
    Open a new temporary file for writing.

    Opens a new temporary file for writing with little-endian byte order
    (NDI default). The file is created with a unique name.

    MATLAB equivalent: ndi.file.temp_fid()

    Returns:
        tuple: (file_object, filename)
            - file_object: File handle opened for writing in binary mode
            - filename: Full path to the temporary file

    Raises:
        IOError: If the file cannot be opened for writing

    Example:
        >>> fid, fname = temp_fid()
        >>> try:
        ...     fid.write(b'some data')
        ... finally:
        ...     fid.close()
    """
    # Get unique temp filename
    fname = temp_name()

    try:
        # Open for writing in binary mode (equivalent to MATLAB's 'w','l')
        # Python's binary mode is always platform-independent
        fid = open(fname, 'wb')
        return fid, fname
    except IOError as e:
        raise IOError(f'Could not open the file {fname} for writing: {e}')


def pfilemirror(
    m_path: str,
    p_path: str,
    copy_non_m_files: bool = False,
    copy_hidden_files: bool = False,
    verbose: bool = True,
    dry_run: bool = False
) -> bool:
    """
    Mirror a directory tree, optionally processing files.

    In MATLAB, this would convert .m files to .p (compiled) files.
    In Python, we simply mirror the directory structure and copy files.
    This is useful for creating deployment copies of code.

    MATLAB equivalent: ndi.file.pfilemirror()

    Args:
        m_path: Source directory path
        p_path: Destination directory path
        copy_non_m_files: Should non .py files be copied? Default False
        copy_hidden_files: Should hidden files (e.g. .git) be copied? Default False
        verbose: Print files as they are copied? Default True
        dry_run: If True, display actions without executing. Default False

    Returns:
        bool: True if successful, False otherwise

    Example:
        >>> # Mirror a Python package directory
        >>> success = pfilemirror(
        ...     '/path/to/source',
        ...     '/path/to/dest',
        ...     copy_non_m_files=True,
        ...     verbose=True
        ... )
    """
    # Convert to Path objects for easier manipulation
    m_path = Path(m_path)
    p_path = Path(p_path)

    # Verify source exists
    if not m_path.is_dir():
        raise ValueError(f"Source directory does not exist: {m_path}")

    try:
        # Get all files in directory
        for item in m_path.iterdir():
            # Skip '.', '..', '.git'
            if item.name in {'.', '..', '.git'}:
                continue

            # Skip hidden files unless requested
            if not copy_hidden_files and item.name.startswith('.'):
                continue

            src_path = item
            dest_path = p_path / item.name

            if item.is_dir():
                # Create destination directory
                if not dest_path.exists():
                    if verbose or dry_run:
                        print(f'Action: Create directory {dest_path}')
                    if not dry_run:
                        dest_path.mkdir(parents=True, exist_ok=True)

                # Recurse into subdirectory
                success = pfilemirror(
                    str(src_path),
                    str(dest_path),
                    copy_non_m_files=copy_non_m_files,
                    copy_hidden_files=copy_hidden_files,
                    verbose=verbose,
                    dry_run=dry_run
                )
                if not success:
                    return False

            elif item.suffix == '.py':
                # Python file - in Python we just copy (no p-code equivalent)
                # Could optionally compile to .pyc if desired
                if not p_path.exists():
                    if verbose or dry_run:
                        print(f'Action: Create directory {p_path}')
                    if not dry_run:
                        p_path.mkdir(parents=True, exist_ok=True)

                if verbose or dry_run:
                    print(f'Action: Copy {src_path} to {dest_path}')

                if not dry_run:
                    shutil.copy2(src_path, dest_path)

            else:
                # Non-Python file
                if copy_non_m_files:
                    if not p_path.exists():
                        if verbose or dry_run:
                            print(f'Action: Create directory {p_path}')
                        if not dry_run:
                            p_path.mkdir(parents=True, exist_ok=True)

                    if verbose or dry_run:
                        print(f'Action: Copy {src_path} to {dest_path}')

                    if not dry_run:
                        if item.is_file():
                            shutil.copy2(src_path, dest_path)

        return True

    except Exception as e:
        if verbose:
            print(f'Error during mirroring: {e}')
        return False


# Convenience aliases for more Pythonic naming
def create_temp_file() -> Tuple[BinaryIO, str]:
    """
    Alias for temp_fid() with more Pythonic name.

    Returns:
        tuple: (file_object, filename)
    """
    return temp_fid()


def create_temp_filename() -> str:
    """
    Alias for temp_name() with more Pythonic name.

    Returns:
        str: Path to temporary file
    """
    return temp_name()


def mirror_directory(
    source: str,
    destination: str,
    **kwargs
) -> bool:
    """
    Alias for pfilemirror() with more Pythonic name.

    Args:
        source: Source directory
        destination: Destination directory
        **kwargs: Additional arguments passed to pfilemirror

    Returns:
        bool: True if successful
    """
    return pfilemirror(source, destination, **kwargs)
