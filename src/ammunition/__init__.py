"""
Ammunition module for tank armor penetration simulation.

This module defines different types of anti-tank ammunition and their characteristics.
"""

from .base_ammo import BaseAmmunition
from .kinetic_ammo import APFSDS, AP, APCR
from .chemical_ammo import HEAT, HESH

__all__ = ['BaseAmmunition', 'APFSDS', 'AP', 'APCR', 'HEAT', 'HESH']
