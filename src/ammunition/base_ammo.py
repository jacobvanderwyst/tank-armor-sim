"""
Base ammunition class for all anti-tank rounds.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


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
    
    def get_info(self) -> Dict[str, Any]:
        """Get ammunition information as dictionary."""
        return {
            'name': self.name,
            'caliber_mm': self.caliber,
            'mass_kg': self.mass,
            'muzzle_velocity_ms': self.muzzle_velocity,
            'penetration_type': self.penetration_type,
            'kinetic_energy_j': self.kinetic_energy
        }
