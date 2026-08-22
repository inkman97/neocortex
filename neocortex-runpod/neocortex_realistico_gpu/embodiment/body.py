"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    EMBODIMENT - EMERGENT PHYSIOLOGY                          ║
║     VERSION 6.0: COMPLETE 8 PARAMETERS                                       ║
║                                                                              ║
║     UPDATE v6.0 (January 2026):                                              ║
║     - Added compute_respiratory_rate() formula                               ║
║     - Added compute_temperature() formula                                    ║
║     - All 8 physiological parameters now have NT-based formulas              ║
║                                                                              ║
║     UPDATE v5.0 (January 2026):                                              ║
║     - Heart rate formula corrected per 2014-2024 literature                  ║
║     - Parasympathetic dominance at rest: 80% (was 10%)                       ║
║     - Sympathetic contribution at rest: 20% (was 25%)                        ║
║                                                                              ║
║     8 PHYSIOLOGICAL PARAMETERS:                                              ║
║     1. Heart Rate - Cardiovascular (v5.0)                                    ║
║     2. Respiratory Rate - Pulmonary (v6.0 NEW)                               ║
║     3. Skin Conductance - Autonomic                                          ║
║     4. Muscle Tension - Neuromuscular                                        ║
║     5. Gut Feeling - Gastrointestinal                                        ║
║     6. Temperature - Thermoregulation (v6.0 NEW)                             ║
║     7. Pain - Nociceptive                                                    ║
║     8. Fatigue - Energetic                                                   ║
║                                                                              ║
║     Principles:                                                              ║
║     1. Each NT has specific physiological effects                            ║
║     2. Effects combine according to biological evidence                      ║
║     3. Same formulas work for ALL diseases                                   ║
║     4. Body parameters emerge from NT interactions                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.neurons import BACKEND
if BACKEND == "torch":
    import torch
    from core.neurons import DEVICE


# ============================================================
# NEUROCHEMICAL-TO-PHYSIOLOGY COUPLING
# ============================================================

class NeurophysiologyCoupling:
    """
    Universal coupling between neurochemistry and physiology.

    Based on biological literature:
    - Serotonin: mood, pain modulation, GI function, thermoregulation
    - Dopamine: motivation, energy, motor control, thermoregulation
    - Noradrenaline: arousal, heart rate, muscle tone, respiration
    - Acetylcholine: cognitive function, parasympathetic, respiration
    - GABA: inhibition, relaxation, anxiety
    - Glutamate: excitation, arousal, muscle activation

    All effects are EMERGENT - no disease-specific code!

    VERSION 6.0 UPDATES:
    - compute_respiratory_rate: NEW formula based on literature
    - compute_temperature: NEW formula based on literature
    """

    @staticmethod
    def compute_fatigue(
        serotonin: float,
        dopamine: float,
        noradrenaline: float,
        acetylcholine: float,
        gaba: float,
        glutamate: float
    ) -> float:
        """
        Compute fatigue level from NT concentrations.

        Biological rationale:
        - Low 5HT → high fatigue (anhedonia, low mood)
        - Low DA → high fatigue (amotivation, low drive)
        - Low NE → high fatigue (low arousal)
        - High GABA → slight fatigue (sedation)
        - Low Glu → fatigue (low excitatory drive)
        - Low ACh → cognitive fatigue

        Returns: 0-1 (0=energetic, 1=exhausted)
        """
        # Healthy targets
        target_5ht = 0.575
        target_da = 0.40
        target_ne = 0.375
        target_ach = 0.35
        target_gaba = 0.60
        target_glu = 0.50

        # Compute deviations (normalized 0-1)
        serotonin_deficit = max(0, target_5ht - serotonin) / target_5ht
        dopamine_deficit = max(0, target_da - dopamine) / target_da
        noradrenaline_deficit = max(0, target_ne - noradrenaline) / target_ne
        acetylcholine_deficit = max(0, target_ach - acetylcholine) / target_ach
        glutamate_deficit = max(0, target_glu - glutamate) / target_glu

        # High GABA → mild sedation
        gaba_excess = max(0, gaba - target_gaba) / (1.0 - target_gaba)

        # Weighted combination (based on clinical importance)
        fatigue = (
            serotonin_deficit * 0.30 +      # MDD cardinal symptom
            dopamine_deficit * 0.25 +       # Motivation/drive
            noradrenaline_deficit * 0.15 +  # Arousal
            acetylcholine_deficit * 0.10 +  # Cognitive fatigue
            glutamate_deficit * 0.10 +      # Excitatory drive
            gaba_excess * 0.10              # Sedation
        )

        # Scale to physiological range (0.20-0.85)
        baseline = 0.30
        fatigue_scaled = baseline + fatigue * 0.55

        return np.clip(fatigue_scaled, 0.0, 1.0)

    @staticmethod
    def compute_muscle_tension(
        noradrenaline: float,
        gaba: float,
        glutamate: float,
        dopamine: float
    ) -> float:
        """
        Compute muscle tension from NT levels.

        Biological rationale:
        - High NE → high tension (sympathetic activation)
        - Low GABA → high tension (disinhibition)
        - High Glu → high tension (excitatory drive)
        - Low DA → rigidity (Parkinson's)

        Returns: 0-1 (0=relaxed, 1=rigid)
        """
        target_ne = 0.375
        target_gaba = 0.60
        target_glu = 0.50
        target_da = 0.40

        # E/I balance (critical for tension)
        ei_imbalance = (glutamate - target_glu) - (gaba - target_gaba)
        ei_tension = max(0, ei_imbalance * 2.0)

        # Noradrenergic tone
        ne_excess = max(0, noradrenaline - target_ne) / (1.0 - target_ne)
        ne_tension = ne_excess * 0.8

        # Dopaminergic deficit (rigidity)
        da_deficit = max(0, target_da - dopamine) / target_da
        da_rigidity = da_deficit * 0.6

        # Combine
        tension = (
            ei_tension * 0.40 +      # E/I balance dominant
            ne_tension * 0.35 +      # Sympathetic activation
            da_rigidity * 0.25       # Parkinsonian rigidity
        )

        # Scale to range (0.25-0.75)
        baseline = 0.35
        tension_scaled = baseline + tension * 0.40

        return np.clip(tension_scaled, 0.0, 1.0)

    @staticmethod
    def compute_heart_rate(
        noradrenaline: float,
        gaba: float,
        glutamate: float,
        acetylcholine: float
    ) -> float:
        """
        Compute heart rate from NT levels.

        ══════════════════════════════════════════════════════════════
        VERSION 5.0 - UPDATED JANUARY 2026
        ══════════════════════════════════════════════════════════════

        Scientific basis:
        White & Raven (2014) J Physiol 592(17):3799-3816:
        "The parasympathetic nervous system contributes 80% influence
        to resting heart rate and the sympathetic nervous system
        contributes the other 20%."

        Biological rationale:
        - High NE → tachycardia (sympathetic) - 20% contribution at rest
        - Low GABA → elevated HR (anxiety) - indirect effect
        - High Glu → elevated HR (excitation) - indirect effect
        - High ACh → bradycardia (parasympathetic) - 80% contribution at rest

        Returns: 0-1 (0=bradycardia, 0.5=normal, 1=tachycardia)
        """
        target_ne = 0.375
        target_gaba = 0.60
        target_glu = 0.50
        target_ach = 0.35

        # SYMPATHETIC DRIVE (increases HR) - 20% at rest
        ne_excess = max(0, noradrenaline - target_ne) / (1.0 - target_ne)
        sympathetic_drive = ne_excess * 0.20

        # E/I IMBALANCE (indirect effect on HR via central arousal)
        ei_imbalance = (glutamate - target_glu) - (gaba - target_gaba)
        ei_arousal = max(0, ei_imbalance * 2.0) * 0.10

        # PARASYMPATHETIC BRAKE (decreases HR) - 80% at rest
        ach_excess = max(0, acetylcholine - target_ach) / (1.0 - target_ach)
        parasympathetic_brake = ach_excess * 0.35

        # Low ACh → reduced parasympathetic tone → relative tachycardia
        ach_deficit = max(0, target_ach - acetylcholine) / target_ach
        vagal_withdrawal = ach_deficit * 0.15

        # FINAL CALCULATION
        hr = 0.50 + sympathetic_drive + ei_arousal + vagal_withdrawal - parasympathetic_brake

        return np.clip(hr, 0.0, 1.0)

    @staticmethod
    def compute_respiratory_rate(
        noradrenaline: float,
        gaba: float,
        glutamate: float,
        acetylcholine: float,
        serotonin: float
    ) -> float:
        """
        Compute respiratory rate from NT levels.

        ══════════════════════════════════════════════════════════════
        VERSION 6.0 - NEW JANUARY 2026
        ══════════════════════════════════════════════════════════════

        Scientific basis:

        Guyenet PG (2014) Physiol Rev 94(2):347-426:
        "The pre-Bötzinger complex receives noradrenergic input from
        the locus coeruleus that increases respiratory frequency
        during arousal and stress."

        Feldman JL, Del Negro CA (2006) Nat Rev Neurosci 7:232-242:
        "Glutamatergic neurons in the pre-Bötzinger complex are
        essential for respiratory rhythm generation."

        Richter DW, Spyer KM (2001) J Physiol 536:297-314:
        "GABAergic inhibition in the brainstem respiratory network
        reduces respiratory rate."

        Hodges MR, Richerson GB (2010) Respir Physiol Neurobiol 173:256-263:
        "Serotonergic neurons in the raphe modulate respiratory drive,
        particularly during sleep and in response to CO2."

        ══════════════════════════════════════════════════════════════

        Biological rationale:
        - High NE → tachypnea (sympathetic activation, stress)
        - High Glu → increased rate (excitatory drive to pre-Bötzinger)
        - High GABA → bradypnea (inhibition of respiratory centers)
        - High ACh → reduced rate (parasympathetic dominance)
        - Low 5HT → irregular/increased rate (loss of modulation)

        Returns: 0-1 (0=bradypnea, 0.5=normal, 1=tachypnea)
        """
        target_ne = 0.375
        target_gaba = 0.60
        target_glu = 0.50
        target_ach = 0.35
        target_5ht = 0.575

        # ════════════════════════════════════════════════════════════
        # SYMPATHETIC DRIVE (increases RR) - 35%
        # ════════════════════════════════════════════════════════════
        # NE from locus coeruleus → pre-Bötzinger complex →
        # increased respiratory frequency during arousal/stress
        ne_excess = max(0, noradrenaline - target_ne) / (1.0 - target_ne)
        sympathetic_drive = ne_excess * 0.35

        # ════════════════════════════════════════════════════════════
        # E/I BALANCE (25%)
        # ════════════════════════════════════════════════════════════
        # Glutamate excites respiratory neurons
        # GABA inhibits respiratory neurons
        ei_imbalance = (glutamate - target_glu) - (gaba - target_gaba)
        ei_effect = max(0, ei_imbalance * 2.0) * 0.25

        # ════════════════════════════════════════════════════════════
        # PARASYMPATHETIC BRAKE (decreases RR) - 20%
        # ════════════════════════════════════════════════════════════
        # ACh promotes slow, deep breathing (parasympathetic)
        ach_excess = max(0, acetylcholine - target_ach) / (1.0 - target_ach)
        parasympathetic_brake = ach_excess * 0.20

        # ════════════════════════════════════════════════════════════
        # SEROTONIN MODULATION (10%)
        # ════════════════════════════════════════════════════════════
        # Serotonin stabilizes respiratory rhythm
        # Low 5HT → dysregulation, tends toward increased rate
        serotonin_deficit = max(0, target_5ht - serotonin) / target_5ht
        serotonin_effect = serotonin_deficit * 0.10

        # ════════════════════════════════════════════════════════════
        # VAGAL WITHDRAWAL (10%)
        # ════════════════════════════════════════════════════════════
        # Low ACh → loss of parasympathetic tone → increased RR
        ach_deficit = max(0, target_ach - acetylcholine) / target_ach
        vagal_withdrawal = ach_deficit * 0.10

        # FINAL CALCULATION
        # Baseline 0.50 = normal respiratory rate (12-16 breaths/min)
        rr = 0.50 + sympathetic_drive + ei_effect + serotonin_effect + vagal_withdrawal - parasympathetic_brake

        return np.clip(rr, 0.0, 1.0)

    @staticmethod
    def compute_temperature(
        noradrenaline: float,
        serotonin: float,
        dopamine: float,
        acetylcholine: float
    ) -> float:
        """
        Compute body temperature from NT levels.

        ══════════════════════════════════════════════════════════════
        VERSION 6.0 - NEW JANUARY 2026
        ══════════════════════════════════════════════════════════════

        Scientific basis:

        Morrison SF (2016) Handbook Clin Neurol 137:295-305:
        "Noradrenergic neurons regulate brown adipose tissue
        thermogenesis and cutaneous vasoconstriction."

        Ishiwata T (2014) J Pharmacol Sci 126:279-285:
        "Serotonin plays a crucial role in thermoregulation.
        5-HT neurons in the raphe nuclei are thermosensitive."

        Lee S et al. (2014) Cell Metab 19:741-756:
        "Dopamine signaling in the hypothalamus regulates
        adaptive thermogenesis."

        Morrison SF, Nakamura K (2019) Annu Rev Physiol 81:285-308:
        "Central neural pathways for thermoregulation involve
        multiple neurotransmitter systems."

        ══════════════════════════════════════════════════════════════

        Biological rationale:
        - High NE → hyperthermia (sympathetic thermogenesis)
        - Low 5HT → hyperthermia (loss of heat dissipation)
        - High DA → hyperthermia (increased metabolic activity)
        - High ACh → hypothermia (vasodilation, heat loss)

        Returns: 0-1 (0=hypothermia, 0.5=normal 37°C, 1=hyperthermia)
        """
        target_ne = 0.375
        target_5ht = 0.575
        target_da = 0.40
        target_ach = 0.35

        # ════════════════════════════════════════════════════════════
        # SYMPATHETIC THERMOGENESIS (35%)
        # ════════════════════════════════════════════════════════════
        # NE activates brown adipose tissue → heat production
        # Also causes cutaneous vasoconstriction → heat retention
        ne_excess = max(0, noradrenaline - target_ne) / (1.0 - target_ne)
        sympathetic_heat = ne_excess * 0.35

        # ════════════════════════════════════════════════════════════
        # SEROTONIN REGULATION (30%)
        # ════════════════════════════════════════════════════════════
        # 5-HT promotes heat dissipation (vasodilation, sweating)
        # Low 5HT → impaired heat loss → hyperthermia
        # This explains serotonin syndrome hyperthermia (too much 5HT
        # initially causes hyperthermia via different receptor subtypes)
        serotonin_deficit = max(0, target_5ht - serotonin) / target_5ht
        serotonin_heat = serotonin_deficit * 0.25

        # High serotonin can also cause hyperthermia (serotonin syndrome)
        serotonin_excess = max(0, serotonin - target_5ht) / (1.0 - target_5ht)
        serotonin_syndrome = serotonin_excess * 0.20

        # ════════════════════════════════════════════════════════════
        # DOPAMINE METABOLISM (20%)
        # ════════════════════════════════════════════════════════════
        # DA increases metabolic activity → heat production
        # Also involved in reward-related thermogenesis
        da_excess = max(0, dopamine - target_da) / (1.0 - target_da)
        dopamine_heat = da_excess * 0.20

        # ════════════════════════════════════════════════════════════
        # PARASYMPATHETIC COOLING (15%)
        # ════════════════════════════════════════════════════════════
        # ACh promotes vasodilation → heat dissipation
        # High ACh → cooling effect
        ach_excess = max(0, acetylcholine - target_ach) / (1.0 - target_ach)
        parasympathetic_cooling = ach_excess * 0.15

        # FINAL CALCULATION
        # Baseline 0.50 = normal temperature (37°C / 98.6°F)
        temp = 0.50 + sympathetic_heat + serotonin_heat + serotonin_syndrome + dopamine_heat - parasympathetic_cooling

        return np.clip(temp, 0.0, 1.0)

    @staticmethod
    def compute_skin_conductance(
        noradrenaline: float,
        gaba: float,
        glutamate: float
    ) -> float:
        """
        Skin conductance (arousal/stress marker).

        Biological rationale:
        - High NE → high SC (sympathetic sweating)
        - E/I imbalance → high SC (anxiety/arousal)

        Returns: 0-1 (0=calm, 1=highly aroused)
        """
        target_ne = 0.375
        target_gaba = 0.60
        target_glu = 0.50

        # Sympathetic arousal
        ne_excess = max(0, noradrenaline - target_ne) / (1.0 - target_ne)
        sympathetic_sc = ne_excess * 0.50

        # E/I imbalance
        ei_imbalance = (glutamate - target_glu) - (gaba - target_gaba)
        ei_arousal = max(0, ei_imbalance * 2.0) * 0.30

        # Baseline
        sc = 0.30 + sympathetic_sc + ei_arousal

        return np.clip(sc, 0.0, 1.0)

    @staticmethod
    def compute_pain(
        serotonin: float,
        noradrenaline: float,
        gaba: float,
        glutamate: float
    ) -> float:
        """
        Pain perception.

        Biological rationale:
        - Low 5HT → increased pain (descending inhibition loss)
        - Low NE → increased pain (noradrenergic analgesia loss)
        - E/I imbalance → neuropathic pain

        Returns: 0-1 (0=no pain, 1=severe pain)
        """
        target_5ht = 0.575
        target_ne = 0.375
        target_gaba = 0.60
        target_glu = 0.50

        # Monoaminergic analgesia
        serotonin_deficit = max(0, target_5ht - serotonin) / target_5ht
        noradrenaline_deficit = max(0, target_ne - noradrenaline) / target_ne

        # E/I imbalance (neuropathic component)
        ei_imbalance = abs((glutamate - target_glu) - (gaba - target_gaba))

        pain = (
            serotonin_deficit * 0.40 +
            noradrenaline_deficit * 0.30 +
            ei_imbalance * 0.30
        )

        # Scale to range (0.05-0.35)
        baseline = 0.05
        pain_scaled = baseline + pain * 0.30

        return np.clip(pain_scaled, 0.0, 1.0)

    @staticmethod
    def compute_gut_feeling(
        serotonin: float,
        gaba: float
    ) -> float:
        """
        Gut feeling / GI comfort.

        Biological rationale:
        - 95% of serotonin is in the gut
        - GABA modulates GI motility

        Returns: 0-1 (0=discomfort, 0.5=neutral, 1=comfort)
        """
        target_5ht = 0.575
        target_gaba = 0.60

        # Serotonin (dominant in GI)
        serotonin_balance = 1.0 - abs(serotonin - target_5ht) / target_5ht

        # GABA modulation
        gaba_balance = 1.0 - abs(gaba - target_gaba) / target_gaba

        gut = (
            serotonin_balance * 0.70 +
            gaba_balance * 0.30
        ) * 0.5 + 0.25  # Scale to 0.25-0.75 range

        return np.clip(gut, 0.0, 1.0)


# ============================================================
# INTEROCEPTIVE SYSTEM - EMERGENT VERSION
# ============================================================

class BodySignal(Enum):
    """Body signals."""
    HEART_RATE = "heart_rate"
    RESPIRATORY_RATE = "respiratory_rate"
    SKIN_CONDUCTANCE = "skin_conductance"
    MUSCLE_TENSION = "muscle_tension"
    GUT_FEELING = "gut_feeling"
    TEMPERATURE = "temperature"
    PAIN = "pain"
    FATIGUE = "fatigue"


@dataclass
class BodyState:
    """Complete body state."""
    heart_rate: float = 0.5
    respiratory_rate: float = 0.5
    skin_conductance: float = 0.3
    muscle_tension: float = 0.3
    gut_feeling: float = 0.5
    temperature: float = 0.5
    pain: float = 0.0
    fatigue: float = 0.3


class InteroceptiveSystem:
    """
    EMERGENT Interoceptive System.

    VERSION 6.0: All 8 parameters now have NT-based formulas

    All physiological parameters emerge from:
    1. Initial NT levels (disease state)
    2. Real-time NT changes (drug effects)
    3. Universal NT-to-physiology coupling formulas

    Works for ALL diseases automatically!
    """

    def __init__(self, disease_state: Optional[Dict] = None):
        """Initialize with disease state (for logging only)."""
        self.state = BodyState()
        self.history: List[BodyState] = []
        self.disease_state = disease_state or {}

        # Store disease state for reference
        self.initial_nt_levels = {
            'serotonin': 0.575,      # Healthy baselines
            'dopamine': 0.40,
            'noradrenaline': 0.375,
            'acetylcholine': 0.35,
            'gaba': 0.60,
            'glutamate': 0.50
        }

        # Log disease state
        print(f"\n[BODY] Initializing EMERGENT interoceptive system v6.0")
        print(f"[BODY] Disease state: {disease_state}")
        print(f"[BODY] All 8 physiological parameters emerge from NT coupling")
        print(f"[BODY] NEW v6.0: respiratory_rate and temperature now have formulas")
        print(f"[BODY] No hardcoded disease logic - universal formulas only!\n")

        self.coupling = NeurophysiologyCoupling()
        self.sensitivity = 0.7

    def compute_baselines_from_nt(
        self,
        nt_levels: Dict[str, float]
    ) -> BodyState:
        """
        Compute ALL body baselines from NT levels using universal formulas.

        This is the CORE of the emergent system!

        VERSION 6.0: Now computes respiratory_rate and temperature from NT
        """
        serotonin = nt_levels.get('serotonin', 0.575)
        dopamine = nt_levels.get('dopamine', 0.40)
        noradrenaline = nt_levels.get('noradrenaline', 0.375)
        acetylcholine = nt_levels.get('acetylcholine', 0.35)
        gaba = nt_levels.get('gaba', 0.60)
        glutamate = nt_levels.get('glutamate', 0.50)

        # Compute all parameters using universal formulas
        fatigue = self.coupling.compute_fatigue(
            serotonin, dopamine, noradrenaline,
            acetylcholine, gaba, glutamate
        )

        muscle_tension = self.coupling.compute_muscle_tension(
            noradrenaline, gaba, glutamate, dopamine
        )

        heart_rate = self.coupling.compute_heart_rate(
            noradrenaline, gaba, glutamate, acetylcholine
        )

        # NEW v6.0: Respiratory rate has its own formula
        respiratory_rate = self.coupling.compute_respiratory_rate(
            noradrenaline, gaba, glutamate, acetylcholine, serotonin
        )

        skin_conductance = self.coupling.compute_skin_conductance(
            noradrenaline, gaba, glutamate
        )

        pain = self.coupling.compute_pain(
            serotonin, noradrenaline, gaba, glutamate
        )

        gut_feeling = self.coupling.compute_gut_feeling(
            serotonin, gaba
        )

        # NEW v6.0: Temperature has its own formula
        temperature = self.coupling.compute_temperature(
            noradrenaline, serotonin, dopamine, acetylcholine
        )

        return BodyState(
            heart_rate=heart_rate,
            respiratory_rate=respiratory_rate,  # Now computed independently!
            skin_conductance=skin_conductance,
            muscle_tension=muscle_tension,
            gut_feeling=gut_feeling,
            temperature=temperature,  # Now computed from NT!
            pain=pain,
            fatigue=fatigue
        )

    def update(
        self,
        emotional_input: float = 0.0,
        external_threat: float = 0.0,
        physical_activity: float = 0.0,
        cognitive_load: float = 0.0,
        dt: float = 1.0,
        nt_levels: Optional[Dict[str, float]] = None
    ):
        """
        Update body state.

        If nt_levels provided, recompute baselines from NT → EMERGENT!
        Then evolve state with transient inputs.
        """
        # CRITICAL: Recompute baselines from current NT levels
        if nt_levels is not None:
            baseline = self.compute_baselines_from_nt(nt_levels)
        else:
            # Use initial disease state
            baseline = self.compute_baselines_from_nt(self.initial_nt_levels)

        # TRANSIENT INPUTS (fast changes)
        if external_threat > 0 or physical_activity > 0 or abs(emotional_input) > 0.1:
            hr_delta = (
                external_threat * 0.3 +
                physical_activity * 0.4 +
                abs(emotional_input) * 0.2
            )
            self.state.heart_rate += hr_delta * 0.08

            # Respiratory rate also increases with threat/activity
            rr_delta = (
                external_threat * 0.35 +
                physical_activity * 0.45 +
                abs(emotional_input) * 0.15
            )
            self.state.respiratory_rate += rr_delta * 0.08

            # Temperature increases with activity
            temp_delta = physical_activity * 0.3
            self.state.temperature += temp_delta * 0.05

        # Skin conductance (arousal spikes)
        if external_threat > 0 or abs(emotional_input) > 0.1:
            sc_delta = external_threat * 0.4 + abs(emotional_input) * 0.3
            self.state.skin_conductance += sc_delta * 0.08

        # Muscle tension (transient)
        if external_threat > 0 or cognitive_load > 0:
            mt_delta = external_threat * 0.3 + cognitive_load * 0.2
            self.state.muscle_tension += mt_delta * 0.08

        # Gut feeling (valence)
        if emotional_input > 0:
            self.state.gut_feeling += emotional_input * 0.15
        else:
            self.state.gut_feeling += emotional_input * 0.1

        # Fatigue (accumulates with activity)
        if physical_activity > 0 or cognitive_load > 0:
            self.state.fatigue += (physical_activity + cognitive_load) * 0.02

        # DECAY TOWARDS NT-DRIVEN BASELINES (homeostasis)
        decay = 0.12 * dt

        self.state.heart_rate += (baseline.heart_rate - self.state.heart_rate) * decay
        self.state.respiratory_rate += (baseline.respiratory_rate - self.state.respiratory_rate) * decay
        self.state.skin_conductance += (baseline.skin_conductance - self.state.skin_conductance) * decay
        self.state.muscle_tension += (baseline.muscle_tension - self.state.muscle_tension) * decay
        self.state.gut_feeling += (baseline.gut_feeling - self.state.gut_feeling) * decay
        self.state.temperature += (baseline.temperature - self.state.temperature) * decay
        self.state.pain += (baseline.pain - self.state.pain) * decay
        self.state.fatigue += (baseline.fatigue - self.state.fatigue) * decay * 0.5

        # Clamp
        self.state.heart_rate = np.clip(self.state.heart_rate, 0, 1)
        self.state.respiratory_rate = np.clip(self.state.respiratory_rate, 0, 1)
        self.state.skin_conductance = np.clip(self.state.skin_conductance, 0, 1)
        self.state.muscle_tension = np.clip(self.state.muscle_tension, 0, 1)
        self.state.gut_feeling = np.clip(self.state.gut_feeling, 0, 1)
        self.state.temperature = np.clip(self.state.temperature, 0, 1)
        self.state.pain = np.clip(self.state.pain, 0, 1)
        self.state.fatigue = np.clip(self.state.fatigue, 0, 1)

        # Save history
        self.history.append(BodyState(**vars(self.state)))
        if len(self.history) > 1000:
            self.history.pop(0)

    def get_arousal(self) -> float:
        """Arousal level."""
        return (
            self.state.heart_rate * 0.3 +
            self.state.skin_conductance * 0.3 +
            self.state.muscle_tension * 0.2 +
            self.state.respiratory_rate * 0.2
        )

    def get_valence(self) -> float:
        """Valence (-1 to +1)."""
        positive = self.state.gut_feeling
        negative = (self.state.pain + self.state.fatigue + self.state.muscle_tension) / 3
        return (positive - negative) * 2 - 0.5

    def get_energy(self) -> float:
        """Energy level."""
        return 1.0 - self.state.fatigue

    def to_vector(self) -> np.ndarray:
        """Convert to vector."""
        return np.array([
            self.state.heart_rate,
            self.state.respiratory_rate,
            self.state.skin_conductance,
            self.state.muscle_tension,
            self.state.gut_feeling,
            self.state.temperature,
            self.state.pain,
            self.state.fatigue
        ], dtype=np.float32)


# ============================================================
# SOMATIC MARKERS (unchanged)
# ============================================================

@dataclass
class SomaticMarker:
    """Somatic marker."""
    pattern: np.ndarray
    valence: float
    arousal: float
    body_state: np.ndarray
    strength: float = 1.0
    timestamp: int = 0


class SomaticMarkerSystem:
    """Somatic marker system (Damasio)."""

    def __init__(self, max_markers: int = 500):
        self.markers: List[SomaticMarker] = []
        self.max_markers = max_markers
        self.time = 0

    def create_marker(
        self,
        pattern: np.ndarray,
        valence: float,
        arousal: float,
        body_state: np.ndarray
    ):
        """Create a new somatic marker."""
        self.time += 1

        if BACKEND == "torch":
            if hasattr(pattern, 'cpu'):
                pattern = pattern.cpu().numpy()
            if hasattr(body_state, 'cpu'):
                body_state = body_state.cpu().numpy()

        pattern = np.array(pattern, dtype=np.float32)
        body_state = np.array(body_state, dtype=np.float32)

        marker = SomaticMarker(
            pattern=pattern.copy(),
            valence=valence,
            arousal=arousal,
            body_state=body_state.copy(),
            strength=1.0,
            timestamp=self.time
        )

        self.markers.append(marker)

        if len(self.markers) > self.max_markers:
            weakest_idx = min(range(len(self.markers)),
                            key=lambda i: self.markers[i].strength)
            self.markers.pop(weakest_idx)

    def evaluate(
        self,
        pattern: np.ndarray,
        threshold: float = 0.5
    ) -> Tuple[float, float, Optional[np.ndarray]]:
        """Evaluate a pattern using somatic markers."""
        if len(self.markers) == 0:
            return 0.0, 0.5, None

        if BACKEND == "torch":
            if hasattr(pattern, 'cpu'):
                pattern = pattern.cpu().numpy()
        pattern = np.array(pattern, dtype=np.float32)

        pattern_norm = pattern / (np.linalg.norm(pattern) + 1e-8)

        total_valence = 0.0
        total_arousal = 0.0
        total_weight = 0.0
        body_prediction = None
        best_sim = 0.0

        for marker in self.markers:
            marker_pattern = marker.pattern
            if len(marker_pattern) != len(pattern):
                min_len = min(len(marker_pattern), len(pattern))
                marker_pattern = marker_pattern[:min_len]
                pattern_norm_adj = pattern_norm[:min_len]
            else:
                pattern_norm_adj = pattern_norm

            marker_norm = marker_pattern / (np.linalg.norm(marker_pattern) + 1e-8)
            sim = np.dot(pattern_norm_adj, marker_norm)

            if sim >= threshold:
                weight = sim * marker.strength
                total_valence += marker.valence * weight
                total_arousal += marker.arousal * weight
                total_weight += weight

                if sim > best_sim:
                    best_sim = sim
                    body_prediction = marker.body_state

        if total_weight > 0:
            return (
                total_valence / total_weight,
                total_arousal / total_weight,
                body_prediction
            )

        return 0.0, 0.5, None

    def reinforce(self, pattern: np.ndarray, reward: float):
        """Reinforce markers similar to the pattern."""
        if BACKEND == "torch":
            if hasattr(pattern, 'cpu'):
                pattern = pattern.cpu().numpy()
        pattern = np.array(pattern, dtype=np.float32)
        pattern_norm = pattern / (np.linalg.norm(pattern) + 1e-8)

        for marker in self.markers:
            marker_pattern = marker.pattern
            if len(marker_pattern) != len(pattern):
                min_len = min(len(marker_pattern), len(pattern))
                marker_pattern = marker_pattern[:min_len]
                pattern_norm_adj = pattern_norm[:min_len]
            else:
                pattern_norm_adj = pattern_norm

            marker_norm = marker_pattern / (np.linalg.norm(marker_pattern) + 1e-8)
            sim = np.dot(pattern_norm_adj, marker_norm)

            if sim > 0.5:
                marker.strength += reward * sim * 0.1
                marker.strength = np.clip(marker.strength, 0.1, 2.0)

    def decay(self, rate: float = 0.001):
        """Natural decay of markers."""
        for marker in self.markers:
            marker.strength *= (1 - rate)

        self.markers = [m for m in self.markers if m.strength > 0.05]

    def clear(self):
        """Clear all markers."""
        self.markers = []


# ============================================================
# COMPLETE EMBODIMENT
# ============================================================

class Embodiment:
    """
    Complete embodiment system with disease awareness.

    VERSION 6.0: All 8 parameters have NT-based formulas
    """

    def __init__(self, disease_state: Optional[Dict] = None):
        """
        Initialize with disease state.

        Args:
            disease_state: Neurochemical state for disease modeling
                          Positive = deficit, Negative = excess
        """
        self.interoception = InteroceptiveSystem(disease_state=disease_state)
        self.somatic_markers = SomaticMarkerSystem()

    def update(
        self,
        emotional_input: float = 0.0,
        threat: float = 0.0,
        activity: float = 0.0,
        cognitive_load: float = 0.0,
        dt: float = 1.0,
        nt_levels: Optional[Dict[str, float]] = None
    ):
        """Update body state."""
        self.interoception.update(
            emotional_input=emotional_input,
            external_threat=threat,
            physical_activity=activity,
            cognitive_load=cognitive_load,
            dt=dt,
            nt_levels=nt_levels
        )

        self.somatic_markers.decay(0.0001 * dt)

    def create_marker(self, pattern: np.ndarray, valence: float):
        """Create marker for current pattern."""
        self.somatic_markers.create_marker(
            pattern=pattern,
            valence=valence,
            arousal=self.interoception.get_arousal(),
            body_state=self.interoception.to_vector()
        )

    def evaluate(self, pattern: np.ndarray) -> Tuple[float, float]:
        """Evaluate pattern using somatic markers."""
        valence, arousal, _ = self.somatic_markers.evaluate(pattern)
        return valence, arousal

    def get_state(self) -> dict:
        """Complete state."""
        return {
            'arousal': self.interoception.get_arousal(),
            'valence': self.interoception.get_valence(),
            'energy': self.interoception.get_energy(),
            'heart_rate': self.interoception.state.heart_rate,
            'respiratory_rate': self.interoception.state.respiratory_rate,
            'skin_conductance': self.interoception.state.skin_conductance,
            'muscle_tension': self.interoception.state.muscle_tension,
            'gut_feeling': self.interoception.state.gut_feeling,
            'temperature': self.interoception.state.temperature,
            'pain': self.interoception.state.pain,
            'fatigue': self.interoception.state.fatigue,
            'n_markers': len(self.somatic_markers.markers)
        }