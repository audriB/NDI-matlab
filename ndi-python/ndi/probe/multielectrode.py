"""
Multi-Electrode Probe - Arrays of electrodes for simultaneous recording.

MATLAB equivalent: Similar to ndi.probe.multielectrode
"""

from typing import Optional, List, Dict, Any, Tuple
import numpy as np
from ._probe import Probe


class MultiElectrodeProbe(Probe):
    """
    Multi-electrode array probe for simultaneous multi-channel recordings.

    Represents electrode arrays including tetrodes, stereotrodes, silicon probes,
    and multi-electrode arrays (MEAs). Supports channel mapping and geometry.

    Common types:
        - Tetrode: 4 closely-spaced electrodes
        - Stereotrode: 2 closely-spaced electrodes
        - Silicon probe: Linear or 2D array (e.g., Neuropixels, NeuroNexus)
        - MEA: Multi-electrode array for in vitro recordings

    Attributes:
        num_channels: Number of electrode channels
        channel_map: Mapping of logical to physical channels
        geometry: Physical locations of electrodes (um)
        probe_type: Specific probe type ('tetrode', 'neuropixels', 'mea', etc.)

    Examples:
        >>> from ndi.probe import MultiElectrodeProbe
        >>> from ndi import Session
        >>> session = Session('/path/to/data')
        >>>
        >>> # Create a tetrode (4 channels)
        >>> tetrode = MultiElectrodeProbe(
        ...     session,
        ...     name='tetrode1',
        ...     reference=1,
        ...     subject_id='mouse001',
        ...     num_channels=4,
        ...     probe_type='tetrode'
        ... )
        >>>
        >>> # Create Neuropixels probe
        >>> neuropixels = MultiElectrodeProbe(
        ...     session,
        ...     name='neuropixels1',
        ...     reference=1,
        ...     subject_id='mouse001',
        ...     num_channels=384,
        ...     probe_type='neuropixels'
        ... )
    """

    def __init__(self, session, name: str = None, reference: int = None,
                 subject_id: str = None, num_channels: int = 1,
                 probe_type: str = 'multielectrode',
                 channel_map: Optional[List[int]] = None,
                 geometry: Optional[np.ndarray] = None,
                 **kwargs):
        """
        Create a MultiElectrodeProbe.

        Args:
            session: NDI Session object
            name: Probe name
            reference: Reference number
            subject_id: Subject identifier
            num_channels: Number of electrode channels
            probe_type: Specific probe type ('tetrode', 'stereotrode', 'neuropixels', 'mea', etc.)
            channel_map: Mapping of logical to physical channels (optional)
            geometry: Nx2 or Nx3 array of electrode positions in um (optional)
            **kwargs: Additional properties

        Examples:
            >>> # Tetrode with explicit channel mapping
            >>> tetrode = MultiElectrodeProbe(
            ...     session,
            ...     name='tetrode1',
            ...     reference=1,
            ...     subject_id='rat01',
            ...     num_channels=4,
            ...     probe_type='tetrode',
            ...     channel_map=[0, 1, 2, 3]
            ... )
            >>>
            >>> # 16-channel linear probe with geometry
            >>> import numpy as np
            >>> geometry = np.array([[0, i*25] for i in range(16)])  # 25um spacing
            >>> linear_probe = MultiElectrodeProbe(
            ...     session,
            ...     name='linear16',
            ...     reference=1,
            ...     subject_id='mouse01',
            ...     num_channels=16,
            ...     probe_type='linear_array',
            ...     geometry=geometry
            ... )
        """
        # Initialize base Probe
        super().__init__(
            session,
            name,
            reference,
            probe_type,
            subject_id
        )

        # Multi-electrode specific properties
        self.num_channels = num_channels
        self.probe_type = probe_type

        # Channel mapping (defaults to identity mapping)
        if channel_map is not None:
            self.channel_map = channel_map
        else:
            self.channel_map = list(range(num_channels))

        # Electrode geometry (positions in micrometers)
        self.geometry = geometry

        # Store additional properties
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_channel_geometry(self, channel: int) -> Optional[Tuple[float, ...]]:
        """
        Get the physical location of a specific channel.

        Args:
            channel: Channel number (logical)

        Returns:
            Tuple of (x, y) or (x, y, z) coordinates in um, or None if no geometry

        Examples:
            >>> probe = MultiElectrodeProbe(session, 'probe1', 1, 'mouse1',
            ...                            num_channels=4,
            ...                            geometry=np.array([[0, 0], [0, 25], [0, 50], [0, 75]]))
            >>> loc = probe.get_channel_geometry(2)
            >>> print(loc)
            (0.0, 50.0)
        """
        if self.geometry is None:
            return None

        if channel < 0 or channel >= self.num_channels:
            raise ValueError(f"Channel {channel} out of range [0, {self.num_channels-1}]")

        return tuple(self.geometry[channel])

    def get_channel_distance(self, ch1: int, ch2: int) -> Optional[float]:
        """
        Calculate distance between two channels.

        Args:
            ch1: First channel number
            ch2: Second channel number

        Returns:
            Distance in um, or None if no geometry

        Examples:
            >>> distance = probe.get_channel_distance(0, 3)
            >>> print(f"Channels 0 and 3 are {distance:.1f} um apart")
        """
        if self.geometry is None:
            return None

        pos1 = self.geometry[ch1]
        pos2 = self.geometry[ch2]
        return float(np.linalg.norm(pos2 - pos1))

    def get_properties(self) -> Dict[str, Any]:
        """
        Get probe properties.

        Returns:
            Dict with probe properties

        Examples:
            >>> props = probe.get_properties()
            >>> print(f"Probe has {props['num_channels']} channels")
        """
        props = {
            'name': self.name,
            'reference': self.reference,
            'type': self.probe_type,
            'num_channels': self.num_channels,
            'channel_map': self.channel_map
        }

        if self.geometry is not None:
            props['geometry'] = self.geometry.tolist()
            props['geometry_unit'] = 'um'

        return props

    def __repr__(self) -> str:
        """String representation."""
        return (f"MultiElectrodeProbe(name='{self.name}', ref={self.reference}, "
                f"type='{self.probe_type}', channels={self.num_channels})")
