"""DRUG SIMULATOR (Loihi) - pharmacology engine with active metabolites.

Every effect emerges from four inputs, none of them hardcoded clinical outcomes:
molecular targets, Hill coefficients, pharmacokinetics and dose ratio.
"""

import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel

LN_2 = 0.693
ABSORPTION_RATE_FACTOR = 3.0
METABOLITE_PEAK_FACTOR = 0.8
DEFAULT_METABOLITE_HILL = 1.5
DEFAULT_DOSING_INTERVAL_HOURS = 24.0
WARMUP_STEPS = 2000
WARMUP_LOG_EVERY = 400
STEPS_PER_SIMULATED_HOUR = 60
PERCEPTION_WIDTH = 100


@dataclass(frozen=True)
class MechanismSpec:
    """One molecular mechanism: its potency field, its Hill field, the key it
    reports to the brain, and the target names that select it."""
    potency_attr: str
    hill_attr: str
    brain_key: str
    aliases: tuple


MECHANISM_SPECS = (
    MechanismSpec('sert_inhibition', 'sert_hill', 'SERT_inhibition',
                  ('sert_inhibition',)),
    MechanismSpec('dat_inhibition', 'dat_hill', 'DAT_inhibition',
                  ('dat_inhibition',)),
    MechanismSpec('net_inhibition', 'net_hill', 'NET_inhibition',
                  ('net_inhibition',)),
    MechanismSpec('mao_a_inhibition', 'mao_a_hill', 'MAO_A_inhibition',
                  ('mao_a_inhibition', 'maoa_inhibition')),
    MechanismSpec('mao_b_inhibition', 'mao_b_hill', 'MAO_B_inhibition',
                  ('mao_b_inhibition', 'maob_inhibition')),
    MechanismSpec('ache_inhibition', 'ache_hill', 'AChE_inhibition',
                  ('ache_inhibition', 'acetylcholinesterase_inhibition')),
    MechanismSpec('da_precursor', 'da_precursor_hill', 'DA_precursor',
                  ('da_precursor',)),
    MechanismSpec('d2_agonism', 'd2_agonism_hill', 'D2_agonism',
                  ('d2_agonism',)),
    MechanismSpec('d3_agonism', 'd3_agonism_hill', 'D3_agonism',
                  ('d3_agonism',)),
    MechanismSpec('d2_antagonism', 'd2_antagonism_hill', 'D2_antagonism',
                  ('d2_antagonism',)),
    MechanismSpec('d3_antagonism', 'd3_antagonism_hill', 'D3_antagonism',
                  ('d3_antagonism',)),
    MechanismSpec('d2_partial_agonism', 'd2_partial_agonism_hill', 'D2_partial_agonism',
                  ('d2_partial_agonism',)),
    MechanismSpec('ht1a_agonism', 'ht1a_agonism_hill', 'HT1A_agonism',
                  ('ht1a_agonism', '5ht1a_agonism')),
    MechanismSpec('ht2a_antagonism', 'ht2a_antagonism_hill', 'HT2A_antagonism',
                  ('ht2a_antagonism', '5ht2a_antagonism')),
    MechanismSpec('alpha2_antagonism', 'alpha2_antagonism_hill', 'ALPHA2_antagonism',
                  ('alpha2_antagonism',)),
    MechanismSpec('h1_antagonism', 'h1_antagonism_hill', 'H1_antagonism',
                  ('h1_antagonism',)),
    MechanismSpec('gaba_a_pam', 'gaba_a_pam_hill', 'GABA_A_PAM',
                  ('gaba_a_pam',)),
    MechanismSpec('gat_inhibition', 'gat_hill', 'GAT_inhibition',
                  ('gat_inhibition',)),
    MechanismSpec('gaba_transaminase_inhibition', 'gaba_transaminase_hill',
                  'GABA_transaminase_inhibition', ('gaba_transaminase_inhibition',)),
    MechanismSpec('nmda_antagonism', 'nmda_antagonism_hill', 'NMDA_antagonism',
                  ('nmda_antagonism',)),
    MechanismSpec('glutamate_release_inhibition', 'glutamate_release_inhibition_hill',
                  'glutamate_release_inhibition', ('glutamate_release_inhibition',)),
    MechanismSpec('voltage_gated_sodium_blocker', 'voltage_gated_sodium_blocker_hill',
                  'voltage_gated_sodium_blocker', ('voltage_gated_sodium_blocker',)),
    MechanismSpec('alpha2delta_blocker', 'alpha2delta_blocker_hill',
                  'alpha2delta_calcium_channel_blocker',
                  ('alpha2delta_blocker', 'alpha2delta_calcium_channel_blocker')),
)

SPEC_BY_ALIAS = {alias: spec for spec in MECHANISM_SPECS for alias in spec.aliases}


@dataclass
class DiseaseProfile:
    """Neurotransmitter deficits and excesses, across the 6 NT systems."""
    serotonin_deficit: float = 0.0
    dopamine_deficit: float = 0.0
    noradrenaline_deficit: float = 0.0
    acetylcholine_deficit: float = 0.0
    gaba_deficit: float = 0.0
    glutamate_deficit: float = 0.0

    def as_dict(self) -> Dict[str, float]:
        return {
            'serotonin': self.serotonin_deficit,
            'dopamine': self.dopamine_deficit,
            'noradrenaline': self.noradrenaline_deficit,
            'acetylcholine': self.acetylcholine_deficit,
            'gaba': self.gaba_deficit,
            'glutamate': self.glutamate_deficit,
        }


class Pharmacokinetics(BaseModel):
    """Pharmacokinetic parameters."""
    halfLife_hours: float = 24.0
    tmax_hours: float = 2.0
    bioavailability: float = 0.7
    vd_L_kg: Optional[float] = 20.0


class ActiveMetabolite(BaseModel):
    """A metabolite carries its own targets and its own kinetics."""
    name: str
    formation_fraction: float = 0.8
    halfLife_hours: float = 24.0
    tmax_hours: float = 4.0
    targets: List[Dict] = []


@dataclass
class DrugMechanism:
    """Molecular mechanisms with their dose-response curves.

    Each mechanism has a potency in 0-1 and a Hill coefficient shaping how
    that potency scales with dose.
    """

    sert_inhibition: float = 0.0
    sert_hill: float = 1.0

    dat_inhibition: float = 0.0
    dat_hill: float = 1.0

    net_inhibition: float = 0.0
    net_hill: float = 1.0

    mao_a_inhibition: float = 0.0
    mao_a_hill: float = 1.0

    mao_b_inhibition: float = 0.0
    mao_b_hill: float = 1.0

    ache_inhibition: float = 0.0
    ache_hill: float = 1.0

    da_precursor: float = 0.0
    da_precursor_hill: float = 1.0

    d2_agonism: float = 0.0
    d2_agonism_hill: float = 1.0

    d3_agonism: float = 0.0
    d3_agonism_hill: float = 1.0

    d2_antagonism: float = 0.0
    d2_antagonism_hill: float = 1.0

    d3_antagonism: float = 0.0
    d3_antagonism_hill: float = 1.0

    d2_partial_agonism: float = 0.0
    d2_partial_agonism_hill: float = 1.0

    ht1a_agonism: float = 0.0
    ht1a_agonism_hill: float = 1.0

    ht2a_antagonism: float = 0.0
    ht2a_antagonism_hill: float = 1.0

    alpha2_antagonism: float = 0.0
    alpha2_antagonism_hill: float = 1.0

    h1_antagonism: float = 0.0
    h1_antagonism_hill: float = 1.0

    gaba_a_pam: float = 0.0
    gaba_a_pam_hill: float = 1.0

    gat_inhibition: float = 0.0
    gat_hill: float = 1.0

    gaba_transaminase_inhibition: float = 0.0
    gaba_transaminase_hill: float = 1.0

    nmda_antagonism: float = 0.0
    nmda_antagonism_hill: float = 1.0

    glutamate_release_inhibition: float = 0.0
    glutamate_release_inhibition_hill: float = 1.0

    voltage_gated_sodium_blocker: float = 0.0
    voltage_gated_sodium_blocker_hill: float = 1.0

    alpha2delta_blocker: float = 0.0
    alpha2delta_blocker_hill: float = 1.0

    @classmethod
    def from_targets(cls, targets: List[Dict]) -> 'DrugMechanism':
        """Build a mechanism from a list of target dicts, as sent over HTTP."""
        kwargs = {}

        for target_dict in targets:
            spec = SPEC_BY_ALIAS.get(target_dict.get('target', '').lower())
            if spec is None:
                continue
            kwargs[spec.potency_attr] = target_dict.get('potency', 0.0)
            kwargs[spec.hill_attr] = target_dict.get('hill', DEFAULT_METABOLITE_HILL)

        return cls(**kwargs)

    def _apply_hill_transform(self, dose_ratio: float, hill: float) -> float:
        """Hill equation: dose^hill / (1 + dose^hill)."""
        numerator = dose_ratio ** hill
        return numerator / (1.0 + numerator)

    def active_mechanisms(self, plasma_concentration: float, dose_ratio: float) -> Dict[str, float]:
        """Combine dose dynamics (Hill) with time dynamics (plasma level)."""
        mechanisms = {}

        for spec in MECHANISM_SPECS:
            potency = getattr(self, spec.potency_attr)
            if potency <= 0:
                continue
            dose_effect = self._apply_hill_transform(dose_ratio, getattr(self, spec.hill_attr))
            mechanisms[spec.brain_key] = potency * dose_effect * plasma_concentration

        return mechanisms

    def apply_to_brain(self, brain, plasma_concentration: float, dose_ratio: float):
        brain.neuromodulation.apply_drug_to_synapses(
            self.active_mechanisms(plasma_concentration, dose_ratio)
        )


class DrugSimulator:
    """Runs a drug trial on a brain model, parent compound plus metabolites."""

    def __init__(
        self,
        brain,
        drug_mechanism: DrugMechanism,
        disease_profile: DiseaseProfile,
        pharmacokinetics: Pharmacokinetics,
        active_metabolites: Optional[List[ActiveMetabolite]] = None
    ):
        self.brain = brain
        self.drug_mechanism = drug_mechanism
        self.disease_profile = disease_profile
        self.pk = pharmacokinetics
        self.active_metabolites = active_metabolites or []
        self.metabolite_mechanisms = [
            DrugMechanism.from_targets(metabolite.targets)
            for metabolite in self.active_metabolites
        ]

        for metabolite in self.active_metabolites:
            print(f"[METABOLITE] {metabolite.name}: t1/2={metabolite.halfLife_hours}h, "
                  f"formation={metabolite.formation_fraction:.0%}")

        self._initialize_disease_state()

    def _create_mechanism_from_targets(self, targets: List[Dict]) -> DrugMechanism:
        return DrugMechanism.from_targets(targets)

    def _initialize_disease_state(self):
        """Set the disease at neural level, then rebuild the body with it."""
        self.brain.neuromodulation.set_disease_state(self.disease_profile)
        print("[DISEASE] Profile set at neural level")

        from embodiment import Embodiment
        self.brain.embodiment = Embodiment(disease_state=self.disease_profile.as_dict())

    def _calculate_plasma_concentration(self, hours_after_dose: float) -> float:
        """One-compartment model with an absorption and an elimination phase."""
        if hours_after_dose < 0:
            return 0.0

        tmax = self.pk.tmax_hours
        ke = LN_2 / self.pk.halfLife_hours
        ka = ABSORPTION_RATE_FACTOR / tmax
        bioavailability = self.pk.bioavailability

        if hours_after_dose <= tmax * 2:
            absorption = 1.0 - np.exp(-ka * hours_after_dose)
            elimination = np.exp(-ke * hours_after_dose)
            return bioavailability * absorption * elimination

        peak_conc = bioavailability * (1.0 - np.exp(-ka * tmax)) * np.exp(-ke * tmax)
        return peak_conc * np.exp(-ke * (hours_after_dose - tmax))

    def _calculate_metabolite_concentration(
        self,
        hours_after_dose: float,
        parent_pk: Pharmacokinetics,
        metabolite: ActiveMetabolite
    ) -> float:
        """Formation-rate-limited kinetics: the metabolite forms as the parent
        is cleared, then eliminates on its own half-life."""
        if hours_after_dose < 0:
            return 0.0

        tmax_metabolite = metabolite.tmax_hours
        formation_fraction = metabolite.formation_fraction

        if hours_after_dose < tmax_metabolite:
            formation_factor = hours_after_dose / tmax_metabolite
            parent_conc = self._calculate_plasma_concentration(hours_after_dose)
            return formation_fraction * formation_factor * parent_conc

        ke_metabolite = LN_2 / metabolite.halfLife_hours
        time_from_peak = hours_after_dose - tmax_metabolite
        peak_metabolite = formation_fraction * parent_pk.bioavailability * METABOLITE_PEAK_FACTOR
        return peak_metabolite * np.exp(-ke_metabolite * time_from_peak)

    def _accumulate_over_doses(self, current_time_hours, dosing_interval_hours, concentration_at):
        """Superpose the contribution of every dose given so far."""
        total = 0.0
        dose_count = int(current_time_hours / dosing_interval_hours)

        for dose_idx in range(dose_count + 1):
            time_since_dose = current_time_hours - dose_idx * dosing_interval_hours
            if time_since_dose >= 0:
                total += concentration_at(time_since_dose)

        return min(1.0, total)

    def _calculate_plasma_concentration_multiple_doses(
        self,
        current_time_hours: float,
        dosing_interval_hours: float = DEFAULT_DOSING_INTERVAL_HOURS
    ) -> float:
        return self._accumulate_over_doses(
            current_time_hours,
            dosing_interval_hours,
            self._calculate_plasma_concentration
        )

    def _calculate_metabolite_concentration_multiple_doses(
        self,
        current_time_hours: float,
        metabolite: ActiveMetabolite,
        dosing_interval_hours: float = DEFAULT_DOSING_INTERVAL_HOURS
    ) -> float:
        return self._accumulate_over_doses(
            current_time_hours,
            dosing_interval_hours,
            lambda hours: self._calculate_metabolite_concentration(hours, self.pk, metabolite)
        )

    def run_trial(
        self,
        dose_mg: float,
        typical_dose_mg: float,
        duration_hours: int,
        sampling_interval_hours: int = 24
    ) -> List[Dict]:
        """Warm the model up, then dose it and sample it over the trial."""
        dose_ratio = dose_mg / typical_dose_mg

        print(f"[TRIAL] {dose_mg}mg / {typical_dose_mg}mg = {dose_ratio:.2f}x typical, "
              f"{duration_hours}h ({duration_hours / 24:.1f} days), "
              f"sampled every {sampling_interval_hours}h")

        self._run_warmup()

        timepoints = [{
            "hours": -1.0,
            "days": -1.0 / 24,
            "phase": "baseline",
            "drug_concentration": 0.0,
            "metabolite_concentrations": {},
            **self._get_brain_state()
        }]

        for sample_idx in range(duration_hours // sampling_interval_hours + 1):
            hours_elapsed = sample_idx * sampling_interval_hours

            parent_plasma = self._calculate_plasma_concentration_multiple_doses(hours_elapsed)
            metabolite_plasmas = {
                metabolite.name: self._calculate_metabolite_concentration_multiple_doses(
                    hours_elapsed, metabolite
                )
                for metabolite in self.active_metabolites
            }

            print(f"  t={hours_elapsed}h ({hours_elapsed / 24:.1f}d): parent={parent_plasma:.3f}"
                  + "".join(f", {name}={level:.3f}" for name, level in metabolite_plasmas.items()))

            self._simulate_window(hours_elapsed, sampling_interval_hours, dose_ratio)

            timepoints.append({
                "hours": float(hours_elapsed),
                "days": hours_elapsed / 24.0,
                "phase": "treatment",
                "drug_concentration": parent_plasma * 100,
                "metabolite_concentrations": {
                    name: level * 100 for name, level in metabolite_plasmas.items()
                },
                **self._get_brain_state()
            })

        print(f"[TRIAL] Complete: {len(timepoints)} timepoints")

        return timepoints

    def _run_warmup(self):
        """Let the network settle before any drug is present."""
        print("[WARMUP] Running extended warmup")

        for step in range(WARMUP_STEPS):
            if step % WARMUP_LOG_EVERY == 0:
                nm = self.brain.neuromodulation
                print(f"  step {step}/{WARMUP_STEPS}: "
                      f"5HT={nm.serotonin:.3f}, DA={nm.dopamine:.3f}, "
                      f"NE={nm.noradrenaline:.3f}, ACh={nm.acetylcholine:.3f}, "
                      f"GABA={nm.gaba:.3f}, Glu={nm.glutamate:.3f}")

            self.brain.perceive(np.random.rand(PERCEPTION_WIDTH) * 0.3)
            self.brain.step()

        print("[WARMUP] Complete")

    def _simulate_window(self, hours_elapsed: int, window_hours: int, dose_ratio: float):
        """Run one sampling window hour by hour, re-dosing the brain each hour."""
        for hour in range(window_hours):
            time_since_start = hours_elapsed + hour

            self.drug_mechanism.apply_to_brain(
                self.brain,
                self._calculate_plasma_concentration_multiple_doses(time_since_start),
                dose_ratio
            )

            for mechanism, metabolite in zip(self.metabolite_mechanisms, self.active_metabolites):
                mechanism.apply_to_brain(
                    self.brain,
                    self._calculate_metabolite_concentration_multiple_doses(
                        time_since_start, metabolite
                    ),
                    dose_ratio
                )

            self.brain.perceive(np.random.rand(PERCEPTION_WIDTH) * 0.6 + 0.2)

            for _ in range(STEPS_PER_SIMULATED_HOUR):
                self.brain.step()

    def _get_brain_state(self) -> Dict:
        """Read the brain out as 6 neurotransmitters plus body channels."""
        state = self.brain.get_state()

        floats = {
            'serotonin': 0.5,
            'dopamine': 0.5,
            'noradrenaline': 0.3,
            'acetylcholine': 0.4,
            'gaba': 0.6,
            'glutamate': 0.5,
            'arousal': 0.5,
            'valence': 0.0,
            'firing_rate': 0.0,
            'heart_rate': 0.5,
            'respiratory_rate': 0.5,
            'skin_conductance': 0.3,
            'muscle_tension': 0.3,
            'gut_feeling': 0.5,
            'temperature': 0.5,
            'pain': 0.0,
            'fatigue': 0.3,
        }

        readout = {key: float(state.get(key, default)) for key, default in floats.items()}
        readout['dominant_emotion'] = str(state.get('dominant_emotion', 'neutral'))
        return readout
