"""
NDI FileMatch Sync Rule - Match epochs by common files.

This sync rule matches epochs from two DAQ systems based on common underlying
files. If enough files match, it assumes the epochs are already synchronized
(identity time mapping).

MATLAB Equivalent: ndi.time.syncrule.filematch
"""

from typing import Dict, List, Tuple, Optional, Any

from ..syncrule import SyncRule
from ..timemapping import TimeMapping


class FileMatch(SyncRule):
    """
    Sync rule that matches epochs with common files.

    This rule:
    1. Checks that both epoch nodes are from DAQ systems
    2. Finds common underlying files between the epochs
    3. If enough common files exist, assumes times are already synchronized
    4. Returns an identity time mapping (time_B = time_A)

    This is useful when multiple DAQ systems share a common clock or when
    data files from different systems are stored together and implicitly
    synchronized.

    Parameters:
        number_fullpath_matches: Number of common files required (default: 2)

    Examples:
        >>> # Create a FileMatch rule
        >>> rule = FileMatch({'number_fullpath_matches': 2})
        >>>
        >>> # Apply to two epoch nodes that share files
        >>> cost, mapping = rule.apply(epochnode_a, epochnode_b)
        >>> if mapping:
        ...     # Times are already synchronized
        ...     time_b = mapping.map(time_a)  # Returns time_a

    MATLAB Equivalent:
        ndi.time.syncrule.filematch
    """

    def __init__(self, parameters: Optional[Dict[str, Any]] = None):
        """
        Create a FileMatch sync rule.

        Args:
            parameters: Parameter dictionary with keys:
                - number_fullpath_matches: int (default: 2)

        Examples:
            >>> rule = FileMatch()  # Use default (2 matches)
            >>> rule = FileMatch({'number_fullpath_matches': 3})
        """
        if parameters is None:
            parameters = {'number_fullpath_matches': 2}
        super().__init__(parameters)

    def isvalidparameters(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate parameters for FileMatch rule.

        Args:
            parameters: Parameters to validate

        Returns:
            Tuple of (is_valid, error_message)

        Examples:
            >>> rule = FileMatch()
            >>> valid, msg = rule.isvalidparameters({'number_fullpath_matches': 2})
            >>> valid
            True
        """
        # Check required fields
        if 'number_fullpath_matches' not in parameters:
            return False, "Missing required field: number_fullpath_matches"

        # Validate type
        if not isinstance(parameters['number_fullpath_matches'], int):
            return False, "number_fullpath_matches must be an integer"

        # Validate value
        if parameters['number_fullpath_matches'] < 1:
            return False, "number_fullpath_matches must be >= 1"

        return True, ""

    def eligible_epochsets(self) -> List[str]:
        """
        Return eligible epoch set class names for this rule.

        Returns:
            List of class names that this rule can process

        Examples:
            >>> rule = FileMatch()
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
            >>> rule = FileMatch()
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
        Apply FileMatch rule to two epoch nodes.

        Checks if epochs have enough common files. If so, assumes they
        are already synchronized and returns an identity mapping.

        Args:
            epochnode_a: First epoch node (from epochset.epochnodes())
            epochnode_b: Second epoch node (from epochset.epochnodes())

        Returns:
            Tuple of (cost, mapping):
            - cost: Cost of synchronization (1.0 if successful, None if failed)
            - mapping: Identity TimeMapping (time_out = time_in) or None

        Examples:
            >>> rule = FileMatch({'number_fullpath_matches': 1})
            >>> cost, mapping = rule.apply(epochnode_a, epochnode_b)
            >>> if mapping:
            ...     # Epochs share files, times are synchronized
            ...     assert mapping.map(10.0) == 10.0
        """
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

        if len(common_files) >= self.parameters['number_fullpath_matches']:
            # Enough common files - epochs are considered synchronized
            cost = 1.0
            # Identity mapping: time_out = 1.0 * time_in + 0.0
            mapping = TimeMapping('linear', [1.0, 0.0])
            return cost, mapping

        return None, None
