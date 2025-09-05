"""
Advanced physics module for tank armor penetration simulation.

This module implements sophisticated physics calculations including:
- Multi-hit damage accumulation and armor degradation
- Ricochet and deflection probability modeling  
- Temperature effects on ammunition and armor performance
- Advanced ballistic calculations with environmental factors
"""

from .advanced_physics import AdvancedPhysicsEngine
from .damage_system import ArmorDamageSystem
from .ricochet_calculator import RicochetCalculator
from .temperature_effects import TemperatureEffects

__all__ = ['AdvancedPhysicsEngine', 'ArmorDamageSystem', 'RicochetCalculator', 'TemperatureEffects']
