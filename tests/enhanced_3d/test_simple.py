
"""
Simple Test Script for Enhanced 3D Visualization

Run this script to quickly test the enhanced 3D visualization system.
"""

import sys
import os
# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.visualization.enhanced_3d_visualizer import Enhanced3DVisualizer
from src.physics.advanced_physics import EnvironmentalConditions
from src.ammunition import APFSDS
from src.armor import CompositeArmor
import matplotlib.pyplot as plt

def run_simple_test():
    """Run a simple test of the enhanced 3D visualization."""
    
    print("Testing Enhanced 3D Visualization System...")
    
    # Create test ammunition and armor
    ammo = APFSDS(name="M829A4", caliber=120, penetrator_diameter=22, 
                  penetrator_mass=8.5, muzzle_velocity=1680, penetrator_length=570)
    
    armor = CompositeArmor("Modern Tank Armor", thickness=600, 
                          steel_layers=400, ceramic_layers=200)
    
    # Set up environmental conditions
    env_conditions = EnvironmentalConditions(
        temperature_celsius=25.0,
        wind_speed_ms=7.0,
        wind_angle_deg=30.0,
        humidity_percent=65.0,
        altitude_m=200.0
    )
    
    # Create enhanced visualizer
    visualizer = Enhanced3DVisualizer(figsize=(16, 12), debug_level="INFO")
    visualizer.show_trajectory_debug = True
    
    # Create interactive 3D visualization
    fig = visualizer.create_interactive_3d_visualization(
        ammo, armor, target_range=2500.0, launch_angle=1.5,
        environmental_conditions=env_conditions
    )
    
    if fig:
        print("✓ Enhanced 3D visualization created successfully!")
        print("✓ Use mouse to rotate and zoom the 3D view")
        print("✓ Trajectory follows accurate ballistic physics")
        print("✓ Tank model has realistic proportions")
        
        # Save the visualization
        result_path = os.path.join("..", "..", "results", "enhanced_3d", "test_enhanced_3d.png")
        visualizer.save_visualization(result_path, dpi=300)
        print(f"✓ Static image saved as: {result_path}")
        
        # Show interactive visualization
        plt.show()
    else:
        print("❌ Failed to create visualization")

if __name__ == "__main__":
    run_simple_test()
