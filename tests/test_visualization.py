#!/usr/bin/env python3
"""
Quick test script for the visualization functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from ammunition import APFSDS, HEAT
    from armor import RHA, CompositeArmor
    from visualization import BallisticsVisualizer, PenetrationVisualizer
    
    print("Testing Tank Armor Simulation Visualization...")
    
    # Create test ammunition and armor
    apfsds = APFSDS("Test M829A4", 120.0, 22.0, 4.6, 1680, 570)
    heat = HEAT("Test HEAT", 120.0, 18.6, 2.4, 150)
    rha = RHA(200.0)
    composite = CompositeArmor("Test Composite", 650.0, 200.0, 350.0, 100.0)
    
    # Test parameters
    range_m = 2000.0
    impact_angle = 15.0
    
    print(f"Testing: {apfsds.name} vs {rha.name} at {range_m}m, {impact_angle}°")
    
    # Test ballistics visualization
    print("Creating ballistic trajectory visualization...")
    ballistics_viz = BallisticsVisualizer()
    ballistics_fig = ballistics_viz.visualize_flight_path(apfsds, rha, range_m, impact_angle, True)
    ballistics_viz.save_plot('test_trajectory.png')
    print("✓ Ballistic trajectory visualization created")
    
    # Test penetration visualization  
    print("Creating penetration mechanics visualization...")
    penetration_viz = PenetrationVisualizer()
    penetration_fig = penetration_viz.visualize_penetration_process(apfsds, rha, range_m, impact_angle)
    penetration_viz.save_plot('test_penetration.png')
    print("✓ Penetration mechanics visualization created")
    
    # Test with different ammunition type
    print(f"Testing: {heat.name} vs {composite.name}")
    penetration_viz2 = PenetrationVisualizer()
    penetration_fig2 = penetration_viz2.visualize_penetration_process(heat, composite, range_m, impact_angle)
    penetration_viz2.save_plot('test_heat_penetration.png')
    print("✓ HEAT penetration visualization created")
    
    print("\nAll visualization tests passed! Check the generated PNG files in results/:")
    print("- results/test_trajectory.png")
    print("- results/test_penetration.png") 
    print("- results/test_heat_penetration.png")
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you have installed the required dependencies:")
    print("pip install matplotlib numpy")
except Exception as e:
    print(f"Error during testing: {e}")
    import traceback
    traceback.print_exc()
