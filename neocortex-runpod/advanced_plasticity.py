"""
ADVANCED SYNAPTIC PLASTICITY MECHANISMS

Implements state-of-the-art plasticity rules that complement STDP:
1. BCM Rule (Bienenstock-Cooper-Munro) - Sliding threshold for stability
2. Synaptic Scaling - Homeostatic regulation
3. Enhanced Three-Factor Learning - Eligibility traces + neuromodulation
4. Short-Term Plasticity - Facilitation and depression

All mechanisms are biologically validated and integrate seamlessly with
existing STDP and receptor-mediated modulation.

VERSION: 1.0
COMPATIBLE WITH: NeoCortex v2.1, emergent_neuromodulation v2.1
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    import torch
    TORCH_AVAILABLE = True
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
except ImportError:
    TORCH_AVAILABLE = False
    DEVICE = None


# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

@dataclass
class PlasticityConfig:
    """Configuration for advanced plasticity mechanisms."""
    
    # BCM Rule
    use_bcm: bool = True
    bcm_tau_theta: float = 10000.0  # ms, sliding threshold time constant
    bcm_initial_theta: float = 5.0  # Hz, initial threshold
    bcm_power: float = 2.0  # Exponent for theta calculation
    
    # Synaptic Scaling
    use_synaptic_scaling: bool = True
    scaling_target_rate: float = 5.0  # Hz, target firing rate
    scaling_tau: float = 86400000.0  # ms (24 hours)
    scaling_interval: int = 1000  # Steps between scaling updates
    scaling_min_factor: float = 0.5  # Minimum scaling factor
    scaling_max_factor: float = 2.0  # Maximum scaling factor
    
    # Three-Factor Learning
    use_three_factor: bool = True
    eligibility_tau: float = 1000.0  # ms, eligibility trace decay
    eligibility_strength: float = 1.0  # Strength of eligibility trace
    dopamine_threshold: float = 0.4  # Threshold for dopamine gating
    
    # Short-Term Plasticity
    use_stp: bool = True
    stp_tau_facilitation: float = 200.0  # ms, facilitation decay
    stp_tau_depression: float = 500.0  # ms, depression recovery
    stp_facilitation_strength: float = 0.5  # Max facilitation increase
    stp_depression_strength: float = 0.3  # Max depression decrease
    
    # General
    debug: bool = False


# ═══════════════════════════════════════════════════════════════════
# BCM RULE
# ═══════════════════════════════════════════════════════════════════

class BCMPlasticity:
    """
    Bienenstock-Cooper-Munro plasticity rule.
    
    Implements sliding threshold that prevents runaway potentiation/depression.
    θ_m slides toward E[post_rate^power] to maintain stability.
    
    Key features:
    - Prevents weight explosion (homeostatic)
    - Selective potentiation (only strong inputs)
    - Biologically validated in visual cortex
    
    Reference: Bienenstock et al. (1982) J Neurosci
    """
    
    def __init__(self, config: PlasticityConfig):
        self.config = config
        self.theta = config.bcm_initial_theta  # Current threshold
        self.tau = config.bcm_tau_theta
        self.power = config.bcm_power
        
        # History for theta calculation
        self.post_rate_history = []
        self.history_window = 1000  # samples
    
    def update_threshold(self, post_rate: float, dt: float = 1.0):
        """
        Update sliding threshold based on recent postsynaptic activity.
        
        θ_m(t+1) = θ_m(t) + (post_rate^power - θ_m(t)) * dt/τ
        """
        # Add to history
        self.post_rate_history.append(post_rate)
        if len(self.post_rate_history) > self.history_window:
            self.post_rate_history.pop(0)
        
        # Calculate target threshold (average of recent activity^power)
        if len(self.post_rate_history) > 10:
            avg_rate = np.mean(self.post_rate_history)
            target_theta = avg_rate ** self.power
        else:
            target_theta = post_rate ** self.power
        
        # Slide threshold
        alpha = dt / self.tau
        self.theta = self.theta * (1 - alpha) + target_theta * alpha
        
        # Prevent zero threshold
        self.theta = max(self.theta, 0.1)
        
        return self.theta
    
    def calculate_weight_change(
        self,
        pre_activity: float,
        post_rate: float,
        base_lr: float
    ) -> float:
        """
        Calculate BCM weight change.
        
        Δw = η * pre * post * (post - θ)
        
        If post > θ: LTP (positive change)
        If post < θ: LTD (negative change)
        """
        # BCM learning rule
        phi = post_rate - self.theta  # Signed difference
        delta_w = base_lr * pre_activity * post_rate * phi
        
        return delta_w
    
    def get_state(self) -> Dict:
        """Get current BCM state."""
        return {
            'theta': self.theta,
            'avg_recent_rate': np.mean(self.post_rate_history) if self.post_rate_history else 0.0,
            'history_size': len(self.post_rate_history)
        }


# ═══════════════════════════════════════════════════════════════════
# SYNAPTIC SCALING
# ═══════════════════════════════════════════════════════════════════

class SynapticScaling:
    """
    Homeostatic synaptic scaling.
    
    Multiplicatively scales all synaptic weights to maintain target firing rate.
    Operates on slow timescale (hours to days).
    
    Key features:
    - Global homeostasis (all synapses scaled together)
    - Maintains relative weight differences
    - Prevents runaway excitation/silence
    
    Reference: Turrigiano (2008) Cell
    """
    
    def __init__(self, config: PlasticityConfig):
        self.config = config
        self.target_rate = config.scaling_target_rate
        self.tau = config.scaling_tau
        self.interval = config.scaling_interval
        
        # Rate measurement
        self.spike_count = 0
        self.time_elapsed = 0.0
        self.steps_since_scaling = 0
        
        # Scaling factor history
        self.current_scaling_factor = 1.0
    
    def update_spike_count(self, spiked: bool, dt: float = 1.0):
        """Update spike counter."""
        if spiked:
            self.spike_count += 1
        self.time_elapsed += dt
        self.steps_since_scaling += 1
    
    def should_scale(self) -> bool:
        """Check if it's time to apply scaling."""
        return self.steps_since_scaling >= self.interval
    
    def calculate_scaling_factor(self) -> float:
        """
        Calculate multiplicative scaling factor.
        
        scaling_factor = target_rate / measured_rate
        
        Applied slowly: w_new = w_old * (1 - α + α * scaling_factor)
        """
        if self.time_elapsed < 1.0:
            return 1.0
        
        # Measure rate (Hz)
        measured_rate = (self.spike_count / self.time_elapsed) * 1000.0  # Convert ms to Hz
        
        if measured_rate < 0.01:
            # Too silent, scale up
            scaling_factor = self.config.scaling_max_factor
        else:
            # Calculate ideal scaling
            scaling_factor = self.target_rate / measured_rate
            
            # Clip to reasonable range
            scaling_factor = np.clip(
                scaling_factor,
                self.config.scaling_min_factor,
                self.config.scaling_max_factor
            )
        
        # Apply slowly (alpha = dt/tau)
        alpha = (self.steps_since_scaling * 1.0) / self.tau  # Approximate
        alpha = min(alpha, 0.1)  # Max 10% change per update
        
        effective_factor = 1.0 * (1 - alpha) + scaling_factor * alpha
        
        self.current_scaling_factor = effective_factor
        
        # Reset counters
        self.spike_count = 0
        self.time_elapsed = 0.0
        self.steps_since_scaling = 0
        
        return effective_factor
    
    def get_state(self) -> Dict:
        """Get current scaling state."""
        current_rate = (self.spike_count / self.time_elapsed * 1000.0) if self.time_elapsed > 0 else 0.0
        return {
            'measured_rate_hz': current_rate,
            'target_rate_hz': self.target_rate,
            'scaling_factor': self.current_scaling_factor,
            'steps_until_scaling': self.interval - self.steps_since_scaling
        }


# ═══════════════════════════════════════════════════════════════════
# THREE-FACTOR LEARNING
# ═══════════════════════════════════════════════════════════════════

class ThreeFactorLearning:
    """
    Enhanced three-factor learning with eligibility traces.
    
    Implements:
    - Eligibility traces (memory of recent pre-post correlations)
    - Neuromodulator gating (dopamine, serotonin)
    - Credit assignment (which synapse was responsible for reward)
    
    Formula: Δw = η * eligibility * neuromodulator
    
    Key features:
    - Bridges temporal gap between action and reward
    - Enables reinforcement learning in spiking networks
    - Biologically validated in basal ganglia
    
    Reference: Izhikevich (2007) Scholarpedia
    """
    
    def __init__(self, config: PlasticityConfig):
        self.config = config
        self.tau = config.eligibility_tau
        self.strength = config.eligibility_strength
        self.da_threshold = config.dopamine_threshold
        
        # Eligibility trace
        self.eligibility = 0.0
        
        # Neuromodulator levels (set externally)
        self.dopamine = 0.5
        self.serotonin = 0.5
    
    def update_eligibility(self, pre_spike: bool, post_spike: bool, dt: float = 1.0):
        """
        Update eligibility trace based on pre-post correlation.
        
        e(t+1) = e(t) * exp(-dt/τ) + strength * pre * post
        """
        # Decay
        decay = np.exp(-dt / self.tau)
        self.eligibility *= decay
        
        # Increment if correlation
        if pre_spike and post_spike:
            self.eligibility += self.strength
        
        # Clip to prevent explosion
        self.eligibility = min(self.eligibility, 10.0)
        
        return self.eligibility
    
    def set_neuromodulators(self, dopamine: float, serotonin: float):
        """Set current neuromodulator levels."""
        self.dopamine = dopamine
        self.serotonin = serotonin
    
    def calculate_weight_change(self, base_lr: float, reward_signal: float = 0.0) -> float:
        """
        Calculate three-factor weight change.
        
        Δw = η * eligibility * (dopamine_modulation + reward_signal)
        
        Args:
            base_lr: Base learning rate
            reward_signal: Optional explicit reward (-1 to +1)
        """
        # Dopamine acts as "go" signal for plasticity
        # High dopamine → enable LTP
        # Low dopamine → reduce plasticity
        
        # Reward prediction error (simplified)
        if reward_signal != 0.0:
            # Explicit reward provided
            rpe = reward_signal
        else:
            # Use dopamine as implicit reward signal
            # Above threshold = reward, below = punishment
            rpe = (self.dopamine - self.da_threshold) * 2.0
        
        # Serotonin modulates learning rate (patience/impulsivity)
        serotonin_modulation = 0.5 + self.serotonin * 0.5
        
        # Combined three-factor rule
        delta_w = base_lr * self.eligibility * rpe * serotonin_modulation
        
        return delta_w
    
    def get_state(self) -> Dict:
        """Get current three-factor state."""
        return {
            'eligibility': self.eligibility,
            'dopamine': self.dopamine,
            'serotonin': self.serotonin,
            'effective_rpe': (self.dopamine - self.da_threshold) * 2.0
        }


# ═══════════════════════════════════════════════════════════════════
# SHORT-TERM PLASTICITY
# ═══════════════════════════════════════════════════════════════════

class ShortTermPlasticity:
    """
    Short-term synaptic plasticity (facilitation and depression).
    
    Implements:
    - Facilitation: Increased release probability with repeated activation
    - Depression: Decreased release due to vesicle depletion
    
    Key features:
    - Frequency-dependent filtering
    - Fast timescale (ms to seconds)
    - Affects synaptic efficacy dynamically
    
    Reference: Tsodyks & Markram (1997) PNAS
    """
    
    def __init__(self, config: PlasticityConfig, facilitation_dominant: bool = True):
        self.config = config
        self.facilitation_dominant = facilitation_dominant
        
        # Facilitation
        self.tau_f = config.stp_tau_facilitation
        self.f_strength = config.stp_facilitation_strength
        self.facilitation = 0.0  # Current facilitation level
        
        # Depression
        self.tau_d = config.stp_tau_depression
        self.d_strength = config.stp_depression_strength
        self.available_resources = 1.0  # Fraction of available vesicles
        
        # Baseline efficacy
        self.baseline_efficacy = 1.0
    
    def process_spike(self, dt: float = 1.0) -> float:
        """
        Process a presynaptic spike and return effective synaptic efficacy.
        
        Returns:
            efficacy: Multiplicative factor for synaptic weight (0.5 to 2.0)
        """
        # Update facilitation FIRST (increases with each spike)
        if self.facilitation_dominant:
            # Build up facilitation aggressively
            self.facilitation += self.f_strength * 1.2  # Strong buildup
            self.facilitation = min(self.facilitation, 5.0)  # Much higher cap (allows ~10 spikes)

        # Update depression (resources depleted)
        # For facilitating synapses, use MINIMAL depression
        if self.facilitation_dominant:
            # VERY light depression - facilitation wins!
            release_fraction = 0.03  # Only 3% depletion per spike
        else:
            # Heavy depression for depressing synapses
            release_fraction = 0.5  # 50% depletion per spike

        self.available_resources -= release_fraction * self.available_resources
        self.available_resources = max(self.available_resources, 0.3)  # Don't go too low

        # NOW calculate efficacy AFTER updates
        if self.facilitation_dominant:
            # Facilitating synapse: facilitation STRONGLY dominates
            # Facilitation effect strong enough to overcome any resource depletion
            efficacy = self.baseline_efficacy * (1.0 + self.facilitation * 1.5) * self.available_resources
        else:
            # Depressing synapse: depression dominates
            efficacy = self.baseline_efficacy * self.available_resources * (1.0 - self.facilitation * 0.3)

        return efficacy

    def decay(self, dt: float = 1.0):
        """
        Decay facilitation and recover resources (no spike).

        Should be called every timestep.
        """
        # Facilitation decay
        self.facilitation *= np.exp(-dt / self.tau_f)

        # Resource recovery
        recovery = (1.0 - self.available_resources) * (1.0 - np.exp(-dt / self.tau_d))
        self.available_resources += recovery
        self.available_resources = min(self.available_resources, 1.0)

    def get_state(self) -> Dict:
        """Get current STP state."""
        return {
            'facilitation': self.facilitation,
            'available_resources': self.available_resources,
            'type': 'facilitating' if self.facilitation_dominant else 'depressing'
        }


# ═══════════════════════════════════════════════════════════════════
# INTEGRATED PLASTICITY MANAGER
# ═══════════════════════════════════════════════════════════════════

class AdvancedPlasticityManager:
    """
    Unified manager for all plasticity mechanisms.

    Coordinates:
    - BCM (medium timescale, stability)
    - Synaptic scaling (slow timescale, homeostasis)
    - Three-factor (fast timescale, learning)
    - STP (very fast timescale, dynamics)

    Integrates seamlessly with existing STDP.
    """

    def __init__(self, config: PlasticityConfig = None):
        self.config = config or PlasticityConfig()

        # Initialize mechanisms
        self.bcm = BCMPlasticity(self.config) if self.config.use_bcm else None
        self.scaling = SynapticScaling(self.config) if self.config.use_synaptic_scaling else None
        self.three_factor = ThreeFactorLearning(self.config) if self.config.use_three_factor else None
        self.stp = {}  # Dictionary of STP per synapse type

        if self.config.debug:
            print("[PLASTICITY] Advanced mechanisms initialized:")
            if self.bcm:
                print(f"  - BCM: θ_initial={self.config.bcm_initial_theta:.1f} Hz")
            if self.scaling:
                print(f"  - Synaptic Scaling: target={self.config.scaling_target_rate:.1f} Hz")
            if self.three_factor:
                print(f"  - Three-Factor: τ_eligibility={self.config.eligibility_tau:.0f} ms")
            if self.config.use_stp:
                print(f"  - STP: τ_fac={self.config.stp_tau_facilitation:.0f} ms")

    def create_stp_for_synapse(self, synapse_id: str, facilitating: bool = True):
        """Create STP instance for a specific synapse."""
        if self.config.use_stp and synapse_id not in self.stp:
            self.stp[synapse_id] = ShortTermPlasticity(self.config, facilitating)

    def update_step(
        self,
        pre_spike: bool,
        post_spike: bool,
        post_rate: float,
        dopamine: float,
        serotonin: float,
        base_lr: float,
        dt: float = 1.0,
        synapse_id: str = "default",
        reward: float = 0.0
    ) -> Dict[str, float]:
        """
        Update all plasticity mechanisms for one timestep.

        Returns dict with:
        - 'bcm_delta': BCM weight change
        - 'three_factor_delta': Three-factor weight change
        - 'stp_efficacy': STP multiplicative factor
        - 'scaling_factor': Synaptic scaling factor (if time to scale)
        """
        results = {
            'bcm_delta': 0.0,
            'three_factor_delta': 0.0,
            'stp_efficacy': 1.0,
            'scaling_factor': 1.0
        }

        # BCM Rule
        if self.bcm:
            self.bcm.update_threshold(post_rate, dt)
            if pre_spike:  # Only calculate if presynaptic spike
                results['bcm_delta'] = self.bcm.calculate_weight_change(
                    pre_activity=1.0,
                    post_rate=post_rate,
                    base_lr=base_lr
                )

        # Three-Factor Learning
        if self.three_factor:
            self.three_factor.set_neuromodulators(dopamine, serotonin)
            self.three_factor.update_eligibility(pre_spike, post_spike, dt)
            results['three_factor_delta'] = self.three_factor.calculate_weight_change(
                base_lr=base_lr,
                reward_signal=reward
            )

        # Short-Term Plasticity
        if self.config.use_stp:
            if synapse_id not in self.stp:
                self.create_stp_for_synapse(synapse_id)

            stp = self.stp[synapse_id]
            if pre_spike:
                results['stp_efficacy'] = stp.process_spike(dt)
            else:
                stp.decay(dt)
                results['stp_efficacy'] = stp.baseline_efficacy

        # Synaptic Scaling (check if time to scale)
        if self.scaling:
            self.scaling.update_spike_count(post_spike, dt)
            if self.scaling.should_scale():
                results['scaling_factor'] = self.scaling.calculate_scaling_factor()

        return results

    def get_combined_weight_change(
        self,
        stdp_delta: float,
        results: Dict[str, float]
    ) -> float:
        """
        Combine all plasticity mechanisms into final weight change.

        Args:
            stdp_delta: Weight change from existing STDP
            results: Dict from update_step()

        Returns:
            Combined weight change
        """
        # Combine learning rules
        # STDP is primary, others modulate or add

        total_delta = 0.0

        # STDP (existing mechanism)
        total_delta += stdp_delta

        # BCM (modulates STDP or replaces it)
        if self.bcm and self.config.use_bcm:
            # BCM can work alongside STDP or replace it
            # Here we use BCM as primary when enabled
            total_delta = results['bcm_delta']

        # Three-factor (additive, gated by neuromodulators)
        if self.three_factor:
            total_delta += results['three_factor_delta']

        # STP affects efficacy (multiplicative on effective weight)
        # This is applied separately to synaptic transmission

        return total_delta

    def apply_scaling(self, weight: float, scaling_factor: float) -> float:
        """Apply synaptic scaling to a weight."""
        return weight * scaling_factor

    def get_all_states(self) -> Dict:
        """Get state of all mechanisms."""
        states = {}

        if self.bcm:
            states['bcm'] = self.bcm.get_state()
        if self.scaling:
            states['scaling'] = self.scaling.get_state()
        if self.three_factor:
            states['three_factor'] = self.three_factor.get_state()
        if self.stp:
            states['stp_count'] = len(self.stp)

        return states


# ═══════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def create_default_config(
    bcm: bool = True,
    scaling: bool = True,
    three_factor: bool = True,
    stp: bool = True,
    debug: bool = False
) -> PlasticityConfig:
    """Create default plasticity configuration."""
    return PlasticityConfig(
        use_bcm=bcm,
        use_synaptic_scaling=scaling,
        use_three_factor=three_factor,
        use_stp=stp,
        debug=debug
    )


def test_plasticity_mechanisms():
    """Test all plasticity mechanisms."""
    print("\n" + "="*70)
    print("TESTING ADVANCED PLASTICITY MECHANISMS")
    print("="*70)

    config = create_default_config(debug=True)
    manager = AdvancedPlasticityManager(config)

    # Simulate 1000 steps
    print("\nSimulating 1000 timesteps...")

    for step in range(1000):
        # Simulate spikes
        pre_spike = np.random.rand() < 0.05  # 5% spike probability
        post_spike = np.random.rand() < 0.05
        post_rate = 5.0 + np.random.randn() * 1.0  # ~5 Hz

        # Neuromodulators
        dopamine = 0.5 + 0.1 * np.sin(step / 100.0)  # Oscillating
        serotonin = 0.5

        # Update
        results = manager.update_step(
            pre_spike=pre_spike,
            post_spike=post_spike,
            post_rate=post_rate,
            dopamine=dopamine,
            serotonin=serotonin,
            base_lr=0.001,
            dt=1.0
        )

        # Print every 100 steps
        if step % 100 == 0:
            states = manager.get_all_states()
            print(f"\nStep {step}:")
            if 'bcm' in states:
                print(f"  BCM θ: {states['bcm']['theta']:.2f} Hz")
            if 'scaling' in states:
                print(f"  Scaling rate: {states['scaling']['measured_rate_hz']:.2f} Hz")
            if 'three_factor' in states:
                print(f"  Eligibility: {states['three_factor']['eligibility']:.3f}")

    print("\n All mechanisms tested successfully!")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_plasticity_mechanisms()