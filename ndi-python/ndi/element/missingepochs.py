"""
Missing Epochs - Determine missing epochs between two elements.

MATLAB equivalent: ndi.element.missingepochs
"""

from typing import Tuple, List, Union


def missingepochs(element1, element2) -> Tuple[bool, List[str]]:
    """
    Determine if there are epochs in element1 that are not in element2.

    Compares epoch tables of two elements and identifies epoch IDs present
    in the first but not in the second.

    MATLAB equivalent: ndi.element.missingepochs()

    Args:
        element1: First element or its epoch table (list of dicts)
        element2: Second element or its epoch table (list of dicts)

    Returns:
        Tuple of (missing, epoch_ids) where:
        - missing: True if any epochs are missing
        - epoch_ids: List of epoch IDs in element1 but not in element2

    Examples:
        >>> from ndi.element import missingepochs
        >>> missing, ids = missingepochs(elem1, elem2)
        >>> if missing:
        ...     print(f'Missing epochs: {ids}')
    """
    # Get epoch tables
    if isinstance(element1, (list, tuple)):
        et1 = element1  # Already an epoch table
    elif hasattr(element1, 'epochtable'):
        et1 = element1.epochtable()
    else:
        raise ValueError('Element1 must be an element or epoch table')

    if isinstance(element2, (list, tuple)):
        et2 = element2
    elif hasattr(element2, 'epochtable'):
        et2 = element2.epochtable()
    else:
        raise ValueError('Element2 must be an element or epoch table')

    # Extract epoch IDs
    ids1 = set(entry.get('epoch_id', '') for entry in et1)
    ids2 = set(entry.get('epoch_id', '') for entry in et2)

    # Find missing IDs
    missing_ids = list(ids1 - ids2)
    missing = len(missing_ids) > 0

    return missing, missing_ids


class MissingEpochs:
    """Placeholder class for MissingEpochs element type."""
    pass
