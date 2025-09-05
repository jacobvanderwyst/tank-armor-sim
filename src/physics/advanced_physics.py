"""
Advanced physics engine for tank armor penetration simulation.

This module implements sophisticated physics calculations including:
- Complex atmospheric modeling
- Advanced ballistic trajectories
- Environmental factor integration
- Multi-variable physics calculations
"""

import math
import numpy as np
from typing import Dict, Tuple, Any, Optional
from dataclasses import dataclass


@dataclass
class EnvironmentalConditions:
    """Environmental conditions affecting ballistic performance."""
    temperature_celsius: float = 15.0  # Standard temperature
    air_pressure_kpa: float = 101.325  # Standard atmospheric pressure
    humidity_percent: float = 50.0     # Relative humidity
    altitude_m: float = 0.0            # Altitude above sea level
    wind_speed_ms: float = 0.0         # Wind speed (positive = headwind)
    wind_angle_deg: float = 0.0        # Wind direction relative to trajectory


@dataclass
class AdvancedBallisticResult:
    """Result of advanced ballistic calculation."""
    velocity_at_target: float
    time_of_flight: float
    energy_at_target: float
    trajectory_angle: float
    penetration_modifier: float
    ricochet_probability: float
    environmental_effects: Dict[str, float]


class AdvancedPhysicsEngine:
    """Advanced physics engine for comprehensive ballistic modeling."""
    
    def __init__(self):
        """Initialize the advanced physics engine."""
        self.air_density_sea_level = 1.225  # kg/m³ at 15°C, 101.325 kPa
        self.gravity = 9.80665  # m/s² (standard gravity)
        self.gas_constant = 287.058  # J/(kg·K) for dry air
        
    def calculate_air_density(self, conditions: EnvironmentalConditions) -> float:
        """
        Calculate air density based on environmental conditions.
        
        Args:
            conditions: Environmental conditions
            
        Returns:
            Air density in kg/m³
        """
        # Convert temperature to Kelvin
        temp_k = conditions.temperature_celsius + 273.15
        
        # Pressure correction for altitude (simplified barometric formula)
        pressure_pa = conditions.air_pressure_kpa * 1000
        if conditions.altitude_m > 0:
            # Standard atmospheric model
            pressure_pa *= (1 - 2.25577e-5 * conditions.altitude_m) ** 5.25588
        
        # Humidity correction (approximate)
        humidity_factor = 1.0 - 0.378 * (conditions.humidity_percent / 100.0) * 0.01
        
        # Ideal gas law: ρ = P / (R * T)
        density = (pressure_pa * humidity_factor) / (self.gas_constant * temp_k)
        
        return density
    
    def calculate_drag_coefficient(self, velocity: float, ammo_type: str) -> float:
        """
        Calculate drag coefficient based on velocity and projectile type.
        
        Args:
            velocity: Projectile velocity in m/s
            ammo_type: Type of ammunition ('kinetic', 'chemical', 'spalling')
            
        Returns:
            Drag coefficient (Cd)
        """
        mach_number = velocity / 343.0  # Approximate speed of sound at 20°C
        
        # Base drag coefficients by ammunition type
        base_cd = {
            'kinetic': 0.15,    # Streamlined penetrators
            'chemical': 0.25,   # Blunt warheads
            'spalling': 0.30    # Less aerodynamic shells
        }
        
        cd_base = base_cd.get(ammo_type, 0.25)
        
        # Mach number effects
        if mach_number < 0.8:
            # Subsonic - constant Cd
            cd_modifier = 1.0
        elif mach_number < 1.2:
            # Transonic - increased drag
            cd_modifier = 1.0 + 2.0 * (mach_number - 0.8)
        elif mach_number < 3.0:
            # Supersonic - wave drag
            cd_modifier = 1.8 - 0.2 * (mach_number - 1.2)
        else:
            # Hypersonic - stabilized high drag
            cd_modifier = 1.4
        
        return cd_base * cd_modifier
    
    def calculate_advanced_trajectory(self, ammo, range_m: float, 
                                    conditions: EnvironmentalConditions,
                                    launch_angle: float = 0.0,
                                    time_step: float = 0.001) -> AdvancedBallisticResult:
        """
        Calculate advanced ballistic trajectory with environmental effects.
        
        Args:
            ammo: Ammunition object
            range_m: Target range in meters
            conditions: Environmental conditions
            launch_angle: Launch angle in degrees
            time_step: Integration time step in seconds
            
        Returns:
            Advanced ballistic calculation result
        """
        # Initial conditions
        angle_rad = math.radians(launch_angle)
        vx = ammo.muzzle_velocity * math.cos(angle_rad)
        vy = ammo.muzzle_velocity * math.sin(angle_rad)
        x, y = 0.0, 0.0
        t = 0.0
        
        # Environmental parameters
        air_density = self.calculate_air_density(conditions)
        wind_vx = -conditions.wind_speed_ms * math.cos(math.radians(conditions.wind_angle_deg))
        wind_vy = -conditions.wind_speed_ms * math.sin(math.radians(conditions.wind_angle_deg))
        
        # Projectile parameters
        mass = ammo.mass
        cross_sectional_area = math.pi * (ammo.caliber / 2000.0) ** 2  # Convert mm to m
        
        # Integration loop
        while x < range_m:
            # Current velocity relative to air
            v_rel_x = vx - wind_vx
            v_rel_y = vy - wind_vy
            v_rel = math.sqrt(v_rel_x**2 + v_rel_y**2)
            
            if v_rel < 1.0:  # Prevent division by zero
                break
                
            # Drag calculation
            cd = self.calculate_drag_coefficient(v_rel, ammo.penetration_type)
            drag_force = 0.5 * air_density * v_rel**2 * cd * cross_sectional_area
            
            # Drag acceleration components
            drag_ax = -drag_force * (v_rel_x / v_rel) / mass
            drag_ay = -drag_force * (v_rel_y / v_rel) / mass
            
            # Total acceleration
            ax = drag_ax
            ay = drag_ay - self.gravity
            
            # Update velocity and position
            vx += ax * time_step
            vy += ay * time_step
            x += vx * time_step
            y += vy * time_step
            t += time_step
            
            # Prevent infinite loops
            if t > 60.0:  # 60 second maximum flight time
                break
        
        # Calculate final parameters
        final_velocity = math.sqrt(vx**2 + vy**2)
        final_energy = 0.5 * mass * final_velocity**2
        trajectory_angle = math.degrees(math.atan2(vy, vx))
        
        # Environmental effects summary
        temp_effect = (conditions.temperature_celsius - 15.0) / 15.0 * 0.1
        altitude_effect = conditions.altitude_m / 1000.0 * 0.05
        humidity_effect = (conditions.humidity_percent - 50.0) / 50.0 * 0.02
        
        penetration_modifier = 1.0 + temp_effect - altitude_effect + humidity_effect
        
        environmental_effects = {
            'temperature_effect': temp_effect,
            'altitude_effect': altitude_effect,
            'humidity_effect': humidity_effect,
            'wind_effect': conditions.wind_speed_ms / 10.0 * 0.1,
            'air_density_ratio': air_density / self.air_density_sea_level
        }
        
        return AdvancedBallisticResult(
            velocity_at_target=final_velocity,
            time_of_flight=t,
            energy_at_target=final_energy,
            trajectory_angle=trajectory_angle,
            penetration_modifier=penetration_modifier,
            ricochet_probability=0.0,  # Will be calculated by RicochetCalculator
            environmental_effects=environmental_effects
        )
    
    def calculate_penetration_enhancement(self, base_penetration: float,
                                        velocity_ratio: float,
                                        angle_deg: float,
                                        ammo_type: str) -> float:
        """
        Calculate enhanced penetration with advanced physics.
        
        Args:
            base_penetration: Base penetration value in mm RHA
            velocity_ratio: Actual velocity / nominal velocity
            angle_deg: Impact angle from vertical
            ammo_type: Ammunition type
            
        Returns:
            Enhanced penetration value in mm RHA
        """
        # Velocity effect (non-linear)
        if ammo_type == 'kinetic':
            velocity_exponent = 1.43  # APFSDS velocity dependence
        elif ammo_type == 'chemical':
            velocity_exponent = 0.1   # HEAT less velocity dependent
        else:
            velocity_exponent = 0.5   # HESH moderate dependence
        
        velocity_factor = velocity_ratio ** velocity_exponent
        
        # Advanced angle effects
        angle_rad = math.radians(angle_deg)
        if ammo_type == 'kinetic':
            # APFSDS angle effect (less severe than conventional)
            angle_factor = 1.0 / (math.cos(angle_rad) ** 0.5)
        elif ammo_type == 'chemical':
            # HEAT severe angle degradation
            angle_factor = 1.0 / (math.cos(angle_rad) ** 2)
        else:
            # HESH moderate angle effect
            angle_factor = 1.0 / (math.cos(angle_rad) ** 0.7)
        
        # Combine factors
        enhanced_penetration = base_penetration * velocity_factor * angle_factor
        
        return enhanced_penetration
    
    def calculate_behind_armor_effects(self, ammo, armor, penetration_mm: float,
                                     overmatch_mm: float) -> Dict[str, Any]:
        """
        Calculate behind-armor effects after successful penetration.
        
        Args:
            ammo: Ammunition object
            armor: Armor object
            penetration_mm: Penetration capability in mm
            overmatch_mm: Overmatch amount in mm
            
        Returns:
            Dictionary of behind-armor effects
        """
        effects = {}
        
        if overmatch_mm <= 0:
            # No penetration
            effects['penetration_achieved'] = False
            effects['spall_mass'] = 0.0
            effects['fragment_velocity'] = 0.0
            effects['damage_cone_angle'] = 0.0
            return effects
        
        effects['penetration_achieved'] = True
        
        if ammo.penetration_type == 'kinetic':
            # Kinetic penetrators
            residual_velocity = math.sqrt(2 * overmatch_mm / armor.thickness) * 100
            spall_mass = armor.thickness * 0.01 * ammo.caliber * 0.001  # kg
            fragment_velocity = residual_velocity * 0.6
            damage_cone_angle = min(30.0, 15.0 + overmatch_mm / 10.0)
            
        elif ammo.penetration_type == 'chemical':
            # HEAT jets
            spall_mass = armor.thickness * 0.005 * ammo.caliber * 0.001
            fragment_velocity = 800 + overmatch_mm * 2  # High velocity fragments
            damage_cone_angle = 45.0  # Wide cone for HEAT
            
        else:
            # HESH spalling
            spall_mass = armor.thickness * 0.02 * ammo.caliber * 0.001
            fragment_velocity = 300 + overmatch_mm  # Lower velocity, more mass
            damage_cone_angle = 60.0  # Very wide spall cone
        
        effects['spall_mass'] = spall_mass
        effects['fragment_velocity'] = fragment_velocity
        effects['damage_cone_angle'] = damage_cone_angle
        effects['lethal_area'] = math.pi * (damage_cone_angle / 57.3) ** 2  # Rough area in m²
        
        return effects
