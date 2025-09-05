#!/usr/bin/env python3
"""
Test runner for the Tank Armor Simulation project.
Runs all test scripts in the tests directory.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_test_script(script_path):
    """Run a single test script and return success status."""
    print(f"\n{'='*80}")
    print(f"🧪 RUNNING: {script_path.name}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    try:
        # Run the test script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=script_path.parent.parent,  # Run from project root
            capture_output=False,  # Show output in real-time
            text=True
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"\n✅ {script_path.name} PASSED (took {duration:.2f}s)")
            return True
        else:
            print(f"\n❌ {script_path.name} FAILED (took {duration:.2f}s)")
            return False
            
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"\n💥 {script_path.name} CRASHED: {e} (took {duration:.2f}s)")
        return False

def discover_and_run_tests():
    """Discover and run all test scripts."""
    tests_dir = Path(__file__).parent
    project_root = tests_dir.parent
    
    print("🚀 Tank Armor Simulation - Test Runner")
    print("="*80)
    print(f"📁 Tests directory: {tests_dir}")
    print(f"📁 Project root: {project_root}")
    
    # Find all test scripts
    test_scripts = []
    
    # Look for test_*.py files
    for test_file in tests_dir.glob("test_*.py"):
        if test_file.name != "run_tests.py":  # Don't run ourselves
            test_scripts.append(test_file)
    
    if not test_scripts:
        print("\n⚠️  No test scripts found in tests directory!")
        return False
    
    print(f"\n🔍 Found {len(test_scripts)} test script(s):")
    for script in test_scripts:
        print(f"   - {script.name}")
    
    # Run all tests
    results = []
    start_total = time.time()
    
    for script in sorted(test_scripts):
        success = run_test_script(script)
        results.append((script.name, success))
    
    end_total = time.time()
    total_duration = end_total - start_total
    
    # Print summary
    print(f"\n{'🏆'*80}")
    print("TEST EXECUTION SUMMARY")
    print(f"{'🏆'*80}")
    
    passed = 0
    failed = 0
    
    for script_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {script_name:<30} {status}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 Results:")
    print(f"   🎯 Total Tests: {len(results)}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   ⏱️  Total Time: {total_duration:.2f}s")
    
    if failed == 0:
        print(f"\n🎉 ALL TESTS PASSED! The system is working correctly.")
        return True
    else:
        print(f"\n⚠️  {failed} test script(s) failed. Please check the output above.")
        return False

def main():
    """Main test runner entry point."""
    success = discover_and_run_tests()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
