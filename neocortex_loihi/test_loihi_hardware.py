#!/usr/bin/env python3
"""
Test Loihi hardware deployment.

Run this after installation to verify everything works.
"""

import sys


def test_nxsdk():
    """Test 1: NxSDK import."""
    print("\n[TEST 1] NxSDK Import")
    print("-" * 60)
    try:
        import nxsdk
        version = getattr(nxsdk, '__version__', 'unknown')
        print(f"[OK] NxSDK imported (version: {version})")
        return True
    except ImportError as e:
        print(f"[X] NxSDK not available: {e}")
        print("  Install: pip install nxsdk")
        return False


def test_hardware_init():
    """Test 2: Hardware initialization."""
    print("\n[TEST 2] Hardware Initialization")
    print("-" * 60)
    try:
        from loihi_hardware_init import create_loihi_hardware_system
        
        mapper, board = create_loihi_hardware_system(10000)
        print(f"[OK] Hardware initialized")
        return True
    except Exception as e:
        print(f"[X] Hardware init failed: {e}")
        return False


def test_brain_creation():
    """Test 3: Brain creation on hardware."""
    print("\n[TEST 3] Brain Creation")
    print("-" * 60)
    try:
        from brain_loihi import create_brain
        
        brain = create_brain(n_neurons=10000, backend="loihi", debug=False)
        print(f"[OK] Brain created on hardware")
        return True
    except Exception as e:
        print(f"[X] Brain creation failed: {e}")
        return False


def test_execution():
    """Test 4: Hardware execution."""
    print("\n[TEST 4] Hardware Execution")
    print("-" * 60)
    try:
        from brain_loihi import create_brain
        
        brain = create_brain(n_neurons=1000, backend="loihi", debug=False)
        
        for t in range(10):
            state = brain.step()
            if t % 5 == 0:
                print(f"  t={t}: firing_rate={state['firing_rate']:.4f}")
        
        print(f"[OK] Hardware execution successful")
        return True
    except Exception as e:
        print(f"[X] Execution failed: {e}")
        return False


def main():
    print("=" * 60)
    print("NEOCORTEX LOIHI - HARDWARE TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_nxsdk,
        test_hardware_init,
        test_brain_creation,
        test_execution,
    ]
    
    passed = 0
    for test_func in tests:
        if test_func():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    print("=" * 60)
    
    if passed == len(tests):
        print("[OK] ALL TESTS PASSED - HARDWARE READY")
        return 0
    else:
        print("[X] SOME TESTS FAILED - CHECK ERRORS ABOVE")
        return 1


if __name__ == "__main__":
    sys.exit(main())
