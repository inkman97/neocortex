#!/usr/bin/env python3
"""
RECEPTOR SYSTEM - USAGE EXAMPLE

Demonstrates how neuromodulator receptors affect neuronal properties.
"""

import numpy as np
from neuromodulator_receptors import *

print("=" * 70)
print("  NEUROMODULATOR RECEPTOR SYSTEM - DEMO")
print("=" * 70)

# ═══════════════════════════════════════════════════════════════════
# EXAMPLE 1: Depression (Low Serotonin) vs Healthy
# ═══════════════════════════════════════════════════════════════════

print("\n" + "─" * 70)
print("EXAMPLE 1: DEPRESSION (Low Serotonin)")
print("─" * 70)

print("\n1A. Healthy Brain (5HT = 0.50):")
healthy_5ht = 0.50

activations_healthy = {}
for expr in PYRAMIDAL_RECEPTORS[:2]:  # Just 5-HT1A and 5-HT2A
    receptor = expr.receptor
    params = RECEPTOR_DATABASE[receptor]
    activation = calculate_receptor_activation(healthy_5ht, params, expr.density)
    activations_healthy[receptor] = activation
    print(f"  {params.name}: {activation:.3f} activation")

mod_healthy = calculate_neuronal_modulation(activations_healthy, RECEPTOR_DATABASE)
print(f"\n  → Excitability: {mod_healthy['excitability_change']:+.3f}")
print(f"  → Gain:         {mod_healthy['gain_change']:+.3f}")
print(f"  → Plasticity:   {mod_healthy['plasticity_change']:+.3f}")

print("\n1B. Depressed Brain (5HT = 0.12):")
depressed_5ht = 0.12

activations_depressed = {}
for expr in PYRAMIDAL_RECEPTORS[:2]:
    receptor = expr.receptor
    params = RECEPTOR_DATABASE[receptor]
    activation = calculate_receptor_activation(depressed_5ht, params, expr.density)
    activations_depressed[receptor] = activation
    print(f"  {params.name}: {activation:.3f} activation")

mod_depressed = calculate_neuronal_modulation(activations_depressed, RECEPTOR_DATABASE)
print(f"\n  → Excitability: {mod_depressed['excitability_change']:+.3f}")
print(f"  → Gain:         {mod_depressed['gain_change']:+.3f}")
print(f"  → Plasticity:   {mod_depressed['plasticity_change']:+.3f}")

print(f"\n  DELTA from healthy:")
print(f"  → Excitability: {mod_depressed['excitability_change'] - mod_healthy['excitability_change']:+.3f}")
print(f"  → Gain:         {mod_depressed['gain_change'] - mod_healthy['gain_change']:+.3f}")
print(f"  → Plasticity:   {mod_depressed['plasticity_change'] - mod_healthy['plasticity_change']:+.3f}")

# ═══════════════════════════════════════════════════════════════════
# EXAMPLE 2: SSRI Treatment
# ═══════════════════════════════════════════════════════════════════

print("\n" + "─" * 70)
print("EXAMPLE 2: SSRI TREATMENT")
print("─" * 70)

print("\n2. SSRI brings serotonin from 0.12 → 0.50:")

for day, ht_level in [(0, 0.12), (7, 0.35), (14, 0.45), (28, 0.50)]:
    activations = {}
    for expr in PYRAMIDAL_RECEPTORS[:2]:
        receptor = expr.receptor
        params = RECEPTOR_DATABASE[receptor]
        activation = calculate_receptor_activation(ht_level, params, expr.density)
        activations[receptor] = activation

    mod = calculate_neuronal_modulation(activations, RECEPTOR_DATABASE)

    print(f"\n  Day {day:2d} (5HT={ht_level:.2f}):")
    print(f"    Excitability: {mod['excitability_change']:+.3f}")
    print(f"    Gain:         {mod['gain_change']:+.3f}")
    print(f"    Plasticity:   {mod['plasticity_change']:+.3f}")

# ═══════════════════════════════════════════════════════════════════
# EXAMPLE 3: Dopamine and Learning
# ═══════════════════════════════════════════════════════════════════

print("\n" + "─" * 70)
print("EXAMPLE 3: DOPAMINE SURGE DURING REWARD")
print("─" * 70)

print("\n3A. Baseline dopamine (0.20):")
baseline_da = 0.20

activations_baseline_da = {}
for expr in PYRAMIDAL_RECEPTORS:
    if expr.receptor in [DopamineReceptor.D1, DopamineReceptor.D2]:
        receptor = expr.receptor
        params = RECEPTOR_DATABASE[receptor]
        activation = calculate_receptor_activation(baseline_da, params, expr.density)
        activations_baseline_da[receptor] = activation
        print(f"  {params.name}: {activation:.3f} activation (density={expr.density})")

mod_baseline_da = calculate_neuronal_modulation(activations_baseline_da, RECEPTOR_DATABASE)
print(f"\n  → Plasticity: {mod_baseline_da['plasticity_change']:+.3f}")

print("\n3B. Dopamine surge during reward (0.80):")
reward_da = 0.80

activations_reward_da = {}
for expr in PYRAMIDAL_RECEPTORS:
    if expr.receptor in [DopamineReceptor.D1, DopamineReceptor.D2]:
        receptor = expr.receptor
        params = RECEPTOR_DATABASE[receptor]
        activation = calculate_receptor_activation(reward_da, params, expr.density)
        activations_reward_da[receptor] = activation
        print(f"  {params.name}: {activation:.3f} activation (density={expr.density})")

mod_reward_da = calculate_neuronal_modulation(activations_reward_da, RECEPTOR_DATABASE)
print(f"\n  → Plasticity: {mod_reward_da['plasticity_change']:+.3f}")
print(f"\n  INCREASE: {mod_reward_da['plasticity_change'] - mod_baseline_da['plasticity_change']:+.3f}")
print(f"  → Learning rate increased by {((mod_reward_da['plasticity_change'] - mod_baseline_da['plasticity_change']) / (1 + mod_baseline_da['plasticity_change'])) * 100:.1f}%")

# ═══════════════════════════════════════════════════════════════════
# EXAMPLE 4: Different Neuron Types
# ═══════════════════════════════════════════════════════════════════

print("\n" + "─" * 70)
print("EXAMPLE 4: SEROTONIN EFFECTS ON DIFFERENT NEURONS")
print("─" * 70)

ht_high = 0.70

neuron_types = [
    ("Pyramidal", PYRAMIDAL_RECEPTORS),
    ("PV (fast-spiking)", PV_RECEPTORS),
    ("SST (dendrite-targeting)", SST_RECEPTORS),
    ("VIP (disinhibitory)", VIP_RECEPTORS)
]

for name, receptor_list in neuron_types:
    activations = {}
    for expr in receptor_list:
        receptor = expr.receptor
        if receptor not in RECEPTOR_DATABASE:
            continue
        params = RECEPTOR_DATABASE[receptor]

        # Only process serotonin receptors
        if not params.name.startswith("5-HT"):
            continue

        activation = calculate_receptor_activation(ht_high, params, expr.density)
        activations[receptor] = activation

    if activations:
        mod = calculate_neuronal_modulation(activations, RECEPTOR_DATABASE)
        print(f"\n{name}:")
        print(f"  Excitability: {mod['excitability_change']:+.3f}")
        print(f"  Gain:         {mod['gain_change']:+.3f}")
        print(f"  Plasticity:   {mod['plasticity_change']:+.3f}")

# ═══════════════════════════════════════════════════════════════════
# EXAMPLE 5: Receptor Affinity
# ═══════════════════════════════════════════════════════════════════

print("\n" + "─" * 70)
print("EXAMPLE 5: RECEPTOR AFFINITY (Kd) EFFECTS")
print("─" * 70)

print("\nHow activation changes with NT concentration for different receptors:\n")
print("  NT Conc  │  5-HT1A  │  5-HT2A  │  D1      │  D2      │  M1")
print("           │ (Kd=5nM) │ (Kd=10nM)│ (Kd=20nM)│ (Kd=15nM)│ (Kd=25nM)")
print("  ─────────┼──────────┼──────────┼──────────┼──────────┼──────────")

for conc_nM in [1, 5, 10, 20, 50, 100]:
    ht1a_act = calculate_receptor_activation(conc_nM, RECEPTOR_DATABASE[SerotoninReceptor.HT1A], 1.0)
    ht2a_act = calculate_receptor_activation(conc_nM, RECEPTOR_DATABASE[SerotoninReceptor.HT2A], 1.0)
    d1_act = calculate_receptor_activation(conc_nM, RECEPTOR_DATABASE[DopamineReceptor.D1], 1.0)
    d2_act = calculate_receptor_activation(conc_nM, RECEPTOR_DATABASE[DopamineReceptor.D2], 1.0)
    m1_act = calculate_receptor_activation(conc_nM, RECEPTOR_DATABASE[AcetylcholineReceptorM.M1], 1.0)

    print(f"  {conc_nM:5.2f}    │  {ht1a_act:.3f}   │  {ht2a_act:.3f}   │  {d1_act:.3f}   │  {d2_act:.3f}   │  {m1_act:.3f}")

print("\n→ Higher affinity (lower Kd) = activated at lower concentrations")

print("\n" + "=" * 70)
print("  END OF DEMO")
print("=" * 70)