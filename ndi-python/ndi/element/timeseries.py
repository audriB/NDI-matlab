"""
NDI Element TimeSeries - Time series element with epoch-based data storage.

MATLAB equivalent: ndi.element.timeseries
"""

from typing import Optional, Tuple, Union, List, Any
import numpy as np
from pathlib import Path

from ..element import Element
from ..time import TimeReference, ClockType
from ..document import Document


class TimeSeriesElement(Element):
    """
    Time Series Element - Element with time series data storage.

    This class combines Element and TimeSeries functionality, storing
    time series data in binary files associated with epochs.

    MATLAB equivalent: ndi.element.timeseries

    Attributes:
        session: NDI Session object
        name: Element name
        reference: Reference number
        type: Element type
        underlying_element: Parent element (if any)
        direct: Whether this directly uses underlying epochs
        subject_id: Subject ID

    Examples:
        >>> from ndi.session import SessionDir
        >>> from ndi.element.timeseries import TimeSeriesElement
        >>> session = SessionDir('/path/to/data')
        >>> elem = TimeSeriesElement(session, 'neuron1', 1, 'spiketimes')
        >>>
        >>> # Add epoch with data
        >>> import numpy as np
        >>> timepoints = np.array([0.1, 0.2, 0.3])
        >>> datapoints = np.array([[1.0], [2.0], [3.0]])
        >>> elem.addepoch('t00001', 'dev_local_time', [0, 1], timepoints, datapoints)
        >>>
        >>> # Read data back
        >>> data, t, timeref = elem.readtimeseries(1, 0, 1)
    """

    def __init__(self, session, *args, **kwargs):
        """
        Create a TimeSeriesElement.

        Args:
            See parent Element class for argument details.

        Examples:
            >>> # Create from parameters
            >>> elem = TimeSeriesElement(session, 'elem1', 1, 'timeseries')
            >>>
            >>> # Create from document
            >>> elem = TimeSeriesElement(session, element_doc)
        """
        super().__init__(session, *args, **kwargs)

    def readtimeseries(self, timeref_or_epoch: Union[Any, int],
                      t0: float, t1: float) -> Tuple[np.ndarray, Union[np.ndarray, dict], Any]:
        """
        Read time series data from the element.

        MATLAB equivalent: ndi.element.timeseries.readtimeseries()

        Args:
            timeref_or_epoch: Either a TimeReference object or epoch number
            t0: Start time
            t1: End time

        Returns:
            Tuple of (data, t, timeref):
            - data: Time series data array
            - t: Time array or dict of time arrays
            - timeref: The TimeReference used

        Examples:
            >>> # Read from epoch 1
            >>> data, t, timeref = elem.readtimeseries(1, 0.0, 1.0)
            >>>
            >>> # Read using time reference
            >>> from ndi.time import TimeReference, ClockType
            >>> timeref = TimeReference(elem, ClockType('dev_local_time'), 't00001', 0)
            >>> data, t, timeref_out = elem.readtimeseries(timeref, 0.0, 1.0)
        """
        if self.direct:
            # Read directly from underlying element
            return self.underlying_element.readtimeseries(timeref_or_epoch, t0, t1)

        # Convert to time reference if needed
        if isinstance(timeref_or_epoch, TimeReference):
            timeref = timeref_or_epoch
        else:
            # Convert epoch number to time reference
            epoch_id = self.epochid(timeref_or_epoch)
            et_entry = self.epochtableentry(epoch_id)

            # Get first clock type for this epoch
            epoch_clock = et_entry['epoch_clock'][0]
            timeref = TimeReference(self, epoch_clock, epoch_id, 0)

        # Convert requested times to epoch local time
        from ..query import Query

        epoch_t0_out, epoch_timeref, msg = self.session.syncgraph.time_convert(
            timeref, t0, self, ClockType('dev_local_time')
        )
        epoch_t1_out, epoch_timeref, msg = self.session.syncgraph.time_convert(
            timeref, t1, self, ClockType('dev_local_time')
        )

        if epoch_timeref is None:
            raise ValueError(f'Could not find time mapping (maybe wrong epoch name?): {msg}')

        # Find the epoch document
        element_doc = self.load_element_doc()

        sq = (
            Query('depends_on', 'depends_on', 'element_id', element_doc.id()) &
            Query('', 'isa', 'element_epoch') &
            Query('epochid.epochid', 'exact_string', epoch_timeref.epoch)
        )

        epochdoc_list = self.session.database_search(sq)

        if len(epochdoc_list) == 0:
            raise ValueError(f'Could not find epochdoc for epoch {epoch_timeref.epoch}')
        if len(epochdoc_list) > 1:
            raise ValueError(f'Found too many epochdocs for epoch {epoch_timeref.epoch}')

        epochdoc = epochdoc_list[0]

        # Read binary data
        f = self.session.database_openbinarydoc(epochdoc, 'epoch_binary_data.vhsb')
        try:
            # Read VHSB format data
            data, t = self._vhsb_read(f, epoch_t0_out, epoch_t1_out)
        finally:
            self.session.database_closebinarydoc(f)

        # Convert time back to requested reference frame if numeric
        if isinstance(t, np.ndarray):
            t = self.session.syncgraph.time_convert(
                epoch_timeref, t,
                timeref.referent, timeref.clocktype
            )

        return data, t, timeref

    def addepoch(self, epochid: str, epochclock: Union[str, ClockType],
                t0_t1: List[float], timepoints: Union[np.ndarray, str],
                datapoints: Union[np.ndarray, str],
                epochids: Optional[List[str]] = None) -> Tuple['TimeSeriesElement', Optional[Document]]:
        """
        Add an epoch to the element with time series data.

        MATLAB equivalent: ndi.element.timeseries.addepoch()

        Args:
            epochid: Epoch identifier (e.g., 't00001')
            epochclock: Clock type for this epoch
            t0_t1: [start_time, end_time] for this epoch
            timepoints: Time points array (Tx1) or 'probe' to read from probe
            datapoints: Data points array (TxN) or 'probe' to read from probe
            epochids: Original epoch IDs (for oneepoch documents)

        Returns:
            Tuple of (element_obj, epochdoc):
            - element_obj: The modified element
            - epochdoc: The epoch document (if nargout < 2, adds to database)

        Raises:
            ValueError: If trying to add to a direct element

        Examples:
            >>> import numpy as np
            >>> timepoints = np.linspace(0, 1, 100)
            >>> datapoints = np.random.randn(100, 2)  # 100 samples, 2 channels
            >>> elem, epochdoc = elem.addepoch(
            ...     't00001',
            ...     'dev_local_time',
            ...     [0.0, 1.0],
            ...     timepoints,
            ...     datapoints
            ... )
        """
        if self.direct:
            raise ValueError(
                'Cannot add external observations to an element that is '
                'directly based on another element.'
            )

        # Call parent addepoch (creates epoch document)
        if epochids is not None:
            self, epochdoc = super().addepoch(epochid, epochclock, t0_t1, 0, epochids)
        else:
            self, epochdoc = super().addepoch(epochid, epochclock, t0_t1, 0)

        # Create binary file with data
        from ..file import temp_name
        fname = temp_name() + '.vhsb'

        # Write VHSB format
        self._vhsb_write(fname, timepoints, datapoints)

        # Attach file to document
        epochdoc = epochdoc.add_file('epoch_binary_data.vhsb', fname)

        # Add to database if not returning document
        # (Python doesn't have nargout, so we always return the document
        #  and let caller decide whether to add to database)

        return self, epochdoc

    def samplerate(self, epoch: Union[int, str]) -> float:
        """
        Get sample rate for an epoch.

        MATLAB equivalent: ndi.element.timeseries.samplerate()

        Args:
            epoch: Epoch number or epoch ID

        Returns:
            Sample rate in Hz

        Examples:
            >>> sr = elem.samplerate(1)
            >>> print(f'Sample rate: {sr} Hz')
        """
        et = self.epochtableentry(epoch)
        t0_t1 = et['t0_t1'][0]

        # Read a small amount of data to estimate sample rate
        data, t, timeref = self.readtimeseries(epoch, t0_t1[0], min(t0_t1[0] + 0.5, t0_t1[1]))

        if len(t) < 2:
            return 0.0

        # Calculate from median time difference
        dt = np.diff(t)
        return 1.0 / np.median(dt)

    @staticmethod
    def _vhsb_read(fileobj, t0: float, t1: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Read VHSB (VH Simple Binary) format data.

        This is a simplified implementation. The full VHSB format
        includes headers and metadata.

        Args:
            fileobj: File object to read from
            t0: Start time
            t1: End time

        Returns:
            Tuple of (data, time)
        """
        # Simplified implementation - reads binary numpy arrays
        # In production, this should read the full VHSB format
        import struct

        # Read time array
        time = np.load(fileobj) if hasattr(fileobj, 'read') else np.load(fileobj.name)

        # Reset file position (simplified)
        # In reality, VHSB has structured headers

        # Read data array
        data = np.load(fileobj) if hasattr(fileobj, 'read') else np.load(fileobj.name)

        # Filter by time range
        mask = (time >= t0) & (time <= t1)
        return data[mask], time[mask]

    @staticmethod
    def _vhsb_write(filename: str, timepoints: Union[np.ndarray, str],
                   datapoints: Union[np.ndarray, str]) -> None:
        """
        Write VHSB (VH Simple Binary) format data.

        This is a simplified implementation.

        Args:
            filename: Output filename
            timepoints: Time array or 'probe'
            datapoints: Data array or 'probe'
        """
        # Simplified implementation - writes numpy arrays
        # In production, this should write full VHSB format with headers

        if isinstance(timepoints, str) and timepoints == 'probe':
            raise NotImplementedError("Reading from probe not yet implemented")

        if isinstance(datapoints, str) and datapoints == 'probe':
            raise NotImplementedError("Reading from probe not yet implemented")

        # Write to temp file
        # In production VHSB format, would write:
        # - Header with version, data types, dimensions
        # - Time array
        # - Data array
        # For now, simple numpy save
        with open(filename, 'wb') as f:
            np.save(f, timepoints)
            np.save(f, datapoints)

    def newdocument(self, *args, **kwargs) -> Document:
        """Create a new document for this element."""
        return super().newdocument(*args, **kwargs)

    def searchquery(self, *args, **kwargs):
        """Create a search query for this element."""
        return super().searchquery(*args, **kwargs)
