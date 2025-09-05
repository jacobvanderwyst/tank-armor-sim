#!/usr/bin/env python3
"""
Test script for the comparison visualization functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from ammunition import APFSDS, HEAT, HESH, AP
    from armor import RHA, CompositeArmor, ReactiveArmor
    from visualization import ComparisonVisualizer
    
    print("Testing Ammunition & Armor Comparison System...")
    
    # Create test ammunition
    m829a4 = APFSDS("M829A4 APFSDS", 120.0, 22.0, 4.6, 1680, 570)
    svinets = APFSDS("3BM60 Svinets-2", 125.0, 24.0, 5.2, 1750, 600)
    heat_round = HEAT("M830A1 HEAT", 120.0, 18.6, 2.4, 150)
    hesh_round = HESH("L31A7 HESH", 120.0, 17.2, 4.1)
    
    # Create test armor
    rha_200 = RHA(200.0)
    m1a2_armor = CompositeArmor("M1A2 Frontal", 650.0, 200.0, 350.0, 100.0)
    t90m_armor = ReactiveArmor("T-90M Relikt", 500.0, 45.0, 0.8)
    
    print("\n=== Testing Ammunition Comparison ===")
    print("Comparing APFSDS rounds vs M1A2 Frontal Armor")
    
    # Test ammunition comparison
    comparison_viz = ComparisonVisualizer()
    ammo_comparison_fig = comparison_viz.compare_ammunition(
        [m829a4, svinets], m1a2_armor
    )
    comparison_viz.save_plot('test_ammo_comparison.png')
    print("✓ Ammunition comparison visualization created")
    
    print("\n=== Testing Armor Comparison ===")
    print("Comparing armor types vs M829A4 APFSDS")
    
    # Test armor comparison
    comparison_viz2 = ComparisonVisualizer()
    armor_comparison_fig = comparison_viz2.compare_armor(
        [rha_200, m1a2_armor, t90m_armor], m829a4
    )
    comparison_viz2.save_plot('test_armor_comparison.png')
    print("✓ Armor comparison visualization created")
    
    print("\n=== Testing Mixed Ammunition Types ===")
    print("Comparing different ammunition mechanisms vs RHA")
    
    # Test mixed ammunition comparison
    comparison_viz3 = ComparisonVisualizer()
    mixed_comparison_fig = comparison_viz3.compare_ammunition(
        [m829a4, heat_round, hesh_round], rha_200
    )
    comparison_viz3.save_plot('test_mixed_comparison.png')
    print("✓ Mixed ammunition comparison visualization created")
    
    print("\nAll comparison tests passed! Check the generated PNG files in results/:")
    print("- results/test_ammo_comparison.png")
    print("- results/test_armor_comparison.png")
    print("- results/test_mixed_comparison.png")
    
    print("\nComparison system features demonstrated:")
    print("✓ Range vs penetration curves")
    print("✓ Angle effectiveness analysis")
    print("✓ Ammunition characteristics comparison")
    print("✓ Protection factor analysis")
    print("✓ Summary statistics tables")
    print("✓ Color-coded results visualization")
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you have installed the required dependencies:")
    print("pip install matplotlib numpy seaborn")
except Exception as e:
    print(f"Error during testing: {e}")
    import traceback
    traceback.print_exc()
