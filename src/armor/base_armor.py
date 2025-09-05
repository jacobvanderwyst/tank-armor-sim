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
        
        # Advanced physics integration
        self._advanced_physics_enabled = False
        self._damage_system = None
        self._initial_properties = {
            'thickness': thickness,
            'hardness': hardness,
            'density': density
        }
    
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
    
    def enable_advanced_physics(self, damage_system=None):
        """
        Enable advanced physics calculations including damage accumulation.
        
        Args:
            damage_system: ArmorDamageSystem instance (optional)
        """
        self._advanced_physics_enabled = True
        
        if damage_system is None:
            try:
                from ..physics.damage_system import ArmorDamageSystem
                self._damage_system = ArmorDamageSystem(self.thickness, self.armor_type)
            except ImportError:
                pass
        else:
            self._damage_system = damage_system
    
    def apply_damage_from_impact(self, ammo, impact_location, penetration_attempted,
                               energy_joules, penetration_achieved, timestamp=0.0):
        """
        Apply damage from a projectile impact.
        
        Args:
            ammo: Ammunition object
            impact_location: (x, y) impact coordinates in mm
            penetration_attempted: Attempted penetration in mm RHA
            energy_joules: Impact energy in Joules
            penetration_achieved: Whether penetration was successful
            timestamp: Time of impact in seconds
        """
        if self._advanced_physics_enabled and self._damage_system:
            self._damage_system.apply_damage(
                ammo, impact_location, penetration_attempted,
                energy_joules, penetration_achieved, timestamp
            )
            
            # Update armor properties based on damage
            self._update_properties_from_damage()
    
    def _update_properties_from_damage(self):
        """
        Update armor properties based on accumulated damage.
        """
        if not self._damage_system:
            return
        
        condition = self._damage_system.condition
        
        # Update thickness based on damage
        thickness_ratio = condition.thickness_remaining / self._initial_properties['thickness']
        self.thickness = self._initial_properties['thickness'] * thickness_ratio
        
        # Update hardness based on damage
        self.hardness = self._initial_properties['hardness'] * condition.hardness_factor
        
        # Update mass per area
        self.mass_per_area = self.thickness * self.density / 1000
    
    def get_current_effectiveness(self, ammo_type: str) -> float:
        """
        Get current armor effectiveness considering accumulated damage.
        
        Args:
            ammo_type: Type of ammunition
            
        Returns:
            Effectiveness multiplier (1.0 = full effectiveness)
        """
        if self._advanced_physics_enabled and self._damage_system:
            return self._damage_system.get_current_effectiveness(ammo_type)
        return 1.0
    
    def get_damage_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive damage analysis.
        
        Returns:
            Dictionary containing damage information
        """
        if self._advanced_physics_enabled and self._damage_system:
            return self._damage_system.get_damage_summary()
        return {
            'total_impacts': 0,
            'successful_penetrations': 0,
            'armor_status': 'PRISTINE',
            'current_condition': {
                'integrity_percent': 100.0,
                'thickness_remaining': self.thickness,
                'hardness_factor': 1.0
            }
        }
    
    def reset_damage(self):
        """Reset armor to pristine condition."""
        if self._damage_system:
            self._damage_system.reset_damage()
            
        # Restore original properties
        self.thickness = self._initial_properties['thickness']
        self.hardness = self._initial_properties['hardness']
        self.density = self._initial_properties['density']
        self.mass_per_area = self.thickness * self.density / 1000
    
    def get_effective_thickness(self, ammo_type: str, impact_angle: float) -> float:
        """
        Calculate effective thickness considering angle, armor type, and damage.
        
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
        
        # Apply damage effects if advanced physics is enabled
        if self._advanced_physics_enabled:
            damage_effectiveness = self.get_current_effectiveness(ammo_type)
            effective_thickness *= damage_effectiveness
        
        return effective_thickness
    
    def get_info(self) -> Dict[str, Any]:
        """Get armor information as dictionary."""
        info = {
            'name': self.name,
            'thickness_mm': self.thickness,
            'armor_type': self.armor_type,
            'density_kg_m3': self.density,
            'hardness_factor': self.hardness,
            'mass_per_area_kg_m2': self.mass_per_area,
            'advanced_physics_enabled': self._advanced_physics_enabled
        }
        
        # Add damage information if available
        if self._advanced_physics_enabled:
            damage_info = self.get_damage_summary()
            info['damage_status'] = damage_info['armor_status']
            info['integrity_percent'] = damage_info['current_condition']['integrity_percent']
        
        return info
