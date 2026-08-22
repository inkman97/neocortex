"""
╔═══════════════════════════════════════════════════════════════════╗
║              LOIHI HARDWARE INITIALIZATION MODULE                  ║
║                                                                    ║
║  Complete hardware mapping for Intel Loihi neuromorphic chips     ║
║  - Physical board initialization                                  ║
║  - Neuron-to-core mapping                                         ║
║  - Hardware execution path                                        ║
║                                                                    ║
║  REQUIRES: Intel NxSDK + Physical Loihi board access             ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Try to import NxSDK
try:
    import nxsdk
    from nxsdk.graph.processes.phase_enums import Phase
    NXSDK_AVAILABLE = True
    print("[LOIHI-HW] NxSDK available - hardware support enabled")
except ImportError:
    NXSDK_AVAILABLE = False
    nxsdk = None
    print("[LOIHI-HW] NxSDK not available - using NumPy simulation")


@dataclass
class LoihiHardwareConfig:
    """Configuration for Loihi hardware deployment."""
    neurons_per_core: int = 1000  # Max neurons per core
    cores_per_chip: int = 128     # Loihi 1: 128 cores/chip
    chips_available: int = 1      # Number of chips in your system
    voltage_threshold: int = 100  # mV, firing threshold
    bias_exponent: int = 6        # Current bias exponent
    voltage_decay: int = 4096     # Voltage decay (tau_v)
    current_decay: int = 2048     # Current decay (tau_i)
    refractory_period: int = 2    # Timesteps


class LoihiHardwareMapper:
    """
    Maps NeoCortex brain to physical Loihi hardware.
    
    Critical: This class handles the neuron → core → chip mapping
    that makes the brain actually run on silicon.
    """
    
    def __init__(self, config: LoihiHardwareConfig):
        self.config = config
        self.board = None
        self.neuron_mappings = {}
        self.current_chip = 0
        self.current_core = 0
        self.neurons_in_current_core = 0
        
    def initialize_board(self) -> Optional[object]:
        """Initialize physical Loihi board."""
        if not NXSDK_AVAILABLE:
            raise RuntimeError(
                "NxSDK not available! Install with: pip install nxsdk\n"
                "Requires Intel INRC membership."
            )
        
        print("[LOIHI-HW] Connecting to physical Loihi board...")
        
        try:
            self.board = nxsdk.Board()
            n_chips = self.board.numChips
            n_cores_per_chip = self.board.numCoresPerChip
            
            print(f"[LOIHI-HW] [OK] Connected to board")
            print(f"[LOIHI-HW]   Chips: {n_chips}")
            print(f"[LOIHI-HW]   Cores per chip: {n_cores_per_chip}")
            
            self.config.chips_available = n_chips
            return self.board
            
        except Exception as e:
            print(f"[LOIHI-HW] [X] Failed to connect: {e}")
            raise
    
    def calculate_resource_requirements(self, n_neurons: int) -> Dict:
        """Calculate cores/chips needed."""
        cores_needed = int(np.ceil(n_neurons / self.config.neurons_per_core))
        chips_needed = int(np.ceil(cores_needed / self.config.cores_per_chip))
        
        return {
            'neurons': n_neurons,
            'cores_needed': cores_needed,
            'chips_needed': chips_needed,
        }
    
    def check_hardware_capacity(self, n_neurons: int) -> bool:
        """Check if hardware has enough capacity."""
        reqs = self.calculate_resource_requirements(n_neurons)
        
        if reqs['chips_needed'] > self.config.chips_available:
            print(f"[LOIHI-HW] [X] Insufficient hardware!")
            print(f"[LOIHI-HW]   Need: {reqs['chips_needed']} chips")
            print(f"[LOIHI-HW]   Have: {self.config.chips_available} chips")
            return False
        
        print(f"[LOIHI-HW] [OK] Hardware capacity OK")
        print(f"[LOIHI-HW]   Neurons: {n_neurons:,}")
        print(f"[LOIHI-HW]   Cores: {reqs['cores_needed']}")
        print(f"[LOIHI-HW]   Chips: {reqs['chips_needed']}")
        
        return True
    
    def map_neuron_population(
        self,
        population_name: str,
        n_neurons: int,
        neuron_params: Dict
    ) -> List[Dict]:
        """Map neuron population to Loihi cores."""
        print(f"[LOIHI-HW] Mapping '{population_name}': {n_neurons:,} neurons")
        
        mappings = []
        neurons_mapped = 0
        
        while neurons_mapped < n_neurons:
            space_in_core = self.config.neurons_per_core - self.neurons_in_current_core
            neurons_in_this_allocation = min(
                space_in_core,
                n_neurons - neurons_mapped
            )
            
            chip = self.board.n2Chips[self.current_chip]
            core = chip.n2Cores[self.current_core]
            
            start_idx = self.neurons_in_current_core
            end_idx = start_idx + neurons_in_this_allocation
            compartments = core.cxCfg[start_idx:end_idx]
            
            compartments.configure(
                vth=neuron_params.get('threshold', self.config.voltage_threshold),
                biasExp=self.config.bias_exponent,
                vMinExp=0,
                numDendriticAccumulators=8,
            )
            
            compartments.decayV = neuron_params.get('voltage_decay', self.config.voltage_decay)
            compartments.decayU = neuron_params.get('current_decay', self.config.current_decay)
            compartments.refractDelay = self.config.refractory_period
            
            mapping = {
                'chip_id': self.current_chip,
                'core_id': self.current_core,
                'compartment_start': start_idx,
                'compartment_end': end_idx,
                'n_neurons': neurons_in_this_allocation,
                'compartments': compartments,
            }
            mappings.append(mapping)
            
            neurons_mapped += neurons_in_this_allocation
            self.neurons_in_current_core += neurons_in_this_allocation
            
            if self.neurons_in_current_core >= self.config.neurons_per_core:
                self._advance_to_next_core()
        
        self.neuron_mappings[population_name] = mappings
        print(f"[LOIHI-HW]   [OK] Mapped to {len(mappings)} core(s)")
        
        return mappings
    
    def _advance_to_next_core(self):
        """Move to next core."""
        self.neurons_in_current_core = 0
        self.current_core += 1
        
        if self.current_core >= self.config.cores_per_chip:
            self.current_core = 0
            self.current_chip += 1
            
            if self.current_chip >= self.config.chips_available:
                raise RuntimeError("Ran out of hardware!")
    
    def get_mapping_summary(self) -> Dict:
        """Get mapping summary."""
        total_neurons = sum(
            sum(m['n_neurons'] for m in mappings)
            for mappings in self.neuron_mappings.values()
        )
        
        total_cores_used = self.current_core + (self.current_chip * self.config.cores_per_chip)
        if self.neurons_in_current_core > 0:
            total_cores_used += 1
        
        return {
            'total_neurons_mapped': total_neurons,
            'populations': len(self.neuron_mappings),
            'chips_used': self.current_chip + 1,
            'cores_used': total_cores_used,
        }


class LoihiHardwareExecutor:
    """Execute brain simulation on physical Loihi hardware."""
    
    def __init__(self, board, mappings: Dict):
        self.board = board
        self.mappings = mappings
        self.timestep = 0
        
    def run_timestep(self) -> Dict[str, np.ndarray]:
        """Execute one timestep on hardware."""
        self.board.run(steps=1, aSync=False)
        
        spikes = {}
        for pop_name, mappings_list in self.mappings.items():
            pop_spikes = []
            for mapping in mappings_list:
                compartments = mapping['compartments']
                spike_data = compartments.spikes
                pop_spikes.extend(spike_data)
            spikes[pop_name] = np.array(pop_spikes, dtype=bool)
        
        self.timestep += 1
        return spikes
    
    def apply_external_input(self, population: str, input_currents: np.ndarray):
        """Apply external input currents."""
        mappings_list = self.mappings[population]
        
        input_idx = 0
        for mapping in mappings_list:
            compartments = mapping['compartments']
            n_neurons = mapping['n_neurons']
            currents = input_currents[input_idx:input_idx + n_neurons]
            
            for i, current in enumerate(currents):
                compartments[i].biasMant = int(current)
            
            input_idx += n_neurons
    
    def reset_board(self):
        """Reset board."""
        self.board.reset()
        self.timestep = 0


def create_loihi_hardware_system(n_neurons: int) -> Tuple:
    """
    One-function setup of complete Loihi hardware system.
    
    Returns:
        (mapper, board) tuple
    """
    config = LoihiHardwareConfig()
    mapper = LoihiHardwareMapper(config)
    
    board = mapper.initialize_board()
    
    if not mapper.check_hardware_capacity(n_neurons):
        raise RuntimeError("Insufficient Loihi hardware")
    
    print(f"[LOIHI-HW] [OK] System ready for {n_neurons:,} neurons")
    
    return mapper, board
