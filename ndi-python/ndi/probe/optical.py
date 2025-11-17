"""
Optical Probe - Imaging and optogenetic devices.

MATLAB equivalent: Similar to ndi.probe.optical
"""

from typing import Optional, Dict, Any, List
from ._probe import Probe


class OpticalProbe(Probe):
    """
    Optical probe for imaging or optogenetic stimulation.

    Represents optical devices including:
        - Two-photon microscopes
        - Widefield imaging cameras
        - Fiber photometry systems
        - Optogenetic stimulation LEDs/lasers

    Attributes:
        imaging_type: Type of imaging ('two_photon', 'widefield', 'confocal', 'fiber_photometry')
        wavelength: Excitation/emission wavelength(s) in nm
        resolution: Spatial resolution in um/pixel (for imaging)
        field_of_view: Field of view dimensions in um
        frame_rate: Imaging frame rate in Hz (for imaging)
        power: Optical power in mW (for stimulation)

    Examples:
        >>> from ndi.probe import OpticalProbe
        >>> from ndi import Session
        >>> session = Session('/path/to/data')
        >>>
        >>> # Two-photon microscope
        >>> microscope = OpticalProbe(
        ...     session,
        ...     name='2p_scope',
        ...     reference=1,
        ...     subject_id='mouse001',
        ...     imaging_type='two_photon',
        ...     wavelength=920,  # nm
        ...     resolution=0.5,  # um/pixel
        ...     frame_rate=30.0  # Hz
        ... )
        >>>
        >>> # Optogenetic LED
        >>> led = OpticalProbe(
        ...     session,
        ...     name='blue_led',
        ...     reference=1,
        ...     subject_id='mouse001',
        ...     imaging_type='optogenetic_stim',
        ...     wavelength=473,  # nm (blue)
        ...     power=10.0  # mW
        ... )
    """

    def __init__(self, session, name: str = None, reference: int = None,
                 subject_id: str = None,
                 imaging_type: str = 'widefield',
                 wavelength: Optional[float] = None,
                 wavelengths: Optional[List[float]] = None,
                 resolution: Optional[float] = None,
                 field_of_view: Optional[tuple] = None,
                 frame_rate: Optional[float] = None,
                 power: Optional[float] = None,
                 **kwargs):
        """
        Create an OpticalProbe.

        Args:
            session: NDI Session object
            name: Probe name
            reference: Reference number
            subject_id: Subject identifier
            imaging_type: Type of optical device
                ('two_photon', 'widefield', 'confocal', 'fiber_photometry',
                 'optogenetic_stim', 'single_photon')
            wavelength: Single wavelength in nm (for single-channel)
            wavelengths: Multiple wavelengths in nm (for multi-channel)
            resolution: Spatial resolution in um/pixel
            field_of_view: Field of view as (width, height) in um
            frame_rate: Frame rate in Hz
            power: Optical power in mW
            **kwargs: Additional properties

        Examples:
            >>> # Widefield calcium imaging
            >>> camera = OpticalProbe(
            ...     session,
            ...     name='widefield_cam',
            ...     reference=1,
            ...     subject_id='mouse01',
            ...     imaging_type='widefield',
            ...     wavelength=525,  # GCaMP emission
            ...     resolution=2.0,  # um/pixel
            ...     field_of_view=(1000, 1000),  # 1mm x 1mm
            ...     frame_rate=20.0
            ... )
            >>>
            >>> # Multi-wavelength fiber photometry
            >>> fiber = OpticalProbe(
            ...     session,
            ...     name='fiber_photometry',
            ...     reference=1,
            ...     subject_id='mouse01',
            ...     imaging_type='fiber_photometry',
            ...     wavelengths=[470, 405],  # GCaMP + isosbestic
            ...     frame_rate=100.0
            ... )
        """
        # Initialize base Probe
        super().__init__(
            session,
            name,
            reference,
            f'optical_{imaging_type}',
            subject_id
        )

        # Optical probe specific properties
        self.imaging_type = imaging_type

        # Handle wavelength(s)
        if wavelengths is not None:
            self.wavelengths = wavelengths
        elif wavelength is not None:
            self.wavelengths = [wavelength]
        else:
            self.wavelengths = None

        self.resolution = resolution  # um/pixel
        self.field_of_view = field_of_view  # (width, height) in um
        self.frame_rate = frame_rate  # Hz
        self.power = power  # mW

        # Store additional properties
        for key, value in kwargs.items():
            setattr(self, key, value)

    def is_imaging(self) -> bool:
        """
        Check if this is an imaging device (vs stimulation).

        Returns:
            True if imaging, False if stimulation

        Examples:
            >>> camera = OpticalProbe(session, 'cam1', 1, 'mouse1', imaging_type='widefield')
            >>> camera.is_imaging()
            True
            >>> led = OpticalProbe(session, 'led1', 1, 'mouse1', imaging_type='optogenetic_stim')
            >>> led.is_imaging()
            False
        """
        return 'stim' not in self.imaging_type.lower()

    def is_stimulation(self) -> bool:
        """
        Check if this is a stimulation device.

        Returns:
            True if stimulation, False if imaging

        Examples:
            >>> led = OpticalProbe(session, 'led1', 1, 'mouse1', imaging_type='optogenetic_stim')
            >>> led.is_stimulation()
            True
        """
        return 'stim' in self.imaging_type.lower() or 'opto' in self.imaging_type.lower()

    def get_properties(self) -> Dict[str, Any]:
        """
        Get optical probe properties.

        Returns:
            Dict with probe properties

        Examples:
            >>> props = camera.get_properties()
            >>> print(f"Frame rate: {props['frame_rate']} Hz")
        """
        props = {
            'name': self.name,
            'reference': self.reference,
            'type': f'optical_{self.imaging_type}',
            'imaging_type': self.imaging_type
        }

        if self.wavelengths is not None:
            if len(self.wavelengths) == 1:
                props['wavelength'] = self.wavelengths[0]
            else:
                props['wavelengths'] = self.wavelengths
            props['wavelength_unit'] = 'nm'

        if self.resolution is not None:
            props['resolution'] = self.resolution
            props['resolution_unit'] = 'um/pixel'

        if self.field_of_view is not None:
            props['field_of_view'] = self.field_of_view
            props['fov_unit'] = 'um'

        if self.frame_rate is not None:
            props['frame_rate'] = self.frame_rate
            props['frame_rate_unit'] = 'Hz'

        if self.power is not None:
            props['power'] = self.power
            props['power_unit'] = 'mW'

        return props

    def __repr__(self) -> str:
        """String representation."""
        wl_str = ""
        if self.wavelengths:
            if len(self.wavelengths) == 1:
                wl_str = f", {self.wavelengths[0]}nm"
            else:
                wl_str = f", {len(self.wavelengths)} wavelengths"

        return (f"OpticalProbe(name='{self.name}', ref={self.reference}, "
                f"type='{self.imaging_type}'{wl_str})")
