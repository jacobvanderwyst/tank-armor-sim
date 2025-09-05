"""
Spaced armor implementation.
"""

from .base_armor import BaseArmor


class SpacedArmor(BaseArmor):
    """Spaced armor with air gaps."""
    
    def __init__(self, name: str, front_plate: float, rear_plate: float,
                 spacing: float):
        """
        Initialize spaced armor.
        
        Args:
            name: Armor designation
            front_plate: Front plate thickness in mm
            rear_plate: Rear plate thickness in mm
            spacing: Air gap between plates in mm
        """
        total_thickness = front_plate + rear_plate
        
        super().__init__(
            name=name,
            thickness=total_thickness,
            armor_type="spaced",
            density=4000.0,  # Lower effective density due to air gap
            hardness=1.0
        )
        
        self.front_plate = front_plate
        self.rear_plate = rear_plate
        self.spacing = spacing
    
    def get_protection_against(self, ammo_type: str) -> float:
        """
        Spaced armor protection factors.
        
        Spacing is effective against HEAT and HESH but minimal against kinetic.
        """
        if ammo_type == 'kinetic':
            # Minimal benefit against kinetic rounds - may even be detrimental
            return 0.95
            
        elif ammo_type == 'chemical':
            # Good protection against HEAT by allowing jet to expand
            spacing_factor = min(2.0, 1.0 + (self.spacing / 100))
            return spacing_factor
            
        elif ammo_type == 'spalling':
            # Excellent protection against HESH - prevents spall transfer
            return 1.8
            
        else:
            return 1.0
