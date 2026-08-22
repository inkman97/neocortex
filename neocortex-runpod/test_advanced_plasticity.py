#!/usr/bin/env python3
"""
ADVANCED PLASTICITY - TEST SUITE

Comprehensive tests for all plasticity mechanisms:
1. BCM Rule
2. Synaptic Scaling  
3. Three-Factor Learning
4. Short-Term Plasticity
5. Integration with NeoCortex

Run this before deploying to verify everything works!
"""

import numpy as np
import sys

print("="*70)
print("ADVANCED PLASTICITY - COMPREHENSIVE TEST SUITE")
print("="*70)

# ═══════════════════════════════════════════════════════════════════
# TEST 1: BCM RULE
# ═══════════════════════════════════════════════════════════════════

def test_bcm():
    print("\n[TEST 1] BCM Rule...")
    
    from advanced_plasticity import BCMPlasticity, PlasticityConfig
    
    config = PlasticityConfig(use_bcm=True, debug=False)
    bcm = BCMPlasticity(config)
    
    # Test 1: Threshold slides with activity
    print("  Test 1a: Threshold sliding...")
    initial_theta = bcm.theta
    
    for i in range(100):
        post_rate = 10.0  # High activity
        bcm.update_threshold(post_rate, dt=10.0)
    
    assert bcm.theta > initial_theta, "BCM threshold should increase with high activity!"
    print(f"    θ increased: {initial_theta:.2f} → {bcm.theta:.2f}")

    # Test 2: LTP when post > theta
    print("  Test 1b: LTP/LTD...")
    bcm.theta = 5.0

    delta_high = bcm.calculate_weight_change(
        pre_activity=1.0,
        post_rate=10.0,  # Above theta
        base_lr=0.001
    )
    assert delta_high > 0, "Should be LTP when post > theta!"
    print(f"    LTP: Δw = {delta_high:+.6f} (post=10 > θ=5)")

    # Test 3: LTD when post < theta
    delta_low = bcm.calculate_weight_change(
        pre_activity=1.0,
        post_rate=2.0,  # Below theta
        base_lr=0.001
    )
    assert delta_low < 0, "Should be LTD when post < theta!"
    print(f"    LTD: Δw = {delta_low:+.6f} (post=2 < θ=5)")

    print("  BCM PASSED\n")


# ═══════════════════════════════════════════════════════════════════
# TEST 2: SYNAPTIC SCALING
# ═══════════════════════════════════════════════════════════════════

def test_synaptic_scaling():
    print("[TEST 2] Synaptic Scaling...")

    from advanced_plasticity import SynapticScaling, PlasticityConfig

    config = PlasticityConfig(
        use_synaptic_scaling=True,
        scaling_target_rate=5.0,
        scaling_interval=100,
        debug=False
    )
    scaling = SynapticScaling(config)

    # Test 1: Too high activity → scale down
    print("  Test 2a: Scale down (high activity)...")
    for i in range(100):
        scaling.update_spike_count(spiked=True, dt=1.0)  # Always spiking

    assert scaling.should_scale(), "Should be time to scale!"
    factor = scaling.calculate_scaling_factor()
    assert factor < 1.0, f"Should scale down! Got {factor:.3f}"
    print(f"    Scaling down: factor = {factor:.3f} (high activity)")

    # Test 2: Too low activity → scale up
    print("  Test 2b: Scale up (low activity)...")
    scaling2 = SynapticScaling(config)
    for i in range(100):
        scaling2.update_spike_count(spiked=False, dt=1.0)  # Never spiking

    factor2 = scaling2.calculate_scaling_factor()
    assert factor2 > 1.0, f"Should scale up! Got {factor2:.3f}"
    print(f"    Scaling up: factor = {factor2:.3f} (low activity)")

    # Test 3: Target activity → no scaling
    print("  Test 2c: Maintain (target activity)...")
    scaling3 = SynapticScaling(config)
    target_rate = config.scaling_target_rate  # 5 Hz

    # Generate 5 Hz activity
    for i in range(100):
        spike = (i % 20) == 0  # 5% = 5 Hz at 1ms steps
        scaling3.update_spike_count(spiked=spike, dt=1.0)

    factor3 = scaling3.calculate_scaling_factor()
    assert 0.9 < factor3 < 1.1, f"Should be near 1.0! Got {factor3:.3f}"
    print(f"    Maintaining: factor = {factor3:.3f} (target activity)")

    print("  SYNAPTIC SCALING PASSED\n")


# ═══════════════════════════════════════════════════════════════════
# TEST 3: THREE-FACTOR LEARNING
# ═══════════════════════════════════════════════════════════════════

def test_three_factor():
    print("[TEST 3] Three-Factor Learning...")

    from advanced_plasticity import ThreeFactorLearning, PlasticityConfig

    config = PlasticityConfig(
        use_three_factor=True,
        eligibility_tau=100.0,
        debug=False
    )
    tfl = ThreeFactorLearning(config)

    # Test 1: Eligibility builds with correlation
    print("  Test 3a: Eligibility trace formation...")
    for i in range(10):
        tfl.update_eligibility(pre_spike=True, post_spike=True, dt=1.0)

    assert tfl.eligibility > 0, "Eligibility should build up!"
    elig_after_correlation = tfl.eligibility
    print(f"    Eligibility formed: {elig_after_correlation:.3f}")

    # Test 2: Eligibility decays
    print("  Test 3b: Eligibility decay...")
    for i in range(100):
        tfl.update_eligibility(pre_spike=False, post_spike=False, dt=10.0)

    assert tfl.eligibility < elig_after_correlation * 0.5, "Eligibility should decay!"
    print(f"    Eligibility decayed: {elig_after_correlation:.3f} → {tfl.eligibility:.3f}")

    # Test 3: Dopamine gates learning
    print("  Test 3c: Dopamine gating...")
    tfl.eligibility = 1.0  # Reset

    # High dopamine = reward = positive weight change
    tfl.set_neuromodulators(dopamine=0.8, serotonin=0.5)
    delta_high_da = tfl.calculate_weight_change(base_lr=0.001)

    # Low dopamine = punishment = negative weight change
    tfl.set_neuromodulators(dopamine=0.2, serotonin=0.5)
    delta_low_da = tfl.calculate_weight_change(base_lr=0.001)

    assert delta_high_da > delta_low_da, "High DA should give more positive change!"
    print(f"    DA gating: High DA={delta_high_da:+.6f}, Low DA={delta_low_da:+.6f}")

    print("  THREE-FACTOR LEARNING PASSED\n")


# ═══════════════════════════════════════════════════════════════════
# TEST 4: SHORT-TERM PLASTICITY
# ═══════════════════════════════════════════════════════════════════

def test_stp():
    print("[TEST 4] Short-Term Plasticity...")

    from advanced_plasticity import ShortTermPlasticity, PlasticityConfig

    config = PlasticityConfig(
        use_stp=True,
        stp_tau_facilitation=500.0,  # Long tau
        stp_tau_depression=1000.0,   # Long tau
        stp_facilitation_strength=1.0,  # Strong
        stp_depression_strength=0.3,
        debug=False
    )

    # Test 1: Facilitation (repeated spikes increase efficacy)
    print("  Test 4a: Facilitation...")
    stp_fac = ShortTermPlasticity(config, facilitation_dominant=True)

    efficacies = []
    print(f"    Initial state: fac={stp_fac.facilitation:.3f}, resources={stp_fac.available_resources:.3f}")

    for i in range(5):  # Fewer spikes, clearer trend
        eff = stp_fac.process_spike(dt=1.0)
        efficacies.append(eff)
        print(f"    Spike {i+1}: efficacy={eff:.3f}, fac={stp_fac.facilitation:.3f}, resources={stp_fac.available_resources:.3f}")
        # No decay between spikes for clearest facilitation

    # Check that facilitation built up
    assert efficacies[-1] > efficacies[0], f"Efficacy should increase with facilitation! Got {efficacies[0]:.3f} → {efficacies[-1]:.3f}"
    print(f"    Facilitation: {efficacies[0]:.3f} → {efficacies[-1]:.3f}")

    # Test 2: Depression (repeated spikes decrease efficacy)
    print("  Test 4b: Depression...")
    stp_dep = ShortTermPlasticity(config, facilitation_dominant=False)

    efficacies_dep = []
    print(f"    Initial state: fac={stp_dep.facilitation:.3f}, resources={stp_dep.available_resources:.3f}")

    for i in range(5):
        eff = stp_dep.process_spike(dt=1.0)
        efficacies_dep.append(eff)
        print(f"    Spike {i+1}: efficacy={eff:.3f}, resources={stp_dep.available_resources:.3f}")

    assert efficacies_dep[-1] < efficacies_dep[0], f"Efficacy should decrease with depression! Got {efficacies_dep[0]:.3f} → {efficacies_dep[-1]:.3f}"
    print(f"    Depression: {efficacies_dep[0]:.3f} → {efficacies_dep[-1]:.3f}")

    # Test 3: Recovery (no spikes → resources recover)
    print("  Test 4c: Recovery...")
    initial_resources = stp_dep.available_resources

    for i in range(100):  # Recovery period
        stp_dep.decay(dt=10.0)

    assert stp_dep.available_resources > initial_resources, f"Resources should recover! Got {initial_resources:.3f} → {stp_dep.available_resources:.3f}"
    print(f"    Recovery: {initial_resources:.3f} → {stp_dep.available_resources:.3f}")

    print("  SHORT-TERM PLASTICITY PASSED\n")


# ═══════════════════════════════════════════════════════════════════
# TEST 5: INTEGRATED MANAGER
# ═══════════════════════════════════════════════════════════════════

def test_integrated_manager():
    print("[TEST 5] Integrated Plasticity Manager...")

    from advanced_plasticity import AdvancedPlasticityManager, create_default_config

    config = create_default_config(debug=False)
    manager = AdvancedPlasticityManager(config)

    # Test 1: All mechanisms initialized
    print("  Test 5a: Initialization...")
    assert manager.bcm is not None, "BCM should be initialized!"
    assert manager.scaling is not None, "Scaling should be initialized!"
    assert manager.three_factor is not None, "Three-factor should be initialized!"
    print("    All mechanisms initialized")

    # Test 2: Update step
    print("  Test 5b: Update step...")
    results = manager.update_step(
        pre_spike=True,
        post_spike=True,
        post_rate=5.0,
        dopamine=0.6,
        serotonin=0.5,
        base_lr=0.001,
        dt=1.0
    )

    assert 'bcm_delta' in results, "Missing BCM delta!"
    assert 'three_factor_delta' in results, "Missing three-factor delta!"
    assert 'stp_efficacy' in results, "Missing STP efficacy!"
    print("    Update step returns all values")

    # Test 3: Get states
    print("  Test 5c: State retrieval...")
    states = manager.get_all_states()
    assert 'bcm' in states, "Missing BCM state!"
    assert 'scaling' in states, "Missing scaling state!"
    assert 'three_factor' in states, "Missing three-factor state!"
    print("    All states retrievable")

    print("  INTEGRATED MANAGER PASSED\n")


# ═══════════════════════════════════════════════════════════════════
# RUN ALL TESTS
# ═══════════════════════════════════════════════════════════════════

def run_all_tests():
    """Run complete test suite."""

    print("\nStarting test suite...\n")

    tests = [
        ("BCM Rule", test_bcm),
        ("Synaptic Scaling", test_synaptic_scaling),
        ("Three-Factor Learning", test_three_factor),
        ("Short-Term Plasticity", test_stp),
        ("Integrated Manager", test_integrated_manager)
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"  {name} FAILED: {e}\n")
            failed += 1
            import traceback
            traceback.print_exc()

    # Summary
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n ALL TESTS PASSED! System ready for deployment!")
        print("="*70)
        return True
    else:
        print(f"\n{failed} TEST(S) FAILED - Fix before deploying!")
        print("="*70)
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)