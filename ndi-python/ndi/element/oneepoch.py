"""
One Epoch - Create a concatenated single-epoch version of a timeseries element.

MATLAB equivalent: ndi.element.oneepoch
"""

from typing import Union, Optional
import numpy as np

from ..element import Element
from .timeseries import TimeSeriesElement


def oneepoch(
    D,
    element_in: Union[Element, TimeSeriesElement],
    name_out: str,
    reference_out: int
) -> TimeSeriesElement:
    """
    Create a concatenated version of a timeseries element.

    Creates a single-epoch element by concatenating all epochs from the input
    element. Use with caution as this could create enormous documents.

    MATLAB equivalent: ndi.element.oneepoch()

    Args:
        D: NDI Session or Dataset object
        element_in: The element to concatenate
        name_out: Name for the new element
        reference_out: Reference number for the new element

    Returns:
        TimeSeriesElement: New concatenated element

    Notes:
        The epoch will use the most "global" clock available. Preference order:
        'utc', 'approx_utc', 'exp_global_time', 'approx_exp_global_time',
        'dev_global_time', 'approx_dev_global_time'. If no global clock is
        found, uses 'dev_local_time'.

    Examples:
        >>> from ndi.element import oneepoch
        >>> # Concatenate all epochs into one
        >>> elem_concat = oneepoch(session, elem_original, 'concat', 1)
    """
    raise NotImplementedError(
        "oneepoch() function not yet fully implemented. "
        "This is a complex function that requires full epoch "
        "concatenation and time synchronization."
    )


class OneEpoch:
    """Placeholder class for OneEpoch element type."""
    pass
