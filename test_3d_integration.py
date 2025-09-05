"""
Test script for the 3D visualization integration.

This script demonstrates the complete 3D visualization system including:
- Interactive 3D renderer
- Tank models with armor zones
- Ballistic trajectories with environmental effects
- Penetration analysis visualization
- Animation capabilities
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
import matplotlib.pyplot as plt

# Import our simulation components
from ammunition import APFSDS
from armor import CompositeArmor
from visualization.renderer_3d import Interactive3DRenderer, Animated3DRenderer

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
    
    # Enable advanced physics if available
    try:
        ammunition.enable_advanced_physics()
    except:
        pass  # Continue without advanced physics if not available
    
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
    
    # Enable advanced physics if available
    try:
        armor.enable_advanced_physics()
    except:
        pass  # Continue without advanced physics if not available
    
    return armor

def test_static_3d_visualization():
    """Test the static interactive 3D visualization."""
    
    print("Testing Static 3D Visualization...")
    print("=" * 50)
    
    # Create test objects
    ammunition = create_test_ammunition()
    armor = create_test_armor()
    
    # Create renderer
    renderer = Interactive3DRenderer(figsize=(14, 10), style='professional')
    
    # Environmental conditions
    environmental_conditions = {
        'wind_speed': 8.0,      # m/s
        'wind_direction': 30.0,  # degrees
        'temperature': 20.0,     # °C
        'altitude': 100.0,       # m
        'humidity': 65.0         # %
    }
    
    # Create visualization
    try:
        fig = renderer.create_complete_3d_visualization(
            ammunition=ammunition,
            armor=armor,
            target_range=2000.0,    # 2 km
            impact_angle=15.0,      # degrees
            launch_angle=2.5,       # degrees
            environmental_conditions=environmental_conditions
        )
        
        print("✓ 3D visualization created successfully")
        
        # Save the visualization
        output_file = "test_3d_visualization.png"
        renderer.save_visualization(output_file, dpi=150)
        print(f"✓ Visualization saved to: {output_file}")
        
        # Show the visualization (this will open an interactive window)
        print("\n🎯 Showing interactive 3D visualization...")
        print("   - Use mouse to rotate the view")
        print("   - Use sliders to adjust parameters")
        print("   - Use checkboxes to toggle elements")
        print("   - Close the window when done")
        
        renderer.show_visualization()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating static visualization: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_animated_3d_visualization():
    """Test the animated 3D visualization."""
    
    print("\nTesting Animated 3D Visualization...")
    print("=" * 50)
    
    # Create test objects
    ammunition = create_test_ammunition()
    armor = create_test_armor()
    
    # Create animated renderer
    renderer = Animated3DRenderer(figsize=(12, 9), style='tactical')
    
    # Define impact point
    impact_point = [20.0, 0.0, 2.0]  # 20m distance, centered, 2m height
    impact_angle = 12.0  # degrees
    
    try:
        # Create animated sequence
        animation = renderer.create_animated_penetration_sequence(
            ammunition=ammunition,
            armor=armor,
            impact_point=impact_point,
            impact_angle=impact_angle,
            duration=4.0  # 4 seconds
        )
        
        print("✓ Animation created successfully")
        
        # Save animation
        animation_file = "test_penetration_animation.gif"
        renderer.save_animation(animation_file, fps=20)
        print(f"✓ Animation saved to: {animation_file}")
        
        # Show animation
        print("\n🎬 Showing animated penetration sequence...")
        print("   - Animation shows projectile approach, impact, and effects")
        print("   - Close the window when done viewing")
        
        renderer.show_visualization()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating animation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_different_styles():
    """Test different visualization styles."""
    
    print("\nTesting Different Visualization Styles...")
    print("=" * 50)
    
    ammunition = create_test_ammunition()
    armor = create_test_armor()
    
    styles = ['professional', 'tactical', 'educational']
    
    for style in styles:
        print(f"\nTesting {style} style...")
        
        try:
            renderer = Interactive3DRenderer(figsize=(10, 8), style=style)
            
            fig = renderer.create_complete_3d_visualization(
                ammunition=ammunition,
                armor=armor,
                target_range=1500.0,
                impact_angle=20.0,
                launch_angle=3.0
            )
            
            # Save each style
            output_file = f"test_3d_{style}_style.png"
            renderer.save_visualization(output_file, dpi=120)
            print(f"✓ {style.capitalize()} style saved to: {output_file}")
            
            plt.close(fig)  # Close to avoid too many open figures
            
        except Exception as e:
            print(f"❌ Error with {style} style: {e}")

def run_integration_tests():
    """Run all integration tests."""
    
    print("🚀 Tank Armor Simulation - 3D Visualization Integration Test")
    print("=" * 65)
    
    # Check if required modules are available
    try:
        import matplotlib
        print(f"✓ Matplotlib version: {matplotlib.__version__}")
    except ImportError:
        print("❌ Matplotlib not available")
        return False
    
    try:
        import numpy
        print(f"✓ NumPy version: {numpy.__version__}")
    except ImportError:
        print("❌ NumPy not available")
        return False
    
    # Set matplotlib backend for testing
    matplotlib.use('TkAgg')  # Use TkAgg backend for interactive display
    print(f"✓ Using matplotlib backend: {matplotlib.get_backend()}")
    
    # Run tests
    results = []
    
    # Test 1: Different styles (non-interactive)
    print("\n" + "="*65)
    results.append(test_different_styles())
    
    # Test 2: Static interactive visualization
    print("\n" + "="*65)
    results.append(test_static_3d_visualization())
    
    # Test 3: Animated visualization
    print("\n" + "="*65)
    results.append(test_animated_3d_visualization())
    
    # Summary
    print("\n" + "="*65)
    print("📋 Test Results Summary:")
    print("-" * 30)
    
    if all(results):
        print("✅ All integration tests passed!")
        print("\nGenerated files:")
        for style in ['professional', 'tactical', 'educational']:
            print(f"   📄 test_3d_{style}_style.png")
        print("   📄 test_3d_visualization.png")
        print("   🎬 test_penetration_animation.gif")
        
    else:
        print("❌ Some tests failed")
        print(f"   Passed: {sum(results)}/{len(results)}")
    
    return all(results)

if __name__ == "__main__":
    success = run_integration_tests()
    
    if success:
        print("\n🎉 Integration test completed successfully!")
        print("The 3D visualization system is working correctly.")
    else:
        print("\n⚠️  Integration test completed with issues.")
        print("Check the error messages above for details.")
    
    input("\nPress Enter to exit...")
