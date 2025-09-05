"""
Base armor class for all armor types.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import math


class BaseArmor(ABC):
    """Base class for all armor types."""
    
    def __init__(self, name: str, thickness: float, armor_type: str, 
                 density: float = 7850.0, hardness: float = 1.0):
        """
        Initialize armor.
        
        Args:
            name: Armor designation/name
            thickness: Nominal thickness in mm
            armor_type: Type of armor (steel, composite, etc.)
            density: Armor density in kg/m³
            hardness: Relative hardness factor (1.0 = standard RHA)
        """
        self.name = name
        self.thickness = thickness
        self.armor_type = armor_type
        self.density = density
        self.hardness = hardness
        self.mass_per_area = thickness * density / 1000  # kg/m²
    
    @abstractmethod
    def get_protection_against(self, ammo_type: str) -> float:
        """
        Get protection factor against specific ammunition type.
        
        Args:
            ammo_type: Type of ammunition ('kinetic', 'chemical', 'spalling')
            
        Returns:
            Protection factor (multiplier for effective thickness)
        """
        pass
    
    def get_effective_thickness(self, ammo_type: str, impact_angle: float) -> float:
        """
        Calculate effective thickness considering angle and armor type.
        
        Args:
            ammo_type: Type of ammunition
            impact_angle: Impact angle from vertical in degrees
            
        Returns:
            Effective thickness in mm RHA equivalent
        """
        # Base thickness adjusted for angle
        angled_thickness = self.thickness / math.cos(math.radians(impact_angle))
        
        # Apply armor type protection factor
        protection_factor = self.get_protection_against(ammo_type)
        
        # Apply hardness factor
        effective_thickness = angled_thickness * protection_factor * self.hardness
        
        return effective_thickness
    
    def can_defeat(self, penetration_capability: float, ammo_type: str, 
                   impact_angle: float) -> bool:
        """
        Determine if armor can defeat incoming round.
        
        Args:
            penetration_capability: Round's penetration in mm RHA
            ammo_type: Type of ammunition
            impact_angle: Impact angle from vertical
            
        Returns:
            True if armor defeats the round
        """
        effective_thickness = self.get_effective_thickness(ammo_type, impact_angle)
        return effective_thickness >= penetration_capability
    
    def get_info(self) -> Dict[str, Any]:
        """Get armor information as dictionary."""
        return {
            'name': self.name,
            'thickness_mm': self.thickness,
            'armor_type': self.armor_type,
            'density_kg_m3': self.density,
            'hardness_factor': self.hardness,
            'mass_per_area_kg_m2': self.mass_per_area
        }
