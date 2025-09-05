"""
Ricochet calculation system for tank armor penetration simulation.

This module implements:
- Angle-dependent ricochet probability
- Projectile deflection calculations
- Ammunition-specific ricochet behavior
- Surface condition effects
"""

import math
import numpy as np
from typing import Dict, Tuple, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class RicochetResult(Enum):
    """Possible outcomes of projectile impact."""
    PENETRATION = "penetration"
    RICOCHET = "ricochet"
    SHATTERING = "shattering"
    EMBEDDING = "embedding"


@dataclass
class RicochetParameters:
    """Parameters affecting ricochet probability."""
    impact_angle_deg: float         # Impact angle from normal (0° = perpendicular)
    impact_velocity_ms: float       # Impact velocity in m/s
    projectile_hardness: float      # Relative hardness (0-1)
    target_hardness: float          # Target hardness (0-1)
    surface_roughness: float = 0.5  # Surface roughness factor (0-1)
    target_slope_deg: float = 0.0   # Additional target slope


@dataclass
class RicochetCalculationResult:
    """Result of ricochet calculation."""
    ricochet_probability: float
    predicted_outcome: RicochetResult
    deflection_angle_deg: float
    exit_velocity_ms: float
    energy_retained: float          # Fraction of original energy
    penetration_probability: float
    critical_angle_deg: float       # Angle at which ricochet becomes likely


class RicochetCalculator:
    """Calculator for projectile ricochet probability and behavior."""
    
    def __init__(self):
        """Initialize the ricochet calculator."""
        
        # Material hardness values (relative scale 0-1)
        self.material_hardness = {
            'steel': 0.8,
            'RHA': 0.85,
            'composite': 0.7,
            'ceramic': 0.95,
            'tungsten': 1.0,
            'lead': 0.2,
            'copper': 0.3
        }
        
        # Ammunition type characteristics
        self.ammo_characteristics = {
            'kinetic': {
                'hardness_factor': 0.9,      # High hardness penetrators
                'brittleness': 0.3,          # Low brittleness
                'critical_angle_base': 65.0, # Base critical ricochet angle
                'velocity_dependence': 0.3   # Velocity effect on ricochet
            },
            'chemical': {
                'hardness_factor': 0.4,      # Softer warheads
                'brittleness': 0.6,          # More brittle
                'critical_angle_base': 45.0, # More prone to ricochet
                'velocity_dependence': 0.1   # Less velocity dependent
            },
            'spalling': {
                'hardness_factor': 0.5,      # Medium hardness
                'brittleness': 0.5,          # Medium brittleness
                'critical_angle_base': 55.0, # Moderate ricochet resistance
                'velocity_dependence': 0.2   # Moderate velocity dependence
            }
        }
    
    def calculate_ricochet_probability(self, ammo, armor, 
                                     params: RicochetParameters) -> RicochetCalculationResult:
        """
        Calculate comprehensive ricochet probability and behavior.
        
        Args:
            ammo: Ammunition object
            armor: Armor object
            params: Ricochet calculation parameters
            
        Returns:
            Detailed ricochet calculation result
        """
        # Get ammunition and armor characteristics
        ammo_chars = self.ammo_characteristics.get(ammo.penetration_type,
                                                  self.ammo_characteristics['kinetic'])
        
        # Calculate effective impact angle (including target slope)
        effective_angle = params.impact_angle_deg + params.target_slope_deg
        effective_angle = max(0.0, min(90.0, effective_angle))
        
        # Calculate critical angle for this combination
        critical_angle = self._calculate_critical_angle(ammo, armor, params, ammo_chars)
        
        # Base ricochet probability from angle
        angle_probability = self._calculate_angle_probability(effective_angle, critical_angle)
        
        # Velocity effects
        velocity_factor = self._calculate_velocity_factor(params.impact_velocity_ms, 
                                                        ammo.muzzle_velocity,
                                                        ammo_chars['velocity_dependence'])
        
        # Material interaction effects
        material_factor = self._calculate_material_interaction(ammo, armor, params)
        
        # Surface condition effects
        surface_factor = self._calculate_surface_effects(params.surface_roughness)
        
        # Combine all factors
        ricochet_probability = angle_probability * velocity_factor * material_factor * surface_factor
        ricochet_probability = max(0.0, min(1.0, ricochet_probability))
        
        # Calculate deflection properties
        deflection_angle = self._calculate_deflection_angle(effective_angle, ricochet_probability)
        exit_velocity = self._calculate_exit_velocity(params.impact_velocity_ms, 
                                                    effective_angle, ricochet_probability)
        energy_retained = (exit_velocity / params.impact_velocity_ms) ** 2
        
        # Determine most likely outcome
        predicted_outcome = self._predict_outcome(ricochet_probability, effective_angle, 
                                                params.impact_velocity_ms, ammo_chars)
        
        # Penetration probability is inverse of ricochet (with some adjustment)
        penetration_probability = max(0.0, 1.0 - ricochet_probability * 1.2)
        penetration_probability = min(1.0, penetration_probability)
        
        return RicochetCalculationResult(
            ricochet_probability=ricochet_probability,
            predicted_outcome=predicted_outcome,
            deflection_angle_deg=deflection_angle,
            exit_velocity_ms=exit_velocity,
            energy_retained=energy_retained,
            penetration_probability=penetration_probability,
            critical_angle_deg=critical_angle
        )
    
    def _calculate_critical_angle(self, ammo, armor, params: RicochetParameters,
                                ammo_chars: Dict[str, float]) -> float:
        """Calculate the critical angle for ricochet onset."""
        
        base_critical = ammo_chars['critical_angle_base']
        
        # Adjust for ammunition characteristics
        if hasattr(ammo, 'ld_ratio'):  # APFSDS L/D ratio effect
            ld_adjustment = (ammo.ld_ratio - 20) * 0.5  # Longer rods ricochet less
            base_critical += ld_adjustment
        
        # Adjust for velocity (higher velocity reduces ricochet tendency)
        velocity_ratio = params.impact_velocity_ms / 1000.0  # Normalize around 1000 m/s
        velocity_adjustment = (velocity_ratio - 1.0) * 10.0
        base_critical += velocity_adjustment
        
        # Adjust for material properties
        hardness_ratio = params.projectile_hardness / params.target_hardness
        hardness_adjustment = (hardness_ratio - 1.0) * 5.0
        base_critical += hardness_adjustment
        
        return max(30.0, min(80.0, base_critical))
    
    def _calculate_angle_probability(self, angle_deg: float, critical_angle_deg: float) -> float:
        """Calculate ricochet probability based on impact angle."""
        
        if angle_deg <= critical_angle_deg:
            # Below critical angle - low ricochet probability
            normalized_angle = angle_deg / critical_angle_deg
            probability = 0.1 * (1 - normalized_angle) ** 2
        else:
            # Above critical angle - increasing ricochet probability
            excess_angle = angle_deg - critical_angle_deg
            max_excess = 90.0 - critical_angle_deg
            normalized_excess = excess_angle / max_excess
            
            # Exponential increase in ricochet probability
            probability = 0.1 + 0.85 * (1 - math.exp(-3 * normalized_excess))
        
        return probability
    
    def _calculate_velocity_factor(self, impact_velocity: float, nominal_velocity: float,
                                 velocity_dependence: float) -> float:
        """Calculate velocity effect on ricochet probability."""
        
        velocity_ratio = impact_velocity / nominal_velocity
        
        if velocity_ratio > 1.0:
            # Higher velocity reduces ricochet
            factor = 1.0 - velocity_dependence * (velocity_ratio - 1.0) * 0.5
        else:
            # Lower velocity increases ricochet
            factor = 1.0 + velocity_dependence * (1.0 - velocity_ratio) * 0.8
        
        return max(0.2, min(2.0, factor))
    
    def _calculate_material_interaction(self, ammo, armor, params: RicochetParameters) -> float:
        """Calculate material interaction effects on ricochet."""
        
        # Hardness differential effect
        hardness_ratio = params.projectile_hardness / params.target_hardness
        
        if hardness_ratio > 1.5:
            # Much harder projectile - lower ricochet
            hardness_factor = 0.7
        elif hardness_ratio < 0.7:
            # Softer projectile - higher ricochet
            hardness_factor = 1.4
        else:
            # Similar hardness - moderate effect
            hardness_factor = 1.0 + (1.0 - hardness_ratio) * 0.3
        
        # Armor type specific effects
        armor_factors = {
            'RHA': 1.0,
            'composite': 0.9,    # Better ricochet characteristics
            'reactive': 1.2,     # ERA can cause more ricochets
            'spaced': 0.8        # Spaced armor reduces ricochet
        }
        
        armor_factor = armor_factors.get(armor.armor_type, 1.0)
        
        return hardness_factor * armor_factor
    
    def _calculate_surface_effects(self, surface_roughness: float) -> float:
        """Calculate surface roughness effects on ricochet."""
        
        # Rough surfaces reduce ricochet probability
        # Smooth surfaces increase ricochet probability
        roughness_factor = 1.0 + (0.5 - surface_roughness) * 0.4
        
        return max(0.6, min(1.4, roughness_factor))
    
    def _calculate_deflection_angle(self, impact_angle: float, 
                                  ricochet_probability: float) -> float:
        """Calculate projectile deflection angle upon ricochet."""
        
        if ricochet_probability < 0.1:
            return 0.0  # No significant deflection
        
        # Deflection angle depends on impact angle and ricochet strength
        base_deflection = impact_angle * 0.6  # Typical deflection is 60% of impact angle
        
        # Higher ricochet probability means more deflection
        probability_factor = 0.5 + ricochet_probability * 0.5
        
        deflection = base_deflection * probability_factor
        
        return max(0.0, min(80.0, deflection))
    
    def _calculate_exit_velocity(self, impact_velocity: float, impact_angle: float,
                               ricochet_probability: float) -> float:
        """Calculate exit velocity after ricochet."""
        
        if ricochet_probability < 0.1:
            return impact_velocity * 0.1  # Minimal exit velocity if no ricochet
        
        # Energy loss during ricochet
        # Normal component energy is lost, tangential component is partially retained
        angle_rad = math.radians(impact_angle)
        
        normal_component = impact_velocity * math.cos(angle_rad)
        tangential_component = impact_velocity * math.sin(angle_rad)
        
        # Normal component energy lost
        # Tangential component partially retained
        retained_tangential = tangential_component * (0.7 + ricochet_probability * 0.2)
        
        # Some normal component may be converted to tangential
        converted_normal = normal_component * ricochet_probability * 0.3
        
        exit_velocity = math.sqrt(retained_tangential ** 2 + converted_normal ** 2)
        
        return max(50.0, exit_velocity)  # Minimum exit velocity for visible ricochet
    
    def _predict_outcome(self, ricochet_probability: float, impact_angle: float,
                        impact_velocity: float, ammo_chars: Dict[str, float]) -> RicochetResult:
        """Predict the most likely outcome of impact."""
        
        if ricochet_probability < 0.2:
            return RicochetResult.PENETRATION
        elif ricochet_probability > 0.7:
            return RicochetResult.RICOCHET
        elif impact_velocity < 300 and ammo_chars['brittleness'] > 0.7:
            return RicochetResult.SHATTERING
        elif impact_angle > 75 and impact_velocity < 500:
            return RicochetResult.EMBEDDING
        else:
            # Borderline case - use probability
            if ricochet_probability > 0.45:
                return RicochetResult.RICOCHET
            else:
                return RicochetResult.PENETRATION
    
    def analyze_ricochet_envelope(self, ammo, armor, velocity_range: Tuple[float, float],
                                angle_range: Tuple[float, float], 
                                num_points: int = 50) -> Dict[str, Any]:
        """
        Analyze ricochet behavior over ranges of velocity and angle.
        
        Args:
            ammo: Ammunition object
            armor: Armor object
            velocity_range: (min_velocity, max_velocity) in m/s
            angle_range: (min_angle, max_angle) in degrees
            num_points: Number of calculation points for each parameter
            
        Returns:
            Analysis results with ricochet envelopes
        """
        velocities = np.linspace(velocity_range[0], velocity_range[1], num_points)
        angles = np.linspace(angle_range[0], angle_range[1], num_points)
        
        # Create meshgrid for analysis
        vel_mesh, angle_mesh = np.meshgrid(velocities, angles)
        ricochet_mesh = np.zeros_like(vel_mesh)
        penetration_mesh = np.zeros_like(vel_mesh)
        
        # Default parameters
        base_params = RicochetParameters(
            impact_angle_deg=0,
            impact_velocity_ms=0,
            projectile_hardness=self.material_hardness.get('tungsten', 0.9),
            target_hardness=self.material_hardness.get(armor.armor_type, 0.8)
        )
        
        # Calculate ricochet probabilities across the envelope
        for i in range(num_points):
            for j in range(num_points):
                params = RicochetParameters(
                    impact_angle_deg=angle_mesh[i, j],
                    impact_velocity_ms=vel_mesh[i, j],
                    projectile_hardness=base_params.projectile_hardness,
                    target_hardness=base_params.target_hardness
                )
                
                result = self.calculate_ricochet_probability(ammo, armor, params)
                ricochet_mesh[i, j] = result.ricochet_probability
                penetration_mesh[i, j] = result.penetration_probability
        
        # Find critical boundaries
        ricochet_50_percent = self._find_contour(vel_mesh, angle_mesh, ricochet_mesh, 0.5)
        penetration_50_percent = self._find_contour(vel_mesh, angle_mesh, penetration_mesh, 0.5)
        
        return {
            'velocity_range': velocity_range,
            'angle_range': angle_range,
            'ricochet_probabilities': ricochet_mesh.tolist(),
            'penetration_probabilities': penetration_mesh.tolist(),
            'ricochet_50_boundary': ricochet_50_percent,
            'penetration_50_boundary': penetration_50_percent,
            'velocities': velocities.tolist(),
            'angles': angles.tolist()
        }
    
    def _find_contour(self, x_mesh: np.ndarray, y_mesh: np.ndarray, 
                     z_mesh: np.ndarray, level: float) -> List[Tuple[float, float]]:
        """Find approximate contour line for given level."""
        # Simplified contour finding - return points near the target level
        contour_points = []
        
        for i in range(z_mesh.shape[0] - 1):
            for j in range(z_mesh.shape[1] - 1):
                # Check if contour passes through this cell
                cell_values = [z_mesh[i, j], z_mesh[i+1, j], z_mesh[i, j+1], z_mesh[i+1, j+1]]
                if min(cell_values) <= level <= max(cell_values):
                    # Interpolate position
                    x_pos = (x_mesh[i, j] + x_mesh[i+1, j+1]) / 2
                    y_pos = (y_mesh[i, j] + y_mesh[i+1, j+1]) / 2
                    contour_points.append((x_pos, y_pos))
        
        return contour_points
