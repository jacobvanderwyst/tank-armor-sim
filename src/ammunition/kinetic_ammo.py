"""
Kinetic energy ammunition types for tank armor penetration.
"""

import math
from .base_ammo import BaseAmmunition


class APFSDS(BaseAmmunition):
    """Armor-Piercing Fin-Stabilized Discarding Sabot ammunition."""
    
    def __init__(self, name: str, caliber: float, penetrator_diameter: float,
                 penetrator_mass: float, muzzle_velocity: float, 
                 penetrator_length: float):
        """
        Initialize APFSDS round.
        
        Args:
            penetrator_diameter: Actual penetrator diameter in mm
            penetrator_length: Penetrator length in mm (affects L/D ratio)
        """
        super().__init__(name, caliber, penetrator_mass, muzzle_velocity, "kinetic")
        self.penetrator_diameter = penetrator_diameter
        self.penetrator_length = penetrator_length
        self.ld_ratio = penetrator_length / penetrator_diameter
    
    def calculate_penetration(self, range_m: float, impact_angle: float) -> float:
        """Calculate APFSDS penetration using DeMarre formula variants."""
        velocity = self.get_velocity_at_range(range_m)
        
        # APFSDS penetration formula (simplified)
        # Based on kinetic energy and penetrator characteristics
        base_penetration = (velocity / 1000) ** 1.43 * self.penetrator_diameter * 25
        
        # L/D ratio effect (longer penetrators are more effective)
        ld_factor = min(1.0 + (self.ld_ratio - 15) * 0.02, 1.4)
        
        # Angle effect (APFSDS less affected by angle than conventional rounds)
        angle_factor = 1.0 / (math.cos(math.radians(impact_angle)) ** 0.5)
        
        return base_penetration * ld_factor * angle_factor


class AP(BaseAmmunition):
    """Traditional Armor-Piercing solid shot ammunition."""
    
    def __init__(self, name: str, caliber: float, mass: float, muzzle_velocity: float):
        super().__init__(name, caliber, mass, muzzle_velocity, "kinetic")
    
    def calculate_penetration(self, range_m: float, impact_angle: float) -> float:
        """Calculate AP penetration using DeMarre formula."""
        velocity = self.get_velocity_at_range(range_m)
        
        # Classic DeMarre formula for AP rounds
        # P = K * (m/d²) * v^n * cos(θ)
        k_factor = 0.5  # Material constant
        sectional_density = self.mass / (self.caliber ** 2)
        velocity_factor = (velocity / 1000) ** 1.4
        angle_factor = math.cos(math.radians(impact_angle))
        
        penetration = k_factor * sectional_density * velocity_factor * angle_factor * self.caliber * 100
        
        return max(penetration, 0)


class APCR(BaseAmmunition):
    """Armor-Piercing Composite Rigid (sub-caliber) ammunition."""
    
    def __init__(self, name: str, caliber: float, core_diameter: float,
                 core_mass: float, muzzle_velocity: float):
        """
        Initialize APCR round.
        
        Args:
            core_diameter: Diameter of tungsten/hard core in mm
            core_mass: Mass of the penetrating core in kg
        """
        super().__init__(name, caliber, core_mass, muzzle_velocity, "kinetic")
        self.core_diameter = core_diameter
        self.core_mass = core_mass
    
    def calculate_penetration(self, range_m: float, impact_angle: float) -> float:
        """Calculate APCR penetration."""
        velocity = self.get_velocity_at_range(range_m)
        
        # APCR uses sub-caliber core, higher velocity
        # Similar to AP but with modified sectional density based on core
        sectional_density = self.core_mass / (self.core_diameter ** 2)
        velocity_factor = (velocity / 1000) ** 1.5  # Higher velocity dependence
        angle_factor = math.cos(math.radians(impact_angle)) ** 0.8
        
        penetration = 0.6 * sectional_density * velocity_factor * angle_factor * self.core_diameter * 100
        
        return max(penetration, 0)
