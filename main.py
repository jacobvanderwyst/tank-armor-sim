#!/usr/bin/env python3
"""
Tank Armor Penetration Simulator - Main Game Script

An interactive simulation of tank armor penetration mechanics.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ammunition import APFSDS, AP, APCR, HEAT, HESH
from src.armor import RHA, CompositeArmor, ReactiveArmor, SpacedArmor
from src.visualization import BallisticsVisualizer, PenetrationVisualizer, ComparisonVisualizer
from typing import List, Dict, Any


class TankArmorSimulator:
    """Main game class for the tank armor penetration simulator."""
    
    def __init__(self):
        """Initialize the simulator with predefined ammunition and armor."""
        self.ammunition_catalog = self._create_ammunition_catalog()
        self.armor_catalog = self._create_armor_catalog()
    
    def _create_ammunition_catalog(self) -> Dict[str, Any]:
        """Create catalog of available ammunition types."""
        return {
            "M829A4 APFSDS": APFSDS(
                name="M829A4 APFSDS",
                caliber=120.0,
                penetrator_diameter=22.0,
                penetrator_mass=4.6,
                muzzle_velocity=1680,
                penetrator_length=570
            ),
            "3BM60 APFSDS": APFSDS(
                name="3BM60 Svinets-2",
                caliber=125.0,
                penetrator_diameter=24.0,
                penetrator_mass=5.2,
                muzzle_velocity=1750,
                penetrator_length=600
            ),
            "M830A1 HEAT": HEAT(
                name="M830A1 HEAT-MP",
                caliber=120.0,
                warhead_mass=18.6,
                explosive_mass=2.4,
                standoff_distance=150
            ),
            "3BK29 HEAT": HEAT(
                name="3BK29 HEAT",
                caliber=125.0,
                warhead_mass=19.8,
                explosive_mass=2.8,
                standoff_distance=180
            ),
            "L31A7 HESH": HESH(
                name="L31A7 HESH",
                caliber=120.0,
                shell_mass=17.2,
                explosive_mass=4.1
            ),
            "M72 AP": AP(
                name="M72 AP Shot",
                caliber=76.0,
                mass=6.8,
                muzzle_velocity=792
            )
        }
    
    def _create_armor_catalog(self) -> Dict[str, Any]:
        """Create catalog of available armor configurations."""
        return {
            "100mm RHA": RHA(thickness=100.0),
            "200mm RHA": RHA(thickness=200.0),
            "M1A2 Frontal": CompositeArmor(
                name="M1A2 Frontal Armor",
                thickness=650.0,
                steel_layers=200.0,
                ceramic_layers=350.0,
                other_layers=100.0
            ),
            "T-90M Frontal": ReactiveArmor(
                name="T-90M with Relikt ERA",
                base_thickness=500.0,
                era_thickness=45.0,
                explosive_mass=0.8
            ),
            "Leopard 2A7 Side": SpacedArmor(
                name="Leopard 2A7 Side Armor",
                front_plate=35.0,
                rear_plate=70.0,
                spacing=150.0
            ),
            "Challenger 2 Frontal": CompositeArmor(
                name="Challenger 2 Dorchester",
                thickness=800.0,
                steel_layers=250.0,
                ceramic_layers=450.0,
                other_layers=100.0
            )
        }
    
    def display_menu(self):
        """Display the main menu."""
        print("\n" + "="*60)
        print("    TANK ARMOR PENETRATION SIMULATOR")
        print("="*60)
        print("1. Run Penetration Test")
        print("2. Run Penetration Test with Visualization")
        print("3. View Ballistic Trajectory")
        print("4. Compare Ammunition")
        print("5. Compare Armor")
        print("6. View Ammunition Catalog")
        print("7. View Armor Catalog")
        print("8. Exit")
        print("="*60)
    
    def run_penetration_test(self):
        """Run an interactive penetration test."""
        print("\n--- PENETRATION TEST ---")
        
        # Select ammunition
        print("\nAvailable Ammunition:")
        ammo_list = list(self.ammunition_catalog.keys())
        for i, ammo_name in enumerate(ammo_list, 1):
            ammo = self.ammunition_catalog[ammo_name]
            print(f"{i}. {ammo_name} ({ammo.penetration_type.upper()})")
        
        try:
            ammo_choice = int(input(f"\nSelect ammunition (1-{len(ammo_list)}): ")) - 1
            if ammo_choice < 0 or ammo_choice >= len(ammo_list):
                print("Invalid selection!")
                return
            selected_ammo = self.ammunition_catalog[ammo_list[ammo_choice]]
        except ValueError:
            print("Invalid input!")
            return
        
        # Select armor
        print("\nAvailable Armor:")
        armor_list = list(self.armor_catalog.keys())
        for i, armor_name in enumerate(armor_list, 1):
            armor = self.armor_catalog[armor_name]
            print(f"{i}. {armor_name} ({armor.armor_type.upper()}, {armor.thickness}mm)")
        
        try:
            armor_choice = int(input(f"\nSelect armor (1-{len(armor_list)}): ")) - 1
            if armor_choice < 0 or armor_choice >= len(armor_list):
                print("Invalid selection!")
                return
            selected_armor = self.armor_catalog[armor_list[armor_choice]]
        except ValueError:
            print("Invalid input!")
            return
        
        # Get engagement parameters
        try:
            range_m = float(input("\nEnter engagement range (meters, 0-4000): "))
            if range_m < 0 or range_m > 4000:
                print("Range must be between 0 and 4000 meters!")
                return
                
            angle = float(input("Enter impact angle from vertical (degrees, 0-75): "))
            if angle < 0 or angle > 75:
                print("Angle must be between 0 and 75 degrees!")
                return
        except ValueError:
            print("Invalid input!")
            return
        
        # Perform calculation
        self.calculate_and_display_result(selected_ammo, selected_armor, range_m, angle)
    
    def calculate_and_display_result(self, ammo, armor, range_m: float, angle: float):
        """Calculate and display penetration test results."""
        print("\n" + "="*60)
        print("PENETRATION TEST RESULTS")
        print("="*60)
        
        # Ammunition info
        print(f"\nAMMUNITION: {ammo.name}")
        print(f"  Type: {ammo.penetration_type.upper()}")
        print(f"  Caliber: {ammo.caliber}mm")
        print(f"  Muzzle Velocity: {ammo.muzzle_velocity} m/s")
        print(f"  Mass: {ammo.mass} kg")
        
        # Armor info
        print(f"\nARMOR: {armor.name}")
        print(f"  Type: {armor.armor_type.upper()}")
        print(f"  Thickness: {armor.thickness}mm")
        print(f"  Density: {armor.density} kg/m³")
        
        # Engagement parameters
        print(f"\nENGAGEMENT:")
        print(f"  Range: {range_m} m")
        print(f"  Impact Angle: {angle}°")
        
        # Calculate penetration capability
        penetration = ammo.calculate_penetration(range_m, angle)
        velocity_at_range = ammo.get_velocity_at_range(range_m)
        effective_thickness = armor.get_effective_thickness(ammo.penetration_type, angle)
        
        print(f"\nCALCULATIONS:")
        print(f"  Velocity at Range: {velocity_at_range:.1f} m/s")
        print(f"  Penetration Capability: {penetration:.1f}mm RHA")
        print(f"  Effective Armor Thickness: {effective_thickness:.1f}mm RHA")
        
        # Determine result
        can_defeat = armor.can_defeat(penetration, ammo.penetration_type, angle)
        
        print(f"\nRESULT:")
        if can_defeat:
            print("  ❌ ARMOR DEFEATS PROJECTILE")
            margin = effective_thickness - penetration
            print(f"  Safety Margin: {margin:.1f}mm RHA")
        else:
            print("  ✅ PROJECTILE PENETRATES ARMOR")
            overmatch = penetration - effective_thickness
            print(f"  Overmatch: {overmatch:.1f}mm RHA")
        
        print("="*60)
    
    def run_penetration_test_with_visualization(self):
        """Run penetration test with comprehensive visualization."""
        print("\n--- PENETRATION TEST WITH VISUALIZATION ---")
        
        # Use the same selection process as regular penetration test
        print("\nAvailable Ammunition:")
        ammo_list = list(self.ammunition_catalog.keys())
        for i, ammo_name in enumerate(ammo_list, 1):
            ammo = self.ammunition_catalog[ammo_name]
            print(f"{i}. {ammo_name} ({ammo.penetration_type.upper()})")
        
        try:
            ammo_choice = int(input(f"\nSelect ammunition (1-{len(ammo_list)}): ")) - 1
            if ammo_choice < 0 or ammo_choice >= len(ammo_list):
                print("Invalid selection!")
                return
            selected_ammo = self.ammunition_catalog[ammo_list[ammo_choice]]
        except ValueError:
            print("Invalid input!")
            return
        
        # Select armor
        print("\nAvailable Armor:")
        armor_list = list(self.armor_catalog.keys())
        for i, armor_name in enumerate(armor_list, 1):
            armor = self.armor_catalog[armor_name]
            print(f"{i}. {armor_name} ({armor.armor_type.upper()}, {armor.thickness}mm)")
        
        try:
            armor_choice = int(input(f"\nSelect armor (1-{len(armor_list)}): ")) - 1
            if armor_choice < 0 or armor_choice >= len(armor_list):
                print("Invalid selection!")
                return
            selected_armor = self.armor_catalog[armor_list[armor_choice]]
        except ValueError:
            print("Invalid input!")
            return
        
        # Get engagement parameters
        try:
            range_m = float(input("\nEnter engagement range (meters, 0-4000): "))
            if range_m < 0 or range_m > 4000:
                print("Range must be between 0 and 4000 meters!")
                return
                
            angle = float(input("Enter impact angle from vertical (degrees, 0-75): "))
            if angle < 0 or angle > 75:
                print("Angle must be between 0 and 75 degrees!")
                return
        except ValueError:
            print("Invalid input!")
            return
        
        # Display text results first
        print("\nGenerating visualization...")
        self.calculate_and_display_result(selected_ammo, selected_armor, range_m, angle)
        
        # Generate comprehensive penetration visualization
        try:
            pen_visualizer = PenetrationVisualizer()
            pen_fig = pen_visualizer.visualize_penetration_process(selected_ammo, selected_armor, range_m, angle)
            
            # Save and show the plot
            pen_visualizer.save_plot(f'penetration_{selected_ammo.name.replace(" ", "_")}_{selected_armor.name.replace(" ", "_")}.png')
            pen_visualizer.show_plot()
            
            print("\nVisualization complete! Check the generated image files.")
            
        except ImportError:
            print("\nVisualization requires matplotlib and numpy. Please install dependencies:")
            print("pip install -r requirements.txt")
        except Exception as e:
            print(f"\nError generating visualization: {e}")
    
    def view_ballistic_trajectory(self):
        """Display ballistic trajectory visualization."""
        print("\n--- BALLISTIC TRAJECTORY VISUALIZATION ---")
        
        # Select ammunition
        print("\nAvailable Ammunition:")
        ammo_list = list(self.ammunition_catalog.keys())
        for i, ammo_name in enumerate(ammo_list, 1):
            ammo = self.ammunition_catalog[ammo_name]
            print(f"{i}. {ammo_name} ({ammo.penetration_type.upper()})")
        
        try:
            ammo_choice = int(input(f"\nSelect ammunition (1-{len(ammo_list)}): ")) - 1
            if ammo_choice < 0 or ammo_choice >= len(ammo_list):
                print("Invalid selection!")
                return
            selected_ammo = self.ammunition_catalog[ammo_list[ammo_choice]]
        except ValueError:
            print("Invalid input!")
            return
        
        # Select armor for target representation (optional)
        print("\nSelect Target Armor (optional):")
        armor_list = list(self.armor_catalog.keys())
        print("0. None (trajectory only)")
        for i, armor_name in enumerate(armor_list, 1):
            armor = self.armor_catalog[armor_name]
            print(f"{i}. {armor_name} ({armor.armor_type.upper()}, {armor.thickness}mm)")
        
        try:
            armor_choice = int(input(f"\nSelect target armor (0-{len(armor_list)}): "))
            if armor_choice < 0 or armor_choice > len(armor_list):
                print("Invalid selection!")
                return
            
            if armor_choice == 0:
                selected_armor = None
                print("No target armor selected - showing trajectory only.")
            else:
                selected_armor = self.armor_catalog[armor_list[armor_choice - 1]]
        except ValueError:
            print("Invalid input!")
            return
        
        # Get trajectory parameters
        try:
            range_m = float(input("\nEnter target range (meters, 0-4000): "))
            if range_m < 0 or range_m > 4000:
                print("Range must be between 0 and 4000 meters!")
                return
                
            angle = float(input("Enter impact angle from vertical (degrees, 0-75): "))
            if angle < 0 or angle > 75:
                print("Angle must be between 0 and 75 degrees!")
                return
                
            show_velocity = input("\nShow velocity decay subplot? (y/N): ").lower().startswith('y')
        except ValueError:
            print("Invalid input!")
            return
        
        # Generate trajectory visualization
        try:
            print("\nGenerating ballistic trajectory visualization...")
            ballistics_visualizer = BallisticsVisualizer()
            traj_fig = ballistics_visualizer.visualize_flight_path(selected_ammo, selected_armor, 
                                                                  range_m, angle, show_velocity)
            
            # Save and show the plot
            ballistics_visualizer.save_plot(f'trajectory_{selected_ammo.name.replace(" ", "_")}_{range_m}m.png')
            ballistics_visualizer.show_plot()
            
            print("\nTrajectory visualization complete! Check the generated image files.")
            
        except ImportError:
            print("\nVisualization requires matplotlib and numpy. Please install dependencies:")
            print("pip install -r requirements.txt")
        except Exception as e:
            print(f"\nError generating trajectory: {e}")
    
    def compare_ammunition(self):
        """Compare multiple ammunition types against selected armor."""
        print("\n--- AMMUNITION COMPARISON ANALYSIS ---")
        
        # Select target armor first
        print("\nSelect Target Armor:")
        armor_list = list(self.armor_catalog.keys())
        for i, armor_name in enumerate(armor_list, 1):
            armor = self.armor_catalog[armor_name]
            print(f"{i}. {armor_name} ({armor.armor_type.upper()}, {armor.thickness}mm)")
        
        try:
            armor_choice = int(input(f"\nSelect target armor (1-{len(armor_list)}): ")) - 1
            if armor_choice < 0 or armor_choice >= len(armor_list):
                print("Invalid selection!")
                return
            selected_armor = self.armor_catalog[armor_list[armor_choice]]
        except ValueError:
            print("Invalid input!")
            return
        
        # Select multiple ammunition types for comparison
        print("\n--- SELECT AMMUNITION FOR COMPARISON ---")
        print("Available Ammunition:")
        ammo_list = list(self.ammunition_catalog.keys())
        for i, ammo_name in enumerate(ammo_list, 1):
            ammo = self.ammunition_catalog[ammo_name]
            print(f"{i}. {ammo_name} ({ammo.penetration_type.upper()})")
        
        selected_ammo = []
        print("\nSelect ammunition to compare (enter numbers separated by commas, e.g., 1,2,4):")
        try:
            choices = input("Ammunition selection: ").strip().split(',')
            for choice in choices:
                idx = int(choice.strip()) - 1
                if 0 <= idx < len(ammo_list):
                    selected_ammo.append(self.ammunition_catalog[ammo_list[idx]])
                else:
                    print(f"Invalid choice: {choice}")
                    return
            
            if len(selected_ammo) < 2:
                print("Please select at least 2 ammunition types for comparison.")
                return
                
        except ValueError:
            print("Invalid input format!")
            return
        
        # Generate comparison visualization
        try:
            print(f"\nGenerating ammunition comparison analysis...")
            comparison_viz = ComparisonVisualizer()
            comp_fig = comparison_viz.compare_ammunition(selected_ammo, selected_armor)
            
            # Save the comparison plot
            ammo_names = '_vs_'.join([ammo.name.split()[0] for ammo in selected_ammo[:3]])  # Limit filename length
            filename = f'ammo_comparison_{ammo_names}_{selected_armor.name.replace(" ", "_")}.png'
            comparison_viz.save_plot(filename)
            comparison_viz.show_plot()
            
            print(f"\nAmmunition comparison complete! Analysis shows:")
            for ammo in selected_ammo:
                pen = ammo.calculate_penetration(2000, 15)  # Standard test conditions
                eff = selected_armor.get_effective_thickness(ammo.penetration_type, 15)
                result = "PENETRATES" if pen > eff else "STOPPED BY"
                print(f"- {ammo.name}: {result} {selected_armor.name} ({pen:.0f} vs {eff:.0f} mm RHA)")
            
        except ImportError:
            print("\nComparison requires matplotlib, numpy, and seaborn. Please install dependencies:")
            print("pip install -r requirements.txt")
        except Exception as e:
            print(f"\nError generating comparison: {e}")
    
    def compare_armor(self):
        """Compare multiple armor types against selected ammunition."""
        print("\n--- ARMOR COMPARISON ANALYSIS ---")
        
        # Select attacking ammunition first
        print("\nSelect Attacking Ammunition:")
        ammo_list = list(self.ammunition_catalog.keys())
        for i, ammo_name in enumerate(ammo_list, 1):
            ammo = self.ammunition_catalog[ammo_name]
            print(f"{i}. {ammo_name} ({ammo.penetration_type.upper()})")
        
        try:
            ammo_choice = int(input(f"\nSelect ammunition (1-{len(ammo_list)}): ")) - 1
            if ammo_choice < 0 or ammo_choice >= len(ammo_list):
                print("Invalid selection!")
                return
            selected_ammo = self.ammunition_catalog[ammo_list[ammo_choice]]
        except ValueError:
            print("Invalid input!")
            return
        
        # Select multiple armor types for comparison
        print("\n--- SELECT ARMOR FOR COMPARISON ---")
        print("Available Armor:")
        armor_list = list(self.armor_catalog.keys())
        for i, armor_name in enumerate(armor_list, 1):
            armor = self.armor_catalog[armor_name]
            print(f"{i}. {armor_name} ({armor.armor_type.upper()}, {armor.thickness}mm)")
        
        selected_armor = []
        print("\nSelect armor to compare (enter numbers separated by commas, e.g., 1,3,4):")
        try:
            choices = input("Armor selection: ").strip().split(',')
            for choice in choices:
                idx = int(choice.strip()) - 1
                if 0 <= idx < len(armor_list):
                    selected_armor.append(self.armor_catalog[armor_list[idx]])
                else:
                    print(f"Invalid choice: {choice}")
                    return
            
            if len(selected_armor) < 2:
                print("Please select at least 2 armor types for comparison.")
                return
                
        except ValueError:
            print("Invalid input format!")
            return
        
        # Generate comparison visualization
        try:
            print(f"\nGenerating armor comparison analysis...")
            comparison_viz = ComparisonVisualizer()
            comp_fig = comparison_viz.compare_armor(selected_armor, selected_ammo)
            
            # Save the comparison plot
            armor_names = '_vs_'.join([armor.name.split()[0] for armor in selected_armor[:3]])  # Limit filename length
            filename = f'armor_comparison_{armor_names}_{selected_ammo.name.replace(" ", "_")}.png'
            comparison_viz.save_plot(filename)
            comparison_viz.show_plot()
            
            print(f"\nArmor comparison complete! Analysis shows:")
            for armor in selected_armor:
                pen = selected_ammo.calculate_penetration(2000, 15)  # Standard test conditions
                eff = armor.get_effective_thickness(selected_ammo.penetration_type, 15)
                result = "STOPS" if eff >= pen else "PENETRATED BY"
                print(f"- {armor.name}: {result} {selected_ammo.name} ({eff:.0f} vs {pen:.0f} mm RHA)")
            
        except ImportError:
            print("\nComparison requires matplotlib, numpy, and seaborn. Please install dependencies:")
            print("pip install -r requirements.txt")
        except Exception as e:
            print(f"\nError generating comparison: {e}")
    def view_ammunition_catalog(self):
        """Display detailed ammunition catalog."""
        print("\n" + "="*60)
        print("AMMUNITION CATALOG")
        print("="*60)
        
        for name, ammo in self.ammunition_catalog.items():
            info = ammo.get_info()
            print(f"\n{name}:")
            print(f"  Type: {info['penetration_type'].upper()}")
            print(f"  Caliber: {info['caliber_mm']}mm")
            print(f"  Mass: {info['mass_kg']}kg")
            print(f"  Muzzle Velocity: {info['muzzle_velocity_ms']} m/s")
            print(f"  Kinetic Energy: {info['kinetic_energy_j']/1000:.0f} kJ")
    
    def view_armor_catalog(self):
        """Display detailed armor catalog."""
        print("\n" + "="*60)
        print("ARMOR CATALOG")
        print("="*60)
        
        for name, armor in self.armor_catalog.items():
            info = armor.get_info()
            print(f"\n{name}:")
            print(f"  Type: {info['armor_type'].upper()}")
            print(f"  Thickness: {info['thickness_mm']}mm")
            print(f"  Density: {info['density_kg_m3']} kg/m³")
            print(f"  Mass per Area: {info['mass_per_area_kg_m2']:.1f} kg/m²")
    
    def run(self):
        """Main game loop."""
        print("Welcome to the Tank Armor Penetration Simulator!")
        print("This simulator models realistic armor penetration mechanics.")
        
        while True:
            self.display_menu()
            try:
                choice = input("\nEnter your choice (1-8): ").strip()
                
                if choice == '1':
                    self.run_penetration_test()
                elif choice == '2':
                    self.run_penetration_test_with_visualization()
                elif choice == '3':
                    self.view_ballistic_trajectory()
                elif choice == '4':
                    self.compare_ammunition()
                elif choice == '5':
                    self.compare_armor()
                elif choice == '6':
                    self.view_ammunition_catalog()
                elif choice == '7':
                    self.view_armor_catalog()
                elif choice == '8':
                    print("\nThank you for using the Tank Armor Penetration Simulator!")
                    break
                else:
                    print("Invalid choice! Please enter 1-8.")
                    
            except KeyboardInterrupt:
                print("\n\nExiting simulator...")
                break
            except Exception as e:
                print(f"An error occurred: {e}")


if __name__ == "__main__":
    simulator = TankArmorSimulator()
    simulator.run()
