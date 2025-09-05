"""
Simplified 3D visualization integration test.

This script tests the basic integration between ammunition, armor, and
visualization components without the complex 3D renderer.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
import matplotlib.pyplot as plt

try:
    # Import our simulation components
    from ammunition import APFSDS
    from armor import CompositeArmor
    from visualization.interactive_3d import Interactive3DVisualizer
    
    print("✓ Successfully imported all required modules")
    
except ImportError as e:
    print(f"❌ Failed to import modules: {e}")
    sys.exit(1)

def create_test_ammunition():
    """Create test ammunition for visualization."""
    
    # Create M829A4 APFSDS round for testing
    ammunition = APFSDS(
        name="M829A4 APFSDS",
        caliber=120,
        penetrator_diameter=22,  # mm (subcaliber)
        penetrator_mass=7.0,  # kg
        muzzle_velocity=1670,  # m/s
        penetrator_length=685  # mm
    )
    
    print(f"✓ Created ammunition: {ammunition.name}")
    print(f"  - Caliber: {ammunition.caliber}mm")
    print(f"  - Penetrator mass: {ammunition.mass}kg")
    print(f"  - Muzzle velocity: {ammunition.muzzle_velocity}m/s")
    
    return ammunition

def create_test_armor():
    """Create test armor for visualization."""
    
    # Create modern MBT composite armor
    armor = CompositeArmor(
        name="Modern MBT Composite",
        thickness=650,  # mm total
        steel_layers=250,  # mm (100 + 150)
        ceramic_layers=400,  # mm
        other_layers=0  # mm
    )
    
    print(f"✓ Created armor: {armor.name}")
    print(f"  - Total thickness: {armor.thickness}mm")
    print(f"  - Steel layers: {armor.steel_layers}mm")
    print(f"  - Ceramic layers: {armor.ceramic_layers}mm")
    
    return armor

def test_basic_calculations():
    """Test basic ammunition and armor calculations."""
    
    print("\n📊 Testing Basic Calculations...")
    print("=" * 40)
    
    # Create test objects
    ammunition = create_test_ammunition()
    armor = create_test_armor()
    
    # Test penetration calculation
    test_range = 2000  # meters
    test_angle = 15    # degrees
    
    penetration = ammunition.calculate_penetration(test_range, test_angle)
    print(f"\n🎯 Penetration at {test_range}m, {test_angle}°: {penetration:.1f}mm RHA")
    
    # Test armor effectiveness
    can_defeat = armor.can_defeat(penetration, 'kinetic', test_angle)
    effective_thickness = armor.get_effective_thickness('kinetic', test_angle)
    
    print(f"🛡️  Effective armor thickness: {effective_thickness:.1f}mm RHA")
    print(f"🎲 Can armor defeat round: {'❌ NO' if not can_defeat else '✅ YES'}")
    
    return ammunition, armor

def test_3d_visualizer():
    """Test the 3D visualizer component."""
    
    print("\n🎨 Testing 3D Visualizer...")
    print("=" * 40)
    
    try:
        # Create visualizer
        visualizer = Interactive3DVisualizer(figsize=(12, 8))
        print("✓ Created 3D visualizer")
        
        # Test tank model creation
        tank_model = visualizer.create_3d_tank_model('modern_mbt')
        print("✓ Created 3D tank model")
        
        # Check model structure
        expected_components = ['hull', 'turret', 'gun', 'tracks', 'armor_zones', 'dimensions']
        for component in expected_components:
            if component in tank_model:
                print(f"  ✓ {component.capitalize()} component present")
            else:
                print(f"  ❌ {component.capitalize()} component missing")
        
        return visualizer, tank_model
        
    except Exception as e:
        print(f"❌ Error testing 3D visualizer: {e}")
        return None, None

def test_basic_3d_plot():
    """Create a basic 3D plot to test matplotlib 3D functionality."""
    
    print("\n📈 Testing Basic 3D Plotting...")
    print("=" * 40)
    
    try:
        from mpl_toolkits.mplot3d import Axes3D
        
        # Create simple 3D plot
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Simple tank hull representation
        x = np.array([0, 4, 4, 0, 0])  # Tank length
        y = np.array([-1, -1, 1, 1, -1])  # Tank width
        z = np.array([0, 0, 0, 0, 0])  # Ground level
        
        # Plot tank outline
        ax.plot(x, y, z, 'b-', linewidth=3, label='Tank Hull')
        
        # Add gun barrel
        gun_x = [2, 6]
        gun_y = [0, 0]
        gun_z = [0.5, 0.5]
        ax.plot(gun_x, gun_y, gun_z, 'k-', linewidth=4, label='Gun Barrel')
        
        # Add projectile trajectory
        traj_x = np.linspace(-5, 2, 20)
        traj_z = 2 - 0.1 * (traj_x + 5)**2 / 5  # Parabolic trajectory
        traj_y = np.zeros_like(traj_x)
        
        ax.plot(traj_x, traj_y, traj_z, 'r--', linewidth=2, alpha=0.7, label='Trajectory')
        
        # Add impact point
        ax.scatter([2], [0], [0.2], c='red', s=100, marker='*', label='Impact')
        
        # Styling
        ax.set_xlabel('Distance (m)')
        ax.set_ylabel('Lateral (m)')
        ax.set_zlabel('Height (m)')
        ax.legend()
        ax.set_title('Tank Armor Simulation - Basic 3D View')
        
        # Set equal aspect ratio
        ax.set_xlim([-6, 8])
        ax.set_ylim([-3, 3])
        ax.set_zlim([0, 3])
        
        # Save plot
        plt.savefig('test_basic_3d_plot.png', dpi=150, bbox_inches='tight')
        print("✓ Created basic 3D plot")
        print("✓ Saved plot as: test_basic_3d_plot.png")
        
        # Don't show interactively for now
        plt.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating basic 3D plot: {e}")
        return False

def run_simple_integration_test():
    """Run simplified integration tests."""
    
    print("🚀 Tank Armor Simulation - Simplified 3D Integration Test")
    print("=" * 60)
    
    # Check matplotlib
    try:
        import matplotlib
        print(f"✓ Matplotlib version: {matplotlib.__version__}")
        
        # Set backend for headless operation
        matplotlib.use('Agg')  # Non-interactive backend
        print("✓ Using non-interactive matplotlib backend (Agg)")
        
    except ImportError:
        print("❌ Matplotlib not available")
        return False
    
    # Run tests
    success_count = 0
    total_tests = 3
    
    # Test 1: Basic calculations
    try:
        ammunition, armor = test_basic_calculations()
        success_count += 1
        print("✅ Test 1: Basic calculations - PASSED")
    except Exception as e:
        print(f"❌ Test 1: Basic calculations - FAILED: {e}")
    
    # Test 2: 3D visualizer
    try:
        visualizer, tank_model = test_3d_visualizer()
        if visualizer and tank_model:
            success_count += 1
            print("✅ Test 2: 3D visualizer - PASSED")
        else:
            print("❌ Test 2: 3D visualizer - FAILED")
    except Exception as e:
        print(f"❌ Test 2: 3D visualizer - FAILED: {e}")
    
    # Test 3: Basic 3D plotting
    try:
        if test_basic_3d_plot():
            success_count += 1
            print("✅ Test 3: Basic 3D plotting - PASSED")
        else:
            print("❌ Test 3: Basic 3D plotting - FAILED")
    except Exception as e:
        print(f"❌ Test 3: Basic 3D plotting - FAILED: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📋 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! Basic integration is working.")
        return True
    else:
        print(f"⚠️  {total_tests - success_count} test(s) failed.")
        return False

if __name__ == "__main__":
    success = run_simple_integration_test()
    
    if success:
        print("\n✅ Simple integration test completed successfully!")
    else:
        print("\n❌ Some integration issues detected.")
    
    print("\nGenerated files:")
    if os.path.exists('test_basic_3d_plot.png'):
        print("  📄 test_basic_3d_plot.png")
    
    print("\nPress any key to continue...")
    input()
