"""
Chemical energy ammunition types for tank armor penetration.
"""

import math
from .base_ammo import BaseAmmunition


class HEAT(BaseAmmunition):
    """High Explosive Anti-Tank ammunition."""
    
    def __init__(self, name: str, caliber: float, warhead_mass: float,
                 explosive_mass: float, standoff_distance: float = 0.0):
        """
        Initialize HEAT round.
        
        Args:
            warhead_mass: Total warhead mass in kg
            explosive_mass: Mass of explosive charge in kg
            standoff_distance: Optimal standoff for shaped charge in mm
        """
        # HEAT velocity is less critical than kinetic rounds
        muzzle_velocity = 800  # Typical HEAT velocity
        super().__init__(name, caliber, warhead_mass, muzzle_velocity, "chemical")
        self.explosive_mass = explosive_mass
        self.standoff_distance = standoff_distance
    
    def calculate_penetration(self, range_m: float, impact_angle: float) -> float:
        """
        Calculate HEAT penetration.
        
        HEAT penetration is mostly independent of velocity but heavily 
        dependent on warhead diameter and angle of impact.
        """
        # HEAT penetration formula (Monroe effect)
        # Penetration ≈ 2-8 × warhead diameter for well-designed charges
        base_penetration = self.caliber * 6.0  # Conservative estimate
        
        # Angle degradation is severe for HEAT
        angle_factor = math.cos(math.radians(impact_angle)) ** 2
        
        # Explosive mass factor
        explosive_factor = (self.explosive_mass / (self.caliber/1000)) ** 0.3
        
        # Standoff effect (optimal standoff improves penetration)
        if self.standoff_distance > 0:
            standoff_factor = min(1.2, 1.0 + self.standoff_distance / (self.caliber * 3))
        else:
            standoff_factor = 0.9  # Contact detonation is less optimal
        
        penetration = base_penetration * angle_factor * explosive_factor * standoff_factor
        
        return max(penetration, 0)


class HESH(BaseAmmunition):
    """High Explosive Squash Head ammunition."""
    
    def __init__(self, name: str, caliber: float, shell_mass: float,
                 explosive_mass: float, muzzle_velocity: float = 700):
        """
        Initialize HESH round.
        
        Args:
            shell_mass: Total shell mass in kg
            explosive_mass: Mass of plastic explosive in kg
            muzzle_velocity: Muzzle velocity in m/s
        """
        super().__init__(name, caliber, shell_mass, muzzle_velocity, "spalling")
        self.explosive_mass = explosive_mass
    
    def calculate_penetration(self, range_m: float, impact_angle: float) -> float:
        """
        Calculate HESH effectiveness.
        
        HESH works by spalling - it doesn't penetrate directly but causes
        armor fragments to break off the inside face.
        """
        # HESH effectiveness against different armor types varies greatly
        # This is a simplified model
        
        # Base spalling effect
        base_effect = self.explosive_mass * 200  # Arbitrary scale
        
        # Angle effect (HESH works better against sloped armor than HEAT)
        angle_factor = math.cos(math.radians(impact_angle * 0.7))
        
        # Velocity has minimal effect on HESH
        velocity = self.get_velocity_at_range(range_m)
        velocity_factor = min(1.2, velocity / 600)  # Slight benefit from higher velocity
        
        # HESH is less effective against very thin or very thick armor
        # This would need target armor thickness to calculate properly
        # For now, assume optimal thickness
        thickness_factor = 1.0
        
        effectiveness = base_effect * angle_factor * velocity_factor * thickness_factor
        
        return max(effectiveness, 0)
