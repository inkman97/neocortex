"""
TRUE BIOLOGICAL NEUROMODULATION - 6 NT System (No Enum Duplication)

COMPLETE 6 NT SYSTEM - All Active and Implemented

FIXED: Drug application now uses consistent logic (= assignment instead of *=)
       to match the working SERT/DAT/NET pattern and prevent value degradation.

Principles:
1. Neuromodulatory neurons receive continuous brainstem/thalamic input
2. Disease = reduced/increased synaptic efficacy in these pathways
3. Drugs = block reuptake -> more NT at synapses -> higher postsynaptic response
4. Receptors = NT binds to specific receptors -> modulates neuronal properties
5. All effects emerge from real neural dynamics

NEUROTRANSMITTERS (6):
- Serotonin (5HT) - Mood, impulse control
- Dopamine (DA) - Reward, motivation, movement
- Noradrenaline (NE) - Arousal, attention, stress
- Acetylcholine (ACh) - Memory, learning
- GABA - Primary inhibitory NT
- Glutamate - Primary excitatory NT

ENUM: Imported from core.neuromodulation (no duplication!)

VERSION: 3.1 (Complete 6 NT, unified drug application logic)
"""
from core import CorticalLayer, NeuronType, Neuromodulator
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Import receptor system
try:
    from neuromodulator_receptors import (
        RECEPTOR_DATABASE,
        PYRAMIDAL_RECEPTORS,
        PV_RECEPTORS,
        SST_RECEPTORS,
        VIP_RECEPTORS,
        calculate_receptor_activation,
        calculate_neuronal_modulation
    )
    RECEPTORS_AVAILABLE = True
except ImportError:
    RECEPTORS_AVAILABLE = False
    print("[NEUROMOD] WARNING: Receptor system not available")

try:
    import torch
    TORCH_AVAILABLE = True
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
except:
    TORCH_AVAILABLE = False
    DEVICE = None



EFFECT_CAP = 0.95
D2_PARTIAL_BASELINE_DA = 0.50


@dataclass(frozen=True)
class ReuptakeBlock:
    """A transporter blocker: reuptake drops to 1 - min(cap, potency * factor)."""
    attr: str
    cap: float
    factor: float


@dataclass(frozen=True)
class EfficacyShift:
    """A receptor mechanism that moves a postsynaptic efficacy off its baseline."""
    attr: str
    cap: float
    factor: float
    scale: float
    increases: bool


@dataclass(frozen=True)
class ConcentrationBoost:
    """A mechanism that adds directly to a neurotransmitter concentration."""
    attr: str
    cap: float
    factor: float
    scale: float


@dataclass(frozen=True)
class PoolContribution:
    """One mechanism's share of a pooled effect."""
    pool: str
    cap: float
    factor: float
    scale: float


@dataclass(frozen=True)
class PooledEffect:
    """Where a pool is written once every contribution has been summed."""
    attr: str
    baseline_attr: str
    increases: bool


REUPTAKE_BLOCKS = {
    "SERT_inhibition": ReuptakeBlock("serotonin_reuptake", 0.85, 1.3),
    "DAT_inhibition": ReuptakeBlock("dopamine_reuptake", 0.85, 1.3),
    "NET_inhibition": ReuptakeBlock("noradrenaline_reuptake", 0.85, 1.3),
    "GAT_inhibition": ReuptakeBlock("gaba_reuptake", 0.80, 1.2),
}

EFFICACY_SHIFTS = {
    "GABA_A_PAM": EfficacyShift("gaba_efficacy", 0.85, 1.2, 0.6, increases=True),
    "GABA_A_modulation": EfficacyShift("gaba_efficacy", 0.85, 1.2, 0.6, increases=True),
    "NMDA_antagonism": EfficacyShift("glutamate_efficacy", 0.70, 1.1, 0.4, increases=False),
    "D2_antagonism": EfficacyShift("dopamine_efficacy", 0.85, 1.3, 0.6, increases=False),
    "D3_antagonism": EfficacyShift("dopamine_efficacy", 0.85, 1.3, 0.6, increases=False),
    "HT2A_antagonism": EfficacyShift("serotonin_efficacy", 0.85, 1.3, 0.3, increases=False),
}

CONCENTRATION_BOOSTS = {
    "D2_agonism": ConcentrationBoost("dopamine_concentration", 0.8, 1.2, 0.25),
    "D3_agonism": ConcentrationBoost("dopamine_concentration", 0.8, 1.2, 0.25),
    "HT1A_agonism": ConcentrationBoost("serotonin_concentration", 0.8, 1.2, 0.20),
}

ACCUMULATING_MECHANISMS = {
    "GABA_transaminase_inhibition": (
        PoolContribution("clearance_gaba", 0.75, 0.7, 1.0),
    ),
    "glutamate_release_inhibition": (
        PoolContribution("glu_release", 0.70, 0.8, 0.5),
    ),
    "voltage_gated_sodium_blocker": (
        PoolContribution("glu_release", 0.70, 0.8, 0.4),
    ),
    "alpha2delta_calcium_channel_blocker": (
        PoolContribution("glu_release", 0.70, 0.8, 0.5),
        PoolContribution("gaba_release", 0.70, 0.8, 0.2),
    ),
    "MAO_A_inhibition": (
        PoolContribution("clearance_5ht", 0.8, 0.6, 1.0),
        PoolContribution("clearance_ne", 0.8, 0.6, 1.0),
        PoolContribution("clearance_da", 0.8, 0.6, 0.5),
    ),
    "MAO_B_inhibition": (
        PoolContribution("clearance_da", 0.8, 0.6, 1.0),
    ),
    "AChE_inhibition": (
        PoolContribution("clearance_ach", 0.9, 0.7, 1.0),
    ),
    "ALPHA2_antagonism": (
        PoolContribution("ne_release_boost", 0.8, 1.2, 0.4),
    ),
}

ACCUMULATED_EFFECTS = {
    "glu_release": PooledEffect("release_glu", "baseline_release_glu", increases=False),
    "gaba_release": PooledEffect("release_gaba", "baseline_release_gaba", increases=False),
    "ne_release_boost": PooledEffect("release_ne", "baseline_release_ne", increases=True),
    "clearance_5ht": PooledEffect("baseline_clearance_5ht", "baseline_clearance_5ht_initial", increases=False),
    "clearance_da": PooledEffect("baseline_clearance_da", "baseline_clearance_da_initial", increases=False),
    "clearance_ne": PooledEffect("baseline_clearance_ne", "baseline_clearance_ne_initial", increases=False),
    "clearance_ach": PooledEffect("baseline_clearance_ach", "baseline_clearance_ach_initial", increases=False),
    "clearance_gaba": PooledEffect("baseline_clearance_gaba", "baseline_clearance_gaba_initial", increases=False),
}


class BiologicalNeuromodulation:
    """
    Biologically accurate neuromodulation with complete 6 NT system.

    Key mechanisms:
    - Neuromodulatory neurons get tonic drive (simulates brainstem input)
    - Output is proportional to firing rate
    - Disease reduces/increases synaptic efficacy
    - Drugs block reuptake -> accumulation
    - GABA/Glutamate added for E/I balance
    """

    def __init__(self, brain, debug=False):
        self.brain = brain
        self.debug = debug

        # IDENTIFY NEUROMODULATORY POPULATIONS (DISTRIBUTED)
        n_cols = len(brain.columns)

        if debug:
            print(f"[NEUROMOD] Brain has {n_cols} columns, {brain.total_neurons} total neurons")

        if n_cols == 0:
            raise ValueError("[NEUROMOD] ERROR: Brain has no columns!")

        n_per_type = max(30, brain.total_neurons // 200)

        # Distribute neurons across ALL available columns
        self.serotonin_neurons = self._select_neurons_distributed(n_per_type, "5HT")
        self.dopamine_neurons = self._select_neurons_distributed(int(n_per_type * 1.2), "DA")
        self.noradrenaline_neurons = self._select_neurons_distributed(int(n_per_type * 0.8), "NE")
        self.acetylcholine_neurons = self._select_neurons_distributed(n_per_type, "ACh")
        self.gaba_neurons = self._select_neurons_distributed(int(n_per_type * 1.5), "GABA")
        self.glutamate_neurons = self._select_neurons_distributed(int(n_per_type * 1.3), "Glu")

        if debug:
            print(f"[NEUROMOD] Populations: 5HT={len(self.serotonin_neurons)}, "
                  f"DA={len(self.dopamine_neurons)}, NE={len(self.noradrenaline_neurons)}, "
                  f"ACh={len(self.acetylcholine_neurons)}, "
                  f"GABA={len(self.gaba_neurons)}, Glu={len(self.glutamate_neurons)}")

            # CRITICAL CHECK
            if len(self.gaba_neurons) == 0:
                print(f"[NEUROMOD] ERROR: No GABA neurons selected!")
            if len(self.glutamate_neurons) == 0:
                print(f"[NEUROMOD] ERROR: No Glutamate neurons selected!")

        # SYNAPTIC PARAMETERS (affected by disease)
        self.serotonin_efficacy = 1.0
        self.dopamine_efficacy = 1.0
        self.noradrenaline_efficacy = 1.0
        self.acetylcholine_efficacy = 1.0
        self.gaba_efficacy = 1.0
        self.glutamate_efficacy = 1.0

        # REUPTAKE (affected by drugs)
        self.serotonin_reuptake = 1.0
        self.dopamine_reuptake = 1.0
        self.noradrenaline_reuptake = 1.0
        self.gaba_reuptake = 1.0
        self.glutamate_reuptake = 1.0

        # TONIC DRIVE
        self.tonic_drive = 25.0

        # CONCENTRATIONS
        self.serotonin_concentration = 0.0
        self.dopamine_concentration = 0.0
        self.noradrenaline_concentration = 0.0
        self.acetylcholine_concentration = 0.0
        self.gaba_concentration = 0.0
        self.glutamate_concentration = 0.0

        # RELEASE/CLEARANCE RATES - BASELINE VALUES
        self.release_5ht = 0.05
        self.release_da = 0.03
        self.release_ne = 0.04
        self.release_ach = 0.04
        self.release_gaba = 0.08
        self.release_glu = 0.10

        self.baseline_clearance_5ht = 0.012
        self.baseline_clearance_da = 0.020
        self.baseline_clearance_ne = 0.016
        self.baseline_clearance_ach = 0.030
        self.baseline_clearance_gaba = 0.035
        self.baseline_clearance_glu = 0.040

        # STORE BASELINE VALUES FOR DRUG APPLICATION (NEW!)
        # These are used to reset parameters before applying drug effects
        self.baseline_release_5ht = self.release_5ht
        self.baseline_release_da = self.release_da
        self.baseline_release_ne = self.release_ne
        self.baseline_release_ach = self.release_ach
        self.baseline_release_gaba = self.release_gaba
        self.baseline_release_glu = self.release_glu

        self.baseline_clearance_5ht_initial = self.baseline_clearance_5ht
        self.baseline_clearance_da_initial = self.baseline_clearance_da
        self.baseline_clearance_ne_initial = self.baseline_clearance_ne
        self.baseline_clearance_ach_initial = self.baseline_clearance_ach
        self.baseline_clearance_gaba_initial = self.baseline_clearance_gaba
        self.baseline_clearance_glu_initial = self.baseline_clearance_glu

        if debug:
            print(f"[NEUROMOD] Initialized 6 NT system with tonic drive={self.tonic_drive:.1f} pA")

        self._inject_tonic_drive()

    def _select_neurons_distributed(self, n_total: int, nt_name: str) -> List[Tuple[int, CorticalLayer, NeuronType, int]]:
        """
        Select neurons distributed across ALL columns.

        This ensures GABA and Glutamate neurons are always found,
        even if the brain has fewer than 6 columns.
        """
        selected = []
        n_cols = len(self.brain.columns)

        if n_cols == 0:
            if self.debug:
                print(f"[NEUROMOD] {nt_name}: No columns available!")
            return []

        # Distribute evenly across columns
        n_per_col = max(1, n_total // n_cols)
        remainder = n_total % n_cols

        for col_idx in range(n_cols):
            # Give remainder neurons to first columns
            n_from_this_col = n_per_col + (1 if col_idx < remainder else 0)

            col = self.brain.columns[col_idx]

            # Try to get from L2/3 pyramidal neurons
            if CorticalLayer.L2_3 in col.layers:
                if NeuronType.PYRAMIDAL in col.layers[CorticalLayer.L2_3]:
                    group = col.layers[CorticalLayer.L2_3][NeuronType.PYRAMIDAL]
                    actual_n = min(n_from_this_col, group.n)

                    for i in range(actual_n):
                        selected.append((col_idx, CorticalLayer.L2_3, NeuronType.PYRAMIDAL, i))

                    if len(selected) >= n_total:
                        break

        if self.debug:
            print(f"[NEUROMOD] {nt_name}: Selected {len(selected)}/{n_total} neurons from {n_cols} columns")

        return selected

    def _select_neurons(self, col_idx: int, n: int) -> List[Tuple[int, CorticalLayer, NeuronType, int]]:
        """Select neurons from a column."""
        if col_idx >= len(self.brain.columns):
            return []

        col = self.brain.columns[col_idx]
        selected = []

        if CorticalLayer.L2_3 in col.layers:
            if NeuronType.PYRAMIDAL in col.layers[CorticalLayer.L2_3]:
                group = col.layers[CorticalLayer.L2_3][NeuronType.PYRAMIDAL]
                actual_n = min(n, group.n)
                for i in range(actual_n):
                    selected.append((col_idx, CorticalLayer.L2_3, NeuronType.PYRAMIDAL, i))

        return selected

    def _inject_tonic_drive(self):
        """Inject constant current to neuromodulatory neurons."""

        def inject_to_population(neurons_list, efficacy, name="UNKNOWN"):
            injected = 0

            for col_idx, layer, neuron_type, local_idx in neurons_list:
                if col_idx >= len(self.brain.columns):
                    continue

                col = self.brain.columns[col_idx]

                if layer not in col.layers:
                    continue
                if neuron_type not in col.layers[layer]:
                    continue

                group = col.layers[layer][neuron_type]

                if not hasattr(group, 'I_tonic'):
                    continue

                if local_idx >= group.n:
                    continue

                current = self.tonic_drive * efficacy

                if name == "DA":
                    current *= 1.4
                elif name == "GABA":
                    current *= 1.2
                elif name == "Glu":
                    current *= 0.9

                try:
                    group.I_tonic[local_idx] = current
                    injected += 1
                except Exception as e:
                    if self.debug:
                        print(f"[INJECT-ERROR] {name}: {e}")

            return injected

        inj_5ht = inject_to_population(self.serotonin_neurons, self.serotonin_efficacy, "5HT")
        inj_da = inject_to_population(self.dopamine_neurons, self.dopamine_efficacy, "DA")
        inj_ne = inject_to_population(self.noradrenaline_neurons, self.noradrenaline_efficacy, "NE")
        inj_ach = inject_to_population(self.acetylcholine_neurons, self.acetylcholine_efficacy, "ACh")
        inj_gaba = inject_to_population(self.gaba_neurons, self.gaba_efficacy, "GABA")
        inj_glu = inject_to_population(self.glutamate_neurons, self.glutamate_efficacy, "Glu")

        if self.debug:
            print(f"[NEUROMOD] Injected: 5HT={inj_5ht}, DA={inj_da}, NE={inj_ne}, "
                  f"ACh={inj_ach}, GABA={inj_gaba}, Glu={inj_glu}")

    def _count_spikes(self, neurons_list: List[Tuple[int, CorticalLayer, NeuronType, int]]) -> int:
        """Count how many neurons in population are spiking."""
        spike_count = 0

        for col_idx, layer, neuron_type, local_idx in neurons_list:
            if col_idx >= len(self.brain.columns):
                continue

            col = self.brain.columns[col_idx]

            if layer not in col.layers:
                continue
            if neuron_type not in col.layers[layer]:
                continue

            group = col.layers[layer][neuron_type]
            spikes = group.spike

            try:
                if TORCH_AVAILABLE and hasattr(spikes, 'cpu'):
                    spikes = spikes.cpu().numpy()
                elif hasattr(spikes, 'numpy'):
                    spikes = spikes.numpy()
            except:
                pass

            try:
                if local_idx < len(spikes):
                    if spikes[local_idx]:
                        spike_count += 1
            except:
                pass

        return spike_count

    def update(
        self,
        reward: float = 0.0,
        punishment: float = 0.0,
        salience: float = 0.0,
        novelty: float = 0.0,
        effort: float = 0.0,
        dt: float = 1.0
    ):
        """Update neuromodulator concentrations based on neural activity."""

        # Count spikes
        serotonin_spikes = self._count_spikes(self.serotonin_neurons)
        dopamine_spikes = self._count_spikes(self.dopamine_neurons)
        noradrenaline_spikes = self._count_spikes(self.noradrenaline_neurons)
        acetylcholine_spikes = self._count_spikes(self.acetylcholine_neurons)
        gaba_spikes = self._count_spikes(self.gaba_neurons)
        glutamate_spikes = self._count_spikes(self.glutamate_neurons)

        if self.debug:
            print(f"[NEUROMOD] Spikes: 5HT={serotonin_spikes}/{len(self.serotonin_neurons)}, "
                  f"DA={dopamine_spikes}/{len(self.dopamine_neurons)}, "
                  f"NE={noradrenaline_spikes}/{len(self.noradrenaline_neurons)}, "
                  f"ACh={acetylcholine_spikes}/{len(self.acetylcholine_neurons)}, "
                  f"GABA={gaba_spikes}/{len(self.gaba_neurons)}, "
                  f"Glu={glutamate_spikes}/{len(self.glutamate_neurons)}")

        # Calculate release
        def calc_release(spikes, n_neurons, release_rate, efficacy):
            if n_neurons > 0:
                return (spikes / n_neurons) * release_rate * efficacy
            return 0.0

        serotonin_release = calc_release(serotonin_spikes, len(self.serotonin_neurons),
                                        self.release_5ht, self.serotonin_efficacy)
        dopamine_release = calc_release(dopamine_spikes, len(self.dopamine_neurons),
                                       self.release_da, self.dopamine_efficacy)
        noradrenaline_release = calc_release(noradrenaline_spikes, len(self.noradrenaline_neurons),
                                            self.release_ne, self.noradrenaline_efficacy)
        acetylcholine_release = calc_release(acetylcholine_spikes, len(self.acetylcholine_neurons),
                                            self.release_ach, self.acetylcholine_efficacy)
        gaba_release = calc_release(gaba_spikes, len(self.gaba_neurons),
                                    self.release_gaba, self.gaba_efficacy)
        glutamate_release = calc_release(glutamate_spikes, len(self.glutamate_neurons),
                                        self.release_glu, self.glutamate_efficacy)

        # Calculate clearance
        serotonin_clearance = self.serotonin_concentration * (
            self.serotonin_reuptake * 0.025 + self.baseline_clearance_5ht
        )
        dopamine_clearance = self.dopamine_concentration * (
            self.dopamine_reuptake * 0.035 + self.baseline_clearance_da
        )
        noradrenaline_clearance = self.noradrenaline_concentration * (
            self.noradrenaline_reuptake * 0.030 + self.baseline_clearance_ne
        )
        acetylcholine_clearance = self.acetylcholine_concentration * (
            0.08 + self.baseline_clearance_ach
        )
        gaba_clearance = self.gaba_concentration * (
            self.gaba_reuptake * 0.040 + self.baseline_clearance_gaba
        )
        glutamate_clearance = self.glutamate_concentration * (
            self.glutamate_reuptake * 0.045 + self.baseline_clearance_glu
        )

        # Update concentrations
        self.serotonin_concentration += serotonin_release - serotonin_clearance
        self.dopamine_concentration += dopamine_release - dopamine_clearance
        self.noradrenaline_concentration += noradrenaline_release - noradrenaline_clearance
        self.acetylcholine_concentration += acetylcholine_release - acetylcholine_clearance
        self.gaba_concentration += gaba_release - gaba_clearance
        self.glutamate_concentration += glutamate_release - glutamate_clearance

        # Clamp
        self.serotonin_concentration = np.clip(self.serotonin_concentration, 0.0, 1.0)
        self.dopamine_concentration = np.clip(self.dopamine_concentration, 0.0, 1.0)
        self.noradrenaline_concentration = np.clip(self.noradrenaline_concentration, 0.0, 1.0)
        self.acetylcholine_concentration = np.clip(self.acetylcholine_concentration, 0.0, 1.0)
        self.gaba_concentration = np.clip(self.gaba_concentration, 0.0, 1.0)
        self.glutamate_concentration = np.clip(self.glutamate_concentration, 0.0, 1.0)

        # Re-inject tonic drive
        self._inject_tonic_drive()

        # Receptor effects
        if RECEPTORS_AVAILABLE:
            self.receptor_effects = {
                'PYRAMIDAL': self.calculate_receptor_effects(NeuronType.PYRAMIDAL),
                'PV': self.calculate_receptor_effects(NeuronType.PV),
                'SST': self.calculate_receptor_effects(NeuronType.SST),
                'VIP': self.calculate_receptor_effects(NeuronType.VIP),
                'STELLATE': self.calculate_receptor_effects(NeuronType.PYRAMIDAL)
            }

            if self.debug:
                pyr = self.receptor_effects['PYRAMIDAL']
                print(f"[RECEPTORS] Pyramidal: exc={pyr['excitability_change']:+.3f}, "
                      f"gain={pyr['gain_change']:+.3f}, plasticity={pyr['plasticity_change']:+.3f}")
        else:
            self.receptor_effects = None

    def set_disease_state(self, disease_profile):
        """Apply disease by modifying synaptic efficacy (6 NT - UNIFIED CONVENTION)."""

        # UNIFIED CONVENTION: efficacy = 1.0 - deficit
        # Positive deficit (0.4) → efficacy 0.6 (reduced function)
        # Negative excess (-0.3) → efficacy 1.3 (enhanced function)

        if disease_profile.serotonin_deficit != 0:
            self.serotonin_efficacy = 1.0 - disease_profile.serotonin_deficit
            if self.debug:
                print(f"[DISEASE] Serotonin efficacy: {self.serotonin_efficacy:.2f}")

        if disease_profile.dopamine_deficit != 0:
            self.dopamine_efficacy = 1.0 - disease_profile.dopamine_deficit
            if self.debug:
                print(f"[DISEASE] Dopamine efficacy: {self.dopamine_efficacy:.2f}")

        if disease_profile.noradrenaline_deficit != 0:
            self.noradrenaline_efficacy = 1.0 - disease_profile.noradrenaline_deficit
            if self.debug:
                print(f"[DISEASE] Noradrenaline efficacy: {self.noradrenaline_efficacy:.2f}")

        if disease_profile.acetylcholine_deficit != 0:
            self.acetylcholine_efficacy = 1.0 - disease_profile.acetylcholine_deficit
            if self.debug:
                print(f"[DISEASE] Acetylcholine efficacy: {self.acetylcholine_efficacy:.2f}")

        # GABA (NEW)
        if hasattr(disease_profile, 'gaba_deficit') and disease_profile.gaba_deficit != 0:
            self.gaba_efficacy = 1.0 - disease_profile.gaba_deficit
            if self.debug:
                print(f"[DISEASE] GABA efficacy: {self.gaba_efficacy:.2f}")

        # GLUTAMATE (NEW)
        if hasattr(disease_profile, 'glutamate_deficit') and disease_profile.glutamate_deficit != 0:
            self.glutamate_efficacy = 1.0 - disease_profile.glutamate_deficit
            if self.debug:
                print(f"[DISEASE] Glutamate efficacy: {self.glutamate_efficacy:.2f}")

    def apply_drug_to_synapses(self, drug_mechanisms: Dict[str, float]):
        """Translate molecular mechanisms into synaptic parameters.

        Mechanisms that set a parameter outright are applied as they are read.
        Mechanisms that share a parameter accumulate first and are applied once
        at the end, so two drugs hitting the same clearance path add up instead
        of overwriting each other.
        """
        print(f"    [APPLY-DRUG] Processing {len(drug_mechanisms)} mechanisms")

        totals = dict.fromkeys(ACCUMULATED_EFFECTS, 0.0)

        for mechanism, potency in drug_mechanisms.items():
            self._apply_single_mechanism(mechanism, potency, totals)

        self._apply_accumulated_effects(totals)

    def _apply_single_mechanism(self, mechanism: str, potency: float, totals: Dict[str, float]):
        if mechanism in REUPTAKE_BLOCKS:
            block = REUPTAKE_BLOCKS[mechanism]
            setattr(self, block.attr, 1.0 - min(block.cap, potency * block.factor))
            print(f"    [APPLY-DRUG] {mechanism}: reuptake={getattr(self, block.attr):.3f}")
            return

        if mechanism in EFFICACY_SHIFTS:
            shift = EFFICACY_SHIFTS[mechanism]
            magnitude = min(shift.cap, potency * shift.factor) * shift.scale
            setattr(self, shift.attr, 1.0 + magnitude if shift.increases else 1.0 - magnitude)
            print(f"    [APPLY-DRUG] {mechanism}: efficacy={getattr(self, shift.attr):.3f}")
            return

        if mechanism in CONCENTRATION_BOOSTS:
            boost_spec = CONCENTRATION_BOOSTS[mechanism]
            boost = min(boost_spec.cap, potency * boost_spec.factor) * boost_spec.scale
            setattr(self, boost_spec.attr, np.clip(getattr(self, boost_spec.attr) + boost, 0.0, 1.0))
            print(f"    [APPLY-DRUG] {mechanism}: boost +{boost:.3f}")
            return

        if mechanism in ACCUMULATING_MECHANISMS:
            for contribution in ACCUMULATING_MECHANISMS[mechanism]:
                totals[contribution.pool] += min(contribution.cap, potency * contribution.factor) * contribution.scale
            print(f"    [APPLY-DRUG] {mechanism}: accumulated")
            return

        if mechanism == "DA_precursor":
            self._apply_da_precursor(potency)
        elif mechanism == "D2_partial_agonism":
            self._apply_d2_partial_agonism(potency)

    def _apply_da_precursor(self, potency: float):
        """Levodopa-like: raise dopamine synthesis, and nudge DA neuron firing."""
        synthesis_boost = min(2.5, 1.0 + potency * 2.0)
        self.release_da = self.baseline_release_da * synthesis_boost

        for col_idx, layer, neuron_type, local_idx in self.dopamine_neurons:
            if col_idx >= len(self.brain.columns):
                continue
            col = self.brain.columns[col_idx]
            if layer not in col.layers or neuron_type not in col.layers[layer]:
                continue
            group = col.layers[layer][neuron_type]
            if hasattr(group, 'I_tonic') and local_idx < group.n:
                baseline_current = self.tonic_drive * self.dopamine_efficacy * 1.4
                group.I_tonic[local_idx] = baseline_current * (1.0 + potency * 0.5)

        print(f"    [APPLY-DRUG] DA_precursor: release={self.release_da:.4f} "
              f"(boost={synthesis_boost:.2f}x)")

    def _apply_d2_partial_agonism(self, potency: float):
        """Aripiprazole-like: pull dopamine back toward baseline from either side."""
        current_da = self.dopamine_concentration
        stabilization = potency * 0.8

        if current_da > D2_PARTIAL_BASELINE_DA:
            delta = -(current_da - D2_PARTIAL_BASELINE_DA) * stabilization * 0.4
        else:
            delta = (D2_PARTIAL_BASELINE_DA - current_da) * stabilization * 0.3

        self.dopamine_concentration = np.clip(current_da + delta, 0.0, 1.0)
        print(f"    [APPLY-DRUG] D2_partial: shift {delta:+.3f}")

    def _apply_accumulated_effects(self, totals: Dict[str, float]):
        """Write the pooled effects onto the model, or restore the baseline."""
        for pool, effect in ACCUMULATED_EFFECTS.items():
            total = totals[pool]
            baseline = getattr(self, effect.baseline_attr)

            if total <= 0:
                setattr(self, effect.attr, baseline)
                continue

            if effect.increases:
                setattr(self, effect.attr, baseline * (1.0 + total))
            else:
                setattr(self, effect.attr, baseline * (1.0 - min(EFFECT_CAP, total)))

            print(f"    [APPLY-DRUG] {pool}: {getattr(self, effect.attr):.4f}")

    def warmup(self, steps: int = 500):
        """Warmup to reach steady state."""
        if self.debug:
            print(f"[WARMUP] Running {steps} steps...")

        for step in range(steps):
            self.brain.step(dt=1.0)
            self.update(dt=1.0)

            if self.debug and step % 100 == 0:
                print(f"  Step {step}: 5HT={self.serotonin_concentration:.3f}, "
                      f"DA={self.dopamine_concentration:.3f}, "
                      f"NE={self.noradrenaline_concentration:.3f}, "
                      f"ACh={self.acetylcholine_concentration:.3f}, "
                      f"GABA={self.gaba_concentration:.3f}, "
                      f"Glu={self.glutamate_concentration:.3f}")

        if self.debug:
            print(f"[WARMUP] Complete: All 6 NT at steady state")

    def get_levels(self) -> Dict[str, float]:
        """Get current NT concentrations for all 6 NT."""
        return {
            'serotonin': float(self.serotonin_concentration),
            'dopamine': float(self.dopamine_concentration),
            'noradrenaline': float(self.noradrenaline_concentration),
            'acetylcholine': float(self.acetylcholine_concentration),
            'gaba': float(self.gaba_concentration),
            'glutamate': float(self.glutamate_concentration)
        }

    def calculate_receptor_effects(self, neuron_type: NeuronType) -> Dict[str, float]:
        """Calculate receptor-mediated modulation."""
        if not RECEPTORS_AVAILABLE:
            ei_balance = self.gaba_concentration - self.glutamate_concentration
            return {
                'excitability_change': ei_balance * 0.3,
                'gain_change': self.serotonin_concentration * 0.2,
                'plasticity_change': self.dopamine_concentration * 0.3
            }

        # Full receptor system implementation...
        if neuron_type == NeuronType.PYRAMIDAL:
            receptor_list = PYRAMIDAL_RECEPTORS
        elif neuron_type == NeuronType.PV:
            receptor_list = PV_RECEPTORS
        elif neuron_type == NeuronType.SST:
            receptor_list = SST_RECEPTORS
        elif neuron_type == NeuronType.VIP:
            receptor_list = VIP_RECEPTORS
        else:
            receptor_list = PYRAMIDAL_RECEPTORS

        activations = {}
        for expr in receptor_list:
            receptor = expr.receptor
            params = RECEPTOR_DATABASE[receptor]

            if params.family.value == "serotonin":
                nt_conc = self.serotonin_concentration
            elif params.family.value == "dopamine":
                nt_conc = self.dopamine_concentration
            elif params.family.value == "noradrenaline":
                nt_conc = self.noradrenaline_concentration
            elif "acetylcholine" in params.family.value:
                nt_conc = self.acetylcholine_concentration
            elif "gaba" in params.family.value:
                nt_conc = self.gaba_concentration
            elif "glutamate" in params.family.value:
                nt_conc = self.glutamate_concentration
            else:
                continue

            activation = calculate_receptor_activation(
                nt_conc, params, expr.density
            )
            activations[receptor] = activation

        return calculate_neuronal_modulation(activations, RECEPTOR_DATABASE)

    # Compatibility properties
    @property
    def serotonin(self) -> float:
        return self.serotonin_concentration

    @property
    def dopamine(self) -> float:
        return self.dopamine_concentration

    @property
    def noradrenaline(self) -> float:
        return self.noradrenaline_concentration

    @property
    def acetylcholine(self) -> float:
        return self.acetylcholine_concentration

    @property
    def gaba(self) -> float:
        return self.gaba_concentration

    @property
    def glutamate(self) -> float:
        return self.glutamate_concentration

    @property
    def targets(self):
        """Legacy compatibility."""
        return {
            Neuromodulator.SEROTONIN: 0.5,
            Neuromodulator.DOPAMINE: 0.5,
            Neuromodulator.NORADRENALINE: 0.5,
            Neuromodulator.ACETYLCHOLINE: 0.5,
            Neuromodulator.GABA: 0.6,
            Neuromodulator.GLUTAMATE: 0.5
        }

    def get(self, neurotransmitter: Neuromodulator) -> float:
        """Get concentration for specific NT using enum from core."""
        levels = self.get_levels()
        return levels.get(neurotransmitter.value, 0.5)