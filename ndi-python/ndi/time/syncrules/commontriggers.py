"""
NDI CommonTriggers Sync Rule - Match epochs by common trigger signals.

This sync rule matches epochs from two DAQ systems based on common trigger
signals detected in specified channels.

NOTE: This is currently a placeholder/stub implementation matching the MATLAB
version. Full trigger detection logic is not yet implemented.

MATLAB Equivalent: ndi.time.syncrule.commontriggers
"""

from typing import Dict, List, Tuple, Optional, Any

from ..syncrule import SyncRule
from ..timemapping import TimeMapping


class CommonTriggers(SyncRule):
    """
    Sync rule that matches epochs with common trigger signals.

    **NOTE**: This is a placeholder implementation. The full trigger detection
    and matching logic is not yet implemented.

    The intended behavior is:
    1. Read trigger/event channels from both DAQ systems
    2. Detect common trigger patterns
    3. Compute time mapping based on trigger alignment

    Current behavior (placeholder):
    - Checks for common underlying files
    - Returns identity mapping if enough files match

    Future implementation will include:
    - Trigger detection algorithms
    - Pattern matching across devices
    - Robust timing from multiple triggers

    Parameters:
        daqsystem1: Name of first DAQ system
        channel_daq1: Channel name on first DAQ system
        daqsystem2: Name of second DAQ system
        channel_daq2: Channel name on second DAQ system
        number_fullpath_matches: Number of common files required (default: 2)

    Examples:
        >>> # Create a CommonTriggers rule (placeholder)
        >>> params = {
        ...     'daqsystem1': 'intan',
        ...     'channel_daq1': 'di0',
        ...     'daqsystem2': 'stimulus',
        ...     'channel_daq2': 'trigger_out',
        ...     'number_fullpath_matches': 1
        ... }
        >>> rule = CommonTriggers(params)
        >>> # Currently behaves like FileMatch

    MATLAB Equivalent:
        ndi.time.syncrule.commontriggers (also a stub)
    """

    def __init__(self, parameters: Optional[Dict[str, Any]] = None):
        """
        Create a CommonTriggers sync rule.

        Args:
            parameters: Parameter dictionary with keys:
                - daqsystem1: str (name of first DAQ)
                - channel_daq1: str (channel on first DAQ)
                - daqsystem2: str (name of second DAQ)
                - channel_daq2: str (channel on second DAQ)
                - number_fullpath_matches: int (default: 2)

        Examples:
            >>> rule = CommonTriggers()  # Use defaults
        """
        if parameters is None:
            parameters = {
                'daqsystem1': 'daq1',
                'channel_daq1': 'trigger',
                'daqsystem2': 'daq2',
                'channel_daq2': 'trigger',
                'number_fullpath_matches': 2
            }
        super().__init__(parameters)

        # Warn that this is a placeholder
        import warnings
        warnings.warn(
            "CommonTriggers is currently a placeholder implementation. "
            "Full trigger detection is not yet implemented.",
            UserWarning
        )

    def isvalidparameters(self, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate parameters for CommonTriggers rule.

        Args:
            parameters: Parameters to validate

        Returns:
            Tuple of (is_valid, error_message)

        Examples:
            >>> rule = CommonTriggers()
            >>> valid, msg = rule.isvalidparameters({
            ...     'daqsystem1': 'dev1',
            ...     'channel_daq1': 'ai0',
            ...     'daqsystem2': 'dev2',
            ...     'channel_daq2': 'di0',
            ...     'number_fullpath_matches': 1
            ... })
            >>> valid
            True
        """
        # Check required fields
        required = ['daqsystem1', 'channel_daq1', 'daqsystem2',
                   'channel_daq2', 'number_fullpath_matches']

        for field in required:
            if field not in parameters:
                return False, f"Missing required field: {field}"

        # Validate types
        if not isinstance(parameters['daqsystem1'], str):
            return False, "daqsystem1 must be a string"

        if not isinstance(parameters['channel_daq1'], str):
            return False, "channel_daq1 must be a string"

        if not isinstance(parameters['daqsystem2'], str):
            return False, "daqsystem2 must be a string"

        if not isinstance(parameters['channel_daq2'], str):
            return False, "channel_daq2 must be a string"

        if not isinstance(parameters['number_fullpath_matches'], int):
            return False, "number_fullpath_matches must be an integer"

        # Validate values
        if parameters['number_fullpath_matches'] < 1:
            return False, "number_fullpath_matches must be >= 1"

        return True, ""

    def eligible_epochsets(self) -> List[str]:
        """
        Return eligible epoch set class names for this rule.

        Returns:
            List of class names that this rule can process

        Examples:
            >>> rule = CommonTriggers()
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
            >>> rule = CommonTriggers()
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
        Apply CommonTriggers rule to two epoch nodes.

        **PLACEHOLDER**: Currently just checks for common files like FileMatch.

        Future implementation will:
        - Read trigger channels from both DAQ systems
        - Detect trigger events
        - Align triggers and compute time mapping

        Args:
            epochnode_a: First epoch node (from epochset.epochnodes())
            epochnode_b: Second epoch node (from epochset.epochnodes())

        Returns:
            Tuple of (cost, mapping):
            - cost: Cost of synchronization (1.0 if successful, None if failed)
            - mapping: Identity TimeMapping (placeholder) or None

        Examples:
            >>> rule = CommonTriggers({'number_fullpath_matches': 1})
            >>> cost, mapping = rule.apply(epochnode_a, epochnode_b)
            >>> # Currently returns identity mapping if files match
        """
        # NOTE: This is a placeholder implementation matching MATLAB

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

        # Find common files (placeholder matching logic)
        common_files = set(underlying_a) & set(underlying_b)

        if len(common_files) >= self.parameters['number_fullpath_matches']:
            # TODO: Implement actual trigger detection and alignment
            # For now, return identity mapping like MATLAB version
            cost = 1.0
            mapping = TimeMapping('linear', [1.0, 0.0])  # Identity mapping
            return cost, mapping

        return None, None

    # TODO: Future methods for full implementation:
    # def _read_triggers(self, epochnode, channel):
    #     """Read trigger events from specified channel."""
    #     pass
    #
    # def _detect_triggers(self, data, threshold):
    #     """Detect trigger events in data."""
    #     pass
    #
    # def _align_triggers(self, triggers_a, triggers_b):
    #     """Align triggers and compute time mapping."""
    #     pass
