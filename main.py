#!/usr/bin/env python3
"""
Tank Armor Penetration Simulator - Main Game Script

An interactive simulation of tank armor penetration mechanics.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ammunition import APFSDS, AP, APCR, HEAT, HESH
from armor import RHA, CompositeArmor, ReactiveArmor, SpacedArmor
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
        print("2. Compare Ammunition")
        print("3. Compare Armor")
        print("4. View Ammunition Catalog")
        print("5. View Armor Catalog")
        print("6. Exit")
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
                choice = input("\nEnter your choice (1-6): ").strip()
                
                if choice == '1':
                    self.run_penetration_test()
                elif choice == '2':
                    print("Ammunition comparison feature coming soon!")
                elif choice == '3':
                    print("Armor comparison feature coming soon!")
                elif choice == '4':
                    self.view_ammunition_catalog()
                elif choice == '5':
                    self.view_armor_catalog()
                elif choice == '6':
                    print("\nThank you for using the Tank Armor Penetration Simulator!")
                    break
                else:
                    print("Invalid choice! Please enter 1-6.")
                    
            except KeyboardInterrupt:
                print("\n\nExiting simulator...")
                break
            except Exception as e:
                print(f"An error occurred: {e}")


if __name__ == "__main__":
    simulator = TankArmorSimulator()
    simulator.run()
