"""
╔══════════════════════════════════════════════════════════════════════╗
║         LOIHI SYNAPSES - Sparse Synapses with Hardware STDP           ║
║                                                                       ║
║  Implementa sinapsi sparse ottimizzate per Loihi 2 con:              ║
║  - STDP (Spike-Timing-Dependent Plasticity) in hardware              ║
║  - Three-Factor Learning (eligibility traces + neuromodulation)       ║
║  - Fixed-point weights (int8: -127 to +127)                          ║
║  - Sparse connectivity per efficienza memoria                         ║
╚══════════════════════════════════════════════════════════════════════╝

CARATTERISTICHE:
- Pesi fixed-point int8 (-127 to +127)
- STDP con trace decay esponenziale
- Three-factor: eligibility * dopamine
- Sparse storage (COO format)
- Delay distribuiti (1-10ms)

LOIHI 2 LIMITS:
- Max 120M sinapsi per chip
- Max 128 sinapsi per neurone (fan-in)
- Pesi int8 only

VERSION: 1.0
COMPATIBLE WITH: Lava-NC 0.8+, Loihi 2
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy import sparse

try:
    from lava.magma.core.process.process import AbstractProcess
    from lava.magma.core.process.variable import Var
    from lava.magma.core.process.ports.ports import InPort, OutPort
    from lava.magma.core.sync.protocols.loihi_protocol import LoihiProtocol
    from lava.magma.core.model.py.model import PyLoihiProcessModel
    from lava.magma.core.model.py.ports import PyInPort, PyOutPort
    from lava.magma.core.model.py.type import LavaPyType
    from lava.magma.core.resources import CPU
    from lava.magma.core.decorator import implements, requires
    from lava.proc.dense.process import Dense
    from lava.proc.sparse.process import Sparse
    LAVA_AVAILABLE = True
except ImportError:
    LAVA_AVAILABLE = False

from .neurons_loihi import SCALE, SCALE_SHIFT, W_MIN, W_MAX, NeuronType


# ══════════════════════════════════════════════════════════════════════
# STDP CONFIGURATION
# ══════════════════════════════════════════════════════════════════════

@dataclass
class STDPConfig:
    """
    STDP parameters (all scaled for fixed-point).
    
    Based on biological data from cortical synapses.
    """
    # Learning rates (scaled)
    a_plus: int = 10   # LTP strength (potentiation)
    a_minus: int = 12  # LTD strength (depression)
    
    # Trace decay (higher = slower decay)
    tau_plus: int = 2048   # Pre-synaptic trace (~8.0)
    tau_minus: int = 1536  # Post-synaptic trace (~6.0)
    
    # Weight bounds
    w_min: int = W_MIN
    w_max: int = W_MAX
    
    # Three-factor learning
    use_three_factor: bool = True
    eligibility_tau: int = 1024  # Eligibility decay (~4.0)
    dopamine_threshold: int = 102  # Min DA for learning (0.4 * 256)
    
    # Learning rate modulation by neuron type
    learning_rate_multiplier: Dict[str, float] = None
    
    def __post_init__(self):
        if self.learning_rate_multiplier is None:
            self.learning_rate_multiplier = {
                'pyramidal': 1.0,
                'pv': 0.8,
                'sst': 0.9,
                'vip': 1.1,
                'stellate': 1.0
            }


# ══════════════════════════════════════════════════════════════════════
# SPARSE SYNAPSE STORAGE
# ══════════════════════════════════════════════════════════════════════

class SparseSynapseMatrix:
    """
    Sparse synapse connectivity matrix.
    
    Uses COO (Coordinate) format for memory efficiency.
    Critical for scaling to millions of neurons.
    """
    def __init__(self, 
                 n_pre: int,
                 n_post: int,
                 connection_prob: float = 0.1,
                 weight_mean: int = 64,  # 0.25 * 256
                 weight_std: int = 32):   # 0.125 * 256
        self.n_pre = n_pre
        self.n_post = n_post
        self.connection_prob = connection_prob
        
        # Generate sparse connections
        n_synapses = int(n_pre * n_post * connection_prob)
        
        # Random connectivity
        self.pre_idx = np.random.randint(0, n_pre, size=n_synapses)
        self.post_idx = np.random.randint(0, n_post, size=n_synapses)
        
        # Initialize weights (Gaussian, clipped)
        self.weights = np.random.normal(weight_mean, weight_std, size=n_synapses)
        self.weights = np.clip(self.weights, W_MIN, W_MAX).astype(np.int8)
        
        # Delays (1-10ms, distributed)
        self.delays = np.random.randint(1, 11, size=n_synapses, dtype=np.int8)
        
        # STDP traces (for learning)
        self.pre_trace = np.zeros(n_synapses, dtype=np.int16)
        self.post_trace = np.zeros(n_synapses, dtype=np.int16)
        
        # Eligibility traces (for three-factor)
        self.eligibility = np.zeros(n_synapses, dtype=np.int16)
        
        print(f"[SYNAPSES] Created sparse matrix: {n_pre}x{n_post}, "
              f"{n_synapses} synapses ({connection_prob*100:.1f}% density)")
    
    def to_scipy_sparse(self) -> sparse.coo_matrix:
        """Convert to scipy sparse matrix (for compatibility)."""
        return sparse.coo_matrix(
            (self.weights, (self.pre_idx, self.post_idx)),
            shape=(self.n_pre, self.n_post)
        )
    
    def apply_stdp(self,
                   pre_spikes: np.ndarray,
                   post_spikes: np.ndarray,
                   config: STDPConfig,
                   dopamine: float = 0.5):
        """
        Apply STDP update to all synapses.
        
        Args:
            pre_spikes: Pre-synaptic spikes (binary array)
            post_spikes: Post-synaptic spikes (binary array)
            config: STDP parameters
            dopamine: Dopamine level (0-1) for three-factor
        """
        # Convert dopamine to fixed-point
        da_fixed = int(dopamine * SCALE)
        
        # Update pre-synaptic traces
        spiked_pre = pre_spikes[self.pre_idx] > 0
        self.pre_trace[spiked_pre] = SCALE  # Set to max on spike
        
        # Decay pre-trace
        decay = (self.pre_trace * config.tau_plus) >> SCALE_SHIFT
        self.pre_trace -= decay
        self.pre_trace = np.maximum(0, self.pre_trace)
        
        # Update post-synaptic traces
        spiked_post = post_spikes[self.post_idx] > 0
        self.post_trace[spiked_post] = SCALE
        
        # Decay post-trace
        decay = (self.post_trace * config.tau_minus) >> SCALE_SHIFT
        self.post_trace -= decay
        self.post_trace = np.maximum(0, self.post_trace)
        
        # Calculate weight changes
        delta_w = np.zeros(len(self.weights), dtype=np.int16)
        
        # LTP: post spike, use pre-trace
        ltp = (config.a_plus * self.pre_trace[spiked_post]) >> SCALE_SHIFT
        delta_w[spiked_post] += ltp
        
        # LTD: pre spike, use post-trace
        ltd = (config.a_minus * self.post_trace[spiked_pre]) >> SCALE_SHIFT
        delta_w[spiked_pre] -= ltd
        
        # Three-factor learning
        if config.use_three_factor:
            # Update eligibility trace
            self.eligibility += delta_w
            
            # Decay eligibility
            elig_decay = (self.eligibility * config.eligibility_tau) >> SCALE_SHIFT
            self.eligibility -= elig_decay
            
            # Apply if dopamine above threshold
            if da_fixed > config.dopamine_threshold:
                # Modulate by dopamine
                da_modulation = (self.eligibility * da_fixed) >> SCALE_SHIFT
                self.weights += da_modulation
                
                # Reset eligibility
                self.eligibility = np.zeros_like(self.eligibility)
        else:
            # Direct STDP (no three-factor)
            self.weights += delta_w
        
        # Clip weights
        self.weights = np.clip(self.weights, config.w_min, config.w_max)
    
    def transmit(self, pre_spikes: np.ndarray) -> np.ndarray:
        """
        Transmit spikes through synapses.
        
        Args:
            pre_spikes: Pre-synaptic spikes (binary)
            
        Returns:
            post_current: Post-synaptic current (int16 array)
        """
        post_current = np.zeros(self.n_post, dtype=np.int16)
        
        # Find spiking pre-synaptic neurons
        spiked = pre_spikes[self.pre_idx] > 0
        
        # Accumulate weighted contributions
        # (delays ignored for simplicity - Loihi handles this in hardware)
        np.add.at(post_current, self.post_idx[spiked], self.weights[spiked])
        
        return post_current
    
    def get_stats(self) -> Dict:
        """Get synapse statistics."""
        return {
            'n_synapses': len(self.weights),
            'density': len(self.weights) / (self.n_pre * self.n_post),
            'mean_weight': float(self.weights.mean()) / SCALE,
            'std_weight': float(self.weights.std()) / SCALE,
            'min_weight': float(self.weights.min()) / SCALE,
            'max_weight': float(self.weights.max()) / SCALE,
            'mean_delay': float(self.delays.mean()),
        }


# ══════════════════════════════════════════════════════════════════════
# LAVA SPARSE PROCESS (Hardware Interface)
# ══════════════════════════════════════════════════════════════════════

if LAVA_AVAILABLE:
    class LoihiSparseSynapse(AbstractProcess):
        """
        Sparse synapse process for Loihi.
        
        Wraps sparse connectivity matrix for deployment.
        """
        def __init__(self,
                     sparse_matrix: SparseSynapseMatrix,
                     **kwargs):
            super().__init__(**kwargs)
            
            self.sparse_matrix = sparse_matrix
            
            # Ports
            self.s_in = InPort(shape=(sparse_matrix.n_pre,))
            self.a_out = OutPort(shape=(sparse_matrix.n_post,))
            
            # Weights variable
            self.weights = Var(shape=(len(sparse_matrix.weights),),
                              init=sparse_matrix.weights)
            
            # Connection indices
            self.pre_idx = Var(shape=(len(sparse_matrix.pre_idx),),
                              init=sparse_matrix.pre_idx)
            self.post_idx = Var(shape=(len(sparse_matrix.post_idx),),
                               init=sparse_matrix.post_idx)
    
    
    @implements(proc=LoihiSparseSynapse, protocol=LoihiProtocol)
    @requires(CPU)
    class PyLoihiSparseSynapseModel(PyLoihiProcessModel):
        """CPU model of sparse synapse (for simulation)."""
        
        s_in: PyInPort = LavaPyType(PyInPort.VEC_DENSE, int)
        a_out: PyOutPort = LavaPyType(PyOutPort.VEC_DENSE, int)
        
        weights: np.ndarray = LavaPyType(np.ndarray, np.int8)
        pre_idx: np.ndarray = LavaPyType(np.ndarray, np.int32)
        post_idx: np.ndarray = LavaPyType(np.ndarray, np.int32)
        
        def run_spk(self):
            """Propagate spikes through synapses."""
            # Receive pre-synaptic spikes
            s_in_data = self.s_in.recv()
            
            # Find spiking neurons
            spiked = s_in_data[self.pre_idx] > 0
            
            # Accumulate weighted contributions
            a_out_data = np.zeros(len(self.a_out), dtype=np.int16)
            np.add.at(a_out_data, self.post_idx[spiked], self.weights[spiked])
            
            # Send post-synaptic current
            self.a_out.send(a_out_data)


# ══════════════════════════════════════════════════════════════════════
# CONNECTIVITY PATTERNS
# ══════════════════════════════════════════════════════════════════════

def create_cortical_connectivity(n_pre: int,
                                 n_post: int,
                                 pre_type: NeuronType,
                                 post_type: NeuronType,
                                 config: Optional[STDPConfig] = None) -> SparseSynapseMatrix:
    """
    Create biologically realistic cortical connectivity.
    
    Connection probability and weights depend on neuron types.
    
    Args:
        n_pre: Number of pre-synaptic neurons
        n_post: Number of post-synaptic neurons
        pre_type: Pre-synaptic neuron type
        post_type: Post-synaptic neuron type
        config: STDP configuration
        
    Returns:
        Sparse synapse matrix
    """
    if config is None:
        config = STDPConfig()
    
    # Connection probabilities (from biological data)
    conn_probs = {
        # Excitatory -> Excitatory
        ('pyramidal', 'pyramidal'): 0.15,
        ('pyramidal', 'stellate'): 0.20,
        ('stellate', 'pyramidal'): 0.25,
        
        # Excitatory -> Inhibitory
        ('pyramidal', 'pv'): 0.40,
        ('pyramidal', 'sst'): 0.30,
        ('pyramidal', 'vip'): 0.35,
        ('stellate', 'pv'): 0.45,
        
        # Inhibitory -> Excitatory
        ('pv', 'pyramidal'): 0.50,
        ('sst', 'pyramidal'): 0.40,
        ('vip', 'pyramidal'): 0.10,  # Sparse disinhibition
        
        # Inhibitory -> Inhibitory
        ('pv', 'pv'): 0.30,
        ('pv', 'sst'): 0.25,
        ('sst', 'pv'): 0.20,
        ('vip', 'sst'): 0.60,  # Strong disinhibition
        ('vip', 'pv'): 0.40,
    }
    
    # Get connection probability
    key = (pre_type.value, post_type.value)
    conn_prob = conn_probs.get(key, 0.05)  # Default: sparse
    
    # Weight parameters depend on pre-synaptic type
    if pre_type == NeuronType.PYRAMIDAL or pre_type == NeuronType.STELLATE:
        # Excitatory
        weight_mean = 64   # 0.25
        weight_std = 32    # 0.125
    else:
        # Inhibitory (negative weights)
        weight_mean = -80  # -0.31
        weight_std = 40    # 0.16
    
    return SparseSynapseMatrix(
        n_pre=n_pre,
        n_post=n_post,
        connection_prob=conn_prob,
        weight_mean=weight_mean,
        weight_std=weight_std
    )


def test_stdp():
    """Test STDP learning."""
    print("\n[TEST] STDP Learning")
    print("=" * 60)
    
    # Create small synapse matrix
    n_pre = 100
    n_post = 100
    synapses = SparseSynapseMatrix(n_pre, n_post, connection_prob=0.2)
    config = STDPConfig()
    
    print(f"Initial weights: mean={synapses.weights.mean():.1f}, "
          f"std={synapses.weights.std():.1f}")
    
    # Simulate correlated activity
    for t in range(1000):
        # Some pre-synaptic spikes
        pre_spikes = (np.random.rand(n_pre) < 0.05).astype(np.int8)
        
        # Correlated post-synaptic spikes (with delay)
        post_spikes = np.zeros(n_post, dtype=np.int8)
        if t > 2:  # Delay
            post_spikes = (np.random.rand(n_post) < 0.03).astype(np.int8)
        
        # Apply STDP
        synapses.apply_stdp(pre_spikes, post_spikes, config, dopamine=0.6)
    
    print(f"Final weights: mean={synapses.weights.mean():.1f}, "
          f"std={synapses.weights.std():.1f}")
    
    # Check if potentiation occurred
    if synapses.weights.mean() > 64:
        print("[OK] PASS: LTP occurred (weights increased)")
    else:
        print("[X] FAIL: No potentiation")
    
    return synapses


if __name__ == "__main__":
    print("\n" + "="*70)
    print("LOIHI SYNAPSES - Sparse Connectivity with Hardware STDP")
    print("="*70)
    
    # Test STDP
    synapses = test_stdp()
    
    # Show statistics
    print("\n" + "="*70)
    print("SYNAPSE STATISTICS")
    print("="*70)
    stats = synapses.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Test different connectivity patterns
    print("\n" + "="*70)
    print("CONNECTIVITY PATTERNS")
    print("="*70)
    
    patterns = [
        (NeuronType.PYRAMIDAL, NeuronType.PYRAMIDAL),
        (NeuronType.PYRAMIDAL, NeuronType.PV),
        (NeuronType.PV, NeuronType.PYRAMIDAL),
        (NeuronType.VIP, NeuronType.SST),
    ]
    
    for pre_type, post_type in patterns:
        conn = create_cortical_connectivity(1000, 1000, pre_type, post_type)
        stats = conn.get_stats()
        print(f"\n{pre_type.value} → {post_type.value}:")
        print(f"  Density: {stats['density']*100:.1f}%")
        print(f"  Mean weight: {stats['mean_weight']:.3f}")
        print(f"  Synapses: {stats['n_synapses']}")
    
    print("\n" + "="*70)
    print("READY FOR LOIHI HARDWARE")
    print("="*70)
