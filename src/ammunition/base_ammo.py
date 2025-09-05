"""
Base ammunition class for all anti-tank rounds.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseAmmunition(ABC):
    """Base class for all ammunition types."""
    
    def __init__(self, name: str, caliber: float, mass: float, 
                 muzzle_velocity: float, penetration_type: str):
        """
        Initialize ammunition.
        
        Args:
            name: Ammunition designation/name
            caliber: Caliber in mm
            mass: Projectile mass in kg
            muzzle_velocity: Muzzle velocity in m/s
            penetration_type: Type of penetration mechanism
        """
        self.name = name
        self.caliber = caliber
        self.mass = mass
        self.muzzle_velocity = muzzle_velocity
        self.penetration_type = penetration_type
        self.kinetic_energy = 0.5 * mass * (muzzle_velocity ** 2)
        
        # Advanced physics integration
        self._advanced_physics_enabled = False
        self._advanced_physics_engine = None
        self._ricochet_calculator = None
        self._temperature_effects = None
    
    @abstractmethod
    def calculate_penetration(self, range_m: float, impact_angle: float) -> float:
        """
        Calculate penetration capability at given range and angle.
        
        Args:
            range_m: Range to target in meters
            impact_angle: Impact angle from vertical in degrees
            
        Returns:
            Penetration capability in mm RHA equivalent
        """
        pass
    
    def get_velocity_at_range(self, range_m: float) -> float:
        """
        Calculate velocity at given range (simplified ballistic model).
        
        Args:
            range_m: Range in meters
            
        Returns:
            Velocity at range in m/s
        """
        # Simplified drag model - more realistic models would use ballistic coefficients
        drag_coefficient = 0.0001  # Simplified drag
        velocity = self.muzzle_velocity * (1 - drag_coefficient * range_m)
        return max(velocity, 0.1 * self.muzzle_velocity)  # Minimum 10% of muzzle velocity
    
    def enable_advanced_physics(self, advanced_physics_engine=None, 
                               ricochet_calculator=None, temperature_effects=None):
        """
        Enable advanced physics calculations.
        
        Args:
            advanced_physics_engine: AdvancedPhysicsEngine instance
            ricochet_calculator: RicochetCalculator instance
            temperature_effects: TemperatureEffects instance
        """
        self._advanced_physics_enabled = True
        
        # Initialize advanced physics modules if not provided
        if advanced_physics_engine is None:
            try:
                from ..physics.advanced_physics import AdvancedPhysicsEngine
                self._advanced_physics_engine = AdvancedPhysicsEngine()
            except ImportError:
                pass
        else:
            self._advanced_physics_engine = advanced_physics_engine
            
        if ricochet_calculator is None:
            try:
                from ..physics.ricochet_calculator import RicochetCalculator
                self._ricochet_calculator = RicochetCalculator()
            except ImportError:
                pass
        else:
            self._ricochet_calculator = ricochet_calculator
            
        if temperature_effects is None:
            try:
                from ..physics.temperature_effects import TemperatureEffects
                self._temperature_effects = TemperatureEffects()
            except ImportError:
                pass
        else:
            self._temperature_effects = temperature_effects
    
    def calculate_advanced_penetration(self, armor, range_m: float, impact_angle: float,
                                     environmental_conditions=None,
                                     temperature_conditions=None,
                                     ricochet_params=None) -> Dict[str, Any]:
        """
        Calculate penetration with advanced physics effects.
        
        Args:
            armor: Armor object
            range_m: Range to target in meters
            impact_angle: Impact angle from vertical in degrees
            environmental_conditions: Environmental conditions for advanced ballistics
            temperature_conditions: Temperature conditions
            ricochet_params: Ricochet calculation parameters
            
        Returns:
            Dictionary with advanced penetration results
        """
        # Start with basic penetration calculation
        base_penetration = self.calculate_penetration(range_m, impact_angle)
        
        results = {
            'base_penetration': base_penetration,
            'final_penetration': base_penetration,
            'velocity_at_target': self.get_velocity_at_range(range_m),
            'advanced_effects': {},
            'ricochet_analysis': {},
            'temperature_analysis': {}
        }
        
        if not self._advanced_physics_enabled:
            return results
        
        # Advanced ballistics calculation
        if self._advanced_physics_engine and environmental_conditions:
            try:
                ballistic_result = self._advanced_physics_engine.calculate_advanced_trajectory(
                    self, range_m, environmental_conditions
                )
                
                # Apply environmental effects to penetration
                enhanced_penetration = self._advanced_physics_engine.calculate_penetration_enhancement(
                    base_penetration,
                    ballistic_result.velocity_at_target / self.muzzle_velocity,
                    impact_angle,
                    self.penetration_type
                )
                
                results['final_penetration'] = enhanced_penetration * ballistic_result.penetration_modifier
                results['velocity_at_target'] = ballistic_result.velocity_at_target
                results['advanced_effects'] = {
                    'environmental_modifier': ballistic_result.penetration_modifier,
                    'ballistic_result': ballistic_result
                }
                
            except Exception as e:
                results['advanced_effects']['error'] = str(e)
        
        # Ricochet analysis
        if self._ricochet_calculator and ricochet_params:
            try:
                ricochet_result = self._ricochet_calculator.calculate_ricochet_probability(
                    self, armor, ricochet_params
                )
                results['ricochet_analysis'] = {
                    'ricochet_probability': ricochet_result.ricochet_probability,
                    'predicted_outcome': ricochet_result.predicted_outcome.value,
                    'deflection_angle': ricochet_result.deflection_angle_deg,
                    'critical_angle': ricochet_result.critical_angle_deg
                }
                
                # Adjust penetration based on ricochet probability
                penetration_probability = 1.0 - ricochet_result.ricochet_probability
                results['final_penetration'] *= penetration_probability
                
            except Exception as e:
                results['ricochet_analysis']['error'] = str(e)
        
        # Temperature effects
        if self._temperature_effects and temperature_conditions:
            try:
                temp_result = self._temperature_effects.calculate_temperature_effects(
                    self, armor, temperature_conditions
                )
                
                # Apply temperature effects
                results['final_penetration'] *= temp_result.penetration_modifier
                results['velocity_at_target'] *= temp_result.velocity_modifier
                
                results['temperature_analysis'] = {
                    'velocity_modifier': temp_result.velocity_modifier,
                    'penetration_modifier': temp_result.penetration_modifier,
                    'propellant_efficiency': temp_result.propellant_efficiency,
                    'accuracy_modifier': temp_result.accuracy_modifier
                }
                
            except Exception as e:
                results['temperature_analysis']['error'] = str(e)
        
        return results
    
    def get_info(self) -> Dict[str, Any]:
        """Get ammunition information as dictionary."""
        info = {
            'name': self.name,
            'caliber_mm': self.caliber,
            'mass_kg': self.mass,
            'muzzle_velocity_ms': self.muzzle_velocity,
            'penetration_type': self.penetration_type,
            'kinetic_energy_j': self.kinetic_energy,
            'advanced_physics_enabled': self._advanced_physics_enabled
        }
        
        return info
