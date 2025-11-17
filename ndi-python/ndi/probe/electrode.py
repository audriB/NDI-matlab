"""
Single Electrode Probe - Individual extracellular or intracellular electrode.

MATLAB equivalent: Similar to ndi.probe.electrode
"""

from typing import Optional, Dict, Any
from ._probe import Probe


class ElectrodeProbe(Probe):
    """
    Single electrode probe for neural recordings.

    Represents a single-channel electrode used for extracellular or
    intracellular recordings. Commonly used for single-unit recordings,
    local field potentials (LFP), or intracellular measurements.

    Attributes:
        impedance: Electrode impedance in Ohms (optional)
        material: Electrode material (e.g., 'tungsten', 'platinum', 'glass')
        tip_diameter: Tip diameter in micrometers (optional)

    Examples:
        >>> from ndi.probe import ElectrodeProbe
        >>> from ndi import Session
        >>> session = Session('/path/to/data')
        >>>
        >>> # Create tungsten electrode for extracellular recording
        >>> electrode = ElectrodeProbe(
        ...     session,
        ...     name='electrode1',
        ...     reference=1,
        ...     subject_id='mouse001',
        ...     impedance=1e6,  # 1 MOhm
        ...     material='tungsten'
        ... )
    """

    def __init__(self, session, name: str = None, reference: int = None,
                 subject_id: str = None, impedance: Optional[float] = None,
                 material: str = 'tungsten', tip_diameter: Optional[float] = None,
                 **kwargs):
        """
        Create an ElectrodeProbe.

        Args:
            session: NDI Session object
            name: Probe name (e.g., 'electrode1')
            reference: Reference number
            subject_id: Subject identifier
            impedance: Electrode impedance in Ohms
            material: Electrode material
            tip_diameter: Tip diameter in micrometers
            **kwargs: Additional properties

        Examples:
            >>> # Tungsten electrode for extracellular recording
            >>> electrode = ElectrodeProbe(
            ...     session,
            ...     name='extra1',
            ...     reference=1,
            ...     subject_id='rat01',
            ...     impedance=1e6,
            ...     material='tungsten',
            ...     tip_diameter=1.0
            ... )
        """
        # Initialize base Probe with type 'electrode'
        super().__init__(
            session,
            name,
            reference,
            'electrode',
            subject_id
        )

        # Add electrode-specific properties
        self.impedance = impedance
        self.material = material
        self.tip_diameter = tip_diameter

        # Store additional properties
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_properties(self) -> Dict[str, Any]:
        """
        Get electrode properties.

        Returns:
            Dict with electrode properties

        Examples:
            >>> props = electrode.get_properties()
            >>> print(props['material'])
            'tungsten'
        """
        props = {
            'name': self.name,
            'reference': self.reference,
            'type': 'electrode',
            'material': self.material
        }

        if self.impedance is not None:
            props['impedance'] = self.impedance
            props['impedance_unit'] = 'Ohm'

        if self.tip_diameter is not None:
            props['tip_diameter'] = self.tip_diameter
            props['tip_diameter_unit'] = 'um'

        return props

    def __repr__(self) -> str:
        """String representation."""
        imp_str = f", {self.impedance/1e6:.1f}MOhm" if self.impedance else ""
        return f"ElectrodeProbe(name='{self.name}', ref={self.reference}, {self.material}{imp_str})"
