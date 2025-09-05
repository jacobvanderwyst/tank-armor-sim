#!/usr/bin/env python3
"""
Comprehensive test script for advanced physics features.

This script demonstrates and tests:
- Advanced ballistics calculations
- Multi-hit damage accumulation
- Ricochet probability calculations
- Temperature effects on performance
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ammunition import APFSDS, HEAT, HESH
from src.armor import RHA, CompositeArmor
from src.physics import (AdvancedPhysicsEngine, ArmorDamageSystem, 
                        RicochetCalculator, TemperatureEffects)
from src.physics.advanced_physics import EnvironmentalConditions
from src.physics.temperature_effects import TemperatureConditions
from src.physics.ricochet_calculator import RicochetParameters
import random
import math


def test_advanced_ballistics():
    """Test advanced ballistics calculations."""
    print("=" * 60)
    print("TESTING ADVANCED BALLISTICS")
    print("=" * 60)
    
    # Create ammunition and engine
    ammo = APFSDS(
        name="M829A4 APFSDS",
        caliber=120.0,
        penetrator_diameter=22.0,
        penetrator_mass=4.6,
        muzzle_velocity=1680,
        penetrator_length=570
    )
    
    engine = AdvancedPhysicsEngine()
    
    # Test different environmental conditions
    environments = [
        ("Standard Conditions", EnvironmentalConditions()),
        ("Cold/High Altitude", EnvironmentalConditions(
            temperature_celsius=-20.0,
            altitude_m=3000.0,
            air_pressure_kpa=85.0
        )),
        ("Hot/Desert", EnvironmentalConditions(
            temperature_celsius=45.0,
            humidity_percent=10.0
        )),
        ("Windy Conditions", EnvironmentalConditions(
            wind_speed_ms=15.0,
            wind_angle_deg=30.0
        ))
    ]
    
    range_m = 2000.0
    
    for env_name, conditions in environments:
        print(f"\n--- {env_name} ---")
        result = engine.calculate_advanced_trajectory(ammo, range_m, conditions)
        
        print(f"Velocity at target: {result.velocity_at_target:.1f} m/s")
        print(f"Time of flight: {result.time_of_flight:.2f} s")
        print(f"Energy at target: {result.energy_at_target/1000:.1f} kJ")
        print(f"Penetration modifier: {result.penetration_modifier:.3f}")
        print(f"Environmental effects:")
        for effect, value in result.environmental_effects.items():
            print(f"  - {effect}: {value:.3f}")


def test_armor_damage_system():
    """Test multi-hit damage accumulation."""
    print("\n" + "=" * 60)
    print("TESTING ARMOR DAMAGE SYSTEM")
    print("=" * 60)
    
    # Create armor and damage system
    armor = RHA(thickness=200.0)
    damage_system = ArmorDamageSystem(armor.thickness, armor.armor_type)
    
    # Create different ammunition types
    ammo_types = [
        APFSDS("M829A4", 120.0, 22.0, 4.6, 1680, 570),
        HEAT("M830A1", 120.0, 18.6, 2.4, 150),
        HESH("L31A7", 120.0, 17.2, 4.1)
    ]
    
    print("Initial armor condition:")
    print(f"  Thickness: {armor.thickness}mm")
    print(f"  Integrity: 100%")
    
    # Simulate multiple hits
    for i in range(5):
        ammo = random.choice(ammo_types)
        
        # Random impact location
        impact_location = (random.uniform(-500, 500), random.uniform(-500, 500))
        
        # Calculate penetration attempt
        range_m = random.uniform(1000, 3000)
        angle = random.uniform(0, 30)
        penetration_attempted = ammo.calculate_penetration(range_m, angle)
        energy = 0.5 * ammo.mass * ammo.get_velocity_at_range(range_m) ** 2
        
        # Determine if penetration succeeded
        effective_thickness = armor.get_effective_thickness(ammo.penetration_type, angle)
        penetration_achieved = penetration_attempted > effective_thickness
        
        # Apply damage
        damage_system.apply_damage(
            ammo, impact_location, penetration_attempted, 
            energy, penetration_achieved, i * 10.0
        )
        
        print(f"\nHit #{i+1} - {ammo.name}")
        print(f"  Impact location: ({impact_location[0]:.0f}, {impact_location[1]:.0f}) mm")
        print(f"  Penetration attempted: {penetration_attempted:.1f} mm")
        print(f"  Penetration achieved: {'YES' if penetration_achieved else 'NO'}")
        
        # Get current condition
        summary = damage_system.get_damage_summary()
        condition = summary['current_condition']
        print(f"  Armor integrity: {condition['integrity_percent']:.1f}%")
        print(f"  Thickness remaining: {condition['thickness_remaining']:.1f} mm")
        print(f"  Hardness factor: {condition['hardness_factor']:.3f}")
        print(f"  Status: {summary['armor_status']}")
    
    # Final damage summary
    print("\n--- FINAL DAMAGE SUMMARY ---")
    final_summary = damage_system.get_damage_summary()
    print(f"Total impacts: {final_summary['total_impacts']}")
    print(f"Successful penetrations: {final_summary['successful_penetrations']}")
    print(f"Penetration rate: {final_summary['penetration_rate']:.2f}")
    print(f"Final armor status: {final_summary['armor_status']}")


def test_ricochet_calculator():
    """Test ricochet probability calculations."""
    print("\n" + "=" * 60)
    print("TESTING RICOCHET CALCULATOR")
    print("=" * 60)
    
    calculator = RicochetCalculator()
    
    # Test ammunition
    ammo = APFSDS("M829A4", 120.0, 22.0, 4.6, 1680, 570)
    armor = RHA(thickness=200.0)
    
    print("Testing ricochet probability vs impact angle:")
    print("Angle (°) | Ricochet % | Outcome      | Deflection (°)")
    print("-" * 55)
    
    for angle in range(0, 81, 10):
        params = RicochetParameters(
            impact_angle_deg=angle,
            impact_velocity_ms=1500,
            projectile_hardness=0.9,
            target_hardness=0.8
        )
        
        result = calculator.calculate_ricochet_probability(ammo, armor, params)
        
        print(f"{angle:6d} | {result.ricochet_probability*100:8.1f} | "
              f"{result.predicted_outcome.value:12s} | {result.deflection_angle_deg:10.1f}")
    
    print(f"\nCritical angle: {result.critical_angle_deg:.1f}°")
    
    # Test ricochet envelope analysis
    print("\nGenerating ricochet envelope analysis...")
    envelope = calculator.analyze_ricochet_envelope(
        ammo, armor,
        velocity_range=(500, 2000),
        angle_range=(0, 80),
        num_points=20
    )
    
    print(f"Envelope analysis complete:")
    print(f"  Velocity range: {envelope['velocity_range'][0]}-{envelope['velocity_range'][1]} m/s")
    print(f"  Angle range: {envelope['angle_range'][0]}-{envelope['angle_range'][1]}°")
    print(f"  50% ricochet boundary points: {len(envelope['ricochet_50_boundary'])}")


def test_temperature_effects():
    """Test temperature effects on performance."""
    print("\n" + "=" * 60)
    print("TESTING TEMPERATURE EFFECTS")
    print("=" * 60)
    
    temp_effects = TemperatureEffects()
    
    # Test ammunition and armor
    ammo = APFSDS("M829A4", 120.0, 22.0, 4.6, 1680, 570)
    armor = RHA(thickness=200.0)
    
    # Test different temperature conditions
    temp_conditions = [
        ("Arctic", TemperatureConditions(
            ambient_celsius=-30.0,
            propellant_celsius=-25.0,
            armor_celsius=-28.0,
            barrel_celsius=-20.0
        )),
        ("Standard", TemperatureConditions()),
        ("Desert", TemperatureConditions(
            ambient_celsius=50.0,
            propellant_celsius=45.0,
            armor_celsius=55.0,
            barrel_celsius=40.0,
            humidity_percent=15.0
        ))
    ]
    
    print("Condition | Vel.Mod | Pen.Mod | Prop.Eff | Accuracy | Barrel Wear")
    print("-" * 70)
    
    for condition_name, conditions in temp_conditions:
        result = temp_effects.calculate_temperature_effects(ammo, armor, conditions)
        
        print(f"{condition_name:9s} | {result.velocity_modifier:7.3f} | "
              f"{result.penetration_modifier:7.3f} | {result.propellant_efficiency:8.3f} | "
              f"{result.accuracy_modifier:8.2f} | {result.barrel_wear_factor:11.2f}")
    
    # Test recommendations
    print(f"\nTemperature recommendations for -30°C:")
    recommendations = temp_effects.get_temperature_recommendations(-30.0, "kinetic")
    for category, recommendation in recommendations.items():
        print(f"  {category}: {recommendation}")


def test_integrated_advanced_physics():
    """Test integrated advanced physics calculations."""
    print("\n" + "=" * 60)
    print("TESTING INTEGRATED ADVANCED PHYSICS")
    print("=" * 60)
    
    # Create ammunition and armor with advanced physics enabled
    ammo = APFSDS("M829A4", 120.0, 22.0, 4.6, 1680, 570)
    armor = RHA(thickness=200.0)
    
    # Enable advanced physics
    ammo.enable_advanced_physics()
    armor.enable_advanced_physics()
    
    print("Testing integrated calculation...")
    
    # Set up conditions
    env_conditions = EnvironmentalConditions(
        temperature_celsius=35.0,
        altitude_m=1500.0,
        humidity_percent=30.0
    )
    
    temp_conditions = TemperatureConditions(
        ambient_celsius=35.0,
        propellant_celsius=40.0,
        armor_celsius=45.0,
        barrel_celsius=38.0
    )
    
    ricochet_params = RicochetParameters(
        impact_angle_deg=15.0,
        impact_velocity_ms=1500.0,
        projectile_hardness=0.9,
        target_hardness=0.8
    )
    
    # Calculate advanced penetration
    result = ammo.calculate_advanced_penetration(
        armor, 2000.0, 15.0,
        environmental_conditions=env_conditions,
        temperature_conditions=temp_conditions,
        ricochet_params=ricochet_params
    )
    
    print(f"Base penetration: {result['base_penetration']:.1f} mm RHA")
    print(f"Final penetration: {result['final_penetration']:.1f} mm RHA")
    print(f"Velocity at target: {result['velocity_at_target']:.1f} m/s")
    
    if result['ricochet_analysis']:
        ricochet = result['ricochet_analysis']
        print(f"Ricochet probability: {ricochet.get('ricochet_probability', 0)*100:.1f}%")
        print(f"Predicted outcome: {ricochet.get('predicted_outcome', 'N/A')}")
    
    if result['temperature_analysis']:
        temp = result['temperature_analysis']
        print(f"Temperature velocity modifier: {temp.get('velocity_modifier', 1.0):.3f}")
        print(f"Temperature penetration modifier: {temp.get('penetration_modifier', 1.0):.3f}")
    
    # Test multiple hits with damage accumulation
    print(f"\nTesting damage accumulation...")
    
    for hit in range(3):
        # Apply impact damage
        impact_location = (random.uniform(-200, 200), random.uniform(-200, 200))
        penetration_attempted = result['final_penetration']
        energy = result.get('energy_at_target', 50000)  # Joules
        effective_thickness = armor.get_effective_thickness(ammo.penetration_type, 15.0)
        penetration_achieved = penetration_attempted > effective_thickness
        
        armor.apply_damage_from_impact(
            ammo, impact_location, penetration_attempted,
            energy, penetration_achieved, hit * 15.0
        )
        
        print(f"  Hit {hit+1}: {'PENETRATION' if penetration_achieved else 'DEFEAT'}")
        
        # Recalculate with damaged armor
        new_result = ammo.calculate_advanced_penetration(
            armor, 2000.0, 15.0,
            environmental_conditions=env_conditions,
            temperature_conditions=temp_conditions,
            ricochet_params=ricochet_params
        )
        
        damage_summary = armor.get_damage_summary()
        print(f"    Armor integrity: {damage_summary['current_condition']['integrity_percent']:.1f}%")
        print(f"    Required penetration: {armor.get_effective_thickness(ammo.penetration_type, 15.0):.1f} mm")


def main():
    """Run all advanced physics tests."""
    print("TANK ARMOR SIMULATOR - ADVANCED PHYSICS TEST SUITE")
    print("=" * 60)
    
    try:
        test_advanced_ballistics()
        test_armor_damage_system()
        test_ricochet_calculator()
        test_temperature_effects()
        test_integrated_advanced_physics()
        
        print("\n" + "=" * 60)
        print("ALL ADVANCED PHYSICS TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERROR DURING TESTING: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
