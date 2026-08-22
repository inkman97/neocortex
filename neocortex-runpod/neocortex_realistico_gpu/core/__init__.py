"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    NEOCORTEX REALISTICO - CORE                               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from .neurons import (
    NeuronType,
    NeuronParameters,
    NEURON_PARAMS,
    NeuronGroup,
    create_neuron_group,
    create_population,
    BACKEND
)

from .synapses import (
    ReceptorType,
    ConnectionRule,
    CONNECTION_RULES,
    Synapse,
    connect,
    create_all_connections
)

from .layers import (
    CorticalLayer,
    LayerComposition,
    LAYER_COMPOSITION,
    CorticalColumn,
    create_cortical_column
)

from .enums import Neuromodulator


from .subcortical import (
    Thalamus,
    BasalGanglia,
    Hippocampus,
    Amygdala
)

__all__ = [
    # Neurons
    'NeuronType',
    'NeuronParameters',
    'NEURON_PARAMS',
    'NeuronGroup',
    'create_neuron_group',
    'create_population',
    'BACKEND',
    
    # Synapses
    'ReceptorType',
    'ConnectionRule',
    'CONNECTION_RULES',
    'Synapse',
    'connect',
    'create_all_connections',
    
    # Layers
    'CorticalLayer',
    'LayerComposition',
    'LAYER_COMPOSITION',
    'CorticalColumn',
    'create_cortical_column',
    
    # Neuromodulation
    'Neuromodulator',
    
    # Subcortical
    'Thalamus',
    'BasalGanglia',
    'Hippocampus',
    'Amygdala',
]
