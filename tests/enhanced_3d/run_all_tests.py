"""
Master Test Runner for Enhanced 3D Visualization System

This script runs all enhanced 3D visualization tests and organizes results properly.
"""

import sys
import os
import subprocess
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def run_test_script(script_path, description):
    """Run a test script and capture results."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Script: {script_path}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Change to the test directory to run the script
        test_dir = os.path.dirname(script_path)
        script_name = os.path.basename(script_path)
        
        # Run the script
        result = subprocess.run(
            [sys.executable, script_name],
            cwd=test_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ SUCCESS ({duration:.1f}s)")
            if result.stdout:
                print("Output:")
                print(result.stdout)
        else:
            print(f"❌ FAILED ({duration:.1f}s)")
            print("Error Output:")
            print(result.stderr)
            if result.stdout:
                print("Standard Output:")
                print(result.stdout)
        
        return result.returncode == 0, duration, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT after 5 minutes")
        return False, 300, "", "Test timed out"
    except Exception as e:
        print(f"💥 EXCEPTION: {str(e)}")
        return False, 0, "", str(e)

def create_test_report(test_results):
    """Create a detailed test report."""
    
    report_path = os.path.join("..", "..", "results", "enhanced_3d", "test_report.md")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Enhanced 3D Visualization Test Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Summary
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results if result[1])
        failed_tests = total_tests - passed_tests
        
        f.write("## Summary\n\n")
        f.write(f"- Total Tests: {total_tests}\n")
        f.write(f"- Passed: {passed_tests} ✅\n")
        f.write(f"- Failed: {failed_tests} ❌\n")
        f.write(f"- Success Rate: {(passed_tests/total_tests)*100:.1f}%\n\n")
        
        # Detailed results
        f.write("## Detailed Results\n\n")
        
        for test_name, success, duration, stdout, stderr in test_results:
            status = "✅ PASSED" if success else "❌ FAILED"
            f.write(f"### {test_name} - {status}\n\n")
            f.write(f"Duration: {duration:.1f} seconds\n\n")
            
            if stdout:
                f.write("**Output:**\n```\n")
                f.write(stdout)
                f.write("\n```\n\n")
            
            if stderr:
                f.write("**Error Output:**\n```\n")
                f.write(stderr)
                f.write("\n```\n\n")
    
    print(f"\n📊 Test report saved to: {report_path}")
    return report_path

def main():
    """Run all enhanced 3D visualization tests."""
    
    print("Enhanced 3D Visualization System - Master Test Runner")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define test scripts to run
    test_scripts = [
        ("calculate_max_range.py", "Maximum Range Calculation"),
        ("test_simple.py", "Simple 3D Visualization Test"),
        ("test_comprehensive.py", "Comprehensive System Test"),
        ("integrate_enhanced_3d_viz.py", "Integration Script Test"),
    ]
    
    test_results = []
    total_start_time = time.time()
    
    # Run each test script
    for script_name, description in test_scripts:
        script_path = os.path.join(os.path.dirname(__file__), script_name)
        
        if os.path.exists(script_path):
            success, duration, stdout, stderr = run_test_script(script_path, description)
            test_results.append((description, success, duration, stdout, stderr))
        else:
            print(f"❌ Script not found: {script_path}")
            test_results.append((description, False, 0, "", f"Script not found: {script_path}"))
    
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for result in test_results if result[1])
    failed = len(test_results) - passed
    
    print(f"Total Tests: {len(test_results)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success Rate: {(passed/len(test_results))*100:.1f}%")
    print(f"Total Duration: {total_duration:.1f} seconds")
    
    # Create test report
    report_path = create_test_report(test_results)
    
    # Final status
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Enhanced 3D visualization system is ready!")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the test report for details.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
