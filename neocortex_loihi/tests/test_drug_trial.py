"""
DRUG TRIAL TEST - Complete simulation

Tests the full pipeline:
1. Create brain
2. Apply disease profile
3. Run baseline
4. Apply drug
5. Measure response over time
6. Track NT levels + embodiment
"""

import numpy as np
import sys
sys.path.append('..')

from brain_loihi import create_brain
from pharmacology.drug_mechanisms import DrugSimulator, DrugMechanism, DiseaseProfile, Pharmacokinetics


def simulate_drug_trial(
    neurons: int = 100000,
    backend: str = "numpy",
    duration_hours: int = 168,  # 1 week
    sampling_interval_hours: int = 24,  # Daily samples
    fast_mode: bool = False  # Use 1 hour timesteps instead of 1 minute
):
    """
    Run complete drug trial simulation.
    
    Args:
        neurons: Number of neurons
        backend: "numpy", "lava_sim", or "loihi"
        duration_hours: Trial duration
        sampling_interval_hours: How often to sample
        
    Returns:
        List of timepoints with full state
    """
    print(f"\n{'='*70}")
    print(f"DRUG TRIAL SIMULATION")
    print(f"{'='*70}")
    print(f"Neurons: {neurons:,}")
    print(f"Backend: {backend}")
    print(f"Duration: {duration_hours} hours ({duration_hours//24} days)")
    print(f"Sampling: Every {sampling_interval_hours} hours")
    
    # Create brain
    print(f"\n[1/5] Creating brain...")
    brain = create_brain(n_neurons=neurons, backend=backend, debug=True)
    
    # Define disease (Major Depression)
    print(f"\n[2/5] Applying disease profile (Major Depression)...")
    disease = DiseaseProfile(
        serotonin_deficit=-0.4,   # 40% deficit
        dopamine_deficit=-0.2,    # 20% deficit
        noradrenaline_deficit=-0.1,  # 10% deficit
        acetylcholine_deficit=0.0,
        gaba_deficit=0.0,
        glutamate_deficit=0.0
    )
    
    # Apply disease by reducing NT system efficacy
    # (This would be done by reducing synaptic weights in modulatory pathways)
    # For simplicity, we simulate it as reduced tonic drive
    for nt_name, deficit in [('serotonin', disease.serotonin_deficit),
                              ('dopamine', disease.dopamine_deficit),
                              ('noradrenaline', disease.noradrenaline_deficit)]:
        if deficit < 0:
            # Reduce tonic drive
            factor = 1.0 + deficit  # e.g., -0.4 → 0.6
            pop_map = {
                'serotonin': 'SEROTONIN',
                'dopamine': 'DOPAMINE',
                'noradrenaline': 'NORADRENALINE'
            }
            from core.neuromodulation_loihi import Neuromodulator
            nt = Neuromodulator[pop_map[nt_name]]
            brain.neuromodulation.populations[nt].tonic_drive = int(
                brain.neuromodulation.populations[nt].tonic_drive * factor
            )
    
    # Run baseline
    print(f"\n[3/5] Running baseline (24 hours)...")
    # Timestep resolution
    if fast_mode:
        steps_per_hour = 1  # 1 hour timesteps (FAST)
        print("  [FAST MODE] Using 1-hour timesteps")
    else:
        steps_per_hour = 60  # 1 minute timesteps
        print("  Using 1-minute timesteps")
    
    baseline_steps = 24 * steps_per_hour  # 24 hours
    
    for t in range(baseline_steps):
        brain.step()
        if t % (steps_per_hour * 6) == 0:  # Every 6 hours
            print(f"  Baseline hour {t//steps_per_hour}...")
    
    baseline_state = brain.get_summary()
    print(f"  Baseline 5HT: {baseline_state['nt_levels']['5HT']:.3f}")
    print(f"  Baseline DA: {baseline_state['nt_levels']['DA']:.3f}")
    print(f"  Baseline valence: {baseline_state['embodiment'].get('gut_feeling', 0.5):.3f}")
    
    # Define drug (Fluoxetine - SSRI)
    print(f"\n[4/5] Applying drug (Fluoxetine 20mg)...")
    drug_targets = {
        'SERT': 0.85,  # 85% SERT inhibition
        'DAT': 0.0,
        'NET': 0.0
    }
    brain.apply_drug(drug_targets)
    
    # Run trial with sampling
    print(f"\n[5/5] Running trial with drug...")
    timepoints = []
    
    # Initial timepoint (t=0, drug just applied)
    state = brain.get_summary()
    timepoints.append({
        'hours': 0,
        'days': 0,
        'phase': 'baseline',
        'drug_concentration': 1.0,  # Simplified
        **state['nt_levels'],
        **state['embodiment'],
        'firing_rate': state['firing_rate']
    })
    
    # Simulate over duration
    total_steps = duration_hours * steps_per_hour  # 1 minute timesteps
    sample_every = sampling_interval_hours * steps_per_hour
    
    for t in range(total_steps):
        brain.step()
        
        # Sample at intervals
        if (t + 1) % sample_every == 0:
            hours = (t + 1) / steps_per_hour  # Convert steps to hours
            days = hours / 24
            
            state = brain.get_summary()
            
            # Determine phase
            if days < 1:
                phase = "acute"
            elif days < 7:
                phase = "subacute"
            elif days < 14:
                phase = "therapeutic"
            else:
                phase = "maintenance"
            
            # Simple PK: exponential decay
            # t1/2 = 24h for fluoxetine (simplified)
            drug_conc = np.exp(-0.693 * hours / 24)  # Half-life decay
            
            timepoint = {
                'hours': hours,
                'days': days,
                'phase': phase,
                'drug_concentration': drug_conc,
                **state['nt_levels'],
                **state['embodiment'],
                'firing_rate': state['firing_rate']
            }
            
            timepoints.append(timepoint)
            
            print(f"  Day {days:.1f}: 5HT={state['nt_levels']['5HT']:.3f}, "
                  f"Gut={state['embodiment'].get('gut_feeling', 0.5):.3f}")
    
    print(f"\n{'='*70}")
    print(f"TRIAL COMPLETE")
    print(f"{'='*70}")
    print(f"Timepoints collected: {len(timepoints)}")
    print(f"\nFinal state (Day {timepoints[-1]['days']:.1f}):")
    print(f"  5HT: {timepoints[-1]['5HT']:.3f} (baseline: {timepoints[0]['5HT']:.3f})")
    print(f"  DA: {timepoints[-1]['DA']:.3f} (baseline: {timepoints[0]['DA']:.3f})")
    print(f"  Gut feeling: {timepoints[-1]['gut_feeling']:.3f} (baseline: {timepoints[0]['gut_feeling']:.3f})")
    print(f"  Fatigue: {timepoints[-1]['fatigue']:.3f} (baseline: {timepoints[0]['fatigue']:.3f})")
    
    return timepoints


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run drug trial simulation")
    parser.add_argument("--neurons", type=int, default=10000,
                       help="Number of neurons (default: 10000)")
    parser.add_argument("--backend", type=str, default="numpy",
                       choices=["numpy", "lava_sim", "loihi"],
                       help="Simulation backend")
    parser.add_argument("--duration-hours", type=int, default=168,
                       help="Trial duration in hours (default: 168 = 1 week)")
    parser.add_argument("--sampling-hours", type=int, default=24,
                       help="Sampling interval in hours (default: 24)")
    parser.add_argument("--fast", action="store_true",
                       help="Fast mode: 1-hour timesteps instead of 1-minute (for quick testing)")
    
    args = parser.parse_args()
    
    timepoints = simulate_drug_trial(
        neurons=args.neurons,
        backend=args.backend,
        duration_hours=args.duration_hours,
        sampling_interval_hours=args.sampling_hours,
        fast_mode=args.fast
    )
    
    # Save results
    import json
    output_file = f"trial_results_{args.neurons}n_{args.backend}.json"
    with open(output_file, 'w') as f:
        json.dump(timepoints, f, indent=2)
    
    print(f"\n[OK] Results saved to: {output_file}")
