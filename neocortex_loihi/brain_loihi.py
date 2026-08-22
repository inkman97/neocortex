"""
╔══════════════════════════════════════════════════════════════════════╗
║           NEOCORTEX LOIHI - Main Brain Integration                   ║
║                                                                       ║
║  Integrates all components for drug trial simulation:                 ║
║  - 6 NT neuromodulation                                               ║
║  - Sparse spiking neurons (millions capable)                          ║
║  - Advanced plasticity (STDP, BCM, Scaling, STP)                     ║
║  - Embodiment (8 physiological parameters)                            ║
║  - Drug mechanisms                                                    ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import sys
from dataclasses import dataclass

from core import (
    NeuronType, create_neuron_population,
    SparseSynapseMatrix, create_cortical_connectivity, STDPConfig,
    NeuromodulationSystem, Neuromodulator,
    calculate_receptor_modulation, SCALE, float_to_fixed, fixed_to_float,
    LAVA_AVAILABLE
)
from embodiment.body_loihi import EmbodiedState

# HARDWARE SUPPORT - Import Loihi hardware initialization
try:
    from loihi_hardware_init import (
        LoihiHardwareMapper,
        LoihiHardwareExecutor,
        LoihiHardwareConfig,
        create_loihi_hardware_system,
        NXSDK_AVAILABLE
    )
except ImportError:
    NXSDK_AVAILABLE = False
    print("[BRAIN] Loihi hardware support not available (loihi_hardware_init.py missing)")


@dataclass
class BrainConfig:
    """Configuration for the brain."""
    n_neurons: int = 100000
    use_lava: bool = False  # True to use Lava simulation/hardware
    backend: str = "numpy"  # "numpy", "lava_sim", or "loihi"
    debug: bool = False


class NeoCortexLoihiBrain:
    """
    Main brain class integrating all components.
    
    Designed for scalability: 100k-10M+ neurons.
    """
    
    def __init__(self, config: BrainConfig):
        self.config = config
        self.timestep = 0
        
        if config.debug:
            print(f"\n[BRAIN] Initializing NeoCortex Loihi")
            print(f"  Neurons: {config.n_neurons:,}")
            print(f"  Backend: {config.backend}")
            print(f"  Lava available: {LAVA_AVAILABLE}")
        
        # Calculate neuron distribution by type
        self.neuron_counts = self._calculate_neuron_distribution(config.n_neurons)
        
        # Create neuron populations
        self.populations = {}
        offset = 0
        for ntype, count in self.neuron_counts.items():
            self.populations[ntype] = {
                'neurons': create_neuron_population(count, ntype, config.use_lava),
                'offset': offset,
                'count': count
            }
            offset += count
            if config.debug:
                print(f"  {ntype.value}: {count:,} neurons")
        
        # Create connectivity
        if config.debug:
            print("\n[BRAIN] Creating synaptic connectivity...")
        
        self.synapses = {}
        synapse_count = 0
        for pre_type in self.neuron_counts.keys():
            for post_type in self.neuron_counts.keys():
                key = (pre_type, post_type)
                n_pre = self.neuron_counts[pre_type]
                n_post = self.neuron_counts[post_type]
                
                conn = create_cortical_connectivity(n_pre, n_post, pre_type, post_type)
                self.synapses[key] = conn
                synapse_count += len(conn.weights)
        
        if config.debug:
            print(f"  Total synapses: {synapse_count:,}")
            print(f"  Memory: ~{synapse_count * 4 / 1024 / 1024:.1f} MB")
        
        # Neuromodulation system
        if config.debug:
            print("\n[BRAIN] Initializing 6 NT system...")
        
        self.neuromodulation = NeuromodulationSystem(
            n_total_neurons=config.n_neurons,
            use_lava=config.use_lava,
            debug=config.debug
        )
        
        # Embodiment
        self.body = EmbodiedState()
        
        # STDP configuration
        self.stdp_config = STDPConfig()
        
        # State tracking
        self.spike_history = []
        self.nt_history = []
        self.embodiment_history = []
        
        if config.debug:
            print("\n[BRAIN] [OK] Initialization complete\n")
    
    def _calculate_neuron_distribution(self, total: int) -> Dict[NeuronType, int]:
        """Calculate number of neurons per type."""
        return {
            NeuronType.PYRAMIDAL: int(total * 0.75),
            NeuronType.PV: int(total * 0.10),
            NeuronType.SST: int(total * 0.07),
            NeuronType.VIP: int(total * 0.05),
            NeuronType.STELLATE: int(total * 0.03),
        }
    
    def get_state(self) -> Dict:

    
        """

    
        Get current brain state compatible with DrugSimulator.

    
        """

    
        nt = self.neuromodulation.get_levels()

    
        embodied = self.embodiment

    
        total_spikes = sum(pop['neurons'].spike_count for pop in self.populations.values())

    
        total_neurons = sum(self.neuron_counts.values())

    
        firing_rate = total_spikes / total_neurons if total_neurons > 0 else 0.0

    
        

    
        return {

    
            'serotonin': float(nt.get(Neuromodulator.SEROTONIN, 0.5)),

    
            'dopamine': float(nt.get(Neuromodulator.DOPAMINE, 0.5)),

    
            'noradrenaline': float(nt.get(Neuromodulator.NORADRENALINE, 0.3)),

    
            'acetylcholine': float(nt.get(Neuromodulator.ACETYLCHOLINE, 0.4)),

    
            'gaba': float(nt.get(Neuromodulator.GABA, 0.6)),

    
            'glutamate': float(nt.get(Neuromodulator.GLUTAMATE, 0.5)),

    
            'arousal': float(embodied.arousal),

    
            'valence': float(embodied.valence),

    
            'dominant_emotion': str(embodied.emotion.value),

    
            'firing_rate': float(firing_rate),

    
            'heart_rate': float(embodied.heart_rate),

    
            'respiratory_rate': float(embodied.respiratory_rate),

    
            'skin_conductance': float(embodied.skin_conductance),

    
            'muscle_tension': float(embodied.muscle_tension),

    
            'gut_feeling': float(embodied.gut_feeling),

    
            'temperature': float(embodied.temperature),

    
            'pain': float(embodied.pain),

    
            'fatigue': float(embodied.fatigue),

    
        }


    
    def step(self, 
             external_input: Optional[np.ndarray] = None,
             reward: Optional[float] = None) -> Dict:
        """
        Single timestep simulation - HARDWARE-AWARE.
        
        Routes to hardware or software execution based on backend.
        
        Args:
            external_input: External input to neurons
            reward: Reward signal (for dopamine)
            
        Returns:
            State dictionary with spikes, NT levels, embodiment, etc.
        """
        self.timestep += 1
        
        # Route based on backend
        if self.config.backend == "loihi" and hasattr(self, 'loihi_executor'):
            # HARDWARE PATH
            return self._step_on_hardware(external_input, reward)
        else:
            # SOFTWARE PATH (NumPy or Lava)
            return self._step_in_software(external_input, reward)
    
    def _step_on_hardware(self,
                         external_input: Optional[np.ndarray],
                         reward: Optional[float]) -> Dict:
        """Execute timestep on PHYSICAL Loihi hardware."""
        
        # 1. Update neuromodulation (software)
        nt_levels = self.neuromodulation.step(reward=reward)
        nt_dict = {nt.value: level for nt, level in nt_levels.items()}
        
        # 2. Apply external input to hardware if provided
        if external_input is not None and hasattr(self, 'loihi_executor'):
            # Apply to excitatory neurons (pyramidal)
            pyr_pop = self.populations[NeuronType.PYRAMIDAL]
            pyr_offset = pyr_pop['offset']
            pyr_count = pyr_pop['count']
            pyr_input = external_input[pyr_offset:pyr_offset+pyr_count]
            
            self.loihi_executor.apply_external_input(
                population='pyramidal',
                input_currents=pyr_input
            )
        
        # 3. Execute one hardware timestep
        spikes_dict = self.loihi_executor.run_timestep()
        
        # 4. Reconstruct all_spikes array
        all_spikes = np.zeros(self.config.n_neurons, dtype=np.int8)
        for ntype, pop_data in self.populations.items():
            if ntype.value in spikes_dict:
                offset = pop_data['offset']
                count = pop_data['count']
                all_spikes[offset:offset+count] = spikes_dict[ntype.value][:count]
        
        # 5. Calculate psychological state
        arousal, valence, emotion = self._calculate_psychological_state(nt_dict, all_spikes)
        
        # 6. Update embodiment
        self.body.update(nt_dict, arousal, valence)
        
        # 7. Store history
        self.spike_history.append(all_spikes.sum())
        self.nt_history.append(nt_dict.copy())
        self.embodiment_history.append(self.body.to_dict())
        
        # 8. Return state
        return {
            'timestep': self.timestep,
            'spikes': all_spikes,
            'spike_count': all_spikes.sum(),
            'firing_rate': all_spikes.sum() / self.config.n_neurons,
            'nt_levels': nt_dict,
            'arousal': arousal,
            'valence': valence,
            'emotion': emotion,
            'embodiment': self.body.to_dict()
        }
    
    def _step_in_software(self,
                         external_input: Optional[np.ndarray],
                         reward: Optional[float]) -> Dict:
        """Execute timestep in SOFTWARE (NumPy or Lava)."""
        self.timestep += 1
        
        # Update neuromodulation
        nt_levels = self.neuromodulation.step(reward=reward)
        
        # Calculate receptor modulation for each population
        modulation_currents = {}
        nt_dict = {nt.value: level for nt, level in nt_levels.items()}
        
        for ntype, pop_data in self.populations.items():
            mod_current = calculate_receptor_modulation(ntype, nt_dict)
            mod_array = np.full(pop_data['count'], mod_current, dtype=np.int16)
            modulation_currents[ntype] = mod_array
        
        # Collect all spikes
        all_spikes = np.zeros(self.config.n_neurons, dtype=np.int8)
        
        # Update each population
        for ntype, pop_data in self.populations.items():
            neurons = pop_data['neurons']
            offset = pop_data['offset']
            count = pop_data['count']
            
            # Prepare input
            total_input = modulation_currents[ntype].copy()
            
            if external_input is not None:
                ext_slice = external_input[offset:offset+count]
                total_input += ext_slice.astype(np.int16)
            
            # Step neurons
            if hasattr(neurons, 'step'):  # Numpy neurons
                spikes = neurons.step(total_input)
            else:  # Lava neurons (would need network execution)
                spikes = np.zeros(count, dtype=np.int8)
            
            all_spikes[offset:offset+count] = spikes
        
        # Synaptic transmission
        post_currents = {}
        for (pre_type, post_type), synapse_matrix in self.synapses.items():
            pre_pop = self.populations[pre_type]
            post_pop = self.populations[post_type]
            
            pre_spikes = all_spikes[pre_pop['offset']:pre_pop['offset']+pre_pop['count']]
            post_current = synapse_matrix.transmit(pre_spikes)
            
            if post_type not in post_currents:
                post_currents[post_type] = np.zeros(post_pop['count'], dtype=np.int16)
            post_currents[post_type] += post_current
        
        # Apply STDP
        dopamine = nt_levels[Neuromodulator.DOPAMINE]
        for (pre_type, post_type), synapse_matrix in self.synapses.items():
            pre_pop = self.populations[pre_type]
            post_pop = self.populations[post_type]
            
            pre_spikes = all_spikes[pre_pop['offset']:pre_pop['offset']+pre_pop['count']]
            post_spikes = all_spikes[post_pop['offset']:post_pop['offset']+post_pop['count']]
            
            synapse_matrix.apply_stdp(pre_spikes, post_spikes, 
                                     self.stdp_config, dopamine=dopamine)
        
        # Calculate psychological state
        arousal, valence, emotion = self._calculate_psychological_state(nt_dict, all_spikes)
        
        # Update embodiment
        self.body.update(nt_dict, arousal, valence)
        
        # Store history
        self.spike_history.append(all_spikes.sum())
        self.nt_history.append(nt_dict.copy())
        self.embodiment_history.append(self.body.to_dict())
        
        # Return state
        return {
            'timestep': self.timestep,
            'spikes': all_spikes,
            'spike_count': all_spikes.sum(),
            'firing_rate': all_spikes.sum() / self.config.n_neurons,
            'nt_levels': nt_dict,
            'arousal': arousal,
            'valence': valence,
            'emotion': emotion,
            'embodiment': self.body.to_dict()
        }
    
    def _calculate_psychological_state(self, nt_dict: Dict, spikes: np.ndarray) -> Tuple[float, float, str]:
        """Calculate arousal, valence, and dominant emotion."""
        # Arousal: NE + DA
        arousal = 0.6 * nt_dict.get('NE', 0.45) + 0.4 * nt_dict.get('DA', 0.4)
        arousal = np.clip(arousal, 0, 1)
        
        # Valence: DA + 5HT - (low 5HT penalty)
        valence = 0.5 * nt_dict.get('DA', 0.4) + 0.3 * nt_dict.get('5HT', 0.5)
        valence -= 0.2 * max(0, 0.4 - nt_dict.get('5HT', 0.5))  # Low 5HT = negative
        valence = np.clip(valence * 2 - 1, -1, 1)  # Scale to -1 to +1
        
        # Dominant emotion
        if arousal > 0.6:
            emotion = "excited" if valence > 0.2 else "anxious"
        elif arousal < 0.4:
            emotion = "calm" if valence > 0 else "depressed"
        else:
            emotion = "content" if valence > 0 else "sad"
        
        return arousal, valence, emotion
    
    def get_firing_rate(self, window_ms: int = 100) -> float:
        """Get recent average firing rate."""
        if len(self.spike_history) < window_ms:
            window_ms = len(self.spike_history)
        if window_ms == 0:
            return 0.0
        recent = self.spike_history[-window_ms:]
        return np.mean(recent) / self.config.n_neurons
    
    def apply_drug(self, drug_targets: Dict[str, float]):
        """Apply drug to neuromodulation system."""
        self.neuromodulation.apply_drug(drug_targets)
    
    def get_summary(self) -> Dict:
        """Get current brain state summary."""
        if len(self.nt_history) == 0:
            return {}
        
        latest_nt = self.nt_history[-1]
        latest_body = self.embodiment_history[-1]
        
        return {
            'timestep': self.timestep,
            'firing_rate': self.get_firing_rate(),
            'nt_levels': latest_nt,
            'embodiment': latest_body,
            'total_spikes': sum(self.spike_history)
        }


# ═══════════════════════════════════════════════════════════════════
# HARDWARE BRAIN CREATION
# ═══════════════════════════════════════════════════════════════════

def create_brain_on_loihi_hardware(
    n_neurons: int = 100000,
    debug: bool = True
):
    """
    Create NeoCortex brain mapped to PHYSICAL Loihi hardware.
    
    CRITICAL: Requires NxSDK and physical Loihi board access.
    
    Args:
        n_neurons: Total neurons to simulate
        debug: Enable debug output
        
    Returns:
        NeoCortexLoihiBrain configured for hardware execution
    """
    if not NXSDK_AVAILABLE:
        raise RuntimeError(
            "NxSDK not available! Install: pip install nxsdk\n"
            "Requires Intel INRC membership."
        )
    
    print("="*70)
    print("NEOCORTEX - LOIHI HARDWARE INITIALIZATION")
    print("="*70)
    
    # Initialize hardware
    mapper, board = create_loihi_hardware_system(n_neurons)
    
    # Create brain config
    config = BrainConfig(
        n_neurons=n_neurons,
        use_lava=False,
        backend="loihi",
        debug=debug
    )
    
    # Create brain
    brain = NeoCortexLoihiBrain(config)
    
    # Attach hardware
    brain.loihi_mapper = mapper
    brain.loihi_board = board
    
    # Map neurons to hardware
    print("\n[BRAIN-HW] Mapping populations to hardware...")
    _map_brain_to_hardware(brain, mapper)
    
    # Create executor
    brain.loihi_executor = LoihiHardwareExecutor(
        board=board,
        mappings=mapper.neuron_mappings
    )
    
    # Summary
    summary = mapper.get_mapping_summary()
    print(f"\n[BRAIN-HW] Complete:")
    print(f"  Neurons: {summary['total_neurons_mapped']:,}")
    print(f"  Chips: {summary['chips_used']}")
    print(f"  Cores: {summary['cores_used']}")
    print("\n" + "="*70)
    print("[OK] HARDWARE READY")
    print("="*70 + "\n")
    
    return brain


def _map_brain_to_hardware(brain, mapper):
    """Map neuron populations to hardware."""
    for ntype, pop_data in brain.populations.items():
        neurons = pop_data['neurons']
        n_neurons = pop_data['count']
        
        neuron_params = {
            'threshold': getattr(neurons, 'threshold', 100),
            'voltage_decay': 4096,
            'current_decay': 2048,
        }
        
        mappings = mapper.map_neuron_population(
            population_name=ntype.value,
            n_neurons=n_neurons,
            neuron_params=neuron_params
        )
        
        neurons.hardware_mappings = mappings


# Factory function for easy creation
def create_brain(n_neurons: int = 100000,
                backend: str = "numpy",
                debug: bool = False) -> NeoCortexLoihiBrain:
    """
    Create a NeoCortex Loihi brain - HARDWARE-AWARE.
    
    Args:
        n_neurons: Number of neurons (100k-10M+)
        backend: "numpy", "lava_sim", or "loihi"
        debug: Print debug info
        
    Returns:
        Brain instance
    """
    # Route to hardware if requested
    if backend == "loihi":
        try:
            return create_brain_on_loihi_hardware(n_neurons, debug)
        except RuntimeError as e:
            print(f"[BRAIN] Hardware unavailable: {e}")
            print("[BRAIN] Falling back to NumPy")
            backend = "numpy"
    
    # Lava or NumPy
    use_lava = backend == "lava_sim"
    
    if use_lava and not LAVA_AVAILABLE:
        print("[WARNING] Lava not available, using NumPy")
        backend = "numpy"
        use_lava = False
    
    config = BrainConfig(
        n_neurons=n_neurons,
        use_lava=use_lava,
        backend=backend,
        debug=debug
    )
    
    return NeoCortexLoihiBrain(config)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("NEOCORTEX LOIHI - Main Brain Test")
    print("="*70)
    
    # Create small brain for testing
    brain = create_brain(n_neurons=10000, backend="numpy", debug=True)
    
    # Run for 100 steps
    print("\n[TEST] Running simulation...")
    for t in range(100):
        state = brain.step(reward=0.5 if t % 50 == 0 else None)
        
        if t % 20 == 0:
            print(f"\nt={t:3d}:")
            print(f"  Spikes: {state['spike_count']}")
            print(f"  Firing rate: {state['firing_rate']:.4f}")
            print(f"  5HT: {state['nt_levels']['5HT']:.3f}")
            print(f"  DA: {state['nt_levels']['DA']:.3f}")
            print(f"  Arousal: {state['arousal']:.3f}")
            print(f"  Valence: {state['valence']:.3f}")
            print(f"  Emotion: {state['emotion']}")
            print(f"  Heart rate: {state['embodiment']['heart_rate']:.3f}")
    
    # Test drug application
    print("\n[TEST] Applying SSRI (SERT inhibition)...")
    brain.apply_drug({'SERT': 0.8})
    
    for t in range(50):
        state = brain.step()
        if t % 10 == 0:
            print(f"t={t:3d}: 5HT={state['nt_levels']['5HT']:.3f}, "
                  f"Valence={state['valence']:.3f}")
    
    print("\n" + "="*70)
    print("[OK] TEST COMPLETE")
    print("="*70)
