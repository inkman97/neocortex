"""
NeoCortex Loihi Core Module
"""
from .neurons_loihi import (
    NeuronType, NeuronParams, SCALE, SCALE_SHIFT,
    float_to_fixed, fixed_to_float,
    create_neuron_population, LAVA_AVAILABLE
)
from .synapses_loihi import (
    STDPConfig, SparseSynapseMatrix,
    create_cortical_connectivity
)
from .neuromodulation_loihi import (
    Neuromodulator, ReceptorProfile, RECEPTOR_PROFILES,
    NeuromodulatorPopulation, NeuromodulationSystem,
    calculate_receptor_modulation
)

__all__ = [
    'NeuronType', 'NeuronParams', 'SCALE', 'SCALE_SHIFT',
    'float_to_fixed', 'fixed_to_float',
    'create_neuron_population', 'LAVA_AVAILABLE',
    'STDPConfig', 'SparseSynapseMatrix',
    'create_cortical_connectivity',
    'Neuromodulator', 'ReceptorProfile', 'RECEPTOR_PROFILES',
    'NeuromodulatorPopulation', 'NeuromodulationSystem',
    'calculate_receptor_modulation'
]
