"""
Composite armor implementation.
"""

from .base_armor import BaseArmor


class CompositeArmor(BaseArmor):
    """Multi-layered composite armor systems."""
    
    def __init__(self, name: str, thickness: float, steel_layers: float,
                 ceramic_layers: float = 0.0, other_layers: float = 0.0):
        """
        Initialize composite armor.
        
        Args:
            name: Armor designation
            thickness: Total thickness in mm
            steel_layers: Thickness of steel layers in mm
            ceramic_layers: Thickness of ceramic layers in mm
            other_layers: Thickness of other materials in mm
        """
        # Composite armor has variable density based on composition
        avg_density = self._calculate_average_density(
            thickness, steel_layers, ceramic_layers, other_layers
        )
        
        super().__init__(
            name=name,
            thickness=thickness,
            armor_type="composite",
            density=avg_density,
            hardness=1.0
        )
        
        self.steel_layers = steel_layers
        self.ceramic_layers = ceramic_layers
        self.other_layers = other_layers
    
    def _calculate_average_density(self, total: float, steel: float,
                                 ceramic: float, other: float) -> float:
        """Calculate weighted average density."""
        steel_density = 7850.0  # kg/m³
        ceramic_density = 3900.0  # kg/m³ (alumina)
        other_density = 2000.0  # kg/m³ (various composites)
        
        weighted_density = (
            (steel * steel_density) +
            (ceramic * ceramic_density) +
            (other * other_density)
        ) / total
        
        return weighted_density
    
    def get_protection_against(self, ammo_type: str) -> float:
        """
        Composite armor protection factors.
        
        Composite armor is particularly effective against HEAT.
        """
        # Calculate protection based on layer composition
        steel_ratio = self.steel_layers / self.thickness
        ceramic_ratio = self.ceramic_layers / self.thickness
        
        if ammo_type == 'kinetic':
            # Moderate improvement against kinetic rounds
            protection = 1.0 + (ceramic_ratio * 0.3)
            
        elif ammo_type == 'chemical':
            # Excellent protection against HEAT due to disruption
            protection = 1.2 + (ceramic_ratio * 0.8) + (steel_ratio * 0.2)
            
        elif ammo_type == 'spalling':
            # Good protection against spalling due to layer disruption
            protection = 1.1 + (ceramic_ratio * 0.4) + (steel_ratio * 0.1)
            
        else:
            protection = 1.0
        
        return min(protection, 2.5)  # Cap at 2.5x RHA equivalent
