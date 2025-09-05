"""
Demonstration Script: Tank Armor 3D Visualization System

This script demonstrates how to use the complete 3D visualization system
for tank armor penetration analysis.

Features demonstrated:
- 3D tank models with realistic geometry
- Ballistic trajectory visualization
- Penetration analysis with visual feedback
- Multiple visualization styles
- Animation capabilities
- Interactive 3D views

Usage:
    python demo_3d_visualization.py
"""

import sys
import os
import time

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import matplotlib.pyplot as plt
import numpy as np

# Import our simulation components
from ammunition import APFSDS, AP, HEAT
from armor import CompositeArmor, RHA
from visualization.renderer_3d_working import Working3DRenderer, Simple3DAnimator


class TankArmorDemo:
    """Demonstration class for the 3D visualization system."""
    
    def __init__(self):
        """Initialize the demo."""
        print("🚀 Tank Armor 3D Visualization Demo")
        print("=" * 45)
        
        # Set matplotlib to interactive mode
        try:
            plt.ion()  # Interactive mode
            print("✓ Interactive matplotlib mode enabled")
        except:
            print("⚠️  Interactive mode not available")
    
    def create_demo_scenarios(self):
        """Create demonstration scenarios."""
        
        scenarios = {
            'modern_penetration': {
                'name': 'Modern Tank Battle',
                'description': 'M829A4 APFSDS vs Modern Composite Armor',
                'ammo': APFSDS(
                    name="M829A4 APFSDS",
                    caliber=120,
                    penetrator_diameter=22,
                    penetrator_mass=7.0,
                    muzzle_velocity=1670,
                    penetrator_length=685
                ),
                'armor': CompositeArmor(
                    name="Modern MBT Composite",
                    thickness=650,
                    steel_layers=250,
                    ceramic_layers=400,
                    other_layers=0
                ),
                'range': 2000,
                'angle': 15,
                'style': 'professional'
            },
            
            'historical_defense': {
                'name': 'WWII Tank Engagement',
                'description': '76mm AP vs Tiger I Frontal Armor',
                'ammo': AP(
                    name="76mm AP M79",
                    caliber=76,
                    mass=7.0,
                    muzzle_velocity=792
                ),
                'armor': RHA(thickness=100),
                'range': 500,
                'angle': 0,  # Head-on engagement
                'style': 'tactical'
            },
            
            'heat_engagement': {
                'name': 'HEAT vs Composite',
                'description': '120mm HEAT-MP vs Modern Composite',
                'ammo': HEAT(
                    name="120mm HEAT-MP",
                    caliber=120,
                    warhead_mass=8.5,
                    explosive_mass=2.8,
                    standoff_distance=200
                ),
                'armor': CompositeArmor(
                    name="Composite Armor",
                    thickness=500,
                    steel_layers=200,
                    ceramic_layers=300,
                    other_layers=0
                ),
                'range': 1500,
                'angle': 10,
                'style': 'educational'
            }
        }\n        \n        return scenarios\n    \n    def demo_scenario(self, scenario_key: str, scenarios: dict, save_images: bool = True):\n        \"\"\"Demonstrate a single scenario.\"\"\"\n        \n        scenario = scenarios[scenario_key]\n        \n        print(f\"\\n📊 {scenario['name']}\")\n        print(f\"    {scenario['description']}\")\n        print(\"-\" * 50)\n        \n        # Calculate penetration results\n        penetration = scenario['ammo'].calculate_penetration(\n            scenario['range']/1000, scenario['angle']\n        )\n        effective_thickness = scenario['armor'].get_effective_thickness(\n            'kinetic' if 'APFSDS' in scenario['ammo'].name or 'AP' in scenario['ammo'].name else 'chemical', \n            scenario['angle']\n        )\n        \n        result = \"PENETRATION\" if penetration > effective_thickness else \"NO PENETRATION\"\n        \n        print(f\"🎯 Ammunition: {scenario['ammo'].name}\")\n        print(f\"🛡️  Armor: {scenario['armor'].name}\")\n        print(f\"📏 Range: {scenario['range']}m\")\n        print(f\"📐 Impact Angle: {scenario['angle']}°\")\n        print(f\"⚡ Penetration: {penetration:.0f}mm RHA\")\n        print(f\"🛡️  Effective Armor: {effective_thickness:.0f}mm RHA\")\n        print(f\"🎲 Result: {result}\")\n        \n        # Create 3D visualization\n        print(\"\\n🎨 Creating 3D visualization...\")\n        \n        renderer = Working3DRenderer(figsize=(12, 9), style=scenario['style'])\n        \n        fig = renderer.create_3d_visualization(\n            ammunition=scenario['ammo'],\n            armor=scenario['armor'],\n            target_range=scenario['range'],\n            impact_angle=scenario['angle']\n        )\n        \n        if save_images:\n            filename = f\"demo_{scenario_key}_{scenario['style']}.png\"\n            renderer.save_visualization(filename, dpi=200)\n            print(f\"💾 Saved visualization: {filename}\")\n        \n        print(\"✓ 3D visualization created successfully\")\n        \n        return fig\n    \n    def demo_animation(self):\n        \"\"\"Demonstrate animation capabilities.\"\"\"\n        \n        print(\"\\n🎬 Animation Demonstration\")\n        print(\"=\" * 30)\n        \n        # Create a dramatic scenario for animation\n        apfsds = APFSDS(\n            name=\"M829A4 APFSDS\",\n            caliber=120,\n            penetrator_diameter=22,\n            penetrator_mass=7.0,\n            muzzle_velocity=1670,\n            penetrator_length=685\n        )\n        \n        armor = CompositeArmor(\n            name=\"T-90M Composite\",\n            thickness=800,  # Thick armor for dramatic effect\n            steel_layers=300,\n            ceramic_layers=500,\n            other_layers=0\n        )\n        \n        print(\"🎥 Creating animated penetration sequence...\")\n        \n        animator = Simple3DAnimator(figsize=(10, 8), style='tactical')\n        \n        animation = animator.create_penetration_animation(\n            ammunition=apfsds,\n            armor=armor,\n            target_range=1800,\n            impact_angle=12,\n            duration=4.0\n        )\n        \n        # Save animation\n        print(\"💾 Saving animation (this will take a moment)...\")\n        try:\n            from matplotlib.animation import PillowWriter\n            writer = PillowWriter(fps=24)\n            animation.save('demo_penetration_sequence.gif', writer=writer)\n            print(\"✓ Animation saved: demo_penetration_sequence.gif\")\n        except Exception as e:\n            print(f\"⚠️  Could not save animation: {e}\")\n        \n        return animation\n    \n    def interactive_demo(self):\n        \"\"\"Demonstrate interactive 3D viewing.\"\"\"\n        \n        print(\"\\n🖥️  Interactive 3D Demo\")\n        print(\"=\" * 25)\n        \n        # Create a visually interesting scenario\n        apfsds = APFSDS(\n            name=\"DM53 APFSDS\",\n            caliber=120,\n            penetrator_diameter=22,\n            penetrator_mass=7.2,\n            muzzle_velocity=1650,\n            penetrator_length=700\n        )\n        \n        armor = CompositeArmor(\n            name=\"Leopard 2A7 Composite\",\n            thickness=700,\n            steel_layers=250,\n            ceramic_layers=450,\n            other_layers=0\n        )\n        \n        print(\"🎯 Creating interactive 3D view...\")\n        \n        renderer = Working3DRenderer(figsize=(14, 10), style='professional')\n        \n        fig = renderer.create_3d_visualization(\n            ammunition=apfsds,\n            armor=armor,\n            target_range=2500,\n            impact_angle=18\n        )\n        \n        print(\"\\n🎮 Interactive Controls:\")\n        print(\"   • Click and drag to rotate the 3D view\")\n        print(\"   • Use mouse wheel to zoom in/out\")\n        print(\"   • Right-click and drag to pan\")\n        print(\"   • Close the window when finished\")\n        \n        try:\n            # Switch to interactive backend\n            plt.ioff()  # Turn off interactive mode to show blocking window\n            plt.show()\n            plt.ion()  # Turn back on\n            \n            print(\"✓ Interactive demo completed\")\n            \n        except Exception as e:\n            print(f\"⚠️  Interactive display error: {e}\")\n            plt.close(fig)\n    \n    def run_complete_demo(self):\n        \"\"\"Run the complete demonstration.\"\"\"\n        \n        print(\"\\n🎯 Starting Complete 3D Visualization Demonstration\")\n        print(\"\\nThis demo will showcase:\")\n        print(\"  • Static 3D visualizations with different scenarios\")\n        print(\"  • Multiple visualization styles\")\n        print(\"  • Animated penetration sequences\")\n        print(\"  • Interactive 3D viewing capabilities\")\n        \n        input(\"\\nPress Enter to continue...\")\n        \n        # Get scenarios\n        scenarios = self.create_demo_scenarios()\n        \n        # Demo each scenario\n        figures = []\n        for scenario_key in scenarios.keys():\n            fig = self.demo_scenario(scenario_key, scenarios)\n            figures.append(fig)\n            plt.close(fig)  # Close to save memory\n            time.sleep(1)  # Brief pause\n        \n        print(\"\\n✅ All static scenarios completed\")\n        \n        # Demo animation\n        input(\"\\nPress Enter to see animation demo...\")\n        \n        try:\n            animation = self.demo_animation()\n            plt.close()\n            print(\"✅ Animation demo completed\")\n        except Exception as e:\n            print(f\"⚠️  Animation demo failed: {e}\")\n        \n        # Interactive demo\n        input(\"\\nPress Enter for interactive demo...\")\n        \n        try:\n            self.interactive_demo()\n            print(\"✅ Interactive demo completed\")\n        except Exception as e:\n            print(f\"⚠️  Interactive demo failed: {e}\")\n        \n        # Summary\n        print(\"\\n\" + \"=\"*60)\n        print(\"🎉 3D Visualization Demo Complete!\")\n        print(\"\\n📁 Generated Files:\")\n        \n        import glob\n        demo_files = glob.glob(\"demo_*.png\") + glob.glob(\"demo_*.gif\")\n        if demo_files:\n            for file in demo_files:\n                print(f\"   📄 {file}\")\n        else:\n            print(\"   (Check for any error messages above)\")\n        \n        print(\"\\n💡 Integration Instructions:\")\n        print(\"   To use this 3D visualization system in your projects:\")\n        print(\"   1. Import: from visualization.renderer_3d_working import Working3DRenderer\")\n        print(\"   2. Create: renderer = Working3DRenderer(style='professional')\")\n        print(\"   3. Visualize: fig = renderer.create_3d_visualization(ammo, armor, range, angle)\")\n        print(\"   4. Display: renderer.show_visualization() or renderer.save_visualization('file.png')\")\n        \n        print(\"\\n🚀 The 3D visualization system is ready for integration!\")\n\n\ndef main():\n    \"\"\"Main demonstration function.\"\"\"\n    \n    try:\n        demo = TankArmorDemo()\n        demo.run_complete_demo()\n        \n    except KeyboardInterrupt:\n        print(\"\\n\\n⚠️  Demo interrupted by user\")\n    except Exception as e:\n        print(f\"\\n\\n❌ Demo failed with error: {e}\")\n        import traceback\n        traceback.print_exc()\n    \n    print(\"\\nThank you for trying the 3D Tank Armor Visualization Demo!\")\n\n\nif __name__ == \"__main__\":\n    main()
