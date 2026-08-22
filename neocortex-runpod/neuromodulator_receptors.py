"""
NEUROMODULATOR RECEPTOR SYSTEM

Implements realistic receptor distributions and effects for:
- Serotonin (5-HT1A, 5-HT2A, etc.)
- Dopamine (D1, D2)
- Noradrenaline (α1, α2, β1)
- Acetylcholine (M1-M5, nAChR)

Each receptor type modulates neuronal properties based on:
1. Receptor density (varies by neuron type and layer)
2. Binding affinity (Kd)
3. Efficacy (how strongly it affects the neuron)
4. Second messenger pathway (Gs/Gi/Gq → cAMP/Ca2+)
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np


# ═══════════════════════════════════════════════════════════════
# RECEPTOR TYPES
# ═══════════════════════════════════════════════════════════════

class ReceptorFamily(Enum):
    """Receptor families by neurotransmitter."""
    SEROTONIN = "serotonin"
    DOPAMINE = "dopamine"
    NORADRENALINE = "noradrenaline"
    ACETYLCHOLINE_M = "acetylcholine_muscarinic"
    ACETYLCHOLINE_N = "acetylcholine_nicotinic"


class SerotoninReceptor(Enum):
    """Serotonin receptor subtypes."""
    HT1A = "5-HT1A"  # Gi, inibitorio, ansiolitico
    HT1B = "5-HT1B"  # Gi, autoreceptor
    HT2A = "5-HT2A"  # Gq, eccitatorio, allucinogeni
    HT2C = "5-HT2C"  # Gq, eccitatorio, appetito
    HT3 = "5-HT3"    # Ionotropico, veloce
    HT4 = "5-HT4"    # Gs, pro-cognitivo
    HT6 = "5-HT6"    # Gs, cognitivo
    HT7 = "5-HT7"    # Gs, sonno


class DopamineReceptor(Enum):
    """Dopamine receptor subtypes."""
    D1 = "D1"  # Gs, eccitatorio, Go pathway
    D2 = "D2"  # Gi, inibitorio, NoGo pathway
    D3 = "D3"  # Gi, limbico
    D4 = "D4"  # Gi, corteccia prefrontale
    D5 = "D5"  # Gs, simile D1


class NoradrenalineReceptor(Enum):
    """Noradrenaline receptor subtypes."""
    ALPHA1 = "α1"  # Gq, eccitatorio
    ALPHA2 = "α2"  # Gi, inibitorio, autoreceptor
    BETA1 = "β1"   # Gs, eccitatorio
    BETA2 = "β2"   # Gs, eccitatorio
    BETA3 = "β3"   # Gs


class AcetylcholineReceptorM(Enum):
    """Muscarinic acetylcholine receptors."""
    M1 = "M1"  # Gq, eccitatorio, memoria
    M2 = "M2"  # Gi, inibitorio, cuore
    M3 = "M3"  # Gq, eccitatorio
    M4 = "M4"  # Gi, inibitorio
    M5 = "M5"  # Gq, eccitatorio


class AcetylcholineReceptorN(Enum):
    """Nicotinic acetylcholine receptors."""
    ALPHA4BETA2 = "α4β2"  # Alta affinità nicotina
    ALPHA7 = "α7"         # Alta permeabilità Ca2+


# ═══════════════════════════════════════════════════════════════
# RECEPTOR PARAMETERS
# ═══════════════════════════════════════════════════════════════

@dataclass
class ReceptorParams:
    """Parameters for a receptor subtype."""
    name: str
    family: ReceptorFamily

    # Pharmacology
    kd_nM: float              # Binding affinity (Kd in nM)
    hill_coefficient: float   # Cooperativity (usually 1.0)

    # Signaling pathway
    gprotein: Optional[str]   # "Gs", "Gi", "Gq", or None (ionotropic)
    second_messenger: str     # "cAMP+", "cAMP-", "Ca2+", "ion_channel"

    # Neuronal effects
    excitatory: bool          # Net excitatory or inhibitory?
    tau_onset: float          # Time to peak effect (ms)
    tau_offset: float         # Time to return to baseline (ms)

    # Effect magnitudes (0-1 scale)
    excitability_modulation: float    # Changes firing threshold
    gain_modulation: float            # Changes input-output gain
    plasticity_modulation: float      # Changes learning rate

    # Autoreceptor?
    is_autoreceptor: bool = False


# ═══════════════════════════════════════════════════════════════
# RECEPTOR DATABASE
# ═══════════════════════════════════════════════════════════════

RECEPTOR_DATABASE: Dict[Enum, ReceptorParams] = {

    # ────────────────────────────────────────────────────────────
    # SEROTONIN RECEPTORS
    # ────────────────────────────────────────────────────────────

    SerotoninReceptor.HT1A: ReceptorParams(
        name="5-HT1A",
        family=ReceptorFamily.SEROTONIN,
        kd_nM=5.0,
        hill_coefficient=1.0,
        gprotein="Gi",
        second_messenger="cAMP-",
        excitatory=False,
        tau_onset=500.0,
        tau_offset=2000.0,
        excitability_modulation=-0.3,  # Reduces excitability
        gain_modulation=-0.2,
        plasticity_modulation=0.1,
        is_autoreceptor=False  # Both pre and post
    ),

    SerotoninReceptor.HT1B: ReceptorParams(
        name="5-HT1B",
        family=ReceptorFamily.SEROTONIN,
        kd_nM=8.0,
        hill_coefficient=1.0,
        gprotein="Gi",
        second_messenger="cAMP-",
        excitatory=False,
        tau_onset=300.0,
        tau_offset=1500.0,
        excitability_modulation=-0.2,
        gain_modulation=-0.1,
        plasticity_modulation=0.0,
        is_autoreceptor=True
    ),

    SerotoninReceptor.HT2A: ReceptorParams(
        name="5-HT2A",
        family=ReceptorFamily.SEROTONIN,
        kd_nM=10.0,
        hill_coefficient=1.0,
        gprotein="Gq",
        second_messenger="Ca2+",
        excitatory=True,
        tau_onset=800.0,
        tau_offset=3000.0,
        excitability_modulation=0.4,  # Increases excitability
        gain_modulation=0.3,
        plasticity_modulation=0.2,
        is_autoreceptor=False
    ),

    SerotoninReceptor.HT2C: ReceptorParams(
        name="5-HT2C",
        family=ReceptorFamily.SEROTONIN,
        kd_nM=15.0,
        hill_coefficient=1.0,
        gprotein="Gq",
        second_messenger="Ca2+",
        excitatory=True,
        tau_onset=700.0,
        tau_offset=2500.0,
        excitability_modulation=0.3,
        gain_modulation=0.2,
        plasticity_modulation=0.1,
        is_autoreceptor=False
    ),

    # ────────────────────────────────────────────────────────────
    # DOPAMINE RECEPTORS
    # ────────────────────────────────────────────────────────────

    DopamineReceptor.D1: ReceptorParams(
        name="D1",
        family=ReceptorFamily.DOPAMINE,
        kd_nM=20.0,
        hill_coefficient=1.0,
        gprotein="Gs",
        second_messenger="cAMP+",
        excitatory=True,
        tau_onset=400.0,
        tau_offset=1500.0,
        excitability_modulation=0.3,
        gain_modulation=0.3,
        plasticity_modulation=0.5,  # Strong plasticity effect
        is_autoreceptor=False
    ),

    DopamineReceptor.D2: ReceptorParams(
        name="D2",
        family=ReceptorFamily.DOPAMINE,
        kd_nM=15.0,
        hill_coefficient=1.0,
        gprotein="Gi",
        second_messenger="cAMP-",
        excitatory=False,
        tau_onset=350.0,
        tau_offset=1200.0,
        excitability_modulation=-0.3,
        gain_modulation=-0.2,
        plasticity_modulation=-0.3,
        is_autoreceptor=True  # Can be pre or post
    ),

    # ────────────────────────────────────────────────────────────
    # NORADRENALINE RECEPTORS
    # ────────────────────────────────────────────────────────────

    NoradrenalineReceptor.ALPHA1: ReceptorParams(
        name="α1",
        family=ReceptorFamily.NORADRENALINE,
        kd_nM=50.0,
        hill_coefficient=1.0,
        gprotein="Gq",
        second_messenger="Ca2+",
        excitatory=True,
        tau_onset=200.0,
        tau_offset=800.0,
        excitability_modulation=0.3,
        gain_modulation=0.4,  # Strong gain increase
        plasticity_modulation=0.1,
        is_autoreceptor=False
    ),

    NoradrenalineReceptor.ALPHA2: ReceptorParams(
        name="α2",
        family=ReceptorFamily.NORADRENALINE,
        kd_nM=30.0,
        hill_coefficient=1.0,
        gprotein="Gi",
        second_messenger="cAMP-",
        excitatory=False,
        tau_onset=250.0,
        tau_offset=1000.0,
        excitability_modulation=-0.2,
        gain_modulation=-0.2,
        plasticity_modulation=0.0,
        is_autoreceptor=True
    ),

    NoradrenalineReceptor.BETA1: ReceptorParams(
        name="β1",
        family=ReceptorFamily.NORADRENALINE,
        kd_nM=80.0,
        hill_coefficient=1.0,
        gprotein="Gs",
        second_messenger="cAMP+",
        excitatory=True,
        tau_onset=300.0,
        tau_offset=1200.0,
        excitability_modulation=0.2,
        gain_modulation=0.3,
        plasticity_modulation=0.3,
        is_autoreceptor=False
    ),

    # ────────────────────────────────────────────────────────────
    # ACETYLCHOLINE RECEPTORS - MUSCARINIC
    # ────────────────────────────────────────────────────────────

    AcetylcholineReceptorM.M1: ReceptorParams(
        name="M1",
        family=ReceptorFamily.ACETYLCHOLINE_M,
        kd_nM=25.0,
        hill_coefficient=1.0,
        gprotein="Gq",
        second_messenger="Ca2+",
        excitatory=True,
        tau_onset=500.0,
        tau_offset=2000.0,
        excitability_modulation=0.3,
        gain_modulation=0.2,
        plasticity_modulation=0.5,  # Strong memory effect
        is_autoreceptor=False
    ),

    AcetylcholineReceptorM.M2: ReceptorParams(
        name="M2",
        family=ReceptorFamily.ACETYLCHOLINE_M,
        kd_nM=20.0,
        hill_coefficient=1.0,
        gprotein="Gi",
        second_messenger="cAMP-",
        excitatory=False,
        tau_onset=400.0,
        tau_offset=1500.0,
        excitability_modulation=-0.2,
        gain_modulation=-0.1,
        plasticity_modulation=0.0,
        is_autoreceptor=True
    ),

    # ────────────────────────────────────────────────────────────
    # ACETYLCHOLINE RECEPTORS - NICOTINIC
    # ────────────────────────────────────────────────────────────

    AcetylcholineReceptorN.ALPHA4BETA2: ReceptorParams(
        name="α4β2",
        family=ReceptorFamily.ACETYLCHOLINE_N,
        kd_nM=5.0,
        hill_coefficient=1.6,  # Cooperative
        gprotein=None,
        second_messenger="ion_channel",
        excitatory=True,
        tau_onset=10.0,   # Very fast
        tau_offset=50.0,
        excitability_modulation=0.4,
        gain_modulation=0.3,
        plasticity_modulation=0.2,
        is_autoreceptor=False
    ),

    AcetylcholineReceptorN.ALPHA7: ReceptorParams(
        name="α7",
        family=ReceptorFamily.ACETYLCHOLINE_N,
        kd_nM=100.0,
        hill_coefficient=1.8,
        gprotein=None,
        second_messenger="ion_channel",
        excitatory=True,
        tau_onset=5.0,    # Extremely fast
        tau_offset=30.0,
        excitability_modulation=0.5,
        gain_modulation=0.4,
        plasticity_modulation=0.4,  # Ca2+ influx → plasticity
        is_autoreceptor=False
    ),
}


# ═══════════════════════════════════════════════════════════════
# RECEPTOR DISTRIBUTION BY NEURON TYPE
# ═══════════════════════════════════════════════════════════════

@dataclass
class ReceptorExpression:
    """Receptor expression level for a neuron type."""
    receptor: Enum
    density: float  # 0-1, relative expression level


# Realistic distributions based on literature
PYRAMIDAL_RECEPTORS = [
    ReceptorExpression(SerotoninReceptor.HT1A, 0.8),
    ReceptorExpression(SerotoninReceptor.HT2A, 0.6),
    ReceptorExpression(DopamineReceptor.D1, 0.7),
    ReceptorExpression(DopamineReceptor.D2, 0.3),
    ReceptorExpression(NoradrenalineReceptor.ALPHA1, 0.6),
    ReceptorExpression(NoradrenalineReceptor.BETA1, 0.5),
    ReceptorExpression(AcetylcholineReceptorM.M1, 0.8),
    ReceptorExpression(AcetylcholineReceptorN.ALPHA4BETA2, 0.4),
]

PV_RECEPTORS = [
    ReceptorExpression(SerotoninReceptor.HT1A, 0.3),
    ReceptorExpression(SerotoninReceptor.HT2A, 0.7),  # High 5-HT2A
    ReceptorExpression(DopamineReceptor.D1, 0.4),
    ReceptorExpression(DopamineReceptor.D2, 0.5),
    ReceptorExpression(NoradrenalineReceptor.ALPHA1, 0.7),
    ReceptorExpression(AcetylcholineReceptorN.ALPHA4BETA2, 0.6),
]

SST_RECEPTORS = [
    ReceptorExpression(SerotoninReceptor.HT1A, 0.7),
    ReceptorExpression(SerotoninReceptor.HT2A, 0.4),
    ReceptorExpression(DopamineReceptor.D2, 0.6),
    ReceptorExpression(NoradrenalineReceptor.ALPHA2, 0.5),
    ReceptorExpression(AcetylcholineReceptorM.M2, 0.6),
]

VIP_RECEPTORS = [
    ReceptorExpression(SerotoninReceptor.HT2C, 0.7),
    ReceptorExpression(DopamineReceptor.D1, 0.6),
    ReceptorExpression(NoradrenalineReceptor.BETA1, 0.6),
    ReceptorExpression(AcetylcholineReceptorM.M1, 0.5),
]


# ═══════════════════════════════════════════════════════════════
# RECEPTOR ACTIVATION
# ═══════════════════════════════════════════════════════════════

def calculate_receptor_activation(nt_concentration_nM, receptor_params, density):
    """
    Calculate receptor activation using Hill equation.

    Args:
        nt_concentration_nM: NT concentration in nM (NOT normalized 0-1!)
        receptor_params: ReceptorParameters
        density: receptor density (0-1)
    """
    kd = receptor_params.kd_nM
    n = receptor_params.hill_coefficient

    # Hill equation: activation = C^n / (Kd^n + C^n)
    activation = (nt_concentration_nM ** n) / (kd ** n + nt_concentration_nM ** n)

    # Scale by receptor density
    effective_activation = activation * density

    return np.clip(effective_activation, 0.0, 1.0)


def calculate_neuronal_modulation(
    activations: Dict[Enum, float],
    receptor_database: Dict[Enum, ReceptorParams]
) -> Dict[str, float]:
    """
    Calculate net modulation of neuronal properties.

    Args:
        activations: Dict of receptor → activation level
        receptor_database: Receptor parameter database

    Returns:
        Dict with modulation values:
        - excitability_change: Change in threshold
        - gain_change: Change in input-output gain
        - plasticity_change: Change in learning rate
    """
    excitability = 0.0
    gain = 0.0
    plasticity = 0.0

    for receptor, activation in activations.items():
        if receptor not in receptor_database:
            continue

        params = receptor_database[receptor]

        excitability += activation * params.excitability_modulation
        gain += activation * params.gain_modulation
        plasticity += activation * params.plasticity_modulation

    return {
        'excitability_change': np.clip(excitability, -0.5, 0.5),
        'gain_change': np.clip(gain, -0.5, 0.5),
        'plasticity_change': np.clip(plasticity, -0.5, 0.5)
    }


# ═══════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("NEUROMODULATOR RECEPTOR SYSTEM")
    print("=" * 60)

    # Example: Pyramidal neuron with serotonin
    print("\n1. Pyramidal neuron with elevated serotonin (0.7):")
    serotonin_level = 0.7

    activations = {}
    for expr in PYRAMIDAL_RECEPTORS:
        if expr.receptor.value.startswith("5-HT"):
            receptor = expr.receptor
            params = RECEPTOR_DATABASE[receptor]
            activation = calculate_receptor_activation(
                serotonin_level, params, expr.density
            )
            activations[receptor] = activation
            print(f"  {params.name}: {activation:.3f} (density={expr.density})")

    modulation = calculate_neuronal_modulation(activations, RECEPTOR_DATABASE)
    print(f"\n  Net effects:")
    print(f"    Excitability: {modulation['excitability_change']:+.3f}")
    print(f"    Gain: {modulation['gain_change']:+.3f}")
    print(f"    Plasticity: {modulation['plasticity_change']:+.3f}")

    # Example: Effect of SSRI
    print("\n2. Effect of SSRI (serotonin 0.3 → 0.7):")
    before = calculate_neuronal_modulation({
        SerotoninReceptor.HT1A: calculate_receptor_activation(
            0.3, RECEPTOR_DATABASE[SerotoninReceptor.HT1A], 0.8
        ),
        SerotoninReceptor.HT2A: calculate_receptor_activation(
            0.3, RECEPTOR_DATABASE[SerotoninReceptor.HT2A], 0.6
        )
    }, RECEPTOR_DATABASE)

    after = calculate_neuronal_modulation({
        SerotoninReceptor.HT1A: calculate_receptor_activation(
            0.7, RECEPTOR_DATABASE[SerotoninReceptor.HT1A], 0.8
        ),
        SerotoninReceptor.HT2A: calculate_receptor_activation(
            0.7, RECEPTOR_DATABASE[SerotoninReceptor.HT2A], 0.6
        )
    }, RECEPTOR_DATABASE)

    print(f"  Excitability: {before['excitability_change']:+.3f} → {after['excitability_change']:+.3f}")
    print(f"  Gain: {before['gain_change']:+.3f} → {after['gain_change']:+.3f}")
    print(f"  Plasticity: {before['plasticity_change']:+.3f} → {after['plasticity_change']:+.3f}")