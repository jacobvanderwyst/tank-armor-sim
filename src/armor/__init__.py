"""
Armor module for tank armor penetration simulation.

This module defines different types of tank armor and their protective characteristics.
"""

from .base_armor import BaseArmor
from .steel_armor import RHA, HomogeneousSteel
from .composite_armor import CompositeArmor
from .reactive_armor import ReactiveArmor
from .spaced_armor import SpacedArmor

__all__ = ['BaseArmor', 'RHA', 'HomogeneousSteel', 'CompositeArmor', 
           'ReactiveArmor', 'SpacedArmor']
