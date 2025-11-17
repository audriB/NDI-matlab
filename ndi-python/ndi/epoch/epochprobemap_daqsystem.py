"""
Epoch Probe Map DAQ System - Concrete probe mapping for DAQ systems.

MATLAB equivalent: ndi.epoch.epochprobemap_daqsystem
"""

from typing import List, Dict, Union, Optional
from pathlib import Path
import pandas as pd

# Import from parent package
import sys
if '.' in __name__:
    from ..epoch import EpochProbeMap
else:
    from ndi.epoch import EpochProbeMap


class EpochProbeMapDAQSystem(EpochProbeMap):
    """
    Epoch probe map for DAQ systems.

    Maps probes and channels to epochs with DAQ system device information.

    MATLAB equivalent: ndi.epoch.epochprobemap_daqsystem

    Attributes:
        name: Name of the contents (variable-like string, no whitespace)
        reference: Non-negative integer reference number
        type: Type of recording
        devicestring: DAQ system device and channel specification
        subjectstring: Subject identifier or document ID

    Examples:
        >>> # Create single mapping
        >>> epm = EpochProbeMapDAQSystem(
        ...     name='lfp1',
        ...     reference=1,
        ...     type='ephys',
        ...     devicestring='dev1;ai0:7',
        ...     subjectstring='subject_001@lab.org'
        ... )
        >>>
        >>> # Serialize to string
        >>> s = epm.serialize()
        >>>
        >>> # Create from serialized string
        >>> epm2 = EpochProbeMapDAQSystem.from_string(s)
        >>>
        >>> # Create from file
        >>> epm3 = EpochProbeMapDAQSystem.from_file('probemap.txt')
    """

    def __init__(
        self,
        name: str = 'a',
        reference: int = 0,
        type: str = 'a',
        devicestring: str = 'a',
        subjectstring: str = 'nothing@nosuchlab.org'
    ):
        """
        Create an EpochProbeMapDAQSystem.

        Args:
            name: Name (must be variable-like, no whitespace)
            reference: Non-negative integer
            type: Recording type
            devicestring: Device and channel specification
            subjectstring: Subject ID or document ID

        Raises:
            ValueError: If parameters are invalid
        """
        super().__init__()

        # Validate name
        if not self._is_valid_name(name):
            raise ValueError(
                f"name must start with letter and contain no whitespace: '{name}'"
            )
        self.name = name

        # Validate reference
        if not isinstance(reference, int) or reference < 0:
            raise ValueError(f"reference must be non-negative integer: {reference}")
        self.reference = reference

        # Validate type
        if not self._is_valid_name(type):
            raise ValueError(
                f"type must start with letter and contain no whitespace: '{type}'"
            )
        self.type = type

        # Validate devicestring
        if not self._is_valid_name(devicestring):
            raise ValueError(
                f"devicestring must start with letter and contain no whitespace: '{devicestring}'"
            )
        self.devicestring = devicestring

        self.subjectstring = subjectstring

    @staticmethod
    def _is_valid_name(s: str) -> bool:
        """Check if string is a valid variable-like name."""
        if not s or not isinstance(s, str):
            return False
        if not s[0].isalpha():
            return False
        if any(c.isspace() for c in s):
            return False
        return True

    def serialization_struct(self) -> Dict[str, Union[str, int]]:
        """
        Create a dict for serialization.

        Returns:
            Dict with fields: name, reference, type, devicestring, subjectstring
        """
        return {
            'name': self.name,
            'reference': self.reference,
            'type': self.type,
            'devicestring': self.devicestring,
            'subjectstring': self.subjectstring
        }

    def serialize(self) -> str:
        """
        Turn the EpochProbeMapDAQSystem into a tab-delimited string.

        Returns:
            Tab-delimited string representation

        Format:
            Header row: name<tab>reference<tab>type<tab>devicestring<tab>subjectstring
            Data row: values separated by tabs

        Examples:
            >>> epm = EpochProbeMapDAQSystem('lfp1', 1, 'ephys', 'dev1;ai0', 'subj1')
            >>> s = epm.serialize()
            >>> print(s)
            name    reference    type    devicestring    subjectstring
            lfp1    1    ephys    dev1;ai0    subj1
        """
        st = self.serialization_struct()

        # Create header
        fields = ['name', 'reference', 'type', 'devicestring', 'subjectstring']
        header = '\t'.join(fields)

        # Create data row
        data_parts = []
        for field in fields:
            value = st[field]
            if isinstance(value, int):
                data_parts.append(str(value))
            else:
                data_parts.append(str(value))

        data_row = '\t'.join(data_parts)

        return header + '\n' + data_row + '\n'

    def savetofile(self, filename: Union[str, Path]) -> None:
        """
        Save to a tab-delimited file.

        Args:
            filename: Path to output file

        Examples:
            >>> epm = EpochProbeMapDAQSystem('lfp1', 1, 'ephys', 'dev1;ai0', 'subj1')
            >>> epm.savetofile('probemap.txt')
        """
        filename = Path(filename)

        # Create DataFrame
        df = pd.DataFrame([self.serialization_struct()])

        # Save as tab-delimited
        df.to_csv(filename, sep='\t', index=False)

    @staticmethod
    def decode(s: str) -> List[Dict[str, Union[str, int]]]:
        """
        Decode probe map information from a serialized string.

        Args:
            s: Tab-delimited string with header and data rows

        Returns:
            List of dicts with fields: name, reference, type, devicestring, subjectstring

        Raises:
            ValueError: If string is empty or malformed

        Examples:
            >>> s = "name\\treference\\ttype\\tdevicestring\\tsubjectstring\\n"
            >>> s += "lfp1\\t1\\tephys\\tdev1;ai0\\tsubj1\\n"
            >>> dicts = EpochProbeMapDAQSystem.decode(s)
        """
        if not s:
            raise ValueError("Serialized string is empty")

        lines = s.strip().split('\n')
        if len(lines) < 1:
            raise ValueError("No information in serialized string")

        # Parse header
        header_fields = lines[0].split('\t')

        # Parse data rows
        result = []
        for i in range(1, len(lines)):
            line = lines[i].strip()
            if not line:
                continue

            parts = line.split('\t')
            if len(parts) != len(header_fields):
                continue  # Skip malformed lines

            entry = {}
            for j, field in enumerate(header_fields):
                value = parts[j]

                # Convert reference to int
                if field == 'reference':
                    try:
                        entry[field] = int(value)
                    except ValueError:
                        entry[field] = 0
                else:
                    entry[field] = value

            result.append(entry)

        return result

    @classmethod
    def from_string(cls, s: str) -> Union['EpochProbeMapDAQSystem', List['EpochProbeMapDAQSystem']]:
        """
        Create EpochProbeMapDAQSystem object(s) from serialized string.

        Args:
            s: Serialized tab-delimited string

        Returns:
            Single object or list of objects

        Examples:
            >>> s = "name\\treference\\ttype\\tdevicestring\\tsubjectstring\\n"
            >>> s += "lfp1\\t1\\tephys\\tdev1;ai0\\tsubj1\\n"
            >>> epm = EpochProbeMapDAQSystem.from_string(s)
        """
        structs = cls.decode(s)

        if not structs:
            return []

        objects = []
        for st in structs:
            obj = cls(
                name=st.get('name', 'a'),
                reference=st.get('reference', 0),
                type=st.get('type', 'a'),
                devicestring=st.get('devicestring', 'a'),
                subjectstring=st.get('subjectstring', 'nothing@nosuchlab.org')
            )
            objects.append(obj)

        return objects[0] if len(objects) == 1 else objects

    @classmethod
    def from_file(cls, filename: Union[str, Path]) -> Union['EpochProbeMapDAQSystem', List['EpochProbeMapDAQSystem']]:
        """
        Create EpochProbeMapDAQSystem object(s) from tab-delimited file.

        Args:
            filename: Path to tab-delimited file

        Returns:
            Single object or list of objects

        Examples:
            >>> epm = EpochProbeMapDAQSystem.from_file('probemap.txt')
        """
        filename = Path(filename)

        if not filename.exists():
            raise FileNotFoundError(f"File not found: {filename}")

        # Read file
        df = pd.read_csv(filename, sep='\t')

        # Convert to objects
        objects = []
        for _, row in df.iterrows():
            obj = cls(
                name=row.get('name', 'a'),
                reference=int(row.get('reference', 0)),
                type=row.get('type', 'a'),
                devicestring=row.get('devicestring', 'a'),
                subjectstring=row.get('subjectstring', 'nothing@nosuchlab.org')
            )
            objects.append(obj)

        return objects[0] if len(objects) == 1 else objects

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"EpochProbeMapDAQSystem(name='{self.name}', "
            f"reference={self.reference}, type='{self.type}', "
            f"devicestring='{self.devicestring}')"
        )

    def __eq__(self, other) -> bool:
        """Test equality."""
        if not isinstance(other, EpochProbeMapDAQSystem):
            return False
        return (
            self.name == other.name and
            self.reference == other.reference and
            self.type == other.type and
            self.devicestring == other.devicestring and
            self.subjectstring == other.subjectstring
        )
