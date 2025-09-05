"""
Steel armor types for tank armor simulation.
"""

from .base_armor import BaseArmor


class RHA(BaseArmor):
    """Rolled Homogeneous Armor - the baseline for armor comparisons."""
    
    def __init__(self, thickness: float, hardness: float = 1.0):
        """
        Initialize RHA.
        
        Args:
            thickness: Armor thickness in mm
            hardness: Hardness factor relative to standard RHA
        """
        super().__init__(
            name=f"RHA {thickness}mm",
            thickness=thickness,
            armor_type="RHA",
            density=7850.0,  # kg/m³ for steel
            hardness=hardness
        )
    
    def get_protection_against(self, ammo_type: str) -> float:
        """
        RHA protection factors.
        
        RHA is the baseline (1.0) for all ammunition types.
        """
        protection_factors = {
            'kinetic': 1.0,     # Baseline for AP/APFSDS
            'chemical': 1.0,    # Baseline for HEAT
            'spalling': 1.0     # Baseline for HESH
        }
        return protection_factors.get(ammo_type, 1.0)


class HomogeneousSteel(BaseArmor):
    """General homogeneous steel armor with variable properties."""
    
    def __init__(self, name: str, thickness: float, hardness: float = 1.0,
                 quality_factor: float = 1.0):
        """
        Initialize homogeneous steel armor.
        
        Args:
            name: Armor designation
            thickness: Armor thickness in mm
            hardness: Hardness factor relative to RHA
            quality_factor: Steel quality factor (affects all protection)
        """
        super().__init__(
            name=name,
            thickness=thickness,
            armor_type="steel",
            density=7850.0,
            hardness=hardness
        )
        self.quality_factor = quality_factor
    
    def get_protection_against(self, ammo_type: str) -> float:
        """
        Steel armor protection factors modified by quality.
        """
        base_factors = {
            'kinetic': 1.0,
            'chemical': 1.0,
            'spalling': 1.0
        }
        
        base_protection = base_factors.get(ammo_type, 1.0)
        return base_protection * self.quality_factor
