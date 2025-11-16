"""
NDI Neuron - Element representing a neuron.

A Neuron is simply a TimeSeriesElement with a specific type
that makes it easy to search for and identify neurons in the database.

MATLAB equivalent: ndi.neuron
"""

from .element.timeseries import TimeSeriesElement


class Neuron(TimeSeriesElement):
    """
    Neuron element - represents neural spike data.

    This is a specialized TimeSeriesElement specifically for neurons.
    It inherits all functionality from TimeSeriesElement but has a
    distinct type for easy database queries.

    MATLAB equivalent: ndi.neuron

    Attributes:
        session: NDI Session object
        name: Neuron name
        reference: Reference number
        type: Element type (typically 'neuron')
        underlying_element: Parent element (if any)
        direct: Whether this directly uses underlying epochs
        subject_id: Subject ID

    Examples:
        >>> from ndi.session import SessionDir
        >>> from ndi.neuron import Neuron
        >>> session = SessionDir('/path/to/data')
        >>>
        >>> # Create a neuron
        >>> neuron = Neuron(session, 'cell1', 1, 'neuron')
        >>>
        >>> # Add spike times
        >>> import numpy as np
        >>> spike_times = np.array([0.1, 0.25, 0.4, 0.6, 0.8])
        >>> spike_data = np.ones((len(spike_times), 1))  # All spikes are '1'
        >>> neuron.addepoch(
        ...     't00001',
        ...     'dev_local_time',
        ...     [0.0, 1.0],
        ...     spike_times,
        ...     spike_data
        ... )
        >>>
        >>> # Read spike times back
        >>> data, t, timeref = neuron.readtimeseries(1, 0.0, 1.0)
        >>> print(f'Found {len(t)} spikes')
        >>>
        >>> # Search for all neurons in session
        >>> from ndi.query import Query
        >>> neuron_docs = session.database_search(Query('', 'isa', 'neuron'))
    """

    def __init__(self, session, *args, **kwargs):
        """
        Create a Neuron element.

        This function takes the same input arguments as TimeSeriesElement.

        Args:
            session: NDI Session object
            *args: See TimeSeriesElement for argument details
            **kwargs: See TimeSeriesElement for keyword arguments

        Examples:
            >>> # Create from parameters
            >>> neuron = Neuron(session, 'neuron1', 1, 'neuron')
            >>>
            >>> # Create from document
            >>> neuron = Neuron(session, neuron_doc)
            >>>
            >>> # Create derived neuron from spike sorting
            >>> spike_probe = session.getprobes()[0]
            >>> neuron = Neuron(
            ...     session,
            ...     'sorted_unit_1',
            ...     1,
            ...     'neuron',
            ...     underlying_element=spike_probe,
            ...     direct=False
            ... )
        """
        super().__init__(session, *args, **kwargs)
