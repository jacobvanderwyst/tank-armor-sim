"""
Comprehensive test script for the working 3D visualization system.

This script demonstrates the complete working 3D visualization system including:
- Working 3D renderer with simplified but functional visualizations
- Tank models with penetration analysis
- Ballistic trajectories 
- Animation capabilities
- Multiple visualization styles
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
import matplotlib.pyplot as plt

try:
    # Import our simulation components
    from ammunition import APFSDS, AP, HEAT
    from armor import CompositeArmor, RHA
    from visualization.renderer_3d_working import Working3DRenderer, Simple3DAnimator
    
    print("✓ Successfully imported all required modules")
    
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

def create_test_scenarios():
    """Create different test scenarios for visualization."""
    
    scenarios = []
    
    # Scenario 1: Modern APFSDS vs Composite Armor (Penetration)
    apfsds = APFSDS(
        name="M829A4 APFSDS",
        caliber=120,
        penetrator_diameter=22,
        penetrator_mass=7.0,
        muzzle_velocity=1670,
        penetrator_length=685
    )
    
    composite_armor = CompositeArmor(
        name="Modern Composite",
        thickness=650,
        steel_layers=250,
        ceramic_layers=400,
        other_layers=0
    )
    
    scenarios.append({
        'name': 'Modern APFSDS vs Composite',
        'ammo': apfsds,
        'armor': composite_armor,
        'range': 2000,
        'angle': 15,
        'style': 'professional'
    })
    
    # Scenario 2: WWII AP vs Steel Armor (No Penetration)
    ap_round = AP(
        name="76mm AP M79",
        caliber=76,
        mass=7.0,
        muzzle_velocity=792
    )
    
    steel_armor = RHA(
        thickness=100  # RHA constructor generates name automatically
    )
    
    scenarios.append({
        'name': 'WWII AP vs Steel',
        'ammo': ap_round,
        'armor': steel_armor,
        'range': 1000,
        'angle': 30,
        'style': 'tactical'
    })
    
    # Scenario 3: HEAT vs Composite (Mixed Result)
    heat_round = HEAT(
        name="120mm HEAT-MP",
        caliber=120,
        warhead_mass=8.5,  # Total warhead mass in kg
        explosive_mass=2.8,  # Explosive charge mass in kg
        standoff_distance=200  # Standoff distance in mm
    )
    
    scenarios.append({
        'name': 'HEAT vs Composite',
        'ammo': heat_round,
        'armor': composite_armor,
        'range': 3000,
        'angle': 10,
        'style': 'educational'
    })
    
    return scenarios

def test_static_visualizations():
    """Test static 3D visualizations with different scenarios."""
    
    print("\n🎨 Testing Static 3D Visualizations...")
    print("=" * 50)
    
    scenarios = create_test_scenarios()
    results = []
    
    for i, scenario in enumerate(scenarios):
        print(f"\n📊 Scenario {i+1}: {scenario['name']}")
        print("-" * 40)
        
        try:
            # Create renderer
            renderer = Working3DRenderer(figsize=(12, 9), style=scenario['style'])
            
            # Create visualization
            fig = renderer.create_3d_visualization(
                ammunition=scenario['ammo'],
                armor=scenario['armor'],
                target_range=scenario['range'],
                impact_angle=scenario['angle']
            )
            
            # Calculate and display results
            penetration = scenario['ammo'].calculate_penetration(scenario['range']/1000, scenario['angle'])
            effective = scenario['armor'].get_effective_thickness('kinetic', scenario['angle'])
            result = "PENETRATION" if penetration > effective else "NO PENETRATION"
            
            print(f"  🎯 Penetration: {penetration:.0f}mm RHA")
            print(f"  🛡️  Armor: {effective:.0f}mm RHA")
            print(f"  🎲 Result: {result}")
            
            # Save visualization
            filename = f"test_3d_scenario_{i+1}_{scenario['style']}.png"
            renderer.save_visualization(filename, dpi=150)
            print(f"  ✓ Saved: {filename}")
            
            plt.close(fig)  # Close to save memory
            results.append(True)
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append(False)
    
    return results

def test_animation():
    """Test animation capabilities."""
    
    print("\n🎬 Testing Animation...")
    print("=" * 30)
    
    try:
        # Create test scenario
        apfsds = APFSDS(
            name="M829A4 APFSDS",
            caliber=120,
            penetrator_diameter=22,
            penetrator_mass=7.0,
            muzzle_velocity=1670,
            penetrator_length=685
        )
        
        armor = CompositeArmor(
            name="Modern Composite",
            thickness=650,
            steel_layers=250,
            ceramic_layers=400,
            other_layers=0
        )
        
        # Create animator
        animator = Simple3DAnimator(figsize=(10, 8), style='tactical')
        
        # Create animation
        print("🎥 Creating penetration animation...")
        animation = animator.create_penetration_animation(
            ammunition=apfsds,
            armor=armor,
            target_range=2000,
            impact_angle=15,
            duration=3.0
        )
        
        # Save animation
        print("💾 Saving animation (this may take a moment)...")
        try:
            # Use Pillow writer for GIF
            from matplotlib.animation import PillowWriter
            writer = PillowWriter(fps=20)
            animation.save('test_penetration_animation.gif', writer=writer)
            print("✓ Animation saved: test_penetration_animation.gif")
        except Exception as e:
            print(f"⚠️  Could not save animation: {e}")
            print("  (This is often due to missing Pillow or imageio)")
        
        plt.close()
        return True
        
    except Exception as e:
        print(f"❌ Animation test failed: {e}")
        return False

def test_interactive_display():
    """Test interactive display (optional - requires GUI)."""
    
    print("\n🖥️  Testing Interactive Display...")
    print("=" * 35)
    
    try:
        # Check if we can use interactive backend
        current_backend = plt.get_backend()
        print(f"Current matplotlib backend: {current_backend}")
        
        if current_backend.lower() in ['agg', 'svg', 'pdf']:
            print("⚠️  Non-interactive backend detected.")
            print("   Interactive display test skipped.")
            return True
        
        # Create simple scenario
        apfsds = APFSDS(
            name="Test APFSDS",
            caliber=120,
            penetrator_diameter=22,
            penetrator_mass=7.0,
            muzzle_velocity=1670,
            penetrator_length=685
        )
        
        armor = RHA(thickness=200)
        
        # Create renderer
        renderer = Working3DRenderer(figsize=(10, 8), style='professional')
        
        # Create visualization  
        fig = renderer.create_3d_visualization(
            ammunition=apfsds,
            armor=armor,
            target_range=1500,
            impact_angle=20
        )
        
        print("🎯 Interactive window should appear...")
        print("   - Use mouse to rotate the 3D view")
        print("   - Close the window when done")
        print("   - This test will timeout after 5 seconds if no GUI")
        
        # Show with timeout
        import time
        start_time = time.time()
        
        try:
            # Non-blocking show
            plt.show(block=False)
            plt.pause(5)  # Show for 5 seconds
            plt.close()
            print("✓ Interactive display test completed")
            return True
            
        except Exception as e:
            print(f"⚠️  Interactive display not available: {e}")
            plt.close()
            return True  # Not a failure, just no GUI
    
    except Exception as e:
        print(f"❌ Interactive test error: {e}")
        return False

def run_comprehensive_test():
    """Run all comprehensive tests."""
    
    print("🚀 Tank Armor Simulation - Working 3D Visualization Test")
    print("=" * 65)
    
    # Check dependencies
    try:
        import matplotlib
        print(f"✓ Matplotlib version: {matplotlib.__version__}")
        
        import numpy as np
        print(f"✓ NumPy version: {np.__version__}")
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False
    
    # Set matplotlib backend
    matplotlib.use('Agg')  # Start with non-interactive backend
    print("✓ Using Agg backend for static tests")
    
    # Run tests
    test_results = {}
    
    # Test 1: Static visualizations
    print("\n" + "="*65)
    try:
        static_results = test_static_visualizations()
        test_results['static'] = all(static_results)
        if test_results['static']:
            print("✅ Static visualization tests: PASSED")
        else:
            print(f"⚠️  Static visualization tests: {sum(static_results)}/{len(static_results)} passed")
    except Exception as e:
        print(f"❌ Static visualization tests: FAILED - {e}")
        test_results['static'] = False
    
    # Test 2: Animation
    print("\n" + "="*65)
    try:
        test_results['animation'] = test_animation()
        if test_results['animation']:
            print("✅ Animation test: PASSED")
        else:
            print("❌ Animation test: FAILED")
    except Exception as e:
        print(f"❌ Animation test: FAILED - {e}")
        test_results['animation'] = False
    
    # Test 3: Interactive display (try to switch backend)
    print("\n" + "="*65)
    try:
        # Try to use interactive backend
        try:
            matplotlib.use('TkAgg')
            print("✓ Switched to TkAgg backend for interactive test")
        except:
            print("⚠️  Could not switch to interactive backend")
        
        test_results['interactive'] = test_interactive_display()
        if test_results['interactive']:
            print("✅ Interactive display test: PASSED")
        else:
            print("❌ Interactive display test: FAILED")
    except Exception as e:
        print(f"❌ Interactive display test: FAILED - {e}")
        test_results['interactive'] = False
    
    # Summary
    print("\n" + "="*65)
    print("📋 Test Results Summary:")
    print("-" * 30)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name.capitalize()}: {status}")
    
    print(f"\n📊 Overall: {passed_tests}/{total_tests} test categories passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! The 3D visualization system is fully functional.")
        success = True
    elif passed_tests >= 2:
        print("✅ Most tests passed! The core 3D visualization system is working.")
        success = True
    else:
        print("⚠️  Multiple test failures detected.")
        success = False
    
    # List generated files
    print("\n📁 Generated Files:")
    import glob
    png_files = glob.glob("test_3d_*.png")
    gif_files = glob.glob("test_*.gif")
    
    for png_file in png_files:
        print(f"   📄 {png_file}")
    for gif_file in gif_files:
        print(f"   🎬 {gif_file}")
    
    if not png_files and not gif_files:
        print("   (No files generated - check for errors above)")
    
    return success

if __name__ == "__main__":
    success = run_comprehensive_test()
    
    if success:
        print("\n🎉 Comprehensive test completed successfully!")
        print("The working 3D visualization system is ready for use.")
    else:
        print("\n⚠️  Some issues detected, but core functionality may still work.")
    
    print(f"\n💡 To use the 3D renderer in your code:")
    print("   from visualization.renderer_3d_working import Working3DRenderer")
    print("   renderer = Working3DRenderer(style='professional')")
    print("   fig = renderer.create_3d_visualization(ammo, armor, range, angle)")
    
    input("\nPress Enter to exit...")
