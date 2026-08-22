"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    STRUTTURA A LAYER DELLA CORTECCIA                         ║
║                                                                              ║
║     La corteccia cerebrale ha 6 strati (layer):                              ║
║                                                                              ║
║     Layer 1: Molecolare (pochi neuroni, molti assoni)                        ║
║     Layer 2/3: Supragranulare (connessioni cortico-corticali)                ║
║     Layer 4: Granulare (input dal talamo)                                    ║
║     Layer 5: Infragranulare (output subcorticale)                            ║
║     Layer 6: Multiforme (feedback al talamo)                                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .neurons import NeuronType, NeuronGroup, BACKEND, create_neuron_group
from .synapses import Synapse, connect, ConnectionRule, ReceptorType, CONNECTION_RULES

if BACKEND == "torch":
    import torch
    from .neurons import DEVICE


# ============================================================
# LAYER CORTICALI
# ============================================================

class CorticalLayer(Enum):
    """I 6 layer della corteccia."""
    L1 = 1    # Molecolare
    L2_3 = 2  # Supragranulare (combinato)
    L4 = 4    # Granulare
    L5 = 5    # Infragranulare
    L6 = 6    # Multiforme


@dataclass
class LayerComposition:
    """Composizione di un layer."""
    thickness_fraction: float  # Frazione dello spessore totale
    neuron_fraction: float     # Frazione dei neuroni totali
    cell_types: Dict[NeuronType, float] = field(default_factory=dict)


# Composizione realistica di ogni layer
# Basata su: DeFelipe et al., "The Pyramidal Neuron of the Cerebral Cortex"
LAYER_COMPOSITION = {
    CorticalLayer.L1: LayerComposition(
        thickness_fraction=0.10,
        neuron_fraction=0.02,  # Pochissimi neuroni
        cell_types={
            NeuronType.VIP: 0.50,
            NeuronType.SST: 0.50,
        }
    ),
    CorticalLayer.L2_3: LayerComposition(
        thickness_fraction=0.30,
        neuron_fraction=0.30,
        cell_types={
            NeuronType.PYRAMIDAL: 0.75,
            NeuronType.PV: 0.10,
            NeuronType.SST: 0.08,
            NeuronType.VIP: 0.07,
        }
    ),
    CorticalLayer.L4: LayerComposition(
        thickness_fraction=0.15,
        neuron_fraction=0.20,
        cell_types={
            NeuronType.STELLATE: 0.40,  # Molte stellate in L4
            NeuronType.PYRAMIDAL: 0.35,
            NeuronType.PV: 0.15,
            NeuronType.SST: 0.05,
            NeuronType.VIP: 0.05,
        }
    ),
    CorticalLayer.L5: LayerComposition(
        thickness_fraction=0.25,
        neuron_fraction=0.28,
        cell_types={
            NeuronType.PYRAMIDAL: 0.80,  # Piramidali grossi (output)
            NeuronType.PV: 0.10,
            NeuronType.SST: 0.05,
            NeuronType.VIP: 0.05,
        }
    ),
    CorticalLayer.L6: LayerComposition(
        thickness_fraction=0.20,
        neuron_fraction=0.20,
        cell_types={
            NeuronType.PYRAMIDAL: 0.75,
            NeuronType.PV: 0.10,
            NeuronType.SST: 0.10,
            NeuronType.VIP: 0.05,
        }
    ),
}


# ============================================================
# CONNESSIONI TRA LAYER
# ============================================================

@dataclass
class InterLayerConnection:
    """Connessione tra layer."""
    source_layer: CorticalLayer
    target_layer: CorticalLayer
    source_types: List[NeuronType]
    target_types: List[NeuronType]
    probability: float
    description: str


# Connessioni canoniche tra layer
# Basato su: Douglas & Martin, "Neuronal Circuits of the Neocortex"
CANONICAL_CIRCUIT = [
    # INPUT: Talamo -> L4
    # (gestito separatamente)
    
    # L4 -> L2/3 (feedforward)
    InterLayerConnection(
        source_layer=CorticalLayer.L4,
        target_layer=CorticalLayer.L2_3,
        source_types=[NeuronType.STELLATE, NeuronType.PYRAMIDAL],
        target_types=[NeuronType.PYRAMIDAL, NeuronType.PV],
        probability=0.20,
        description="L4 stellate to L2/3 pyramidal (main feedforward)"
    ),
    
    # L2/3 -> L5 (feedforward)
    InterLayerConnection(
        source_layer=CorticalLayer.L2_3,
        target_layer=CorticalLayer.L5,
        source_types=[NeuronType.PYRAMIDAL],
        target_types=[NeuronType.PYRAMIDAL, NeuronType.PV],
        probability=0.15,
        description="L2/3 pyramidal to L5 (cortico-cortical output prep)"
    ),
    
    # L5 -> L6 (feedforward)
    InterLayerConnection(
        source_layer=CorticalLayer.L5,
        target_layer=CorticalLayer.L6,
        source_types=[NeuronType.PYRAMIDAL],
        target_types=[NeuronType.PYRAMIDAL],
        probability=0.10,
        description="L5 to L6"
    ),
    
    # L6 -> L4 (feedback interno)
    InterLayerConnection(
        source_layer=CorticalLayer.L6,
        target_layer=CorticalLayer.L4,
        source_types=[NeuronType.PYRAMIDAL],
        target_types=[NeuronType.STELLATE, NeuronType.PYRAMIDAL],
        probability=0.10,
        description="L6 feedback to L4"
    ),
    
    # L2/3 -> L2/3 (connessioni laterali)
    InterLayerConnection(
        source_layer=CorticalLayer.L2_3,
        target_layer=CorticalLayer.L2_3,
        source_types=[NeuronType.PYRAMIDAL],
        target_types=[NeuronType.PYRAMIDAL, NeuronType.PV, NeuronType.SST],
        probability=0.10,
        description="L2/3 lateral connections"
    ),
    
    # L5 -> L2/3 (feedback)
    InterLayerConnection(
        source_layer=CorticalLayer.L5,
        target_layer=CorticalLayer.L2_3,
        source_types=[NeuronType.PYRAMIDAL],
        target_types=[NeuronType.PYRAMIDAL, NeuronType.SST],
        probability=0.05,
        description="L5 feedback to L2/3"
    ),
]


# ============================================================
# COLONNA CORTICALE
# ============================================================

class CorticalColumn:
    """
    Colonna corticale completa con tutti i layer e tipi di neuroni.
    
    Una colonna corticale e l'unita funzionale della corteccia.
    Diametro: ~300-500 um
    Neuroni: ~10,000-100,000 per colonna (varia per area)
    """
    
    def __init__(
        self,
        n_neurons: int = 1000,
        name: str = "Column",
        debug: bool = False
    ):
        self.name = name
        self.n_neurons = n_neurons
        self.debug = debug
        
        # Crea struttura
        self.layers: Dict[CorticalLayer, Dict[NeuronType, NeuronGroup]] = {}
        self.synapses: List[Synapse] = []
        
        self._build_layers()
        self._build_connections()
        
        # Conta neuroni totali
        self.total_neurons = sum(
            sum(ng.n for ng in layer.values())
            for layer in self.layers.values()
        )
        
        if debug:
            self._print_structure()
    
    def _build_layers(self):
        """Costruisce tutti i layer con i tipi di neuroni corretti."""
        for layer, comp in LAYER_COMPOSITION.items():
            n_layer = max(10, int(self.n_neurons * comp.neuron_fraction))
            
            self.layers[layer] = {}
            
            for ntype, fraction in comp.cell_types.items():
                n_type = max(1, int(n_layer * fraction))
                name = f"{self.name}_{layer.name}_{ntype.value}"
                self.layers[layer][ntype] = create_neuron_group(n_type, ntype, name)
    
    def _build_connections(self):
        """Costruisce connessioni secondo il circuito canonico."""
        # Connessioni INTRA-layer (dentro stesso layer)
        for layer, populations in self.layers.items():
            for src_type, src_group in populations.items():
                for tgt_type, tgt_group in populations.items():
                    key = (src_type, tgt_type)
                    if key in CONNECTION_RULES:
                        syn = connect(src_group, tgt_group)
                        self.synapses.append(syn)
        
        # Connessioni INTER-layer (tra layer diversi)
        for conn in CANONICAL_CIRCUIT:
            src_layer = self.layers.get(conn.source_layer, {})
            tgt_layer = self.layers.get(conn.target_layer, {})
            
            for src_type in conn.source_types:
                if src_type not in src_layer:
                    continue
                src_group = src_layer[src_type]
                
                for tgt_type in conn.target_types:
                    if tgt_type not in tgt_layer:
                        continue
                    tgt_group = tgt_layer[tgt_type]
                    
                    # Crea connessione con probabilita modificata
                    rule = ConnectionRule(
                        probability=conn.probability,
                        weight_mean=0.5,
                        weight_std=0.2,
                        receptor=ReceptorType.AMPA if src_group.is_excitatory else ReceptorType.GABA_A,
                        plastic=True,
                        target_compartment="soma"
                    )
                    syn = connect(src_group, tgt_group, rule)
                    self.synapses.append(syn)
    
    def _print_structure(self):
        """Stampa struttura della colonna."""
        print(f"\n[COLUMN] {self.name}")
        print("-" * 50)
        for layer in CorticalLayer:
            if layer in self.layers:
                print(f"  {layer.name}:")
                for ntype, group in self.layers[layer].items():
                    exc = "+" if group.is_excitatory else "-"
                    print(f"    {exc} {ntype.value}: {group.n} neuroni")
        print(f"  TOTALE: {self.total_neurons} neuroni")
        print(f"  SINAPSI: {len(self.synapses)} connessioni")
    
    def receive_input(self, input_current, layer: CorticalLayer = CorticalLayer.L4):
        """
        Riceve input esterno (es. dal talamo).
        
        Args:
            input_current: Corrente di input
            layer: Layer target (default L4)
        """
        if layer not in self.layers:
            return
        
        # Distribuisci input ai neuroni eccitatori del layer
        for ntype, group in self.layers[layer].items():
            if group.is_excitatory:
                if BACKEND == "torch":
                    if isinstance(input_current, np.ndarray):
                        input_current = torch.tensor(input_current, device=DEVICE, dtype=torch.float32)
                    # Ridimensiona se necessario
                    if len(input_current) != group.n:
                        indices = torch.linspace(0, len(input_current)-1, group.n).long()
                        current = input_current[indices]
                    else:
                        current = input_current
                else:
                    if len(input_current) != group.n:
                        indices = np.linspace(0, len(input_current)-1, group.n).astype(int)
                        current = input_current[indices]
                    else:
                        current = input_current
                
                group.inject_current(current, excitatory=True)
    
    def step(self, dt: float = 1.0):
        """Simula un timestep."""
        # 1. Propaga sinapsi
        for syn in self.synapses:
            syn.propagate()
        
        # 2. Aggiorna neuroni (ordine: L4 -> L2/3 -> L5 -> L6)
        for layer in [CorticalLayer.L4, CorticalLayer.L2_3, CorticalLayer.L5, CorticalLayer.L6, CorticalLayer.L1]:
            if layer in self.layers:
                for group in self.layers[layer].values():
                    group.step(dt)
    
    def learn(self, reward: float = 1.0, dt: float = 1.0):
        """Applica plasticita."""
        for syn in self.synapses:
            syn.update_stdp(reward, dt)
    
    def get_output(self) -> np.ndarray:
        """
        Ottiene output dalla colonna (L5 pyramidal).
        """
        if CorticalLayer.L5 in self.layers:
            pyr = self.layers[CorticalLayer.L5].get(NeuronType.PYRAMIDAL)
            if pyr:
                if BACKEND == "torch":
                    return pyr.spike.cpu().numpy()
                return pyr.spike.copy()
        return np.array([])
    
    def get_l23_activity(self) -> np.ndarray:
        """Attivita L2/3 (processing)."""
        if CorticalLayer.L2_3 in self.layers:
            pyr = self.layers[CorticalLayer.L2_3].get(NeuronType.PYRAMIDAL)
            if pyr:
                if BACKEND == "torch":
                    return pyr.spike.cpu().numpy()
                return pyr.spike.copy()
        return np.array([])
    
    def get_state(self) -> dict:
        """Stato della colonna."""
        state = {
            "name": self.name,
            "total_neurons": self.total_neurons,
            "n_synapses": len(self.synapses),
            "layers": {}
        }
        
        for layer, pops in self.layers.items():
            state["layers"][layer.name] = {}
            for ntype, group in pops.items():
                if BACKEND == "torch":
                    spikes = group.spike.sum().item()
                else:
                    spikes = group.spike.sum()
                state["layers"][layer.name][ntype.value] = {
                    "n": group.n,
                    "spikes": int(spikes)
                }
        
        return state
    
    def reset(self):
        """Reset stato."""
        for layer in self.layers.values():
            for group in layer.values():
                group.reset()


# ============================================================
# FACTORY
# ============================================================

def create_cortical_column(
    n_neurons: int = 1000,
    name: str = "Column",
    debug: bool = False
) -> CorticalColumn:
    """Crea una colonna corticale."""
    return CorticalColumn(n_neurons, name, debug)
