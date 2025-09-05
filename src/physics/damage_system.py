"""
Armor damage accumulation system for tank armor penetration simulation.

This module implements:
- Multi-hit damage accumulation
- Progressive armor degradation
- Fatigue and stress modeling
- Cumulative failure mechanics
"""

import math
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class DamageType(Enum):
    """Types of damage that can be inflicted on armor."""
    KINETIC_IMPACT = "kinetic_impact"
    CHEMICAL_BURN = "chemical_burn"
    SPALL_CRACKING = "spall_cracking"
    FATIGUE = "fatigue"
    THERMAL_STRESS = "thermal_stress"


@dataclass
class DamageEvent:
    """Record of a single damage event."""
    impact_location: Tuple[float, float]  # (x, y) coordinates in mm
    damage_type: DamageType
    energy_joules: float
    penetration_attempted: float  # mm RHA equivalent
    penetration_achieved: bool
    timestamp: float = 0.0  # Time in seconds from first impact
    affected_radius: float = 0.0  # Area of effect in mm


@dataclass
class ArmorCondition:
    """Current condition of armor plate."""
    integrity_percent: float = 100.0  # Overall structural integrity
    hardness_factor: float = 1.0      # Hardness degradation factor
    thickness_remaining: float = 0.0  # Will be set to original thickness
    crack_density: float = 0.0        # Cracks per square cm
    spall_damage: float = 0.0         # Spalling damage accumulation
    thermal_damage: float = 0.0       # Heat damage accumulation
    fatigue_cycles: int = 0           # Number of impact cycles


class ArmorDamageSystem:
    """System for tracking and calculating cumulative armor damage."""
    
    def __init__(self, armor_thickness: float, armor_type: str = "RHA"):
        """
        Initialize the armor damage system.
        
        Args:
            armor_thickness: Initial armor thickness in mm
            armor_type: Type of armor ("RHA", "composite", "reactive", "spaced")
        """
        self.initial_thickness = armor_thickness
        self.armor_type = armor_type
        self.damage_events: List[DamageEvent] = []
        self.condition = ArmorCondition(thickness_remaining=armor_thickness)
        
        # Material properties by armor type
        self.material_properties = {
            "RHA": {
                "hardness_degradation_rate": 0.02,
                "spall_resistance": 1.0,
                "thermal_resistance": 1.0,
                "fatigue_limit": 50
            },
            "composite": {
                "hardness_degradation_rate": 0.01,
                "spall_resistance": 1.5,
                "thermal_resistance": 1.2,
                "fatigue_limit": 100
            },
            "reactive": {
                "hardness_degradation_rate": 0.05,
                "spall_resistance": 0.8,
                "thermal_resistance": 0.9,
                "fatigue_limit": 20
            },
            "spaced": {
                "hardness_degradation_rate": 0.015,
                "spall_resistance": 1.1,
                "thermal_resistance": 1.0,
                "fatigue_limit": 75
            }
        }
        
        self.properties = self.material_properties.get(armor_type, 
                                                     self.material_properties["RHA"])
    
    def apply_damage(self, ammo, impact_location: Tuple[float, float],
                    penetration_attempted: float, energy_joules: float,
                    penetration_achieved: bool, timestamp: float = 0.0) -> None:
        """
        Apply damage from a projectile impact.
        
        Args:
            ammo: Ammunition object
            impact_location: (x, y) coordinates of impact in mm
            penetration_attempted: Attempted penetration in mm RHA
            energy_joules: Impact energy in Joules
            penetration_achieved: Whether penetration was successful
            timestamp: Time of impact in seconds
        """
        # Determine damage type based on ammunition
        damage_type_map = {
            'kinetic': DamageType.KINETIC_IMPACT,
            'chemical': DamageType.CHEMICAL_BURN,
            'spalling': DamageType.SPALL_CRACKING
        }
        
        damage_type = damage_type_map.get(ammo.penetration_type, DamageType.KINETIC_IMPACT)
        
        # Calculate affected radius based on caliber and energy
        affected_radius = max(ammo.caliber * 2, math.sqrt(energy_joules / 1000))
        
        # Create damage event
        damage_event = DamageEvent(
            impact_location=impact_location,
            damage_type=damage_type,
            energy_joules=energy_joules,
            penetration_attempted=penetration_attempted,
            penetration_achieved=penetration_achieved,
            timestamp=timestamp,
            affected_radius=affected_radius
        )
        
        self.damage_events.append(damage_event)
        self._update_armor_condition(damage_event)
    
    def _update_armor_condition(self, damage_event: DamageEvent) -> None:
        """Update armor condition based on new damage event."""
        
        # Calculate damage magnitude relative to armor thickness
        damage_ratio = damage_event.penetration_attempted / self.initial_thickness
        energy_ratio = damage_event.energy_joules / (self.initial_thickness * 1000)
        
        # Update based on damage type
        if damage_event.damage_type == DamageType.KINETIC_IMPACT:
            self._apply_kinetic_damage(damage_ratio, energy_ratio, damage_event)
        elif damage_event.damage_type == DamageType.CHEMICAL_BURN:
            self._apply_chemical_damage(damage_ratio, energy_ratio, damage_event)
        elif damage_event.damage_type == DamageType.SPALL_CRACKING:
            self._apply_spall_damage(damage_ratio, energy_ratio, damage_event)
        
        # Update fatigue
        self.condition.fatigue_cycles += 1
        if self.condition.fatigue_cycles > self.properties["fatigue_limit"]:
            fatigue_degradation = (self.condition.fatigue_cycles - self.properties["fatigue_limit"]) * 0.005
            self.condition.integrity_percent -= fatigue_degradation
        
        # Check for cumulative effects
        self._calculate_cumulative_effects()
        
        # Ensure values stay within bounds
        self.condition.integrity_percent = max(0.0, min(100.0, self.condition.integrity_percent))
        self.condition.hardness_factor = max(0.1, min(1.0, self.condition.hardness_factor))
        self.condition.thickness_remaining = max(0.0, self.condition.thickness_remaining)
    
    def _apply_kinetic_damage(self, damage_ratio: float, energy_ratio: float, 
                            event: DamageEvent) -> None:
        """Apply damage from kinetic projectiles."""
        
        if event.penetration_achieved:
            # Penetration causes significant local damage
            thickness_loss = min(event.penetration_attempted * 0.1, self.initial_thickness * 0.2)
            self.condition.thickness_remaining -= thickness_loss
            
            # Integrity loss from hole
            integrity_loss = damage_ratio * 15.0
            self.condition.integrity_percent -= integrity_loss
            
            # Spalling around penetration
            spall_increase = damage_ratio * self.properties["spall_resistance"] * 5.0
            self.condition.spall_damage += spall_increase
        else:
            # Non-penetrating hit still causes damage
            integrity_loss = damage_ratio * 3.0
            self.condition.integrity_percent -= integrity_loss
            
            # Hardness degradation from deformation
            hardness_loss = energy_ratio * self.properties["hardness_degradation_rate"]
            self.condition.hardness_factor -= hardness_loss
            
            # Crack propagation
            crack_increase = energy_ratio * 2.0
            self.condition.crack_density += crack_increase
    
    def _apply_chemical_damage(self, damage_ratio: float, energy_ratio: float,
                             event: DamageEvent) -> None:
        """Apply damage from chemical energy projectiles (HEAT)."""
        
        if event.penetration_achieved:
            # HEAT jet burns through armor
            burn_depth = event.penetration_attempted * 1.2  # Deep, narrow channel
            thickness_loss = min(burn_depth * 0.05, self.initial_thickness * 0.15)
            self.condition.thickness_remaining -= thickness_loss
            
            # Thermal damage to surrounding area
            thermal_damage = damage_ratio * 10.0 / self.properties["thermal_resistance"]
            self.condition.thermal_damage += thermal_damage
            
            # Less spalling than kinetic, more thermal effects
            spall_increase = damage_ratio * 2.0
            self.condition.spall_damage += spall_increase
            
            integrity_loss = damage_ratio * 12.0
            self.condition.integrity_percent -= integrity_loss
        else:
            # Disrupted jet still causes surface damage
            surface_damage = damage_ratio * 4.0
            self.condition.integrity_percent -= surface_damage
            
            thermal_damage = energy_ratio * 3.0 / self.properties["thermal_resistance"]
            self.condition.thermal_damage += thermal_damage
    
    def _apply_spall_damage(self, damage_ratio: float, energy_ratio: float,
                          event: DamageEvent) -> None:
        """Apply damage from spalling projectiles (HESH)."""
        
        # HESH works by creating spalling on the back face
        spall_effectiveness = 1.0 / self.properties["spall_resistance"]
        
        if event.penetration_achieved:
            # Successful spalling
            spall_increase = damage_ratio * spall_effectiveness * 20.0
            self.condition.spall_damage += spall_increase
            
            # Extensive cracking
            crack_increase = damage_ratio * 10.0
            self.condition.crack_density += crack_increase
            
            # Thickness loss from spall scabbing
            thickness_loss = min(event.penetration_attempted * 0.05, self.initial_thickness * 0.1)
            self.condition.thickness_remaining -= thickness_loss
            
            integrity_loss = damage_ratio * 8.0
            self.condition.integrity_percent -= integrity_loss
        else:
            # Failed spalling still causes surface damage
            surface_spalling = damage_ratio * spall_effectiveness * 5.0
            self.condition.spall_damage += surface_spalling
            
            crack_increase = energy_ratio * 3.0
            self.condition.crack_density += crack_increase
    
    def _calculate_cumulative_effects(self) -> None:
        """Calculate cumulative effects from multiple damage sources."""
        
        # Spall damage reduces effective thickness
        spall_thickness_loss = self.condition.spall_damage * 0.1
        self.condition.thickness_remaining = max(
            0, self.condition.thickness_remaining - spall_thickness_loss
        )
        
        # Thermal damage affects hardness
        thermal_hardness_loss = self.condition.thermal_damage * 0.005
        self.condition.hardness_factor -= thermal_hardness_loss
        
        # Crack density affects overall integrity
        crack_integrity_loss = self.condition.crack_density * 0.5
        self.condition.integrity_percent -= crack_integrity_loss
        
        # Check for critical failure conditions
        if (self.condition.integrity_percent < 20.0 or 
            self.condition.thickness_remaining < self.initial_thickness * 0.3 or
            self.condition.crack_density > 50.0):
            
            # Armor approaching critical failure
            self.condition.hardness_factor *= 0.5
    
    def get_current_effectiveness(self, penetration_type: str) -> float:
        """
        Get current armor effectiveness as a multiplier.
        
        Args:
            penetration_type: Type of penetration being attempted
            
        Returns:
            Effectiveness multiplier (1.0 = full effectiveness, 0.0 = no protection)
        """
        base_effectiveness = self.condition.integrity_percent / 100.0
        
        # Adjust based on penetration type
        if penetration_type == 'kinetic':
            # Kinetic rounds affected by hardness and thickness
            hardness_effect = self.condition.hardness_factor
            thickness_effect = self.condition.thickness_remaining / self.initial_thickness
            effectiveness = base_effectiveness * hardness_effect * thickness_effect
            
        elif penetration_type == 'chemical':
            # HEAT less affected by hardness, more by thickness
            thickness_effect = self.condition.thickness_remaining / self.initial_thickness
            thermal_effect = max(0.1, 1.0 - self.condition.thermal_damage * 0.01)
            effectiveness = base_effectiveness * thickness_effect * thermal_effect
            
        elif penetration_type == 'spalling':
            # HESH effectiveness reduced by spall resistance and cracking
            spall_effect = max(0.1, 1.0 - self.condition.spall_damage * 0.005)
            crack_effect = max(0.1, 1.0 - self.condition.crack_density * 0.01)
            effectiveness = base_effectiveness * spall_effect * crack_effect
            
        else:
            effectiveness = base_effectiveness
        
        return max(0.0, min(1.0, effectiveness))
    
    def get_damage_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive damage summary.
        
        Returns:
            Dictionary containing damage analysis
        """
        total_hits = len(self.damage_events)
        successful_penetrations = sum(1 for event in self.damage_events 
                                    if event.penetration_achieved)
        
        # Categorize damage by type
        damage_by_type = {}
        for damage_type in DamageType:
            damage_by_type[damage_type.value] = sum(
                1 for event in self.damage_events if event.damage_type == damage_type
            )
        
        # Calculate damage concentration (hits per area)
        if self.damage_events:
            impact_points = [event.impact_location for event in self.damage_events]
            # Simplified damage concentration calculation
            damage_area = max(100.0, len(set(impact_points)) * 10.0)  # cm²
            damage_concentration = total_hits / damage_area
        else:
            damage_concentration = 0.0
        
        return {
            'total_impacts': total_hits,
            'successful_penetrations': successful_penetrations,
            'penetration_rate': successful_penetrations / max(1, total_hits),
            'damage_by_type': damage_by_type,
            'damage_concentration': damage_concentration,
            'current_condition': {
                'integrity_percent': self.condition.integrity_percent,
                'hardness_factor': self.condition.hardness_factor,
                'thickness_remaining': self.condition.thickness_remaining,
                'thickness_loss_percent': (1 - self.condition.thickness_remaining / self.initial_thickness) * 100,
                'crack_density': self.condition.crack_density,
                'spall_damage': self.condition.spall_damage,
                'thermal_damage': self.condition.thermal_damage,
                'fatigue_cycles': self.condition.fatigue_cycles
            },
            'armor_status': self._get_armor_status()
        }
    
    def _get_armor_status(self) -> str:
        """Determine current armor status."""
        if self.condition.integrity_percent > 80:
            return "EXCELLENT"
        elif self.condition.integrity_percent > 60:
            return "GOOD"
        elif self.condition.integrity_percent > 40:
            return "DEGRADED"
        elif self.condition.integrity_percent > 20:
            return "HEAVILY_DAMAGED"
        else:
            return "CRITICAL_FAILURE"
    
    def reset_damage(self) -> None:
        """Reset armor to pristine condition."""
        self.damage_events.clear()
        self.condition = ArmorCondition(thickness_remaining=self.initial_thickness)
