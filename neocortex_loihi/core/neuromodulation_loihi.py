"""
╔══════════════════════════════════════════════════════════════════════╗
║      LOIHI NEUROMODULATION - 6 Neurotransmitter System                ║
║                                                                       ║
║  Sistema biologicamente accurato con:                                 ║
║  - 6 NT: Serotonina, Dopamina, Noradrenalina, Acetilcolina,         ║
║          GABA, Glutammato                                             ║
║  - Recettori specifici per tipo neuronale                            ║
║  - Drug mechanisms (reuptake inhibition, enzyme inhibition, etc.)    ║
║  - Emergent dynamics (no forcing)                                     ║
╚══════════════════════════════════════════════════════════════════════╝

NEUROTRANSMITTERS:
1. Serotonin (5HT) - Mood, impulse control, patience
2. Dopamine (DA) - Reward, motivation, movement
3. Noradrenaline (NE) - Arousal, attention, stress response
4. Acetylcholine (ACh) - Memory, learning, attention
5. GABA - Primary inhibitory neurotransmitter
6. Glutamate - Primary excitatory neurotransmitter

MECHANISMS:
- Neuromodulatory populations receive tonic drive
- Release proportional to firing rate
- Reuptake via transporters (SERT, DAT, NET, GAT)
- Receptor-mediated effects on target neurons
- Disease = altered synaptic efficacy
- Drugs = block reuptake/enzymes

VERSION: 1.0
COMPATIBLE WITH: Lava-NC 0.8+, Loihi 2
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from .neurons_loihi import (
    SCALE, SCALE_SHIFT, NeuronType, NumpyLIFNeuron, 
    create_neuron_population, LAVA_AVAILABLE
)


# ══════════════════════════════════════════════════════════════════════
# NEUROMODULATOR TYPES
# ══════════════════════════════════════════════════════════════════════

class Neuromodulator(Enum):
    """6 NT system."""
    SEROTONIN = "5HT"
    DOPAMINE = "DA"
    NORADRENALINE = "NE"
    ACETYLCHOLINE = "ACh"
    GABA = "GABA"
    GLUTAMATE = "Glu"


# ══════════════════════════════════════════════════════════════════════
# RECEPTOR PROFILES
# ══════════════════════════════════════════════════════════════════════

@dataclass
class ReceptorProfile:
    """
    Receptor expression profile for a neuron type.
    
    Each receptor has:
    - Expression level (0-1)
    - Effect sign (+1 excitatory, -1 inhibitory)
    - Efficacy (how strongly it affects the neuron)
    """
    # Serotonin receptors
    ht1a: Tuple[float, int, float] = (0.0, 0, 0.0)  # (expression, sign, efficacy)
    ht2a: Tuple[float, int, float] = (0.0, 0, 0.0)
    ht2c: Tuple[float, int, float] = (0.0, 0, 0.0)
    ht3: Tuple[float, int, float] = (0.0, 0, 0.0)
    
    # Dopamine receptors
    d1: Tuple[float, int, float] = (0.0, 0, 0.0)
    d2: Tuple[float, int, float] = (0.0, 0, 0.0)
    d3: Tuple[float, int, float] = (0.0, 0, 0.0)
    d4: Tuple[float, int, float] = (0.0, 0, 0.0)
    
    # Adrenergic receptors
    alpha1: Tuple[float, int, float] = (0.0, 0, 0.0)
    alpha2: Tuple[float, int, float] = (0.0, 0, 0.0)
    beta1: Tuple[float, int, float] = (0.0, 0, 0.0)
    beta2: Tuple[float, int, float] = (0.0, 0, 0.0)
    
    # Cholinergic receptors
    m1: Tuple[float, int, float] = (0.0, 0, 0.0)
    m2: Tuple[float, int, float] = (0.0, 0, 0.0)
    nicotinic: Tuple[float, int, float] = (0.0, 0, 0.0)
    
    # GABA receptors
    gaba_a: Tuple[float, int, float] = (0.0, 0, 0.0)
    gaba_b: Tuple[float, int, float] = (0.0, 0, 0.0)
    
    # Glutamate receptors
    ampa: Tuple[float, int, float] = (0.0, 0, 0.0)
    nmda: Tuple[float, int, float] = (0.0, 0, 0.0)
    mglur: Tuple[float, int, float] = (0.0, 0, 0.0)


# Receptor profiles by neuron type (from biological data)
RECEPTOR_PROFILES = {
    NeuronType.PYRAMIDAL: ReceptorProfile(
        # 5-HT: mostly inhibitory via 5-HT1A, excitatory via 5-HT2A
        ht1a=(0.8, -1, 0.7),
        ht2a=(0.6, +1, 0.5),
        ht2c=(0.3, -1, 0.4),
        
        # DA: D1 excitatory, D2 inhibitory
        d1=(0.6, +1, 0.6),
        d2=(0.5, -1, 0.5),
        d3=(0.2, -1, 0.3),
        
        # NE: mostly excitatory
        alpha1=(0.7, +1, 0.6),
        beta1=(0.5, +1, 0.5),
        alpha2=(0.4, -1, 0.4),
        
        # ACh: M1 excitatory
        m1=(0.7, +1, 0.7),
        nicotinic=(0.3, +1, 0.5),
        
        # GABA: inhibitory
        gaba_a=(1.0, -1, 1.0),
        gaba_b=(0.6, -1, 0.6),
        
        # Glutamate: excitatory
        ampa=(1.0, +1, 1.0),
        nmda=(0.9, +1, 0.9),
        mglur=(0.4, -1, 0.3),  # mGluR can be inhibitory
    ),
    
    NeuronType.PV: ReceptorProfile(
        ht3=(0.7, +1, 0.7),    # 5-HT3: fast excitation
        d2=(0.8, -1, 0.7),
        d4=(0.6, -1, 0.5),
        alpha1=(0.5, +1, 0.5),
        m2=(0.6, -1, 0.5),     # M2: inhibitory
        gaba_a=(0.9, -1, 0.8),
        ampa=(1.0, +1, 1.0),
        nmda=(0.6, +1, 0.6),
    ),
    
    NeuronType.SST: ReceptorProfile(
        ht1a=(0.9, -1, 0.8),
        ht2c=(0.5, -1, 0.5),
        d1=(0.5, +1, 0.5),
        alpha2=(0.6, -1, 0.5),
        m1=(0.6, +1, 0.6),
        gaba_a=(0.8, -1, 0.7),
        gaba_b=(0.7, -1, 0.6),
        ampa=(0.9, +1, 0.9),
        mglur=(0.6, -1, 0.5),
    ),
    
    NeuronType.VIP: ReceptorProfile(
        ht2c=(0.8, +1, 0.7),   # 5-HT2C excitatory in VIP
        d1=(0.6, +1, 0.6),
        d3=(0.5, +1, 0.5),
        beta2=(0.7, +1, 0.7),
        nicotinic=(0.8, +1, 0.8),  # Strong cholinergic
        gaba_a=(0.7, -1, 0.6),
        ampa=(1.0, +1, 1.0),
        nmda=(0.7, +1, 0.7),
    ),
    
    NeuronType.STELLATE: ReceptorProfile(
        ht1a=(0.6, -1, 0.5),
        ht2a=(0.5, +1, 0.5),
        d1=(0.5, +1, 0.5),
        alpha1=(0.6, +1, 0.6),
        m1=(0.6, +1, 0.6),
        gaba_a=(1.0, -1, 1.0),
        ampa=(1.0, +1, 1.0),
        nmda=(0.9, +1, 0.9),
    ),
}


# ══════════════════════════════════════════════════════════════════════
# NEUROMODULATOR POPULATION
# ══════════════════════════════════════════════════════════════════════

class NeuromodulatorPopulation:
    """
    Population of neurons that release a specific neurotransmitter.
    
    Key features:
    - Receives tonic drive (simulates brainstem/thalamic input)
    - Firing rate → NT release
    - Reuptake via transporter
    - Degradation via enzymes
    """
    def __init__(self,
                 n_neurons: int,
                 nt_type: Neuromodulator,
                 tonic_drive: int = 128,  # 0.5 * 256
                 reuptake_rate: float = 0.8,
                 degradation_rate: float = 0.1,
                 use_lava: bool = False):
        self.n_neurons = n_neurons
        self.nt_type = nt_type
        self.tonic_drive = tonic_drive
        self.reuptake_rate = reuptake_rate
        self.degradation_rate = degradation_rate
        
        # Create neuron population
        # All modulatory neurons are similar to pyramidal
        self.neurons = create_neuron_population(
            n_neurons=n_neurons,
            neuron_type=NeuronType.PYRAMIDAL,
            use_lava=use_lava and LAVA_AVAILABLE
        )
        
        # NT concentration (fixed-point)
        self.nt_concentration = np.zeros(1, dtype=np.int16)
        
        # History
        self.concentration_history = []
        
    def step(self, external_input: Optional[np.ndarray] = None) -> int:
        """
        Update for one timestep.
        
        Args:
            external_input: Additional input (e.g., from rewards)
            
        Returns:
            NT concentration (fixed-point int)
        """
        # Prepare input
        total_input = np.full(self.n_neurons, self.tonic_drive, dtype=np.int16)
        if external_input is not None:
            total_input += external_input.astype(np.int16)
        
        # Update neurons
        if isinstance(self.neurons, NumpyLIFNeuron):
            spikes = self.neurons.step(total_input)
        else:
            # Lava neurons (would need network run)
            spikes = np.zeros(self.n_neurons, dtype=np.int8)
        
        # Release NT proportional to spikes
        release = int(spikes.sum() * 10)  # Scaling factor
        
        # Add release
        self.nt_concentration[0] += release
        
        # Reuptake (transporter clearance)
        reuptake = int(self.nt_concentration[0] * self.reuptake_rate)
        self.nt_concentration[0] -= reuptake
        
        # Degradation (enzyme metabolism)
        degradation = int(self.nt_concentration[0] * self.degradation_rate)
        self.nt_concentration[0] -= degradation
        
        # Clamp to valid range
        self.nt_concentration[0] = np.clip(self.nt_concentration[0], 0, SCALE * 2)
        
        # Store history
        self.concentration_history.append(self.nt_concentration[0])
        
        return self.nt_concentration[0]
    
    def get_concentration_float(self) -> float:
        """Get NT concentration as float (0-1)."""
        return self.nt_concentration[0] / SCALE
    
    def apply_drug_effect(self,
                         reuptake_inhibition: float = 0.0,
                         enzyme_inhibition: float = 0.0):
        """
        Apply drug effects to this NT system.
        
        Args:
            reuptake_inhibition: Fraction of reuptake blocked (0-1)
            enzyme_inhibition: Fraction of degradation blocked (0-1)
        """
        # Reduce reuptake
        self.reuptake_rate *= (1.0 - reuptake_inhibition)
        
        # Reduce degradation
        self.degradation_rate *= (1.0 - enzyme_inhibition)


# ══════════════════════════════════════════════════════════════════════
# NEUROMODULATION SYSTEM
# ══════════════════════════════════════════════════════════════════════

class NeuromodulationSystem:
    """
    Complete 6 NT neuromodulation system.
    
    Manages all 6 neurotransmitter populations and their effects
    on target neurons.
    """
    def __init__(self,
                 n_total_neurons: int,
                 use_lava: bool = False,
                 debug: bool = False):
        self.n_total_neurons = n_total_neurons
        self.debug = debug
        
        # Calculate size of each modulatory population
        # (~0.5% of total neurons per NT)
        n_per_nt = max(30, n_total_neurons // 200)
        
        # Create populations
        self.populations = {
            Neuromodulator.SEROTONIN: NeuromodulatorPopulation(
                n_neurons=n_per_nt,
                nt_type=Neuromodulator.SEROTONIN,
                tonic_drive=128,  # 0.5
                reuptake_rate=0.8,
                degradation_rate=0.1,
                use_lava=use_lava
            ),
            Neuromodulator.DOPAMINE: NeuromodulatorPopulation(
                n_neurons=int(n_per_nt * 1.2),
                nt_type=Neuromodulator.DOPAMINE,
                tonic_drive=102,  # 0.4
                reuptake_rate=0.9,  # Fast reuptake
                degradation_rate=0.15,
                use_lava=use_lava
            ),
            Neuromodulator.NORADRENALINE: NeuromodulatorPopulation(
                n_neurons=int(n_per_nt * 0.8),
                nt_type=Neuromodulator.NORADRENALINE,
                tonic_drive=115,  # 0.45
                reuptake_rate=0.85,
                degradation_rate=0.12,
                use_lava=use_lava
            ),
            Neuromodulator.ACETYLCHOLINE: NeuromodulatorPopulation(
                n_neurons=n_per_nt,
                nt_type=Neuromodulator.ACETYLCHOLINE,
                tonic_drive=128,
                reuptake_rate=0.7,
                degradation_rate=0.2,  # Fast degradation (AChE)
                use_lava=use_lava
            ),
            Neuromodulator.GABA: NeuromodulatorPopulation(
                n_neurons=int(n_per_nt * 1.5),
                nt_type=Neuromodulator.GABA,
                tonic_drive=140,  # 0.55
                reuptake_rate=0.75,
                degradation_rate=0.05,
                use_lava=use_lava
            ),
            Neuromodulator.GLUTAMATE: NeuromodulatorPopulation(
                n_neurons=int(n_per_nt * 1.3),
                nt_type=Neuromodulator.GLUTAMATE,
                tonic_drive=153,  # 0.6
                reuptake_rate=0.95,  # Very fast reuptake
                degradation_rate=0.08,
                use_lava=use_lava
            ),
        }
        
        if debug:
            print(f"[NEUROMOD] Created 6 NT system:")
            for nt, pop in self.populations.items():
                print(f"  {nt.value}: {pop.n_neurons} neurons")
    
    def step(self, reward: Optional[float] = None) -> Dict[Neuromodulator, float]:
        """
        Update all NT populations.
        
        Args:
            reward: Reward signal (modulates dopamine)
            
        Returns:
            NT concentrations (as floats 0-1)
        """
        concentrations = {}
        
        for nt_type, pop in self.populations.items():
            # Special input for dopamine (reward)
            if nt_type == Neuromodulator.DOPAMINE and reward is not None:
                reward_input = np.full(pop.n_neurons, 
                                      int(reward * SCALE), 
                                      dtype=np.int16)
                pop.step(external_input=reward_input)
            else:
                pop.step()
            
            concentrations[nt_type] = pop.get_concentration_float()
        
        return concentrations
    
    def apply_drug(self,
                   drug_targets: Dict[str, float]):
        """
        Apply drug effects to NT systems.
        
        Args:
            drug_targets: Dict mapping target name to potency
                         e.g., {'SERT': 0.8, 'DAT': 0.3, 'MAO-A': 0.5}
        """
        # Reuptake inhibitors
        if 'SERT' in drug_targets:
            self.populations[Neuromodulator.SEROTONIN].apply_drug_effect(
                reuptake_inhibition=drug_targets['SERT']
            )
        
        if 'DAT' in drug_targets:
            self.populations[Neuromodulator.DOPAMINE].apply_drug_effect(
                reuptake_inhibition=drug_targets['DAT']
            )
        
        if 'NET' in drug_targets:
            self.populations[Neuromodulator.NORADRENALINE].apply_drug_effect(
                reuptake_inhibition=drug_targets['NET']
            )
        
        if 'GAT' in drug_targets:
            self.populations[Neuromodulator.GABA].apply_drug_effect(
                reuptake_inhibition=drug_targets['GAT']
            )
        
        # Enzyme inhibitors
        if 'MAO-A' in drug_targets:
            # MAO-A metabolizes 5HT, NE, DA
            inhibition = drug_targets['MAO-A']
            self.populations[Neuromodulator.SEROTONIN].apply_drug_effect(
                enzyme_inhibition=inhibition
            )
            self.populations[Neuromodulator.NORADRENALINE].apply_drug_effect(
                enzyme_inhibition=inhibition
            )
            self.populations[Neuromodulator.DOPAMINE].apply_drug_effect(
                enzyme_inhibition=inhibition * 0.5  # Less effect on DA
            )
        
        if 'MAO-B' in drug_targets:
            # MAO-B mainly metabolizes DA
            self.populations[Neuromodulator.DOPAMINE].apply_drug_effect(
                enzyme_inhibition=drug_targets['MAO-B']
            )
        
        if 'AChE' in drug_targets:
            # Acetylcholinesterase
            self.populations[Neuromodulator.ACETYLCHOLINE].apply_drug_effect(
                enzyme_inhibition=drug_targets['AChE']
            )
    
    def set_disease_state(self, disease_profile):
        """
        Apply disease state by modifying NT system efficacies.
        
        Reduces tonic drive of each NT population proportionally to simulate
        disease conditions (e.g., depression = reduced serotonin production).
        
        Args:
            disease_profile: DiseaseProfile or dict with NT deficits
                - Positive values = deficit (reduce tonic drive)
                - Negative values = excess (increase tonic drive)
        
        Example:
            Depression: serotonin_deficit = 0.4 (40% deficit)
            → Reduces serotonin tonic drive to 60% of baseline
        """
        # Handle dict or DiseaseProfile
        if isinstance(disease_profile, dict):
            class SimpleDiseaseProfile:
                def __init__(self, **kwargs):
                    self.serotonin_deficit = kwargs.get('serotonin_deficit', 0.0)
                    self.dopamine_deficit = kwargs.get('dopamine_deficit', 0.0)
                    self.noradrenaline_deficit = kwargs.get('noradrenaline_deficit', 0.0)
                    self.acetylcholine_deficit = kwargs.get('acetylcholine_deficit', 0.0)
                    self.gaba_deficit = kwargs.get('gaba_deficit', 0.0)
                    self.glutamate_deficit = kwargs.get('glutamate_deficit', 0.0)
            disease_profile = SimpleDiseaseProfile(**disease_profile)
        
        # Apply disease by reducing tonic drive
        
        # Serotonin
        if abs(disease_profile.serotonin_deficit) > 0.01:
            pop = self.populations[Neuromodulator.SEROTONIN]
            factor = 1.0 - disease_profile.serotonin_deficit
            original = pop.tonic_drive
            pop.tonic_drive = int(pop.tonic_drive * factor)
            if self.debug:
                print(f"[DISEASE] 5HT: tonic_drive {original} → {pop.tonic_drive} (factor={factor:.2f})")
        
        # Dopamine
        if abs(disease_profile.dopamine_deficit) > 0.01:
            pop = self.populations[Neuromodulator.DOPAMINE]
            factor = 1.0 - disease_profile.dopamine_deficit
            original = pop.tonic_drive
            pop.tonic_drive = int(pop.tonic_drive * factor)
            if self.debug:
                print(f"[DISEASE] DA: tonic_drive {original} → {pop.tonic_drive} (factor={factor:.2f})")
        
        # Noradrenaline
        if abs(disease_profile.noradrenaline_deficit) > 0.01:
            pop = self.populations[Neuromodulator.NORADRENALINE]
            factor = 1.0 - disease_profile.noradrenaline_deficit
            original = pop.tonic_drive
            pop.tonic_drive = int(pop.tonic_drive * factor)
            if self.debug:
                print(f"[DISEASE] NE: tonic_drive {original} → {pop.tonic_drive} (factor={factor:.2f})")
        
        # Acetylcholine
        if abs(disease_profile.acetylcholine_deficit) > 0.01:
            pop = self.populations[Neuromodulator.ACETYLCHOLINE]
            factor = 1.0 - disease_profile.acetylcholine_deficit
            original = pop.tonic_drive
            pop.tonic_drive = int(pop.tonic_drive * factor)
            if self.debug:
                print(f"[DISEASE] ACh: tonic_drive {original} → {pop.tonic_drive} (factor={factor:.2f})")
        
        # GABA
        if abs(disease_profile.gaba_deficit) > 0.01:
            pop = self.populations[Neuromodulator.GABA]
            factor = 1.0 - disease_profile.gaba_deficit
            original = pop.tonic_drive
            pop.tonic_drive = int(pop.tonic_drive * factor)
            if self.debug:
                print(f"[DISEASE] GABA: tonic_drive {original} → {pop.tonic_drive} (factor={factor:.2f})")
        
        # Glutamate
        if abs(disease_profile.glutamate_deficit) > 0.01:
            pop = self.populations[Neuromodulator.GLUTAMATE]
            factor = 1.0 - disease_profile.glutamate_deficit
            original = pop.tonic_drive
            pop.tonic_drive = int(pop.tonic_drive * factor)
            if self.debug:
                print(f"[DISEASE] Glu: tonic_drive {original} → {pop.tonic_drive} (factor={factor:.2f})")
    
    def get_all_concentrations(self) -> Dict[str, float]:
        """Get all NT concentrations as dictionary."""
        return {
            '5HT': self.populations[Neuromodulator.SEROTONIN].get_concentration_float(),
            'DA': self.populations[Neuromodulator.DOPAMINE].get_concentration_float(),
            'NE': self.populations[Neuromodulator.NORADRENALINE].get_concentration_float(),
            'ACh': self.populations[Neuromodulator.ACETYLCHOLINE].get_concentration_float(),
            'GABA': self.populations[Neuromodulator.GABA].get_concentration_float(),
            'Glu': self.populations[Neuromodulator.GLUTAMATE].get_concentration_float(),
        }
    
    @property
    def serotonin(self) -> float:
        """Get current serotonin concentration (0-1)."""
        return self.populations[Neuromodulator.SEROTONIN].get_concentration_float()
    
    @property
    def dopamine(self) -> float:
        """Get current dopamine concentration (0-1)."""
        return self.populations[Neuromodulator.DOPAMINE].get_concentration_float()
    
    @property
    def noradrenaline(self) -> float:
        """Get current noradrenaline concentration (0-1)."""
        return self.populations[Neuromodulator.NORADRENALINE].get_concentration_float()
    
    @property
    def acetylcholine(self) -> float:
        """Get current acetylcholine concentration (0-1)."""
        return self.populations[Neuromodulator.ACETYLCHOLINE].get_concentration_float()
    
    @property
    def gaba(self) -> float:
        """Get current GABA concentration (0-1)."""
        return self.populations[Neuromodulator.GABA].get_concentration_float()
    
    @property
    def glutamate(self) -> float:
        """Get current glutamate concentration (0-1)."""
        return self.populations[Neuromodulator.GLUTAMATE].get_concentration_float()



# ══════════════════════════════════════════════════════════════════════
# RECEPTOR MODULATION
# ══════════════════════════════════════════════════════════════════════

def calculate_receptor_modulation(neuron_type: NeuronType,
                                  nt_levels: Dict[str, float]) -> int:
    """
    Calculate total neuromodulation for a neuron based on NT levels.
    
    Args:
        neuron_type: Type of neuron
        nt_levels: NT concentrations (0-1)
        
    Returns:
        Modulation current (fixed-point int)
    """
    profile = RECEPTOR_PROFILES[neuron_type]
    total_modulation = 0.0
    
    # Serotonin
    ht_level = nt_levels.get('5HT', 0.5)
    total_modulation += profile.ht1a[0] * profile.ht1a[1] * profile.ht1a[2] * ht_level
    total_modulation += profile.ht2a[0] * profile.ht2a[1] * profile.ht2a[2] * ht_level
    total_modulation += profile.ht2c[0] * profile.ht2c[1] * profile.ht2c[2] * ht_level
    total_modulation += profile.ht3[0] * profile.ht3[1] * profile.ht3[2] * ht_level
    
    # Dopamine
    da_level = nt_levels.get('DA', 0.4)
    total_modulation += profile.d1[0] * profile.d1[1] * profile.d1[2] * da_level
    total_modulation += profile.d2[0] * profile.d2[1] * profile.d2[2] * da_level
    total_modulation += profile.d3[0] * profile.d3[1] * profile.d3[2] * da_level
    total_modulation += profile.d4[0] * profile.d4[1] * profile.d4[2] * da_level
    
    # Noradrenaline
    ne_level = nt_levels.get('NE', 0.45)
    total_modulation += profile.alpha1[0] * profile.alpha1[1] * profile.alpha1[2] * ne_level
    total_modulation += profile.alpha2[0] * profile.alpha2[1] * profile.alpha2[2] * ne_level
    total_modulation += profile.beta1[0] * profile.beta1[1] * profile.beta1[2] * ne_level
    total_modulation += profile.beta2[0] * profile.beta2[1] * profile.beta2[2] * ne_level
    
    # Acetylcholine
    ach_level = nt_levels.get('ACh', 0.5)
    total_modulation += profile.m1[0] * profile.m1[1] * profile.m1[2] * ach_level
    total_modulation += profile.m2[0] * profile.m2[1] * profile.m2[2] * ach_level
    total_modulation += profile.nicotinic[0] * profile.nicotinic[1] * profile.nicotinic[2] * ach_level
    
    # GABA
    gaba_level = nt_levels.get('GABA', 0.55)
    total_modulation += profile.gaba_a[0] * profile.gaba_a[1] * profile.gaba_a[2] * gaba_level
    total_modulation += profile.gaba_b[0] * profile.gaba_b[1] * profile.gaba_b[2] * gaba_level
    
    # Glutamate
    glu_level = nt_levels.get('Glu', 0.6)
    total_modulation += profile.ampa[0] * profile.ampa[1] * profile.ampa[2] * glu_level
    total_modulation += profile.nmda[0] * profile.nmda[1] * profile.nmda[2] * glu_level
    total_modulation += profile.mglur[0] * profile.mglur[1] * profile.mglur[2] * glu_level
    
    # Scale to fixed-point and add bias current
    # This becomes additional input current to the neuron
    modulation_current = int(total_modulation * 50)  # Scaling factor
    
    return modulation_current


if __name__ == "__main__":
    print("\n" + "="*70)
    print("LOIHI NEUROMODULATION - 6 NT System")
    print("="*70)
    
    # Create system
    system = NeuromodulationSystem(n_total_neurons=100000, debug=True)
    
    # Simulate for 1000 steps
    print("\n[TEST] Baseline dynamics (no drugs)")
    print("=" * 60)
    
    for t in range(100):
        conc = system.step()
        if t % 20 == 0:
            print(f"t={t:3d}: ", end="")
            for nt, level in conc.items():
                print(f"{nt.value}={level:.3f} ", end="")
            print()
    
    # Apply SSRI (blocks SERT)
    print("\n[TEST] After SSRI (SERT inhibition)")
    print("=" * 60)
    system.apply_drug({'SERT': 0.8})
    
    for t in range(100):
        conc = system.step()
        if t % 20 == 0:
            print(f"t={t:3d}: ", end="")
            for nt, level in conc.items():
                print(f"{nt.value}={level:.3f} ", end="")
            print()
    
    print("\n" + "="*70)
    print("READY FOR DRUG TRIALS")
    print("="*70)
