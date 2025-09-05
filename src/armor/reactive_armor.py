"""
Reactive armor implementation.
"""

from .base_armor import BaseArmor


class ReactiveArmor(BaseArmor):
    """Explosive Reactive Armor (ERA) systems."""
    
    def __init__(self, name: str, base_thickness: float, era_thickness: float,
                 explosive_mass: float):
        """
        Initialize reactive armor.
        
        Args:
            name: Armor designation
            base_thickness: Base armor thickness in mm
            era_thickness: ERA tile thickness in mm
            explosive_mass: Explosive mass per tile in kg
        """
        total_thickness = base_thickness + era_thickness
        
        super().__init__(
            name=name,
            thickness=total_thickness,
            armor_type="reactive",
            density=6000.0,  # Lower average density due to air gaps
            hardness=1.0
        )
        
        self.base_thickness = base_thickness
        self.era_thickness = era_thickness
        self.explosive_mass = explosive_mass
    
    def get_protection_against(self, ammo_type: str) -> float:
        """
        Reactive armor protection factors.
        
        ERA is very effective against HEAT but less so against kinetic rounds.
        """
        if ammo_type == 'kinetic':
            # ERA provides some protection against long rod penetrators
            # by destabilizing them, but effect is limited
            return 1.2
            
        elif ammo_type == 'chemical':
            # ERA is very effective against HEAT by disrupting the jet
            return 2.5 + (self.explosive_mass * 10)  # More explosive = better protection
            
        elif ammo_type == 'spalling':
            # ERA helps against HESH by absorbing blast
            return 1.5
            
        else:
            return 1.0
