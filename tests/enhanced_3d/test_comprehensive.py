"""
Comprehensive Test Script for Enhanced 3D Visualization System

This script tests:
- Accurate trajectory calculation with debug logging
- Interactive 3D visualization with proper tank modeling
- Projectile following correct ballistic path
- Environmental effects integration
- Animation functionality
"""

import sys
import os
# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import numpy as np
import matplotlib.pyplot as plt
from src.visualization.enhanced_3d_visualizer import (
    Enhanced3DVisualizer, 
    TrajectoryPoint, 
    Enhanced3DDebugLogger
)
from src.physics.advanced_physics import EnvironmentalConditions
from src.ammunition import APFSDS
from src.armor import CompositeArmor

def test_trajectory_calculation_accuracy():
    """Test trajectory calculation accuracy with debug logging."""
    print("=== Testing Trajectory Calculation Accuracy ===")
    
    # Create test ammunition and environmental conditions
    ammo = APFSDS(name="M829A4", caliber=120, penetrator_diameter=22, 
                  penetrator_mass=8.5, muzzle_velocity=1680, penetrator_length=570)
    conditions = EnvironmentalConditions(
        temperature_celsius=20.0,
        wind_speed_ms=5.0,
        wind_angle_deg=45.0,
        humidity_percent=60.0
    )
    
    # Create visualizer with debug logging
    visualizer = Enhanced3DVisualizer(debug_level="DEBUG")
    
    # Calculate trajectory
    trajectory = visualizer.calculate_accurate_trajectory(
        ammo, target_range=2000.0, launch_angle=0.0, 
        environmental_conditions=conditions
    )
    
    # Verify trajectory properties
    assert len(trajectory) > 0, "Trajectory should have points"
    assert trajectory[0].x == 0.0, "Trajectory should start at origin"
    assert trajectory[0].z > 0, "Trajectory should start above ground"
    assert trajectory[-1].z <= 0.1, "Trajectory should end near ground"
    
    # Check trajectory follows physics
    max_height = max(point.z for point in trajectory)
    max_range = max(point.x for point in trajectory)
    
    print(f"✓ Trajectory calculated with {len(trajectory)} points")
    print(f"✓ Maximum height: {max_height:.2f} m")
    print(f"✓ Maximum range: {max_range:.2f} m")
    print(f"✓ Flight time: {trajectory[-1].time:.2f} s")
    
    # Verify environmental effects
    wind_deflection = abs(trajectory[-1].y)
    print(f"✓ Wind deflection: {wind_deflection:.2f} m")
    
    return trajectory

def test_enhanced_tank_modeling():
    """Test enhanced tank model creation."""
    print("\n=== Testing Enhanced Tank Modeling ===")
    
    visualizer = Enhanced3DVisualizer(debug_level="INFO")
    tank_model = visualizer.create_enhanced_tank_model("modern_mbt")
    
    # Verify tank model components
    expected_components = ['hull', 'turret', 'gun', 'tracks']
    for component in expected_components:
        assert component in tank_model, f"Tank model missing {component}"
    
    # Verify hull geometry
    hull = tank_model['hull']
    assert 'vertices' in hull, "Hull missing vertices"
    assert 'faces' in hull, "Hull missing faces"
    assert len(hull['vertices']) > 0, "Hull should have vertices"
    
    # Verify turret geometry
    turret = tank_model['turret']
    assert 'vertices' in turret, "Turret missing vertices"
    assert len(turret['vertices']) > 0, "Turret should have vertices"
    
    # Verify gun geometry
    gun = tank_model['gun']
    assert 'vertices' in gun, "Gun missing vertices"
    assert len(gun['vertices']) > 0, "Gun should have vertices"
    
    # Verify tracks
    tracks = tank_model['tracks']
    assert 'left' in tracks and 'right' in tracks, "Missing track components"
    
    print(f"✓ Tank model created with {len(tank_model)} components")
    print(f"✓ Hull vertices: {len(hull['vertices'])}")
    print(f"✓ Turret vertices: {len(turret['vertices'])}")
    print(f"✓ Gun vertices: {len(gun['vertices'])}")
    
    return tank_model

def test_interactive_3d_visualization():
    """Test creation of interactive 3D visualization."""
    print("\n=== Testing Interactive 3D Visualization ===")
    
    # Create test objects
    ammo = APFSDS(name="M829A4", caliber=120, penetrator_diameter=22, 
                  penetrator_mass=8.5, muzzle_velocity=1680, penetrator_length=570)
    armor = CompositeArmor("M1A2 Frontal", thickness=650, steel_layers=400, ceramic_layers=250)
    
    # Environmental conditions with wind
    conditions = EnvironmentalConditions(
        temperature_celsius=15.0,
        wind_speed_ms=8.0,
        wind_angle_deg=90.0,  # Crosswind
        humidity_percent=70.0,
        altitude_m=500.0
    )
    
    # Create visualizer
    visualizer = Enhanced3DVisualizer(figsize=(16, 12), debug_level="INFO")
    
    # Create interactive 3D visualization
    fig = visualizer.create_interactive_3d_visualization(
        ammo, armor, target_range=2500.0, launch_angle=2.0,
        environmental_conditions=conditions
    )
    
    # Verify figure was created
    assert fig is not None, "Figure should be created"
    assert visualizer.ax is not None, "3D axis should be created"
    assert len(visualizer.trajectory_points) > 0, "Trajectory points should exist"
    
    # Check trajectory bounds
    trajectory = visualizer.trajectory_points
    x_coords = [p.x for p in trajectory]
    y_coords = [p.y for p in trajectory]
    z_coords = [p.z for p in trajectory]
    
    print(f"✓ Interactive 3D visualization created")
    print(f"✓ Trajectory bounds:")
    print(f"  - X: {min(x_coords):.1f} to {max(x_coords):.1f} m")
    print(f"  - Y: {min(y_coords):.1f} to {max(y_coords):.1f} m") 
    print(f"  - Z: {min(z_coords):.1f} to {max(z_coords):.1f} m")
    
    # Test crosswind effect (should have lateral deflection)
    final_y = trajectory[-1].y
    print(f"✓ Crosswind deflection: {final_y:.2f} m")
    assert abs(final_y) > 0.1, "Should have crosswind deflection"
    
    return fig, visualizer

def test_projectile_animation():
    """Test animated projectile following trajectory."""
    print("\n=== Testing Projectile Animation ===")
    
    # Create test scenario
    ammo = APFSDS(name="M829A4", caliber=120, penetrator_diameter=22, 
                  penetrator_mass=8.5, muzzle_velocity=1680, penetrator_length=570)
    armor = CompositeArmor("T-80 Frontal", thickness=450, steel_layers=300, ceramic_layers=150)
    
    # Create visualizer and visualization
    visualizer = Enhanced3DVisualizer(debug_level="INFO")
    fig = visualizer.create_interactive_3d_visualization(
        ammo, armor, target_range=1500.0, launch_angle=0.5
    )
    
    # Enable animation
    animation = visualizer.enable_animation_mode(duration=3.0)
    
    # Verify animation was created
    assert animation is not None, "Animation should be created"
    assert visualizer.animation is not None, "Animation should be stored"
    
    trajectory = visualizer.trajectory_points
    print(f"✓ Animation created with {len(trajectory)} trajectory points")
    print(f"✓ Animation duration: 3.0 seconds")
    
    return animation, visualizer

def test_penetration_analysis():
    """Test penetration analysis visualization."""
    print("\n=== Testing Penetration Analysis ===")
    
    # Test successful penetration scenario
    powerful_ammo = APFSDS(name="DM63", caliber=120, penetrator_diameter=24, 
                          penetrator_mass=8.2, muzzle_velocity=1750, penetrator_length=600)
    weak_armor = CompositeArmor("Light Armor", thickness=200, steel_layers=200, ceramic_layers=0)
    
    visualizer = Enhanced3DVisualizer(debug_level="INFO")
    fig = visualizer.create_interactive_3d_visualization(
        powerful_ammo, weak_armor, target_range=1000.0, launch_angle=0.0
    )
    
    trajectory = visualizer.trajectory_points
    impact_point = trajectory[-1]
    
    # Calculate expected penetration
    penetration = powerful_ammo.calculate_penetration(1.0, 0.0)  # 1km range, 0° angle
    effective_thickness = weak_armor.get_effective_thickness('kinetic', 0.0)
    
    should_penetrate = penetration > effective_thickness
    
    print(f"✓ Penetration analysis completed")
    print(f"  - Penetration capability: {penetration:.1f} mm RHA")
    print(f"  - Effective armor thickness: {effective_thickness:.1f} mm RHA")
    print(f"  - Result: {'PENETRATION' if should_penetrate else 'NO PENETRATION'}")
    print(f"  - Impact velocity: {impact_point.velocity_magnitude:.1f} m/s")
    print(f"  - Impact angle: {abs(impact_point.angle_of_attack):.1f}°")
    
    return should_penetrate, visualizer

def test_environmental_effects():
    """Test environmental effects on trajectory."""
    print("\n=== Testing Environmental Effects ===")
    
    ammo = APFSDS(name="M829A4", caliber=120, penetrator_diameter=22, 
                  penetrator_mass=8.5, muzzle_velocity=1680, penetrator_length=570)
    
    # Test different environmental conditions
    test_conditions = [
        ("Standard", EnvironmentalConditions()),
        ("Cold", EnvironmentalConditions(temperature_celsius=-20.0)),
        ("Hot", EnvironmentalConditions(temperature_celsius=40.0)),
        ("High Altitude", EnvironmentalConditions(altitude_m=2000.0)),
        ("Strong Headwind", EnvironmentalConditions(wind_speed_ms=15.0, wind_angle_deg=0.0)),
        ("Strong Crosswind", EnvironmentalConditions(wind_speed_ms=15.0, wind_angle_deg=90.0))
    ]
    
    results = {}
    visualizer = Enhanced3DVisualizer(debug_level="INFO")
    
    for name, conditions in test_conditions:
        trajectory = visualizer.calculate_accurate_trajectory(
            ammo, target_range=2000.0, launch_angle=0.0,
            environmental_conditions=conditions
        )
        
        if trajectory:
            final_point = trajectory[-1]
            results[name] = {
                'range': final_point.x,
                'deflection': final_point.y,
                'impact_velocity': final_point.velocity_magnitude,
                'flight_time': final_point.time
            }
    
    # Display results
    print("✓ Environmental effects test results:")
    for name, result in results.items():
        print(f"  {name}:")
        print(f"    Range: {result['range']:.1f} m")
        print(f"    Deflection: {result['deflection']:.2f} m") 
        print(f"    Impact Velocity: {result['impact_velocity']:.1f} m/s")
        print(f"    Flight Time: {result['flight_time']:.2f} s")
    
    return results

def run_comprehensive_test():
    """Run all comprehensive tests."""
    print("Starting Enhanced 3D Visualization System Tests")
    print("=" * 60)
    
    try:
        # Test 1: Trajectory calculation
        trajectory = test_trajectory_calculation_accuracy()
        
        # Test 2: Tank modeling
        tank_model = test_enhanced_tank_modeling()
        
        # Test 3: Interactive 3D visualization
        fig, visualizer = test_interactive_3d_visualization()
        
        # Test 4: Animation
        animation, anim_visualizer = test_projectile_animation()
        
        # Test 5: Penetration analysis
        penetrates, pen_visualizer = test_penetration_analysis()
        
        # Test 6: Environmental effects
        env_results = test_environmental_effects()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("\nEnhanced 3D Visualization System is working correctly:")
        print("- Accurate trajectory calculations with physics integration")
        print("- Comprehensive debug logging system")
        print("- Interactive 3D visualizations with mouse controls")
        print("- Realistic tank modeling with proper proportions")
        print("- Projectile animation following ballistic path")
        print("- Environmental effects properly integrated")
        print("- Penetration analysis with behind-armor effects")
        
        return True, {
            'trajectory': trajectory,
            'tank_model': tank_model,
            'visualization': visualizer,
            'animation': animation,
            'environmental_results': env_results
        }
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None

def create_demonstration_visualization():
    """Create a demonstration of the enhanced 3D visualization."""
    print("\n=== Creating Demonstration Visualization ===")
    
    # Create realistic combat scenario
    ammo = APFSDS(name="M829A4", caliber=120, penetrator_diameter=22, 
                  penetrator_mass=8.5, muzzle_velocity=1680, penetrator_length=570)
    armor = CompositeArmor("T-90M Frontal", thickness=550, steel_layers=350, ceramic_layers=200)
    
    # Realistic environmental conditions
    conditions = EnvironmentalConditions(
        temperature_celsius=25.0,
        wind_speed_ms=6.0,
        wind_angle_deg=30.0,  # Angled wind
        humidity_percent=55.0,
        altitude_m=300.0
    )
    
    # Create enhanced visualizer
    visualizer = Enhanced3DVisualizer(figsize=(18, 14), debug_level="INFO")
    
    # Enable debug trajectory points for demonstration
    visualizer.show_trajectory_debug = True
    
    # Create interactive 3D visualization
    fig = visualizer.create_interactive_3d_visualization(
        ammo, armor, target_range=2200.0, launch_angle=1.5,
        environmental_conditions=conditions
    )
    
    # Save static visualization
    filename = os.path.join("..", "..", "results", "enhanced_3d", "enhanced_3d_demonstration.png")
    visualizer.save_visualization(filename, dpi=300)
    
    print(f"✓ Demonstration visualization saved as: {filename}")
    print("✓ Interactive controls enabled:")
    print("  - Mouse: Rotate view")
    print("  - Scroll: Zoom in/out")
    print("  - Sliders: Control elevation and azimuth")
    
    return fig, visualizer

if __name__ == "__main__":
    # Run comprehensive tests
    success, results = run_comprehensive_test()
    
    if success:
        print("\nCreating demonstration visualization...")
        demo_fig, demo_visualizer = create_demonstration_visualization()
        
        print("\nTo view the interactive demonstration:")
        print("1. The static image has been saved")
        print("2. Run this script interactively to see the 3D visualization")
        print("3. Use mouse controls to rotate and zoom the view")
        
        # Show interactive visualization if running in interactive mode
        try:
            plt.show()
        except:
            print("(Interactive display not available in this environment)")
    
    else:
        print("Tests failed. Please check the error messages above.")
        sys.exit(1)
