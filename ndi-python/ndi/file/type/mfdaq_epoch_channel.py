"""
MFDAQ Epoch Channel - Multi-File DAQ epoch channel information.

Manages channel information for multi-file DAQ systems, organizing channels
into groups for efficient storage and retrieval.

MATLAB equivalent: ndi.file.type.mfdaq_epoch_channel
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class ChannelInfo:
    """
    Information about a single channel.

    Attributes:
        name: Channel name (e.g., 'ai-1', 'di-1')
        type: Channel type (e.g., 'analog_in', 'digital_in', 'event')
        time_channel: Associated time channel
        sample_rate: Sampling rate in Hz
        offset: Data offset for calibration
        scale: Data scale factor for calibration
        number: Channel number
        group: Group number for multi-file storage
        dataclass: Data class category ('ephys', 'digital', 'eventmarktext', 'time')
    """
    name: str
    type: str
    time_channel: str
    sample_rate: float
    offset: float
    scale: float
    number: int
    group: int
    dataclass: str


class MFDAQEpochChannel:
    """
    Multi-File DAQ Epoch Channel information manager.

    Organizes channels from DAQ systems into groups for segmented file storage.
    Different channel types are grouped separately for efficient I/O.

    MATLAB equivalent: ndi.file.type.mfdaq_epoch_channel

    Attributes:
        channel_information: List of ChannelInfo objects

    Default channels per group:
        - analog_in: 400 channels
        - analog_out: 400 channels
        - auxiliary_in: 400 channels
        - auxiliary_out: 400 channels
        - digital_in: 512 channels
        - digital_out: 512 channels
        - eventmarktext: 100000 channels
        - time: 100000 channels

    Examples:
        >>> # Create from channel structure
        >>> channels = [
        ...     {'name': 'ai-1', 'type': 'analog_in', 'sample_rate': 30000,
        ...      'time_channel': 'time-1', 'offset': 0, 'scale': 1.0},
        ...     {'name': 'ai-2', 'type': 'analog_in', 'sample_rate': 30000,
        ...      'time_channel': 'time-1', 'offset': 0, 'scale': 1.0}
        ... ]
        >>> mfdaq = MFDAQEpochChannel(channels)
        >>>
        >>> # Or load from file
        >>> mfdaq = MFDAQEpochChannel.from_file('channels.json')
        >>>
        >>> # Decode channel groups
        >>> groups, idx_in_groups, idx_in_output = mfdaq.channelgroupdecoding(
        ...     'analog_in', [1, 2]
        ... )
    """

    # Default channels per group for each type
    DEFAULT_CHANNELS_PER_GROUP = {
        'analog_in': 400,
        'analog_out': 400,
        'auxiliary_in': 400,
        'auxiliary_out': 400,
        'digital_in': 512,
        'digital_out': 512,
        'eventmarktext': 100000,
        'time': 100000
    }

    # Default data classes for each type
    DEFAULT_DATACLASS = {
        'analog_in': 'ephys',
        'analog_out': 'ephys',
        'auxiliary_in': 'ephys',
        'auxiliary_out': 'ephys',
        'digital_in': 'digital',
        'digital_out': 'digital',
        'eventmarktext': 'eventmarktext',
        'time': 'time',
        'event': 'eventmarktext',
        'marker': 'eventmarktext',
        'text': 'eventmarktext'
    }

    def __init__(self, channel_structure: Optional[List[Dict]] = None,
                 filename: Optional[str] = None,
                 **kwargs):
        """
        Create an MFDAQEpochChannel object.

        Args:
            channel_structure: List of dicts with channel information
                Each dict should have: name, type, sample_rate, time_channel,
                offset, scale
            filename: Path to file to load from
            **kwargs: Additional parameters:
                - analog_in_channels_per_group
                - analog_out_channels_per_group
                - etc. (overrides defaults)

        Examples:
            >>> # From structure
            >>> channels = [{'name': 'ai-1', 'type': 'analog_in', ...}]
            >>> mfdaq = MFDAQEpochChannel(channels)
            >>>
            >>> # From file
            >>> mfdaq = MFDAQEpochChannel(filename='channels.json')
            >>>
            >>> # With custom grouping
            >>> mfdaq = MFDAQEpochChannel(
            ...     channels,
            ...     analog_in_channels_per_group=200
            ... )
        """
        self.channel_information: List[ChannelInfo] = []

        if channel_structure is not None:
            self.create_properties(channel_structure, **kwargs)
        elif filename is not None:
            self.read_from_file(filename)

    def create_properties(self, channel_structure: List[Dict],
                         **kwargs) -> None:
        """
        Create channel properties from channel structure.

        Organizes channels into groups based on type and assigns group numbers.

        MATLAB equivalent: ndi.file.type.mfdaq_epoch_channel.create_properties()

        Args:
            channel_structure: List of channel dicts
            **kwargs: Override default channels_per_group for any type

        Notes:
            Channels are sorted by type and then by channel number within type.
            Event, marker, and text types are combined into 'eventmarktext'.
        """
        # Get channels per group settings
        channels_per_group = self.DEFAULT_CHANNELS_PER_GROUP.copy()
        for key, value in kwargs.items():
            if key.endswith('_channels_per_group'):
                type_name = key.replace('_channels_per_group', '')
                channels_per_group[type_name] = value

        # Sort channels by type
        sorted_channels = sorted(channel_structure, key=lambda x: x['type'])

        # Get unique types, combining event/marker/text into eventmarktext
        types_available = set(ch['type'] for ch in sorted_channels)
        event_types = {'event', 'marker', 'text'}
        if types_available & event_types:
            types_available = types_available - event_types
            types_available.add('eventmarktext')

        types_list = sorted(types_available)

        # Process each type
        channel_info_list = []

        for channel_type in types_list:
            # Get channels of this type
            if channel_type == 'eventmarktext':
                channels_here = [
                    ch for ch in sorted_channels
                    if ch['type'] in event_types
                ]
            else:
                channels_here = [
                    ch for ch in sorted_channels
                    if ch['type'] == channel_type
                ]

            if not channels_here:
                continue

            # Extract channel numbers and sort
            channel_nums = []
            for ch in channels_here:
                # Extract number from channel name (e.g., 'ai-1' -> 1)
                num = self._extract_channel_number(ch['name'])
                channel_nums.append((num, ch))

            channel_nums.sort(key=lambda x: x[0])
            channels_sorted = [ch for _, ch in channel_nums]

            # Get grouping parameters
            cpg = channels_per_group.get(channel_type, 400)
            dataclass = self.DEFAULT_DATACLASS.get(channel_type, 'unknown')

            # Create channel info for each channel
            for ch_dict in channels_sorted:
                number = self._extract_channel_number(ch_dict['name'])

                # Determine group (1-indexed)
                group = 1 + (number // cpg)

                channel_info = ChannelInfo(
                    name=ch_dict['name'],
                    type=ch_dict['type'],
                    time_channel=ch_dict.get('time_channel', ''),
                    sample_rate=float(ch_dict.get('sample_rate', 0)),
                    offset=float(ch_dict.get('offset', 0)),
                    scale=float(ch_dict.get('scale', 1.0)),
                    number=number,
                    group=group,
                    dataclass=dataclass
                )
                channel_info_list.append(channel_info)

        self.channel_information = channel_info_list

    def read_from_file(self, filename: str) -> None:
        """
        Read channel information from a file.

        MATLAB equivalent: ndi.file.type.mfdaq_epoch_channel.readFromFile()

        Args:
            filename: Path to JSON file with channel information

        Examples:
            >>> mfdaq = MFDAQEpochChannel()
            >>> mfdaq.read_from_file('channels.json')
        """
        with open(filename, 'r') as f:
            data = json.load(f)

        # Convert from list of dicts to list of ChannelInfo
        if isinstance(data, list):
            self.channel_information = [
                ChannelInfo(**item) if isinstance(item, dict) else item
                for item in data
            ]
        else:
            raise ValueError("File must contain a list of channel information")

    def write_to_file(self, filename: str) -> Tuple[bool, str]:
        """
        Write channel information to a file.

        MATLAB equivalent: ndi.file.type.mfdaq_epoch_channel.writeToFile()

        Args:
            filename: Path to output JSON file

        Returns:
            Tuple of (success: bool, error_message: str)

        Examples:
            >>> success, errmsg = mfdaq.write_to_file('channels.json')
            >>> if not success:
            ...     print(f'Error: {errmsg}')
        """
        try:
            # Convert ChannelInfo objects to dicts
            data = [asdict(ch) for ch in self.channel_information]

            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)

            return True, ''
        except Exception as e:
            return False, str(e)

    def channelgroupdecoding(
        self,
        channel_type: str,
        channels: List[int]
    ) -> Tuple[List[int], List[List[int]], List[List[int]]]:
        """
        Decode channel list into groups where channels are stored.

        MATLAB equivalent: ndi.file.type.mfdaq_epoch_channel.channelgroupdecoding()

        Args:
            channel_type: Type of channels to decode (e.g., 'analog_in')
            channels: List of channel numbers to decode

        Returns:
            Tuple of (groups, channel_indexes_in_groups, channel_indexes_in_output):
                - groups: List of group numbers
                - channel_indexes_in_groups: For each group, indexes within that group
                - channel_indexes_in_output: For each group, indexes in output array

        Raises:
            ValueError: If channel not found or found multiple times

        Examples:
            >>> # Get channels 1 and 401 (in different groups)
            >>> groups, idx_in_groups, idx_in_output = mfdaq.channelgroupdecoding(
            ...     'analog_in', [1, 401]
            ... )
            >>> # groups = [1, 2]
            >>> # idx_in_groups = [[1], [1]]  # Both are first in their groups
            >>> # idx_in_output = [[0], [1]]  # Positions in output
        """
        groups = []
        channel_indexes_in_groups = []
        channel_indexes_in_output = []

        # Filter channels by type
        ci = [ch for ch in self.channel_information if ch.type == channel_type]

        if not ci:
            raise ValueError(f"No channels of type '{channel_type}' found")

        for c_idx, channel_num in enumerate(channels):
            # Find channel with this number
            matching = [i for i, ch in enumerate(ci) if ch.number == channel_num]

            if not matching:
                raise ValueError(
                    f'Channel number {channel_num} not found in record for type {channel_type}'
                )
            if len(matching) > 1:
                raise ValueError(
                    f'Channel number {channel_num} found multiple times in record'
                )

            idx = matching[0]
            ch = ci[idx]

            # Find or create group
            try:
                group_loc = groups.index(ch.group)
            except ValueError:
                # Group not yet in list
                groups.append(ch.group)
                group_loc = len(groups) - 1
                channel_indexes_in_groups.append([])
                channel_indexes_in_output.append([])

            # Find index within the subset of this group and type
            subset_group = [ch for ch in ci if ch.group == groups[group_loc]]
            subset_numbers = [ch.number for ch in subset_group]
            try:
                chan_index_in_group = subset_numbers.index(channel_num)
            except ValueError:
                chan_index_in_group = 0  # Shouldn't happen

            channel_indexes_in_groups[group_loc].append(chan_index_in_group)
            channel_indexes_in_output[group_loc].append(c_idx)

        return groups, channel_indexes_in_groups, channel_indexes_in_output

    @staticmethod
    def _extract_channel_number(channel_name: str) -> int:
        """
        Extract channel number from channel name.

        Args:
            channel_name: Channel name (e.g., 'ai-1', 'di-42')

        Returns:
            int: Channel number

        Examples:
            >>> MFDAQEpochChannel._extract_channel_number('ai-1')
            1
            >>> MFDAQEpochChannel._extract_channel_number('di-42')
            42
        """
        # Split by '-' and get last part
        parts = channel_name.split('-')
        if len(parts) >= 2:
            try:
                return int(parts[-1])
            except ValueError:
                pass

        # Try to extract any number from the string
        import re
        numbers = re.findall(r'\d+', channel_name)
        if numbers:
            return int(numbers[-1])

        return 0

    @classmethod
    def from_file(cls, filename: str) -> 'MFDAQEpochChannel':
        """
        Create MFDAQEpochChannel from file (convenience method).

        Args:
            filename: Path to JSON file

        Returns:
            MFDAQEpochChannel object

        Examples:
            >>> mfdaq = MFDAQEpochChannel.from_file('channels.json')
        """
        return cls(filename=filename)

    def __len__(self) -> int:
        """Return number of channels."""
        return len(self.channel_information)

    def __getitem__(self, idx: int) -> ChannelInfo:
        """Get channel info by index."""
        return self.channel_information[idx]

    def __repr__(self) -> str:
        """String representation."""
        return f"MFDAQEpochChannel({len(self)} channels)"
