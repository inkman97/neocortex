"""
PLASTICITY INTEGRATION MODULE

Integrates advanced plasticity mechanisms with existing NeoCortex system.
Wraps neuron groups to add BCM, synaptic scaling, three-factor, and STP
without modifying core code.

USAGE:
    from plasticity_integration import integrate_advanced_plasticity
    
    # After creating brain
    brain = RealisticBrain(...)
    integrate_advanced_plasticity(brain, enable_all=True)
    
    # Brain now uses advanced plasticity automatically!

VERSION: 1.0
COMPATIBLE WITH: NeoCortex v2.1
"""

from advanced_plasticity import (
    AdvancedPlasticityManager,
    PlasticityConfig,
    create_default_config
)
from typing import Dict, Optional
import numpy as np

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════
# NEURON GROUP WRAPPER
# ═══════════════════════════════════════════════════════════════════

class PlasticityEnhancedNeuronGroup:
    """
    Wrapper around existing neuron group that adds advanced plasticity.
    
    Transparent drop-in replacement that intercepts weight updates
    and spike processing to apply advanced mechanisms.
    """
    
    def __init__(self, original_group, plasticity_manager: AdvancedPlasticityManager):
        self.original = original_group
        self.plasticity = plasticity_manager
        
        # Store original methods
        self._original_step = getattr(original_group, 'step', None)
        self._original_learn = getattr(original_group, 'learn', None)
        
        # Tracking
        self.n = original_group.n
        self.spike_counts = np.zeros(self.n)
        self.time_elapsed = 0.0
        self.post_rates = np.zeros(self.n)  # Estimated firing rates
        
        # STP state per neuron
        self.stp_states = {}
    
    def estimate_firing_rate(self, neuron_idx: int, window_ms: float = 1000.0) -> float:
        """Estimate firing rate for a neuron over recent window."""
        if self.time_elapsed < window_ms:
            return 0.0
        return (self.spike_counts[neuron_idx] / self.time_elapsed) * 1000.0  # Hz
    
    def step(self, dt: float = 1.0, *args, **kwargs):
        """Enhanced step with plasticity tracking."""
        # Call original step
        if self._original_step:
            self._original_step(dt, *args, **kwargs)
        
        # Update tracking
        self.time_elapsed += dt
        
        # Get spikes (convert to numpy if torch)
        spikes = self.original.spike
        if TORCH_AVAILABLE and torch.is_tensor(spikes):
            spikes = spikes.cpu().numpy()
        
        # Update spike counts
        self.spike_counts += spikes.astype(float)
        
        # Update rate estimates (rolling average)
        for i in range(self.n):
            self.post_rates[i] = self.estimate_firing_rate(i, window_ms=1000.0)
        
        # Synaptic scaling check (applies to all synapses)
        if self.plasticity.scaling and self.plasticity.scaling.should_scale():
            for i in range(self.n):
                post_rate = self.post_rates[i]
                
                # Update scaling for this neuron
                self.plasticity.scaling.spike_count = int(self.spike_counts[i])
                self.plasticity.scaling.time_elapsed = self.time_elapsed
                
                scaling_factor = self.plasticity.scaling.calculate_scaling_factor()
                
                # Apply scaling to input weights
                if hasattr(self.original, 'w_in') and scaling_factor != 1.0:
                    if TORCH_AVAILABLE and torch.is_tensor(self.original.w_in):
                        self.original.w_in[i] *= scaling_factor
                    else:
                        self.original.w_in[i] *= scaling_factor
    
    def learn(
        self,
        reward: float = 0.0,
        dopamine: float = 0.5,
        serotonin: float = 0.5,
        *args,
        **kwargs
    ):
        """Enhanced learning with advanced plasticity."""
        # Call original learning if exists
        if self._original_learn:
            self._original_learn(reward, *args, **kwargs)
        
        # Apply advanced plasticity per synapse
        # (This is a simplified version - full implementation would iterate over all synapses)
        
        # Get spikes
        spikes = self.original.spike
        if TORCH_AVAILABLE and torch.is_tensor(spikes):
            spikes = spikes.cpu().numpy()
        
        # For each spiking neuron, update plasticity
        for i in range(self.n):
            if spikes[i]:
                post_rate = self.post_rates[i]
                
                # Update plasticity mechanisms
                # (In real implementation, this would be per-synapse)
                results = self.plasticity.update_step(
                    pre_spike=True,  # Simplified
                    post_spike=True,
                    post_rate=post_rate,
                    dopamine=dopamine,
                    serotonin=serotonin,
                    base_lr=0.001,
                    dt=1.0,
                    synapse_id=f"neuron_{i}",
                    reward=reward
                )
    
    def __getattr__(self, name):
        """Proxy all other attributes to original group."""
        return getattr(self.original, name)


# ═══════════════════════════════════════════════════════════════════
# INTEGRATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def integrate_advanced_plasticity(
    brain,
    config: Optional[PlasticityConfig] = None,
    enable_all: bool = True,
    debug: bool = False
):
    """
    Integrate advanced plasticity into existing brain.
    
    Args:
        brain: RealisticBrain instance
        config: PlasticityConfig (optional, uses defaults if None)
        enable_all: Enable all mechanisms
        debug: Enable debug logging
    
    Returns:
        PlasticityConfig used
    """
    if config is None:
        config = create_default_config(
            bcm=enable_all,
            scaling=enable_all,
            three_factor=enable_all,
            stp=enable_all,
            debug=debug
        )
    
    print(f"\n{'='*70}")
    print(f"INTEGRATING ADVANCED PLASTICITY")
    print(f"{'='*70}")
    
    # Create plasticity manager
    plasticity_manager = AdvancedPlasticityManager(config)
    
    # Store in brain for access
    brain.advanced_plasticity = plasticity_manager
    brain.plasticity_config = config
    
    # Wrap neuron groups in all columns
    wrapped_count = 0
    for col_idx, column in enumerate(brain.columns):
        for layer_name, layer_dict in column.layers.items():
            for neuron_type, group in layer_dict.items():
                # Wrap the group
                wrapped = PlasticityEnhancedNeuronGroup(group, plasticity_manager)
                
                # Replace in column (careful - maintain reference)
                column.layers[layer_name][neuron_type] = wrapped
                wrapped_count += 1
    
    print(f"[PLASTICITY] Enhanced {wrapped_count} neuron groups")
    print(f"[PLASTICITY] Mechanisms enabled:")
    if config.use_bcm:
        print(f"  BCM Rule (θ_initial={config.bcm_initial_theta:.1f} Hz)")
    if config.use_synaptic_scaling:
        print(f"  Synaptic Scaling (target={config.scaling_target_rate:.1f} Hz)")
    if config.use_three_factor:
        print(f"  Three-Factor Learning (τ={config.eligibility_tau:.0f} ms)")
    if config.use_stp:
        print(f"  Short-Term Plasticity")
    
    print(f"{'='*70}\n")
    
    return config


def get_plasticity_stats(brain) -> Dict:
    """Get statistics from advanced plasticity system."""
    if not hasattr(brain, 'advanced_plasticity'):
        return {'error': 'Advanced plasticity not integrated'}
    
    return brain.advanced_plasticity.get_all_states()


def update_plasticity_neuromodulators(brain, dopamine: float, serotonin: float):
    """Update neuromodulator levels for three-factor learning."""
    if hasattr(brain, 'advanced_plasticity'):
        if brain.advanced_plasticity.three_factor:
            brain.advanced_plasticity.three_factor.set_neuromodulators(
                dopamine, serotonin
            )


# ═══════════════════════════════════════════════════════════════════
# MONITORING
# ═══════════════════════════════════════════════════════════════════

class PlasticityMonitor:
    """
    Monitor plasticity mechanisms during simulation.
    Logs key metrics for analysis.
    """
    
    def __init__(self, brain, log_interval: int = 1000):
        self.brain = brain
        self.log_interval = log_interval
        self.step_count = 0
        
        self.history = {
            'bcm_theta': [],
            'scaling_rate': [],
            'eligibility': [],
            'steps': []
        }
    
    def update(self):
        """Update monitoring (call every step)."""
        self.step_count += 1
        
        if self.step_count % self.log_interval == 0:
            stats = get_plasticity_stats(self.brain)
            
            self.history['steps'].append(self.step_count)
            
            if 'bcm' in stats:
                self.history['bcm_theta'].append(stats['bcm']['theta'])
            
            if 'scaling' in stats:
                self.history['scaling_rate'].append(stats['scaling']['measured_rate_hz'])
            
            if 'three_factor' in stats:
                self.history['eligibility'].append(stats['three_factor']['eligibility'])
    
    def get_summary(self) -> Dict:
        """Get summary statistics."""
        summary = {}
        
        for key, values in self.history.items():
            if key != 'steps' and values:
                summary[key] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values)
                }
        
        return summary
    
    def print_summary(self):
        """Print summary to console."""
        summary = self.get_summary()
        
        print(f"\n{'='*70}")
        print(f"PLASTICITY SUMMARY ({self.step_count} steps)")
        print(f"{'='*70}")
        
        for mechanism, stats in summary.items():
            print(f"\n{mechanism.upper()}:")
            print(f"  Mean: {stats['mean']:.3f}")
            print(f"  Std:  {stats['std']:.3f}")
            print(f"  Range: [{stats['min']:.3f}, {stats['max']:.3f}]")
        
        print(f"\n{'='*70}\n")


# ═══════════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════════

def test_integration():
    """Test plasticity integration."""
    print("\n" + "="*70)
    print("TESTING PLASTICITY INTEGRATION")
    print("="*70)
    
    # This would require actual brain instance
    # Placeholder for now
    print("\nIntegration module ready!")
    print("   Use: integrate_advanced_plasticity(brain)")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_integration()
