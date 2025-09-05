"""
Calculate Realistic Maximum Range for Tank Ammunition

This script determines the theoretical maximum range for various tank ammunition
types fired at optimal angles, considering realistic physics and environmental factors.
"""

import sys
import os
import math
# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.visualization.enhanced_3d_visualizer import Enhanced3DVisualizer
from src.physics.advanced_physics import EnvironmentalConditions
from src.ammunition import APFSDS, HEAT, HESH
from src.armor import CompositeArmor

def calculate_maximum_range_for_ammo(ammo, launch_angle=45.0, max_time=120.0):
    """Calculate maximum range for given ammunition at specified angle."""
    
    print(f"\nCalculating maximum range for: {ammo.name}")
    print(f"Muzzle Velocity: {ammo.muzzle_velocity} m/s")
    print(f"Mass: {ammo.mass} kg")
    print(f"Launch Angle: {launch_angle}°")
    
    # Standard environmental conditions
    env_conditions = EnvironmentalConditions(
        temperature_celsius=15.0,
        wind_speed_ms=0.0,  # No wind for maximum range
        wind_angle_deg=0.0,
        humidity_percent=50.0,
        altitude_m=0.0
    )
    
    # Create visualizer for trajectory calculation
    visualizer = Enhanced3DVisualizer(debug_level="ERROR")  # Suppress debug output
    
    # Calculate trajectory with extended time limit
    trajectory = []
    
    # Initial conditions
    dt = 0.001  # 1ms time step
    angle_rad = math.radians(launch_angle)
    
    # Initial velocity components
    v0 = ammo.muzzle_velocity
    vx = v0 * math.cos(angle_rad)
    vy = 0.0
    vz = v0 * math.sin(angle_rad)
    
    # Initial position
    x, y, z = 0.0, 0.0, 2.4  # Start at gun height
    t = 0.0
    
    # Environmental parameters
    air_density = visualizer.physics_engine.calculate_air_density(env_conditions)
    gravity = 9.80665
    
    # Projectile parameters
    mass = ammo.mass
    cross_sectional_area = math.pi * (ammo.caliber / 2000.0) ** 2  # mm to m
    
    # Integration loop for maximum range
    while z >= 0 and t < max_time:
        
        # Current velocity magnitude
        v_rel_mag = math.sqrt(vx**2 + vy**2 + vz**2)
        
        # Stop if velocity too low
        if v_rel_mag < 10.0:  # 10 m/s minimum
            break
        
        # Calculate drag
        cd = visualizer.physics_engine.calculate_drag_coefficient(v_rel_mag, ammo.penetration_type)
        drag_force = 0.5 * air_density * v_rel_mag**2 * cd * cross_sectional_area
        
        # Drag acceleration components
        if v_rel_mag > 0:
            drag_ax = -drag_force * (vx / v_rel_mag) / mass
            drag_ay = -drag_force * (vy / v_rel_mag) / mass
            drag_az = -drag_force * (vz / v_rel_mag) / mass
        else:
            drag_ax = drag_ay = drag_az = 0
        
        # Total acceleration
        ax = drag_ax
        ay = drag_ay
        az = drag_az - gravity
        
        # Store trajectory point every 100ms for efficiency
        if int(t * 1000) % 100 == 0:
            trajectory.append({
                'time': t,
                'x': x,
                'y': y,
                'z': z,
                'velocity': v_rel_mag
            })
        
        # Update velocity and position
        vx += ax * dt
        vy += ay * dt
        vz += az * dt
        
        x += vx * dt
        y += vy * dt
        z += vz * dt
        
        t += dt
    
    # Results
    max_range = x
    flight_time = t
    final_velocity = math.sqrt(vx**2 + vy**2 + vz**2) if trajectory else 0
    
    print(f"Maximum Range: {max_range:.0f} m ({max_range/1000:.2f} km)")
    print(f"Flight Time: {flight_time:.1f} s")
    print(f"Final Velocity: {final_velocity:.1f} m/s")
    
    return max_range, flight_time, trajectory

def find_optimal_angle_for_ammo(ammo, angle_range=(30, 60), step=5):
    """Find optimal launch angle for maximum range."""
    
    print(f"\nFinding optimal angle for: {ammo.name}")
    
    best_range = 0
    best_angle = 45
    results = []
    
    for angle in range(angle_range[0], angle_range[1] + 1, step):
        max_range, flight_time, _ = calculate_maximum_range_for_ammo(ammo, angle, max_time=60.0)
        results.append((angle, max_range, flight_time))
        
        if max_range > best_range:
            best_range = max_range
            best_angle = angle
        
        print(f"  {angle}°: {max_range:.0f}m ({flight_time:.1f}s)")
    
    print(f"\nOptimal angle: {best_angle}° with range: {best_range:.0f}m")
    return best_angle, best_range, results

def main():
    """Calculate maximum ranges for various ammunition types."""
    
    print("Calculating Maximum Ranges for Tank Ammunition")
    print("=" * 60)
    
    # Create test ammunition with realistic parameters
    ammunition_types = [
        # Modern APFSDS rounds
        APFSDS(name="M829A4", caliber=120, penetrator_diameter=22, 
               penetrator_mass=8.5, muzzle_velocity=1680, penetrator_length=570),
        
        APFSDS(name="DM63", caliber=120, penetrator_diameter=24, 
               penetrator_mass=8.2, muzzle_velocity=1750, penetrator_length=600),
        
        APFSDS(name="3BM60", caliber=125, penetrator_diameter=24, 
               penetrator_mass=7.8, muzzle_velocity=1800, penetrator_length=740),
        
        # HEAT rounds (name, caliber, warhead_mass, explosive_mass, standoff_distance)
        # Note: HEAT uses fixed 800 m/s velocity from class definition
        HEAT(name="M830A1", caliber=120, warhead_mass=18.6, 
             explosive_mass=7.4, standoff_distance=150),
        
        # HESH rounds (name, caliber, shell_mass, explosive_mass, muzzle_velocity)
        HESH(name="L31A7", caliber=120, shell_mass=22.5, 
             explosive_mass=7.5, muzzle_velocity=670),
    ]
    
    max_ranges = {}
    optimal_angles = {}
    
    # Calculate maximum range at 45 degrees for each ammunition type
    for ammo in ammunition_types:
        max_range, flight_time, trajectory = calculate_maximum_range_for_ammo(ammo, 45.0)
        max_ranges[ammo.name] = max_range
        
        # Find optimal angle for kinetic rounds (more relevant for long range)
        if ammo.penetration_type == 'kinetic':
            best_angle, best_range, _ = find_optimal_angle_for_ammo(ammo)
            optimal_angles[ammo.name] = (best_angle, best_range)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY - Maximum Ranges at 45°")
    print("=" * 60)
    
    sorted_ranges = sorted(max_ranges.items(), key=lambda x: x[1], reverse=True)
    
    for name, range_m in sorted_ranges:
        print(f"{name:15}: {range_m:6.0f}m ({range_m/1000:5.2f}km)")
    
    # Determine system maximum range
    absolute_max_range = max(max_ranges.values())
    fastest_ammo = max(ammunition_types, key=lambda a: a.muzzle_velocity)
    
    print(f"\nFastest Ammunition: {fastest_ammo.name} ({fastest_ammo.muzzle_velocity} m/s)")
    print(f"Absolute Maximum Range: {absolute_max_range:.0f}m ({absolute_max_range/1000:.2f}km)")
    
    # Recommend system limits
    recommended_max = absolute_max_range * 1.1  # Add 10% margin
    
    print(f"\nRecommended System Maximum Range: {recommended_max:.0f}m ({recommended_max/1000:.2f}km)")
    print("(Includes 10% margin for edge cases)")
    
    # Optimal angles summary
    if optimal_angles:
        print("\n" + "=" * 60)
        print("OPTIMAL ANGLES FOR KINETIC ROUNDS")
        print("=" * 60)
        
        for name, (angle, range_m) in optimal_angles.items():
            improvement = (range_m - max_ranges[name]) / max_ranges[name] * 100
            print(f"{name:15}: {angle:2}° -> {range_m:6.0f}m (+{improvement:4.1f}%)")
    
    return recommended_max, absolute_max_range, fastest_ammo

if __name__ == "__main__":
    recommended_max, absolute_max, fastest = main()
    
    print(f"\nFor integration into enhanced_3d_visualizer.py:")
    print(f"RECOMMENDED_MAX_RANGE = {recommended_max:.0f}  # meters")
    print(f"ABSOLUTE_MAX_RANGE = {absolute_max:.0f}  # meters")
