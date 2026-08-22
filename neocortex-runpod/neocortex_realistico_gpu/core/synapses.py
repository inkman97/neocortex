"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    SINAPSI BIOLOGICAMENTE REALISTICHE                        ║
║                                                                              ║
║     Tipi di recettori:                                                       ║
║                                                                              ║
║     ECCITATORI (Glutammato):                                                 ║
║       - AMPA: veloce, principale trasmissione eccitatoria                    ║
║       - NMDA: lento, richiede depolarizzazione, plasticita                   ║
║                                                                              ║
║     INIBITORI (GABA):                                                        ║
║       - GABA_A: veloce, principale trasmissione inibitoria                   ║
║       - GABA_B: lento, modulatorio                                           ║
║                                                                              ║
║     Plasticita:                                                              ║
║       - STDP: Spike-Timing-Dependent Plasticity                              ║
║       - Three-factor: STDP + neuromodulazione                                ║
║       - Homeostatic: mantiene attivita stabile                               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple

from .neurons import NeuronType, NeuronGroup, BACKEND
if BACKEND == "torch":
    import torch
    from .neurons import DEVICE


# ============================================================
# TIPI DI RECETTORI
# ============================================================

class ReceptorType(Enum):
    """Tipi di recettori sinaptici."""
    # Eccitatori
    AMPA = "ampa"           # Veloce, Na+/K+
    NMDA = "nmda"           # Lento, Ca2+, voltage-dependent
    
    # Inibitori
    GABA_A = "gaba_a"       # Veloce, Cl-
    GABA_B = "gaba_b"       # Lento, K+, metabotropico


@dataclass
class ReceptorParameters:
    """Parametri per ogni tipo di recettore."""
    tau_rise: float         # Tempo di salita (ms)
    tau_decay: float        # Tempo di decadimento (ms)
    reversal: float         # Potenziale di inversione (normalizzato)
    conductance: float      # Conduttanza massima


RECEPTOR_PARAMS = {
    ReceptorType.AMPA: ReceptorParameters(
        tau_rise=0.5,
        tau_decay=2.0,
        reversal=1.0,       # Eccitatorio
        conductance=1.0
    ),
    ReceptorType.NMDA: ReceptorParameters(
        tau_rise=2.0,
        tau_decay=50.0,     # Molto lento
        reversal=1.0,
        conductance=0.5     # Piu debole ma duraturo
    ),
    ReceptorType.GABA_A: ReceptorParameters(
        tau_rise=0.5,
        tau_decay=5.0,
        reversal=-0.2,      # Inibitorio
        conductance=1.0
    ),
    ReceptorType.GABA_B: ReceptorParameters(
        tau_rise=10.0,
        tau_decay=100.0,    # Molto lento
        reversal=-0.3,
        conductance=0.3
    ),
}


# ============================================================
# CONNESSIONI TRA TIPI DI NEURONI
# ============================================================

@dataclass
class ConnectionRule:
    """Regola di connessione tra tipi di neuroni."""
    probability: float      # Probabilita di connessione
    weight_mean: float      # Peso medio
    weight_std: float       # Deviazione standard peso
    receptor: ReceptorType  # Tipo di recettore
    plastic: bool           # Soggetta a plasticita?
    target_compartment: str # "soma", "proximal_dendrite", "distal_dendrite"


# Matrice di connettivita biologicamente realistica
# Basata su: Markram et al. 2015, "Reconstruction and Simulation of Neocortical Microcircuitry"
CONNECTION_RULES = {
    # PYR -> altri
    (NeuronType.PYRAMIDAL, NeuronType.PYRAMIDAL): ConnectionRule(
        probability=0.10,       # 10% connessi
        weight_mean=0.5,
        weight_std=0.2,
        receptor=ReceptorType.AMPA,
        plastic=True,           # Plasticita Hebbiana
        target_compartment="proximal_dendrite"
    ),
    (NeuronType.PYRAMIDAL, NeuronType.PV): ConnectionRule(
        probability=0.40,       # Forte connessione
        weight_mean=0.8,
        weight_std=0.2,
        receptor=ReceptorType.AMPA,
        plastic=True,
        target_compartment="soma"
    ),
    (NeuronType.PYRAMIDAL, NeuronType.SST): ConnectionRule(
        probability=0.30,
        weight_mean=0.6,
        weight_std=0.2,
        receptor=ReceptorType.AMPA,
        plastic=True,
        target_compartment="soma"
    ),
    (NeuronType.PYRAMIDAL, NeuronType.VIP): ConnectionRule(
        probability=0.20,
        weight_mean=0.5,
        weight_std=0.2,
        receptor=ReceptorType.AMPA,
        plastic=False,
        target_compartment="soma"
    ),
    
    # PV -> altri (INIBIZIONE FORTE E VELOCE)
    (NeuronType.PV, NeuronType.PYRAMIDAL): ConnectionRule(
        probability=0.50,       # Molto connesso
        weight_mean=1.0,        # Forte
        weight_std=0.3,
        receptor=ReceptorType.GABA_A,
        plastic=True,           # Plasticita inibitoria
        target_compartment="soma"  # Inibizione perisomatica
    ),
    (NeuronType.PV, NeuronType.PV): ConnectionRule(
        probability=0.40,       # PV si inibiscono tra loro
        weight_mean=0.8,
        weight_std=0.2,
        receptor=ReceptorType.GABA_A,
        plastic=False,
        target_compartment="soma"
    ),
    (NeuronType.PV, NeuronType.SST): ConnectionRule(
        probability=0.20,
        weight_mean=0.5,
        weight_std=0.2,
        receptor=ReceptorType.GABA_A,
        plastic=False,
        target_compartment="soma"
    ),
    
    # SST -> altri (INIBIZIONE DENDRITICA)
    (NeuronType.SST, NeuronType.PYRAMIDAL): ConnectionRule(
        probability=0.40,
        weight_mean=0.8,
        weight_std=0.2,
        receptor=ReceptorType.GABA_A,
        plastic=True,
        target_compartment="distal_dendrite"  # Blocca input!
    ),
    (NeuronType.SST, NeuronType.PV): ConnectionRule(
        probability=0.30,
        weight_mean=0.6,
        weight_std=0.2,
        receptor=ReceptorType.GABA_A,
        plastic=False,
        target_compartment="soma"
    ),
    (NeuronType.SST, NeuronType.VIP): ConnectionRule(
        probability=0.40,
        weight_mean=0.7,
        weight_std=0.2,
        receptor=ReceptorType.GABA_A,
        plastic=False,
        target_compartment="soma"
    ),
    
    # VIP -> altri (DISINIBIZIONE)
    (NeuronType.VIP, NeuronType.SST): ConnectionRule(
        probability=0.50,       # Forte connessione a SST
        weight_mean=0.9,        # VIP inibisce SST
        weight_std=0.2,
        receptor=ReceptorType.GABA_A,
        plastic=False,
        target_compartment="soma"
    ),
    (NeuronType.VIP, NeuronType.PV): ConnectionRule(
        probability=0.30,
        weight_mean=0.5,
        weight_std=0.2,
        receptor=ReceptorType.GABA_A,
        plastic=False,
        target_compartment="soma"
    ),
    
    # STELLATE -> altri (Layer 4 input)
    (NeuronType.STELLATE, NeuronType.PYRAMIDAL): ConnectionRule(
        probability=0.30,
        weight_mean=0.7,
        weight_std=0.2,
        receptor=ReceptorType.AMPA,
        plastic=True,
        target_compartment="proximal_dendrite"
    ),
    (NeuronType.STELLATE, NeuronType.PV): ConnectionRule(
        probability=0.40,
        weight_mean=0.8,
        weight_std=0.2,
        receptor=ReceptorType.AMPA,
        plastic=False,
        target_compartment="soma"
    ),
}


# ============================================================
# CLASSE SINAPSI
# ============================================================

class Synapse:
    """
    Connessione sinaptica tra due gruppi di neuroni.
    Include STDP e plasticita omeostatica.
    """
    
    def __init__(
        self,
        source: NeuronGroup,
        target: NeuronGroup,
        rule: Optional[ConnectionRule] = None
    ):
        self.source = source
        self.target = target
        
        # Ottieni regola di connessione
        key = (source.neuron_type, target.neuron_type)
        if rule is None:
            rule = CONNECTION_RULES.get(key)
        
        if rule is None:
            # Connessione non definita, usa default
            is_exc = source.is_excitatory
            rule = ConnectionRule(
                probability=0.1,
                weight_mean=0.5,
                weight_std=0.2,
                receptor=ReceptorType.AMPA if is_exc else ReceptorType.GABA_A,
                plastic=False,
                target_compartment="soma"
            )
        
        self.rule = rule
        self.receptor_params = RECEPTOR_PARAMS[rule.receptor]
        
        # Inizializza pesi
        self._init_weights()
        
        # Tracce per STDP
        self._init_traces()
    
    def _init_weights(self):
        """Inizializza matrice pesi."""
        n_src = self.source.n
        n_tgt = self.target.n
        
        # Pesi random con distribuzione specificata
        if BACKEND == "torch":
            self.weights = torch.randn(n_src, n_tgt, device=DEVICE) * self.rule.weight_std
            self.weights = self.weights + self.rule.weight_mean
            self.weights = torch.clamp(self.weights, 0, 2)
            
            # Maschera connettivita
            mask = torch.rand(n_src, n_tgt, device=DEVICE) < self.rule.probability
            self.weights = self.weights * mask.float()
        else:
            self.weights = np.random.randn(n_src, n_tgt).astype(np.float32) * self.rule.weight_std
            self.weights = self.weights + self.rule.weight_mean
            self.weights = np.clip(self.weights, 0, 2)
            
            mask = np.random.random((n_src, n_tgt)) < self.rule.probability
            self.weights = self.weights * mask.astype(np.float32)
    
    def _init_traces(self):
        """Inizializza tracce per STDP."""
        n_src = self.source.n
        n_tgt = self.target.n
        
        if BACKEND == "torch":
            self.pre_trace = torch.zeros(n_src, device=DEVICE)
            self.post_trace = torch.zeros(n_tgt, device=DEVICE)
            self.eligibility = torch.zeros(n_src, n_tgt, device=DEVICE)
        else:
            self.pre_trace = np.zeros(n_src, dtype=np.float32)
            self.post_trace = np.zeros(n_tgt, dtype=np.float32)
            self.eligibility = np.zeros((n_src, n_tgt), dtype=np.float32)
        
        # Parametri STDP
        self.tau_pre = 20.0
        self.tau_post = 20.0
        self.A_plus = 0.01
        self.A_minus = 0.012  # LTD leggermente piu forte
        self.tau_eligibility = 1000.0
        
        # Limiti pesi
        self.w_min = 0.0
        self.w_max = 2.0
    
    def propagate(self) -> None:
        """Propaga spike dalla sorgente al target."""
        if BACKEND == "torch":
            current = torch.matmul(self.source.spike.float(), self.weights)
            current = current * self.receptor_params.conductance
        else:
            current = np.dot(self.source.spike.astype(np.float32), self.weights)
            current = current * self.receptor_params.conductance
        
        # Aggiungi al target (eccitatorio o inibitorio)
        if self.source.is_excitatory:
            self.target.I_exc += current
        else:
            self.target.I_inh += current
    
    def update_stdp(self, reward: float = 1.0, dt: float = 1.0) -> None:
        """
        Aggiorna pesi con STDP + three-factor learning.
        
        Args:
            reward: Segnale di reward (dopamina)
            dt: Timestep
        """
        if not self.rule.plastic:
            return
        
        if BACKEND == "torch":
            self._stdp_torch(reward, dt)
        else:
            self._stdp_numpy(reward, dt)
    
    def _stdp_numpy(self, reward: float, dt: float):
        """STDP con NumPy."""
        # Decay tracce
        decay_pre = np.exp(-dt / self.tau_pre)
        decay_post = np.exp(-dt / self.tau_post)
        
        self.pre_trace *= decay_pre
        self.post_trace *= decay_post
        
        # Aggiorna tracce con spike
        self.pre_trace[self.source.spike] = 1.0
        self.post_trace[self.target.spike] = 1.0
        
        # Calcola LTP e LTD
        # LTP: pre prima, post adesso
        ltp = np.outer(self.pre_trace, self.target.spike.astype(np.float32)) * self.A_plus
        
        # LTD: pre adesso, post prima
        ltd = np.outer(self.source.spike.astype(np.float32), self.post_trace) * self.A_minus
        
        # Aggiorna eligibility trace
        decay_elig = np.exp(-dt / self.tau_eligibility)
        self.eligibility *= decay_elig
        self.eligibility += ltp - ltd
        
        # Three-factor: applica solo con reward
        if reward != 1.0:
            dw = self.eligibility * (reward - 1.0) * 0.1
            self.weights += dw
            self.weights = np.clip(self.weights, self.w_min, self.w_max)
    
    def _stdp_torch(self, reward: float, dt: float):
        """STDP con PyTorch."""
        decay_pre = np.exp(-dt / self.tau_pre)
        decay_post = np.exp(-dt / self.tau_post)
        
        self.pre_trace = self.pre_trace * decay_pre
        self.post_trace = self.post_trace * decay_post
        
        self.pre_trace = torch.where(
            self.source.spike,
            torch.ones_like(self.pre_trace),
            self.pre_trace
        )
        self.post_trace = torch.where(
            self.target.spike,
            torch.ones_like(self.post_trace),
            self.post_trace
        )
        
        ltp = torch.outer(self.pre_trace, self.target.spike.float()) * self.A_plus
        ltd = torch.outer(self.source.spike.float(), self.post_trace) * self.A_minus
        
        decay_elig = np.exp(-dt / self.tau_eligibility)
        self.eligibility = self.eligibility * decay_elig + ltp - ltd
        
        if reward != 1.0:
            dw = self.eligibility * (reward - 1.0) * 0.1
            self.weights = self.weights + dw
            self.weights = torch.clamp(self.weights, self.w_min, self.w_max)
    
    def homeostatic_scaling(self, target_rate: float = 5.0):
        """
        Plasticita omeostatica: scala i pesi per mantenere firing rate target.
        
        Args:
            target_rate: Firing rate target in Hz
        """
        actual_rate = self.target.get_firing_rate()
        
        if actual_rate > 0:
            scale = target_rate / actual_rate
            scale = np.clip(scale, 0.9, 1.1)  # Limita scaling
            
            if BACKEND == "torch":
                self.weights = self.weights * scale
            else:
                self.weights *= scale
    
    @property
    def n_connections(self) -> int:
        """Numero di connessioni attive."""
        if BACKEND == "torch":
            return int((self.weights > 0).sum().item())
        else:
            return int((self.weights > 0).sum())
    
    @property
    def mean_weight(self) -> float:
        """Peso medio delle connessioni attive."""
        if BACKEND == "torch":
            active = self.weights[self.weights > 0]
            return active.mean().item() if len(active) > 0 else 0.0
        else:
            active = self.weights[self.weights > 0]
            return active.mean() if len(active) > 0 else 0.0


# ============================================================
# FACTORY
# ============================================================

def connect(
    source: NeuronGroup,
    target: NeuronGroup,
    rule: Optional[ConnectionRule] = None
) -> Synapse:
    """Crea connessione sinaptica."""
    return Synapse(source, target, rule)


def create_all_connections(
    populations: dict
) -> dict:
    """
    Crea tutte le connessioni tra popolazioni secondo le regole biologiche.
    
    Args:
        populations: Dict[NeuronType, NeuronGroup]
    
    Returns:
        Dict[(source_type, target_type), Synapse]
    """
    synapses = {}
    
    for (src_type, tgt_type), rule in CONNECTION_RULES.items():
        if src_type in populations and tgt_type in populations:
            syn = Synapse(populations[src_type], populations[tgt_type], rule)
            synapses[(src_type, tgt_type)] = syn
    
    return synapses
