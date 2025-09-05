"""
Temperature effects system for tank armor penetration simulation.

This module implements:
- Ambient temperature effects on propellant performance
- Material property variations with temperature
- Thermal expansion and contraction effects
- Temperature-dependent ballistic performance
"""

import math
import numpy as np
from typing import Dict, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum


class TemperatureRange(Enum):
    """Temperature range categories."""
    ARCTIC = "arctic"           # < -20°C
    COLD = "cold"              # -20°C to 0°C
    TEMPERATE = "temperate"    # 0°C to 25°C
    HOT = "hot"                # 25°C to 45°C
    DESERT = "desert"          # > 45°C


@dataclass
class TemperatureConditions:
    """Temperature-related environmental conditions."""
    ambient_celsius: float = 15.0      # Ambient air temperature
    propellant_celsius: float = 15.0   # Propellant temperature (may differ from ambient)
    armor_celsius: float = 15.0        # Armor temperature
    barrel_celsius: float = 15.0       # Barrel temperature
    humidity_percent: float = 50.0     # Relative humidity (affects cooling)


@dataclass
class TemperatureEffectsResult:
    """Result of temperature effects calculation."""
    velocity_modifier: float           # Multiplier for muzzle velocity
    penetration_modifier: float       # Multiplier for penetration capability
    accuracy_modifier: float          # Effect on accuracy/dispersion
    propellant_efficiency: float      # Propellant burn efficiency (0-1.2)
    material_hardness_factor: float   # Armor hardness change factor
    thermal_expansion_mm: float       # Thermal expansion of armor in mm
    barrel_wear_factor: float         # Barrel wear rate multiplier


class TemperatureEffects:
    """Calculator for temperature effects on ballistic performance."""
    
    def __init__(self):
        """Initialize the temperature effects calculator."""
        
        # Reference temperature for baseline performance (°C)
        self.reference_temperature = 15.0
        
        # Propellant temperature coefficients (per °C deviation from reference)
        self.propellant_coefficients = {
            'velocity_change_per_c': 0.008,      # 0.8% velocity change per °C
            'pressure_change_per_c': 0.012,     # 1.2% pressure change per °C
            'burn_rate_change_per_c': 0.006,    # 0.6% burn rate change per °C
            'density_change_per_c': -0.001      # Propellant density change
        }
        
        # Material thermal properties
        self.material_properties = {
            'steel': {
                'thermal_expansion_coeff': 12e-6,    # per °C
                'hardness_temp_coeff': -0.002,      # Hardness change per °C
                'elastic_modulus_temp_coeff': -0.0004,
                'yield_strength_temp_coeff': -0.003
            },
            'tungsten': {
                'thermal_expansion_coeff': 4.5e-6,
                'hardness_temp_coeff': -0.001,
                'elastic_modulus_temp_coeff': -0.0002,
                'yield_strength_temp_coeff': -0.002
            },
            'composite': {
                'thermal_expansion_coeff': 8e-6,     # Average for composites
                'hardness_temp_coeff': -0.003,      # More temperature sensitive
                'elastic_modulus_temp_coeff': -0.001,
                'yield_strength_temp_coeff': -0.004
            },
            'ceramic': {
                'thermal_expansion_coeff': 6e-6,
                'hardness_temp_coeff': -0.001,      # Ceramics more stable
                'elastic_modulus_temp_coeff': -0.0001,
                'yield_strength_temp_coeff': -0.002
            }
        }
        
        # Propellant type characteristics
        self.propellant_types = {
            'single_base': {
                'temperature_sensitivity': 1.0,      # Baseline
                'cold_threshold': -10.0,             # °C where performance drops
                'hot_threshold': 40.0,               # °C where performance peaks
                'critical_hot': 60.0                 # °C where degradation begins
            },
            'double_base': {
                'temperature_sensitivity': 0.8,      # Less sensitive
                'cold_threshold': -15.0,
                'hot_threshold': 45.0,
                'critical_hot': 70.0
            },
            'triple_base': {
                'temperature_sensitivity': 0.6,      # Even less sensitive
                'cold_threshold': -20.0,
                'hot_threshold': 50.0,
                'critical_hot': 75.0
            }
        }
    
    def calculate_temperature_effects(self, ammo, armor, 
                                    conditions: TemperatureConditions,
                                    propellant_type: str = "double_base") -> TemperatureEffectsResult:
        """
        Calculate comprehensive temperature effects on ballistic performance.
        
        Args:
            ammo: Ammunition object
            armor: Armor object
            conditions: Temperature conditions
            propellant_type: Type of propellant used
            
        Returns:
            Temperature effects calculation result
        """
        # Get propellant characteristics
        prop_chars = self.propellant_types.get(propellant_type, 
                                             self.propellant_types["double_base"])
        
        # Calculate propellant effects
        velocity_modifier = self._calculate_velocity_effects(conditions.propellant_celsius, 
                                                           prop_chars)
        
        propellant_efficiency = self._calculate_propellant_efficiency(conditions.propellant_celsius,
                                                                    prop_chars)
        
        # Calculate armor material effects
        armor_material = self._get_armor_material_type(armor)
        material_props = self.material_properties.get(armor_material,
                                                     self.material_properties['steel'])
        
        material_hardness_factor = self._calculate_hardness_effects(conditions.armor_celsius,
                                                                  material_props)
        
        thermal_expansion = self._calculate_thermal_expansion(armor.thickness,
                                                            conditions.armor_celsius,
                                                            material_props)
        
        # Calculate penetration effects
        penetration_modifier = self._calculate_penetration_effects(
            velocity_modifier, material_hardness_factor, conditions, ammo.penetration_type
        )
        
        # Calculate accuracy effects
        accuracy_modifier = self._calculate_accuracy_effects(conditions, prop_chars)
        
        # Calculate barrel wear effects
        barrel_wear_factor = self._calculate_barrel_wear_effects(conditions.barrel_celsius,
                                                               propellant_efficiency)
        
        return TemperatureEffectsResult(
            velocity_modifier=velocity_modifier,
            penetration_modifier=penetration_modifier,
            accuracy_modifier=accuracy_modifier,
            propellant_efficiency=propellant_efficiency,
            material_hardness_factor=material_hardness_factor,
            thermal_expansion_mm=thermal_expansion,
            barrel_wear_factor=barrel_wear_factor
        )
    
    def _calculate_velocity_effects(self, propellant_temp: float,
                                  prop_chars: Dict[str, float]) -> float:
        """Calculate temperature effects on muzzle velocity."""
        
        temp_delta = propellant_temp - self.reference_temperature
        sensitivity = prop_chars['temperature_sensitivity']
        
        # Base temperature coefficient effect
        base_change = temp_delta * self.propellant_coefficients['velocity_change_per_c']
        
        # Non-linear effects at extreme temperatures
        if propellant_temp < prop_chars['cold_threshold']:
            # Cold weather performance degradation
            cold_penalty = (prop_chars['cold_threshold'] - propellant_temp) * 0.01
            base_change -= cold_penalty
            
        elif propellant_temp > prop_chars['critical_hot']:
            # Hot weather degradation (propellant decomposition)
            hot_penalty = (propellant_temp - prop_chars['critical_hot']) * 0.005
            base_change -= hot_penalty
            
        elif propellant_temp > prop_chars['hot_threshold']:
            # Optimal hot temperature range
            hot_bonus = min(0.02, (propellant_temp - prop_chars['hot_threshold']) * 0.002)
            base_change += hot_bonus
        
        # Apply sensitivity factor
        velocity_change = base_change * sensitivity
        
        return 1.0 + velocity_change
    
    def _calculate_propellant_efficiency(self, propellant_temp: float,
                                       prop_chars: Dict[str, float]) -> float:
        """Calculate propellant burn efficiency based on temperature."""
        
        temp_delta = propellant_temp - self.reference_temperature
        
        # Efficiency peaks at slightly elevated temperatures
        optimal_temp = self.reference_temperature + 25
        temp_from_optimal = propellant_temp - optimal_temp
        
        # Gaussian-like efficiency curve
        efficiency = 1.0 + 0.15 * math.exp(-0.5 * (temp_from_optimal / 20.0) ** 2)
        
        # Penalties for extreme temperatures
        if propellant_temp < -30:
            efficiency *= 0.7  # Severe cold penalty
        elif propellant_temp > 70:
            efficiency *= 0.8  # Severe heat penalty
        
        return max(0.3, min(1.2, efficiency))
    
    def _calculate_hardness_effects(self, armor_temp: float,
                                  material_props: Dict[str, float]) -> float:
        """Calculate temperature effects on armor hardness."""
        
        temp_delta = armor_temp - self.reference_temperature
        hardness_coeff = material_props['hardness_temp_coeff']
        
        # Linear hardness change with temperature
        hardness_change = temp_delta * hardness_coeff
        
        # Additional effects for extreme temperatures
        if armor_temp < -40:
            # Severe cold can make some materials brittle
            hardness_change += 0.1  # Increased hardness but brittle
        elif armor_temp > 500:
            # High temperature softening (e.g., from previous HEAT impacts)
            hardness_change -= 0.3
        
        hardness_factor = 1.0 + hardness_change
        
        return max(0.3, min(1.5, hardness_factor))
    
    def _calculate_thermal_expansion(self, thickness_mm: float, armor_temp: float,
                                   material_props: Dict[str, float]) -> float:
        """Calculate thermal expansion of armor."""
        
        temp_delta = armor_temp - self.reference_temperature
        expansion_coeff = material_props['thermal_expansion_coeff']
        
        # Linear thermal expansion
        expansion_mm = thickness_mm * expansion_coeff * temp_delta
        
        return expansion_mm
    
    def _calculate_penetration_effects(self, velocity_modifier: float,
                                     hardness_factor: float,
                                     conditions: TemperatureConditions,
                                     ammo_type: str) -> float:
        """Calculate combined temperature effects on penetration."""
        
        # Base penetration scales with velocity squared for kinetic rounds
        if ammo_type == 'kinetic':
            velocity_effect = velocity_modifier ** 1.8  # Strong velocity dependence
        elif ammo_type == 'chemical':
            velocity_effect = velocity_modifier ** 0.2  # Weak velocity dependence
        else:
            velocity_effect = velocity_modifier ** 0.8  # Moderate dependence
        
        # Armor hardness effects (higher hardness reduces penetration)
        hardness_effect = 1.0 / hardness_factor
        
        # Additional environmental effects
        env_effect = 1.0
        
        # Humidity affects chemical rounds (HEAT jet stability)
        if ammo_type == 'chemical':
            humidity_factor = 1.0 - (conditions.humidity_percent - 50.0) / 500.0
            env_effect *= humidity_factor
        
        # Combine all effects
        penetration_modifier = velocity_effect * hardness_effect * env_effect
        
        return max(0.2, min(2.0, penetration_modifier))
    
    def _calculate_accuracy_effects(self, conditions: TemperatureConditions,
                                  prop_chars: Dict[str, float]) -> float:
        """Calculate temperature effects on accuracy/dispersion."""
        
        # Temperature differential effects (barrel vs propellant vs ambient)
        barrel_prop_diff = abs(conditions.barrel_celsius - conditions.propellant_celsius)
        ambient_prop_diff = abs(conditions.ambient_celsius - conditions.propellant_celsius)
        
        # Base dispersion increases with temperature differentials
        differential_effect = 1.0 + (barrel_prop_diff + ambient_prop_diff) * 0.01
        
        # Extreme temperature effects
        extreme_penalty = 0.0
        if conditions.propellant_celsius < -20 or conditions.propellant_celsius > 50:
            extreme_penalty = 0.1
        
        # Cold barrel effects (different thermal expansion)
        if conditions.barrel_celsius < conditions.ambient_celsius - 10:
            differential_effect += 0.05
        
        accuracy_modifier = differential_effect + extreme_penalty
        
        return max(1.0, min(3.0, accuracy_modifier))  # 1.0 = no change, >1.0 = worse accuracy
    
    def _calculate_barrel_wear_effects(self, barrel_temp: float,
                                     propellant_efficiency: float) -> float:
        """Calculate temperature effects on barrel wear rate."""
        
        # Higher temperatures increase barrel wear
        temp_effect = 1.0 + max(0, (barrel_temp - 20.0)) * 0.02
        
        # Higher propellant efficiency (higher pressures) increases wear
        efficiency_effect = propellant_efficiency ** 0.5
        
        # Extreme temperature penalties
        if barrel_temp > 80:
            temp_effect *= 2.0  # Severe high temperature wear
        elif barrel_temp < -30:
            temp_effect *= 1.3  # Cold temperature brittleness
        
        wear_factor = temp_effect * efficiency_effect
        
        return max(0.5, min(5.0, wear_factor))
    
    def _get_armor_material_type(self, armor) -> str:
        """Determine the primary material type of armor."""
        
        armor_type_to_material = {
            'RHA': 'steel',
            'steel': 'steel',
            'composite': 'composite',
            'reactive': 'steel',     # ERA backing is typically steel
            'spaced': 'steel'        # Spaced armor typically steel plates
        }
        
        return armor_type_to_material.get(armor.armor_type, 'steel')
    
    def get_temperature_range_category(self, temperature: float) -> TemperatureRange:
        """Categorize temperature into operational range."""
        
        if temperature < -20:
            return TemperatureRange.ARCTIC
        elif temperature < 0:
            return TemperatureRange.COLD
        elif temperature < 25:
            return TemperatureRange.TEMPERATE
        elif temperature < 45:
            return TemperatureRange.HOT
        else:
            return TemperatureRange.DESERT
    
    def get_temperature_recommendations(self, temperature: float,
                                      ammo_type: str) -> Dict[str, str]:
        """Get operational recommendations for given temperature conditions."""
        
        temp_range = self.get_temperature_range_category(temperature)
        recommendations = {}
        
        if temp_range == TemperatureRange.ARCTIC:
            recommendations.update({
                'propellant': 'Use cold-weather propellant formulation',
                'storage': 'Warm ammunition before use if possible',
                'accuracy': 'Expect reduced accuracy, adjust for temperature',
                'penetration': 'Reduced performance expected'
            })
            
        elif temp_range == TemperatureRange.COLD:
            recommendations.update({
                'propellant': 'Monitor propellant temperature',
                'storage': 'Insulate ammunition storage',
                'accuracy': 'Minor accuracy degradation expected',
                'penetration': 'Slightly reduced performance'
            })
            
        elif temp_range == TemperatureRange.HOT:
            recommendations.update({
                'propellant': 'Monitor for propellant heating',
                'storage': 'Avoid prolonged sun exposure',
                'accuracy': 'Good accuracy expected',
                'penetration': 'Near-optimal performance'
            })
            
        elif temp_range == TemperatureRange.DESERT:
            recommendations.update({
                'propellant': 'Risk of propellant degradation',
                'storage': 'Active cooling may be required',
                'accuracy': 'Temperature differentials affect accuracy',
                'penetration': 'Performance may degrade at extreme heat',
                'barrel': 'Increased barrel wear rate'
            })
        
        # Ammunition-specific recommendations
        if ammo_type == 'chemical' and temp_range in [TemperatureRange.HOT, TemperatureRange.DESERT]:
            recommendations['chemical'] = 'HEAT rounds sensitive to temperature - monitor jet stability'
        elif ammo_type == 'kinetic' and temp_range == TemperatureRange.ARCTIC:
            recommendations['kinetic'] = 'APFSDS less affected by cold than other rounds'
        
        return recommendations
