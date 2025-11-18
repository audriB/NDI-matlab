"""
NDI Epoch Directory File Navigator.

Navigator for file trees where each epoch is organized in its own subdirectory.

MATLAB equivalent: ndi.file.navigator.epochdir
"""

import os
from pathlib import Path
from typing import List, Optional, Any
import glob

# Import Navigator from _navigator module (renamed to avoid package conflict)
from .._navigator import Navigator


class EpochDir(Navigator):
    """
    File Navigator for epoch-directory organization.

    In this organization scheme, each epoch's data files are stored in a separate
    subdirectory. The epoch identifier is the name of the subdirectory.

    Example directory structure:
        mysession/
            t00001/
                mydata.dat
                metadata.txt
            t00002/
                mydata.dat
                metadata.txt

    In this example, epochs have IDs 't00001' and 't00002'.

    MATLAB equivalent: ndi.file.navigator.epochdir

    Attributes:
        session: NDI Session object
        fileparameters: File matching parameters
        epochprobemap_class: Class name for epoch probe maps
        epochprobemap_fileparameters: Parameters for epoch probe map files

    Examples:
        >>> from ndi.session import SessionDir
        >>> from ndi.file.navigator import EpochDir
        >>> session = SessionDir('/path/to/mysession')
        >>> # Match all .dat files in epoch subdirectories
        >>> nav = EpochDir(session, {'filematch': ['*.dat']})
        >>> # Get epoch information
        >>> epochtable = nav.epochtable()
    """

    def __init__(self, session=None, fileparameters=None,
                 epochprobemap_class: str = None,
                 epochprobemap_fileparameters=None):
        """
        Create an EpochDir File Navigator.

        Args:
            session: NDI Session object
            fileparameters: File matching parameters (dict or Document)
                - If dict, should contain 'filematch' key with list of patterns
                - If Document, loads from document properties
            epochprobemap_class: Class for epoch probe maps
                Default: 'ndi.epoch.epochprobemap_daqsystem'
            epochprobemap_fileparameters: Parameters for finding epochprobemap files

        Examples:
            >>> # Simple usage with file pattern
            >>> nav = EpochDir(session, {'filematch': ['*.rhd']})
            >>>
            >>> # With epoch probe map parameters
            >>> nav = EpochDir(
            ...     session,
            ...     {'filematch': ['*.dat']},
            ...     epochprobemap_class='ndi.epoch.epochprobemap_daqsystem',
            ...     epochprobemap_fileparameters={'filematch': ['*.epm']}
            ... )
        """
        # Call parent constructor
        super().__init__(
            session,
            fileparameters,
            epochprobemap_class,
            epochprobemap_fileparameters
        )

    def epochid(self, epoch_number: int, epochfiles: Optional[List[str]] = None) -> str:
        """
        Get the epoch identifier for a particular epoch.

        For EpochDir organization, the epoch identifier is the name of the
        subdirectory containing the epoch's files.

        MATLAB equivalent: ndi.file.navigator.epochdir.epochid()

        Args:
            epoch_number: The epoch number (1-indexed)
            epochfiles: Optional list of files in the epoch
                If not provided, will call getepochfiles()

        Returns:
            str: The epoch identifier (subdirectory name)

        Examples:
            >>> nav = EpochDir(session, {'filematch': ['*.dat']})
            >>> # If files are in mysession/t00001/, returns 't00001'
            >>> epoch_id = nav.epochid(1)
            >>> print(epoch_id)
            't00001'
        """
        if epochfiles is None:
            epochfiles = self.getepochfiles(epoch_number)

        if not epochfiles:
            return ''

        # Check if files are ingested
        if self._isingested(epochfiles):
            return self._ingestedfiles_epochid(epochfiles)

        # Get the directory name from the first file
        first_file = epochfiles[0]
        path_obj = Path(first_file)

        # Get parent directory name
        parent_dir = path_obj.parent
        epoch_id = parent_dir.name

        return epoch_id

    def selectfilegroups_disk(self) -> List[List[str]]:
        """
        Return groups of files that will comprise epochs from disk.

        For EpochDir organization, this searches for file matching patterns
        in all subdirectories (at depth 1) within the session directory.

        MATLAB equivalent: ndi.file.navigator.epochdir.selectfilegroups_disk()

        Returns:
            List[List[str]]: List where each element is a list of files
                comprising one epoch

        Notes:
            - Only searches subdirectories at depth 1 (no recursion)
            - Skips the session directory itself (SearchParent=0)
            - Uses file matching patterns from fileparameters

        Examples:
            >>> nav = EpochDir(session, {'filematch': ['*.dat', '*.txt']})
            >>> # Returns: [['t00001/data.dat', 't00001/info.txt'],
            >>> #            ['t00002/data.dat', 't00002/info.txt']]
            >>> epochs = nav.selectfilegroups_disk()
        """
        if self.session is None:
            return []

        # Get session path
        exp_path = self.session.path
        if not exp_path or not os.path.exists(exp_path):
            return []

        # Get file matching patterns
        if not self.fileparameters or 'filematch' not in self.fileparameters:
            return []

        filematch = self.fileparameters['filematch']
        if isinstance(filematch, str):
            filematch = [filematch]

        # Find file groups with specific parameters for epochdir:
        # - SearchParent=0: Don't search parent (session) directory
        # - SearchDepth=1: Only search subdirectories at depth 1
        epochfiles_disk = self._findfilegroups_epochdir(
            exp_path,
            filematch,
            search_parent=False,
            search_depth=1
        )

        return epochfiles_disk

    def _findfilegroups_epochdir(
        self,
        root_path: str,
        filematch_patterns: List[str],
        search_parent: bool = False,
        search_depth: int = 1
    ) -> List[List[str]]:
        """
        Find file groups for epochdir organization.

        Args:
            root_path: Root directory to search
            filematch_patterns: List of file patterns (e.g., ['*.dat', '*.txt'])
            search_parent: Whether to search root directory itself
            search_depth: How deep to search (1 = immediate subdirs only)

        Returns:
            List of file lists (one per epoch)
        """
        root_path = Path(root_path)
        epoch_groups = []

        if not root_path.exists() or not root_path.is_dir():
            return []

        # Get immediate subdirectories
        subdirs = [d for d in root_path.iterdir() if d.is_dir()]
        subdirs = sorted(subdirs)  # Sort for consistent ordering

        # Search each subdirectory
        for subdir in subdirs:
            # Skip hidden directories
            if subdir.name.startswith('.'):
                continue

            # Find matching files in this subdirectory
            epoch_files = []
            for pattern in filematch_patterns:
                # Search for files matching pattern
                matches = glob.glob(str(subdir / pattern))
                epoch_files.extend(matches)

            # If we found files, add this as an epoch
            if epoch_files:
                # Sort files for consistent ordering
                epoch_files = sorted(epoch_files)
                epoch_groups.append(epoch_files)

        # Optionally search parent directory if requested
        if search_parent:
            parent_files = []
            for pattern in filematch_patterns:
                matches = glob.glob(str(root_path / pattern))
                # Only include files directly in root, not in subdirs
                parent_files.extend([
                    f for f in matches
                    if Path(f).parent == root_path
                ])
            if parent_files:
                parent_files = sorted(parent_files)
                epoch_groups.insert(0, parent_files)

        return epoch_groups

    @staticmethod
    def _isingested(epochfiles: List[str]) -> bool:
        """
        Check if epoch files are ingested (stored in database).

        Args:
            epochfiles: List of file paths

        Returns:
            bool: True if files are ingested
        """
        # Check if files have ingestion marker
        # In NDI, ingested files start with a special prefix or are stored in database
        if not epochfiles:
            return False

        # Simple heuristic: if path contains database identifiers
        first_file = epochfiles[0]
        return '_ingested_' in first_file or 'binarydoc' in first_file

    @staticmethod
    def _ingestedfiles_epochid(epochfiles: List[str]) -> str:
        """
        Extract epoch ID from ingested files.

        Args:
            epochfiles: List of ingested file paths

        Returns:
            str: Epoch identifier
        """
        # For ingested files, extract epoch ID from file metadata
        # This is a simplified implementation
        if not epochfiles:
            return ''

        # Extract from filename pattern
        # Ingested files typically have format: epoch_<id>_file_<num>
        first_file = Path(epochfiles[0]).name
        if '_ingested_' in first_file:
            parts = first_file.split('_')
            if len(parts) >= 3:
                return parts[2]  # epoch ID

        return 'ingested'
