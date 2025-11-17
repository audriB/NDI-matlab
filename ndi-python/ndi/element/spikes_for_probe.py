"""
Spikes For Probe - Create a neuron element from probe and spike data.

MATLAB equivalent: ndi.element.spikesForProbe
"""

from typing import List, Dict
import numpy as np

from ..neuron import Neuron


def spikes_for_probe(
    session,
    probe,
    name: str,
    reference: int,
    spikedata: List[Dict]
) -> Neuron:
    """
    Create a spiking neuron element from a probe and spike data.

    MATLAB equivalent: ndi.element.spikesForProbe()

    Args:
        session: NDI Session object
        probe: NDI Probe object
        name: Name for the neuron element
        reference: Reference number (used as unit_id)
        spikedata: List of dicts with fields:
            - 'epochid': Epoch ID string (must exist in probe)
            - 'spiketimes': Array of spike times in probe's clock

    Returns:
        Neuron: New neuron element with spike data

    Examples:
        >>> from ndi.element import spikes_for_probe
        >>> # Create spike data
        >>> spikedata = [
        ...     {'epochid': 't00001', 'spiketimes': [0.01, 0.02, 0.03]},
        ...     {'epochid': 't00002', 'spiketimes': [1.01, 1.02, 1.03]}
        ... ]
        >>> neuron = spikes_for_probe(session, probe, 'unit1', 1, spikedata)
    """
    # Create dependencies
    dependencies = {
        'channel': {'name': 'channel', 'value': 0},
        'unit_id': {'name': 'unit_id', 'value': reference}
    }

    # Create neuron element
    neuron = Neuron(
        session,
        name,
        reference,
        'spikes',
        underlying_element=probe,
        direct=False,
        subject_id=None,  # Take from probe
        dependencies=dependencies
    )

    # Get probe's epoch table
    et = probe.epochtable()

    # Add spike data for each epoch
    for spike_entry in spikedata:
        epoch_id = spike_entry['epochid']
        spiketimes = np.array(spike_entry['spiketimes'])

        # Find matching epoch in probe
        matching_epochs = [e for e in et if e.get('epoch_id') == epoch_id]

        if len(matching_epochs) == 0:
            raise ValueError(f'Could not find epoch with id {epoch_id} in the probe')
        if len(matching_epochs) > 1:
            raise ValueError(f'Found more than one epoch with id {epoch_id} in the probe')

        et_here = matching_epochs[0]

        # Get all clock types and t0_t1 values
        epoch_clocks = et_here['epoch_clock']
        t0_t1 = et_here['t0_t1']

        # Data is just the spike times
        data = spiketimes.reshape(-1, 1)  # Column vector

        # Add epoch with spike data
        neuron, epochdoc = neuron.addepoch(
            epoch_id,
            ','.join([str(c) for c in epoch_clocks]),
            t0_t1,
            spiketimes,
            data
        )

        # Add to database
        session.database_add(epochdoc)

    return neuron


class SpikesForProbe:
    """Placeholder class for SpikesForProbe element type."""
    pass
