"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    NEURONI BIOLOGICAMENTE REALISTICI                         ║
║                                                                              ║
║     Tipi di neuroni nella corteccia cerebrale:                               ║
║                                                                              ║
║     ECCITATORI (80%):                                                        ║
║       - Piramidali: neuroni principali, output della corteccia               ║
║       - Stellate: interneuroni eccitatori in Layer 4                         ║
║                                                                              ║
║     INIBITORI (20%):                                                         ║
║       - PV (Parvalbumin): inibizione veloce sul soma                         ║
║       - SST (Somatostatin): inibizione lenta sui dendriti                    ║
║       - VIP: disinibizione (inibisce gli inibitori)                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional

# ============================================================
# GPU VERSION - FORCED PYTORCH
# ============================================================

import torch
BACKEND = "torch"

if torch.cuda.is_available():
    DEVICE = torch.device("cuda")
    print(f"[GPU] PyTorch + CUDA ({torch.cuda.get_device_name(0)})")
elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
    DEVICE = torch.device("mps")
    print("[GPU] PyTorch + Apple Metal")
else:
    DEVICE = torch.device("cpu")
    print("[GPU] PyTorch (CPU fallback - no CUDA)")


# ============================================================
# TIPI DI NEURONI
# ============================================================

class NeuronType(Enum):
    """
    Tipi di neuroni nella corteccia.
    
    Distribuzione reale:
        Eccitatori: 80%
            - PYRAMIDAL: 75% (neuroni di proiezione)
            - STELLATE: 5% (interneuroni eccitatori, Layer 4)
        
        Inibitori: 20%
            - PV: 10% (fast-spiking, inibizione perisomatica)
            - SST: 5% (regular-spiking, inibizione dendritica)
            - VIP: 5% (disinibizione)
    """
    # Eccitatori
    PYRAMIDAL = "pyramidal"
    STELLATE = "stellate"
    
    # Inibitori
    PV = "parvalbumin"
    SST = "somatostatin"  
    VIP = "vip"


@dataclass
class NeuronParameters:
    """
    Parametri elettrofisiologici per ogni tipo di neurone.
    Basati su dati sperimentali da patch-clamp recordings.
    """
    # Proprieta di membrana
    tau_m: float          # Costante di tempo membrana (ms)
    v_rest: float         # Potenziale di riposo (mV normalizzato a 0)
    v_thresh: float       # Soglia spike (mV normalizzato)
    v_reset: float        # Reset dopo spike (mV normalizzato)
    
    # Dinamica spike
    t_ref: float          # Periodo refrattario (ms)
    
    # Adattamento (spike-frequency adaptation)
    tau_w: float          # Costante tempo adattamento (ms)
    a: float              # Accoppiamento subthreshold
    b: float              # Incremento adattamento per spike
    
    # Proprieta sinaptica
    excitatory: bool      # True = glutammato, False = GABA
    
    # Firing pattern
    max_rate: float       # Rate massimo (Hz)


# Parametri biologicamente realistici per ogni tipo
NEURON_PARAMS: Dict[NeuronType, NeuronParameters] = {
    
    NeuronType.PYRAMIDAL: NeuronParameters(
        tau_m=20.0,           # Membrana lenta
        v_rest=0.0,
        v_thresh=1.0,
        v_reset=0.0,
        t_ref=2.0,            # 2ms refrattario
        tau_w=100.0,          # Adattamento lento
        a=0.0,
        b=0.05,               # Si adattano (riducono firing)
        excitatory=True,
        max_rate=50.0         # Max 50 Hz
    ),
    
    NeuronType.STELLATE: NeuronParameters(
        tau_m=15.0,           # Un po' piu veloce
        v_rest=0.0,
        v_thresh=0.9,
        v_reset=0.0,
        t_ref=1.5,
        tau_w=50.0,
        a=0.0,
        b=0.02,
        excitatory=True,
        max_rate=80.0
    ),
    
    NeuronType.PV: NeuronParameters(
        tau_m=10.0,           # VELOCE! (fast-spiking)
        v_rest=0.0,
        v_thresh=0.8,         # Soglia bassa
        v_reset=0.0,
        t_ref=0.5,            # Recupero rapidissimo
        tau_w=0.0,            # NO adattamento
        a=0.0,
        b=0.0,                # Possono sparare a raffica
        excitatory=False,
        max_rate=200.0        # Fino a 200 Hz!
    ),
    
    NeuronType.SST: NeuronParameters(
        tau_m=20.0,           # Lento
        v_rest=0.0,
        v_thresh=1.0,
        v_reset=0.0,
        t_ref=2.0,
        tau_w=50.0,
        a=0.02,               # Accoppiamento subthreshold
        b=0.03,               # Adattamento moderato
        excitatory=False,
        max_rate=40.0
    ),
    
    NeuronType.VIP: NeuronParameters(
        tau_m=15.0,           # Medio
        v_rest=0.0,
        v_thresh=0.9,
        v_reset=0.0,
        t_ref=1.5,
        tau_w=30.0,
        a=0.01,
        b=0.02,
        excitatory=False,
        max_rate=60.0
    ),
}


# ============================================================
# CLASSE NEURONI (Multi-backend)
# ============================================================

class NeuronGroup:
    """
    Gruppo di neuroni dello stesso tipo.
    
    Modello: Adaptive Exponential Integrate-and-Fire (AdEx) semplificato
    
    dv/dt = (-(v - v_rest) + R*I) / tau_m - w
    dw/dt = (a*(v - v_rest) - w) / tau_w
    
    Se v >= v_thresh:
        spike!
        v = v_reset
        w = w + b
    """
    
    def __init__(self, n: int, neuron_type: NeuronType, name: str = ""):
        self.n = n
        self.neuron_type = neuron_type
        self.name = name or neuron_type.value
        self.params = NEURON_PARAMS[neuron_type]
        
        # Inizializza stato in base al backend
        if BACKEND == "torch":
            self._init_torch()
        else:
            self._init_numpy()
    
    def _init_numpy(self):
        """Inizializza con NumPy."""
        self.v = np.zeros(self.n, dtype=np.float32)
        self.w = np.zeros(self.n, dtype=np.float32)  # Adattamento
        self.spike = np.zeros(self.n, dtype=bool)
        self.refractory = np.zeros(self.n, dtype=np.float32)
        self.spike_trace = np.zeros(self.n, dtype=np.float32)
        
        # Input separati per tipo
        self.I_exc = np.zeros(self.n, dtype=np.float32)  # Eccitatorio
        self.I_inh = np.zeros(self.n, dtype=np.float32)  # Inibitorio
        # Tonic input (NOT reset - for persistent neuromodulation)
        self.I_tonic = np.zeros(self.n, dtype=np.float32)
    
    def _init_torch(self):
        """Inizializza con PyTorch."""
        self.v = torch.zeros(self.n, dtype=torch.float32, device=DEVICE)
        self.w = torch.zeros(self.n, dtype=torch.float32, device=DEVICE)
        self.spike = torch.zeros(self.n, dtype=torch.bool, device=DEVICE)
        self.refractory = torch.zeros(self.n, dtype=torch.float32, device=DEVICE)
        self.spike_trace = torch.zeros(self.n, dtype=torch.float32, device=DEVICE)
        
        self.I_exc = torch.zeros(self.n, dtype=torch.float32, device=DEVICE)
        self.I_inh = torch.zeros(self.n, dtype=torch.float32, device=DEVICE)
        # Tonic input (NOT reset - for persistent neuromodulation)
        self.I_tonic = torch.zeros(self.n, dtype=torch.float32, device=DEVICE)
    
    def step(self, dt: float = 1.0):
        """
        Simula un timestep.
        
        Args:
            dt: Passo temporale in ms
            
        Returns:
            Array di spike (bool)
        """
        if BACKEND == "torch":
            return self._step_torch(dt)
        else:
            return self._step_numpy(dt)
    
    def _step_numpy(self, dt: float):
        """Step con NumPy."""
        p = self.params
        
        # Corrente totale (eccitazione - inibizione)
        I_total = self.I_exc + self.I_tonic - self.I_inh
        
        # Decrementa refrattario
        self.refractory = np.maximum(0, self.refractory - dt)
        
        # Maschera neuroni non refrattari
        active = self.refractory <= 0
        
        # Dinamica membrana (solo neuroni attivi)
        dv = (-(self.v - p.v_rest) + I_total - self.w) / p.tau_m
        self.v[active] += dv[active] * dt
        
        # Dinamica adattamento
        if p.tau_w > 0:
            dw = (p.a * (self.v - p.v_rest) - self.w) / p.tau_w
            self.w += dw * dt
        
        # Spike detection
        self.spike = (self.v >= p.v_thresh) & active
        
        # Reset neuroni che hanno sparato
        self.v[self.spike] = p.v_reset
        self.w[self.spike] += p.b
        self.refractory[self.spike] = p.t_ref
        
        # Aggiorna traccia STDP
        self.spike_trace *= 0.95
        self.spike_trace[self.spike] = 1.0
        
        # Reset input
        self.I_exc *= 0
        self.I_inh *= 0
        
        return self.spike.copy()
    
    def _step_torch(self, dt: float):
        """Step con PyTorch."""
        p = self.params
        
        I_total = self.I_exc + self.I_tonic - self.I_inh
        
        self.refractory = torch.clamp(self.refractory - dt, min=0)
        active = self.refractory <= 0
        
        dv = (-(self.v - p.v_rest) + I_total - self.w) / p.tau_m
        self.v = torch.where(active, self.v + dv * dt, self.v)
        
        if p.tau_w > 0:
            dw = (p.a * (self.v - p.v_rest) - self.w) / p.tau_w
            self.w = self.w + dw * dt
        
        self.spike = (self.v >= p.v_thresh) & active
        
        self.v = torch.where(self.spike, torch.tensor(p.v_reset, device=DEVICE, dtype=torch.float32), self.v)
        self.w = torch.where(self.spike, self.w + p.b, self.w)
        self.refractory = torch.where(self.spike, torch.tensor(p.t_ref, device=DEVICE, dtype=torch.float32), self.refractory)
        
        self.spike_trace = self.spike_trace * 0.95
        self.spike_trace = torch.where(self.spike, torch.ones_like(self.spike_trace), self.spike_trace)
        
        self.I_exc = self.I_exc * 0
        self.I_inh = self.I_inh * 0
        
        return self.spike.clone()
    
    def receive_input(self, source_spikes, weights, excitatory: bool = True):
        """
        Riceve input da un altro gruppo.
        
        Args:
            source_spikes: Spike del gruppo sorgente
            weights: Matrice pesi [n_source, n_target]
            excitatory: True se input eccitatorio
        """
        if BACKEND == "torch":
            current = torch.matmul(source_spikes.float(), weights)
        else:
            current = np.dot(source_spikes.astype(np.float32), weights)
        
        if excitatory:
            self.I_exc += current
        else:
            self.I_inh += current
    
    def inject_current(self, current, excitatory: bool = True):
        """Inietta corrente direttamente."""
        if excitatory:
            self.I_exc += current
        else:
            self.I_inh += current
    
    def reset(self):
        """Reset stato."""
        if BACKEND == "torch":
            self.v.zero_()
            self.w.zero_()
            self.spike.zero_()
            self.refractory.zero_()
            self.spike_trace.zero_()
            self.I_exc.zero_()
            self.I_inh.zero_()
        else:
            self.v.fill(0)
            self.w.fill(0)
            self.spike.fill(False)
            self.refractory.fill(0)
            self.spike_trace.fill(0)
            self.I_exc.fill(0)
            self.I_inh.fill(0)
    
    @property
    def is_excitatory(self) -> bool:
        """Questo gruppo e eccitatorio?"""
        return self.params.excitatory
    
    @property
    def is_inhibitory(self) -> bool:
        """Questo gruppo e inibitorio?"""
        return not self.params.excitatory
    
    def get_firing_rate(self, window: int = 100) -> float:
        """Stima firing rate medio."""
        if BACKEND == "torch":
            return self.spike.float().mean().item() * 1000 / window
        else:
            return self.spike.mean() * 1000 / window


# ============================================================
# FACTORY
# ============================================================

def create_neuron_group(n: int, neuron_type: NeuronType, name: str = "") -> NeuronGroup:
    """Crea un gruppo di neuroni."""
    return NeuronGroup(n, neuron_type, name)


def create_population(
    n_total: int,
    composition: Optional[Dict[NeuronType, float]] = None
) -> Dict[NeuronType, NeuronGroup]:
    """
    Crea una popolazione con la composizione specificata.
    
    Args:
        n_total: Numero totale di neuroni
        composition: Dizionario tipo -> percentuale (default: distribuzione corticale)
    
    Returns:
        Dizionario tipo -> NeuronGroup
    """
    if composition is None:
        # Distribuzione corticale realistica
        composition = {
            NeuronType.PYRAMIDAL: 0.75,
            NeuronType.STELLATE: 0.05,
            NeuronType.PV: 0.10,
            NeuronType.SST: 0.05,
            NeuronType.VIP: 0.05,
        }
    
    groups = {}
    for ntype, fraction in composition.items():
        n = max(1, int(n_total * fraction))
        groups[ntype] = NeuronGroup(n, ntype)
    
    return groups
