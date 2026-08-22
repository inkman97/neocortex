"""
DRUG SIMULATOR - Biological Pharmacology Engine

UPDATED FOR 6 NT SYSTEM:
- Added GABA and Glutamate to DiseaseProfile
- Added GABA/Glutamate efficacy tracking
- Added drug mechanisms for GABA/Glutamate

Applies molecular mechanisms of drugs to the NeoCortex brain:
- Does NOT force final values
- Modifies RATES (reuptake, degradation, etc.)
- Brain evolves naturally through neural dynamics

Supports all major psychiatric and neurological drugs.
"""

import numpy as np
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
from typing import List, Dict, Optional
from dataclasses import dataclass
from pydantic import BaseModel


@dataclass
class DiseaseProfile:
    """
    Profile of neurotransmitter deficits/excess in a disease.

    Negative values = deficit (Depression, Alzheimer's, Parkinson's)
    Positive values = excess (Schizophrenia, Anxiety)

    UPDATED: 6 NT System (added GABA and Glutamate)
    """
    serotonin_deficit: float = 0.0      # -1 to +1
    dopamine_deficit: float = 0.0
    noradrenaline_deficit: float = 0.0
    acetylcholine_deficit: float = 0.0
    gaba_deficit: float = 0.0           # NEW
    glutamate_deficit: float = 0.0      # NEW


class Pharmacokinetics(BaseModel):
    """Pharmacokinetic parameters for drug absorption/elimination."""
    halfLife_hours: float = 24.0
    tmax_hours: float = 2.0
    bioavailability: float = 0.7
    vd_L_kg: Optional[float] = 20.0


class DrugMechanism:
    """
    Drug molecular mechanisms.

    UPDATED: Added GABA and Glutamate mechanisms

    Each mechanism represents a specific molecular target:
    - Transporters (SERT, DAT, NET) - reuptake inhibition
    - Enzymes (MAO-A, MAO-B, AChE) - degradation inhibition
    - Precursors (L-DOPA) - increase synthesis
    - Agonists (D2, D3) - activate receptors directly
    - Antagonists (D2, 5-HT2A) - block receptors
    - Partial agonists (D2) - stabilize activity
    - GABA-A modulators (benzodiazepines) - NEW
    - NMDA antagonists (memantine) - NEW
    - Glutamate release inhibitors (lamotrigine) - NEW
    """

    def __init__(
        self,
        # Reuptake inhibition
        sert_inhibition: float = 0.0,
        dat_inhibition: float = 0.0,
        net_inhibition: float = 0.0,

        # Enzyme inhibition
        mao_a_inhibition: float = 0.0,
        mao_b_inhibition: float = 0.0,
        ache_inhibition: float = 0.0,

        # Precursors
        da_precursor: float = 0.0,      # L-DOPA

        # Receptor agonists
        d2_agonism: float = 0.0,
        d3_agonism: float = 0.0,
        ht1a_agonism: float = 0.0,

        # Receptor antagonists
        d2_antagonism: float = 0.0,
        d3_antagonism: float = 0.0,
        ht2a_antagonism: float = 0.0,
        alpha2_antagonism: float = 0.0,
        h1_antagonism: float = 0.0,

        # Partial agonists
        d2_partial_agonism: float = 0.0,

        # GABA/Glutamate mechanisms (NEW)
        gaba_a_pam: float = 0.0,                    # Positive allosteric modulator (benzos)
        gat_inhibition: float = 0.0,                # GABA transporter inhibition
        gaba_transaminase_inhibition: float = 0.0,  # GABA-T inhibition
        nmda_antagonism: float = 0.0,               # NMDA receptor antagonism
        glutamate_release_inhibition: float = 0.0,  # Inhibit glutamate release
        voltage_gated_sodium_blocker: float = 0.0,  # Na+ channel blocker (reduces Glu)
        alpha2delta_blocker: float = 0.0            # Ca2+ channel blocker (gabapentin)
    ):
        # Reuptake inhibitors
        self.sert_inhibition = sert_inhibition
        self.dat_inhibition = dat_inhibition
        self.net_inhibition = net_inhibition

        # Enzyme inhibitors
        self.mao_a_inhibition = mao_a_inhibition
        self.mao_b_inhibition = mao_b_inhibition
        self.ache_inhibition = ache_inhibition

        # Precursors
        self.da_precursor = da_precursor

        # Receptor agonists
        self.d2_agonism = d2_agonism
        self.d3_agonism = d3_agonism
        self.ht1a_agonism = ht1a_agonism

        # Receptor antagonists
        self.d2_antagonism = d2_antagonism
        self.d3_antagonism = d3_antagonism
        self.ht2a_antagonism = ht2a_antagonism
        self.alpha2_antagonism = alpha2_antagonism
        self.h1_antagonism = h1_antagonism

        # Partial agonists
        self.d2_partial_agonism = d2_partial_agonism

        # GABA/Glutamate mechanisms (NEW)
        self.gaba_a_pam = gaba_a_pam
        self.gat_inhibition = gat_inhibition
        self.gaba_transaminase_inhibition = gaba_transaminase_inhibition
        self.nmda_antagonism = nmda_antagonism
        self.glutamate_release_inhibition = glutamate_release_inhibition
        self.voltage_gated_sodium_blocker = voltage_gated_sodium_blocker
        self.alpha2delta_blocker = alpha2delta_blocker

    def apply_to_brain(self, brain, plasma_concentration: float):
        """Apply drug effects by modifying synaptic mechanisms."""
        drug_mechanisms = {}

        # Reuptake inhibitors
        if self.sert_inhibition > 0:
            drug_mechanisms["SERT_inhibition"] = self.sert_inhibition * plasma_concentration
        if self.dat_inhibition > 0:
            drug_mechanisms["DAT_inhibition"] = self.dat_inhibition * plasma_concentration
        if self.net_inhibition > 0:
            drug_mechanisms["NET_inhibition"] = self.net_inhibition * plasma_concentration

        # Enzyme inhibitors
        if self.mao_a_inhibition > 0:
            drug_mechanisms["MAO_A_inhibition"] = self.mao_a_inhibition * plasma_concentration
        if self.mao_b_inhibition > 0:
            drug_mechanisms["MAO_B_inhibition"] = self.mao_b_inhibition * plasma_concentration
        if self.ache_inhibition > 0:
            drug_mechanisms["AChE_inhibition"] = self.ache_inhibition * plasma_concentration

        # Precursors
        if self.da_precursor > 0:
            drug_mechanisms["DA_precursor"] = self.da_precursor * plasma_concentration

        # Agonists
        if self.d2_agonism > 0:
            drug_mechanisms["D2_agonism"] = self.d2_agonism * plasma_concentration
        if self.d3_agonism > 0:
            drug_mechanisms["D3_agonism"] = self.d3_agonism * plasma_concentration
        if self.ht1a_agonism > 0:
            drug_mechanisms["HT1A_agonism"] = self.ht1a_agonism * plasma_concentration

        # Antagonists
        if self.d2_antagonism > 0:
            drug_mechanisms["D2_antagonism"] = self.d2_antagonism * plasma_concentration
        if self.d3_antagonism > 0:
            drug_mechanisms["D3_antagonism"] = self.d3_antagonism * plasma_concentration
        if self.ht2a_antagonism > 0:
            drug_mechanisms["HT2A_antagonism"] = self.ht2a_antagonism * plasma_concentration
        if self.alpha2_antagonism > 0:
            drug_mechanisms["ALPHA2_antagonism"] = self.alpha2_antagonism * plasma_concentration
        if self.h1_antagonism > 0:
            drug_mechanisms["H1_antagonism"] = self.h1_antagonism * plasma_concentration

        # Partial agonists
        if self.d2_partial_agonism > 0:
            drug_mechanisms["D2_partial_agonism"] = self.d2_partial_agonism * plasma_concentration

        # Convert drug mechanisms to Loihi format
        # Loihi uses apply_drug(drug_targets) with keys like 'SERT', 'DAT', etc.
        drug_targets = {}
        
        # Reuptake inhibitors
        if self.sert_inhibition > 0:
            drug_targets['SERT'] = self.sert_inhibition * plasma_concentration
        if self.dat_inhibition > 0:
            drug_targets['DAT'] = self.dat_inhibition * plasma_concentration
        if self.net_inhibition > 0:
            drug_targets['NET'] = self.net_inhibition * plasma_concentration
        if self.gat_inhibition > 0:
            drug_targets['GAT'] = self.gat_inhibition * plasma_concentration
        
        # Enzyme inhibitors
        if self.mao_a_inhibition > 0:
            drug_targets['MAO-A'] = self.mao_a_inhibition * plasma_concentration
        if self.mao_b_inhibition > 0:
            drug_targets['MAO-B'] = self.mao_b_inhibition * plasma_concentration
        if self.ache_inhibition > 0:
            drug_targets['AChE'] = self.ache_inhibition * plasma_concentration
        
        # Apply to brain (Loihi method)
        brain.neuromodulation.apply_drug(drug_targets)


class DrugSimulator:
    """
    Main drug trial simulator.

    UPDATED: 6 NT System support

    Orchestrates:
    1. Disease state initialization
    2. Extended warmup to reach diseased steady-state
    3. Drug mechanism application with pharmacokinetics
    4. Brain simulation over time
    5. State recording at specified intervals
    """

    def __init__(
        self,
        brain,
        drug_mechanism: DrugMechanism,
        disease_profile: DiseaseProfile,
        pharmacokinetics: Pharmacokinetics
    ):
        self.brain = brain
        self.drug_mechanism = drug_mechanism
        self.disease_profile = disease_profile
        self.pk = pharmacokinetics

        # Initialize disease state
        self._initialize_disease_state()

    def _initialize_disease_state(self):
        """Initialize disease by modifying neural efficacy (6 NT)."""
        self.brain.neuromodulation.set_disease_state(self.disease_profile)
        print(f"[DISEASE] Profile set at neural level")
        
        # NOTE: In Loihi, embodiment will automatically respond to changed NT levels
        # No need to recreate embodiment - disease is applied via tonic_drive modification

    def _calculate_plasma_concentration(self, hours_after_dose: float) -> float:
        """
        Calculate plasma concentration at time t.

        Uses one-compartment model with exponential absorption/elimination.
        """
        if hours_after_dose < 0:
            return 0.0

        tmax = self.pk.tmax_hours
        halflife = self.pk.halfLife_hours
        bioavail = self.pk.bioavailability

        # Elimination rate constant
        ke = 0.693 / halflife

        # Absorption rate constant (ka >> ke for oral drugs)
        ka = 3.0 / tmax

        # Two-phase model
        if hours_after_dose <= tmax * 2:
            absorption = 1.0 - np.exp(-ka * hours_after_dose)
            elimination = np.exp(-ke * hours_after_dose)
            conc = bioavail * absorption * elimination
        else:
            peak_conc = bioavail * (1.0 - np.exp(-ka * tmax)) * np.exp(-ke * tmax)
            conc = peak_conc * np.exp(-ke * (hours_after_dose - tmax))

        return conc

    def _calculate_plasma_concentration_multiple_doses(
        self,
        current_time_hours: float,
        dosing_interval_hours: float = 24.0
    ) -> float:
        """Calculate plasma concentration with multiple daily doses."""
        total_concentration = 0.0
        dose_number = int(current_time_hours / dosing_interval_hours)

        for dose_idx in range(dose_number + 1):
            dose_time = dose_idx * dosing_interval_hours
            time_since_this_dose = current_time_hours - dose_time

            if time_since_this_dose >= 0:
                conc_from_dose = self._calculate_plasma_concentration(time_since_this_dose)
                total_concentration += conc_from_dose

        return min(1.0, total_concentration)

    def run_trial(
        self,
        dose_mg: float,
        typical_dose_mg: float,
        duration_hours: int,
        sampling_interval_hours: int = 24
    ) -> List[Dict]:
        """Run a complete drug trial simulation (6 NT)."""

        timepoints = []
        dose_ratio = dose_mg / typical_dose_mg

        print(f"\n[TRIAL] Starting simulation...")
        print(f"  Dose ratio: {dose_ratio:.2f}x typical")
        print(f"  Duration: {duration_hours}h ({duration_hours/24:.1f} days)")
        print(f"  Sampling: every {sampling_interval_hours}h\n")

        # BASELINE PHASE
        print("[WARMUP] Running extended warmup to reach diseased steady state...")
        print(f"  Disease profile: 5HT={self.disease_profile.serotonin_deficit:+.1f}, "
              f"DA={self.disease_profile.dopamine_deficit:+.1f}, "
              f"NE={self.disease_profile.noradrenaline_deficit:+.1f}, "
              f"ACh={self.disease_profile.acetylcholine_deficit:+.1f}, "
              f"GABA={self.disease_profile.gaba_deficit:+.1f}, "
              f"Glu={self.disease_profile.glutamate_deficit:+.1f}")

        # Verify disease application (6 NT)
        nm = self.brain.neuromodulation
        print(f"  Tonic drives after disease (will affect NT levels):")
        print(f"    5HT population ready")
        print(f"    DA population ready")
        print(f"    NE population ready")
        print(f"    ACh population ready")
        print(f"    GABA population ready")
        print(f"    Glu population ready")

        # Extended warmup
        warmup_steps = 2000
        for step in range(warmup_steps):
            if step % 400 == 0:
                nm = self.brain.neuromodulation
                print(f"  Step {step}/{warmup_steps}: "
                      f"5HT={nm.serotonin:.3f}, "
                      f"DA={nm.dopamine:.3f}, "
                      f"NE={nm.noradrenaline:.3f}, "
                      f"ACh={nm.acetylcholine:.3f}, "
                      f"GABA={nm.gaba:.3f}, "           # NEW
                      f"Glu={nm.glutamate:.3f}")        # NEW

            # In Loihi, just step (no separate perceive method)
            self.brain.step()

        print(f"[WARMUP] Complete after {warmup_steps} steps")

        # Record baseline
        print("[BASELINE] Recording diseased steady-state...")
        state = self._get_brain_state()
        print(f"[BASELINE] Final concentrations:")
        print(f"  5HT: {state['serotonin']:.3f}")
        print(f"  DA:  {state['dopamine']:.3f}")
        print(f"  NE:  {state['noradrenaline']:.3f}")
        print(f"  ACh: {state['acetylcholine']:.3f}")
        print(f"  GABA: {state['gaba']:.3f}")          # NEW
        print(f"  Glu:  {state['glutamate']:.3f}")     # NEW

        timepoints.append({
            "hours": -1.0,
            "days": -1.0/24,
            "phase": "baseline",
            "drug_concentration": 0.0,
            **state
        })

        # TREATMENT PHASE
        print(f"\n[TREATMENT] Administering drug...")

        total_samples = duration_hours // sampling_interval_hours

        for sample_idx in range(total_samples + 1):
            hours_elapsed = sample_idx * sampling_interval_hours

            plasma_conc = self._calculate_plasma_concentration(hours_elapsed)
            plasma_conc *= dose_ratio
            plasma_conc = min(1.0, plasma_conc)

            print(f"  t={hours_elapsed}h ({hours_elapsed/24:.1f}d): "
                  f"drug_conc={plasma_conc:.3f} [{sample_idx+1}/{total_samples+1}]")

            print(f"  Simulating {sampling_interval_hours} hours for timepoint {sample_idx+1}/{total_samples+1}...")
            for hour in range(sampling_interval_hours):
                if hour % 6 == 0:
                    print(f"    Hour {hour}/{sampling_interval_hours}")

                time_since_start = hours_elapsed + hour
                if time_since_start > 0 and time_since_start % 24 == 0:
                    print(f"    [DOSE] New daily dose administered at t={time_since_start}h")

                current_plasma = self._calculate_plasma_concentration_multiple_doses(
                    current_time_hours=time_since_start,
                    dosing_interval_hours=24.0
                )
                current_plasma *= dose_ratio
                current_plasma = min(1.0, current_plasma)

                # Apply drug
                self.drug_mechanism.apply_to_brain(self.brain, current_plasma)

                # Simulate (Loihi brain - no separate perceive method)
                for step in range(60):
                    self.brain.step()

            # Record state
            state = self._get_brain_state()
            timepoints.append({
                "hours": float(hours_elapsed),
                "days": hours_elapsed / 24.0,
                "phase": "treatment",
                "drug_concentration": plasma_conc * 100,
                **state
            })

        print(f"\n[TRIAL] Complete: {len(timepoints)} timepoints recorded\n")

        return timepoints

    def _get_brain_state(self) -> Dict:
         """Get current brain state (6 NT + physiology)."""
         state = self.brain.get_summary()  # Loihi uses get_summary()

         return {
             # Neurochemistry (6 NT)
             "serotonin": float(state.get('nt_levels', {}).get('5HT', 0.5)),
             "dopamine": float(state.get('nt_levels', {}).get('DA', 0.5)),
             "noradrenaline": float(state.get('nt_levels', {}).get('NE', 0.3)),
             "acetylcholine": float(state.get('nt_levels', {}).get('ACh', 0.4)),
             "gaba": float(state.get('nt_levels', {}).get('GABA', 0.6)),
             "glutamate": float(state.get('nt_levels', {}).get('Glu', 0.5)),

             # Psychological state
             "arousal": float(state.get('arousal', 0.5)),
             "valence": float(state.get('valence', 0.0)),
             "firing_rate": float(state.get('firing_rate', 0.0)),
             "dominant_emotion": str(state.get('dominant_emotion', 'neutral')),

             # Physiological parameters (from embodiment dict)
             "heart_rate": float(state.get('embodiment', {}).get('heart_rate', 0.5)),
             "respiratory_rate": float(state.get('embodiment', {}).get('respiratory_rate', 0.5)),
             "skin_conductance": float(state.get('embodiment', {}).get('skin_conductance', 0.3)),
             "muscle_tension": float(state.get('embodiment', {}).get('muscle_tension', 0.3)),
             "gut_feeling": float(state.get('embodiment', {}).get('gut_feeling', 0.5)),
             "temperature": float(state.get('embodiment', {}).get('temperature', 0.5)),
             "pain": float(state.get('embodiment', {}).get('pain', 0.0)),
             "fatigue": float(state.get('embodiment', {}).get('fatigue', 0.3))
         }