"""
NDI FileFind Sync Rule - Match epochs by finding sync files.

This sync rule matches epochs from two DAQ systems by finding common underlying
files and loading time mapping parameters from a synchronization file.

MATLAB Equivalent: ndi.time.syncrule.filefind
"""

from typing import Dict, List, Tuple, Optional, Any
import os
import numpy as np
from pathlib import Path

from ..syncrule import SyncRule
from ..timemapping import TimeMapping


class FileFind(SyncRule):
    """
    Sync rule that finds time mappings from synchronization files.

    This rule:
    1. Checks if two epoch nodes are from the specified DAQ systems
    2. Finds common underlying files between the epochs
    3. Looks for a synchronization file (default: 'syncfile.txt')
    4. Loads time mapping parameters (shift, scale) from that file
    5. Creates a TimeMapping: time_B = shift + scale * time_A

    The sync file should contain 2 numbers (one per line or space-separated):
    - Line 1 or first number: shift
    - Line 2 or second number: scale

    Parameters:
        number_fullpath_matches: Number of full path matches required (default: 1)
        syncfilename: Name of sync file to find (default: 'syncfile.txt')
        daqsystem1: Name of first DAQ system (default: 'mydaq1')
        daqsystem2: Name of second DAQ system (default: 'mydaq2')

    Examples:
        >>> # Create a FileFind rule
        >>> params = {
        ...     'number_fullpath_matches': 1,
        ...     'syncfilename': 'syncfile.txt',
        ...     'daqsystem1': 'intan',
        ...     'daqsystem2': 'stimulus'
        ... }
        >>> rule = FileFind(params)
        >>>
        >>> # Apply to two epoch nodes
        >>> cost, mapping = rule.apply(epochnode_a, epochnode_b)
        >>> if mapping:
        ...     time_b = mapping.map(time_a)

    MATLAB Equivalent:
        ndi.time.syncrule.filefind
    """

    def __init__(self, parameters: Optional[Dict[str, Any]] = None):
        """
        Create a FileFind sync rule.

        Args:
            parameters: Parameter dictionary with keys:
                - number_fullpath_matches: int (default: 1)
                - syncfilename: str (default: 'syncfile.txt')
                - daqsystem1: str (default: 'mydaq1')
                - daqsystem2: str (default: 'mydaq2')

        Examples:
            >>> rule = FileFind()  # Use defaults
            >>> rule = FileFind({'daqsystem1': 'intan', 'daqsystem2': 'stim'})
        """
        if parameters is None:
            parameters = {
                'number_fullpath_matches': 1,
                'syncfilename': 'syncfile.txt',
                'daqsystem1': 'mydaq1',
                'daqsystem2': 'mydaq2'
            }
        super().__init__(parameters)

    def isvalidparameters(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate parameters for FileFind rule.

        Args:
            parameters: Parameters to validate

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if valid, False otherwise
            - error_message: Empty if valid, error description otherwise

        Examples:
            >>> rule = FileFind()
            >>> valid, msg = rule.isvalidparameters({'syncfilename': 'sync.txt'})
            >>> valid
            False
            >>> 'number_fullpath_matches' in msg
            True
        """
        required = ['number_fullpath_matches', 'syncfilename', 'daqsystem1', 'daqsystem2']

        # Check all required fields present
        for field in required:
            if field not in parameters:
                return False, f"Missing required field: {field}"

        # Validate types
        if not isinstance(parameters['number_fullpath_matches'], int):
            return False, "number_fullpath_matches must be an integer"

        if not isinstance(parameters['syncfilename'], str):
            return False, "syncfilename must be a string"

        if not isinstance(parameters['daqsystem1'], str):
            return False, "daqsystem1 must be a string"

        if not isinstance(parameters['daqsystem2'], str):
            return False, "daqsystem2 must be a string"

        # Validate values
        if parameters['number_fullpath_matches'] < 1:
            return False, "number_fullpath_matches must be >= 1"

        if not parameters['syncfilename']:
            return False, "syncfilename cannot be empty"

        if not parameters['daqsystem1']:
            return False, "daqsystem1 cannot be empty"

        if not parameters['daqsystem2']:
            return False, "daqsystem2 cannot be empty"

        return True, ""

    def eligible_epochsets(self) -> List[str]:
        """
        Return eligible epoch set class names for this rule.

        Returns:
            List of class names that this rule can process

        Examples:
            >>> rule = FileFind()
            >>> rule.eligible_epochsets()
            ['ndi.daq.system']
        """
        return ['ndi.daq.system']

    def ineligible_epochsets(self) -> List[str]:
        """
        Return ineligible epoch set class names for this rule.

        Returns:
            List of class names that this rule cannot process

        Examples:
            >>> rule = FileFind()
            >>> ineligible = rule.ineligible_epochsets()
            >>> 'ndi.epoch.epochset' in ineligible
            True
        """
        base_ineligible = super().ineligible_epochsets()
        return base_ineligible + [
            'ndi.epoch.epochset',
            'ndi.epoch.epochset.param',
            'ndi.file.navigator'
        ]

    def apply(self, epochnode_a: Any, epochnode_b: Any) -> Tuple[Optional[float], Optional[TimeMapping]]:
        """
        Apply FileFind rule to two epoch nodes.

        Attempts to find a synchronization file in the underlying files of
        the epochs and load time mapping parameters.

        Args:
            epochnode_a: First epoch node (from epochset.epochnodes())
            epochnode_b: Second epoch node (from epochset.epochnodes())

        Returns:
            Tuple of (cost, mapping):
            - cost: Cost of synchronization (1.0 if successful, None if failed)
            - mapping: TimeMapping object (None if failed)

        Examples:
            >>> rule = FileFind({'daqsystem1': 'dev1', 'daqsystem2': 'dev2'})
            >>> cost, mapping = rule.apply(epochnode_a, epochnode_b)
            >>> if mapping:
            ...     synced_time = mapping.map(original_time)
        """
        # Check if epochnodes match our DAQ systems
        forward = (epochnode_a.get('objectname') == self.parameters['daqsystem1'] and
                  epochnode_b.get('objectname') == self.parameters['daqsystem2'])

        backward = (epochnode_b.get('objectname') == self.parameters['daqsystem1'] and
                   epochnode_a.get('objectname') == self.parameters['daqsystem2'])

        if not forward and not backward:
            return None, None

        # Check that both are DAQ systems
        class_a = epochnode_a.get('objectclass', '')
        class_b = epochnode_b.get('objectclass', '')

        if 'ndi.daq.system' not in class_a or 'ndi.daq.system' not in class_b:
            return None, None

        # Get underlying epochs
        underlying_a = epochnode_a.get('underlying_epochs', {}).get('underlying', [])
        underlying_b = epochnode_b.get('underlying_epochs', {}).get('underlying', [])

        if not underlying_a or not underlying_b:
            return None, None

        # Find common files
        common_files = set(underlying_a) & set(underlying_b)

        if len(common_files) < self.parameters['number_fullpath_matches']:
            return None, None

        # We have enough common files, cost is 1
        cost = 1.0

        # Find the sync file and load mapping
        if forward:
            # Map a -> b: look for sync file in epoch_a
            for filepath in underlying_a:
                filename = os.path.basename(filepath)
                if filename == self.parameters['syncfilename']:
                    mapping = self._load_sync_file(filepath, reverse=False)
                    if mapping:
                        return cost, mapping

            # Sync file not found
            raise FileNotFoundError(
                f"Sync file '{self.parameters['syncfilename']}' not found "
                f"in epoch {epochnode_a.get('epoch_id', 'unknown')}"
            )

        elif backward:
            # Map b -> a: look for sync file in epoch_b, use reverse mapping
            for filepath in underlying_b:
                filename = os.path.basename(filepath)
                if filename == self.parameters['syncfilename']:
                    mapping = self._load_sync_file(filepath, reverse=True)
                    if mapping:
                        return cost, mapping

            # Sync file not found
            raise FileNotFoundError(
                f"Sync file '{self.parameters['syncfilename']}' not found "
                f"in epoch {epochnode_b.get('epoch_id', 'unknown')}"
            )

        return None, None

    def _load_sync_file(self, filepath: str, reverse: bool = False) -> Optional[TimeMapping]:
        """
        Load time mapping from sync file.

        The sync file should contain 2 numbers:
        - First number: shift
        - Second number: scale

        Mapping is: time_out = shift + scale * time_in

        If reverse=True, computes the inverse mapping.

        Args:
            filepath: Path to sync file
            reverse: If True, compute inverse mapping

        Returns:
            TimeMapping object or None if file cannot be loaded

        Raises:
            ValueError: If file format is invalid
        """
        try:
            # Try to load as ASCII data
            data = np.loadtxt(filepath)

            if data.size < 2:
                raise ValueError(
                    f"Sync file {filepath} must contain at least 2 numbers (shift, scale)"
                )

            # Get shift and scale (first 2 values)
            shift = float(data.flat[0])
            scale = float(data.flat[1])

            if reverse:
                # Compute inverse: t_in = (t_out - shift) / scale
                #                      = (-shift/scale) + (1/scale) * t_out
                if scale == 0:
                    raise ValueError("Cannot reverse mapping with scale=0")
                shift_reverse = -shift / scale
                scale_reverse = 1.0 / scale
                return TimeMapping('linear', [scale_reverse, shift_reverse])
            else:
                # Forward mapping: t_out = scale * t_in + shift
                return TimeMapping('linear', [scale, shift])

        except Exception as e:
            raise ValueError(f"Error loading sync file {filepath}: {e}")
