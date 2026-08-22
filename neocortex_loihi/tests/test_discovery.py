#!/usr/bin/env python3
"""
Quick test for Loihi Drug Discovery

Tests:
1. Drug simulator
2. Genetic algorithm
3. Molecular generation
4. Full pipeline
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Use existing Loihi pharmacology!
from pharmacology.drug_mechanisms import DrugMechanism, DiseaseProfile, Pharmacokinetics, DrugSimulator
from drug_discovery_loihi import discover_drug, OptimizationConfig
from brain_loihi import NeoCortexLoihiBrain, BrainConfig


def test_drug_simulator():
    """Test basic drug simulation."""
    print("\n" + "="*60)
    print("TEST 1: Drug Simulator")
    print("="*60)
    
    # Create small brain
    config = BrainConfig(n_neurons=1000, backend="numpy", debug=False)
    brain = NeoCortexLoihiBrain(config)
    
    # Define simple SSRI-like drug
    drug = DrugMechanism(sert_inhibition=0.8)
    
    # Depression profile
    disease = DiseaseProfile(serotonin_deficit=0.4)
    
    # PK
    pk = Pharmacokinetics(halfLife_hours=24, tmax_hours=2)
    
    # Simulate
    simulator = DrugSimulator(brain, drug, disease, pk)
    results = simulator.run_trial(dose_mg=50, typical_dose_mg=50, duration_hours=24, sampling_interval_hours=12)
    
    print(f"\n[OK] Simulated {len(results)} timepoints")
    print(f"  Baseline 5HT: {results[0]['serotonin']:.3f}")
    print(f"  Final 5HT: {results[-1]['serotonin']:.3f}")
    
    return True


def test_genetic_algorithm():
    """Test GA optimization."""
    print("\n" + "="*60)
    print("TEST 2: Genetic Algorithm Optimization")
    print("="*60)
    
    # Create brain
    config = BrainConfig(n_neurons=5000, backend="numpy", debug=False)
    brain = NeoCortexLoihiBrain(config)
    
    # Disease
    disease = DiseaseProfile(
        serotonin_deficit=0.4,
        dopamine_deficit=0.3,
        noradrenaline_deficit=0.25
    )
    
    # Quick optimization
    opt_config = OptimizationConfig(
        iterations=3,
        population_size=3,
        trial_duration=24,
        sampling_interval=12
    )
    
    # Run discovery
    result = discover_drug(brain, disease, opt_config, generate_structure=False)
    
    print(f"\n[OK] Optimization complete")
    print(f"  Best fitness: {result['final_fitness']:.3f}")
    print(f"  Generations: {result['generations']}")
    print(f"  Drug: {result['optimal_drug']['name']}")
    
    return True


def test_molecular_generation():
    """Test SMILES generation."""
    print("\n" + "="*60)
    print("TEST 3: Molecular Structure Generation")
    print("="*60)
    
    from molecular_generator_ai import generate_structure_for_drug
    
    # Target profile (SSRI-like)
    targets = {
        'sert_inhibition': 0.85,
        'net_inhibition': 0.30
    }
    
    # Generate
    result = generate_structure_for_drug(targets, num_candidates=3, mode="fragment")
    
    print(f"\n[OK] Molecular structure generated")
    print(f"  SMILES: {result['smiles']}")
    print(f"  MW: {result['properties']['molecular_weight']:.1f}")
    print(f"  LogP: {result['properties']['logp']:.2f}")
    print(f"  Drug-like: {result['properties']['is_drug_like']}")
    
    return True


def test_full_pipeline():
    """Test complete pipeline."""
    print("\n" + "="*60)
    print("TEST 4: Full Pipeline (Drug Discovery + SMILES)")
    print("="*60)
    
    # Create brain
    config = BrainConfig(n_neurons=3000, backend="numpy", debug=False)
    brain = NeoCortexLoihiBrain(config)
    
    # Disease
    disease = DiseaseProfile(serotonin_deficit=0.4, dopamine_deficit=0.3)
    
    # Quick optimization
    opt_config = OptimizationConfig(
        iterations=2,
        population_size=2,
        trial_duration=12,
        sampling_interval=12
    )
    
    # Run with structure generation
    result = discover_drug(brain, disease, opt_config, generate_structure=True)
    
    print(f"\n[OK] Full pipeline complete")
    print(f"  Fitness: {result['final_fitness']:.3f}")
    print(f"  Drug: {result['optimal_drug']['name']}")
    
    if result['optimal_drug'].get('molecular_structure'):
        print(f"  SMILES: {result['optimal_drug']['molecular_structure']['smiles']}")
    
    return True


def main():
    """Run all tests."""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║       LOIHI DRUG DISCOVERY - QUICK TEST SUITE             ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    tests = [
        ("Drug Simulator", test_drug_simulator),
        ("Genetic Algorithm", test_genetic_algorithm),
        ("Molecular Generation", test_molecular_generation),
        ("Full Pipeline", test_full_pipeline),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
            print(f"\n[OK] {name}: PASSED")
        except Exception as e:
            results.append((name, False))
            print(f"\n[X] {name}: FAILED")
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for name, success in results:
        status = "[OK] PASS" if success else "[X] FAIL"
        print(f"  {status}: {name}")
    
    passed = sum(1 for _, s in results if s)
    total = len(results)
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n All tests passed! System ready for drug discovery.")
        return 0
    else:
        print("\n[!]  Some tests failed. Check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
