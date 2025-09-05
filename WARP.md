# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Quick Start

**Setup:**
```bash
# Python 3.8+ required - includes matplotlib and numpy for visualization
pip install -r requirements.txt
```

**Run the simulator:**
```bash
python main.py
```

**Test visualization (optional):**
```bash
python test_visualization.py
```

**Basic penetration test (programmatic):**
```python
# Create ammunition and armor instances, then calculate results
from src.ammunition import APFSDS
from src.armor import RHA

ammo = APFSDS("M829A4", 120.0, 22.0, 4.6, 1680, 570)
armor = RHA(200.0)
penetration = ammo.calculate_penetration(2000.0, 15.0)  # range_m, angle_deg
can_defeat = armor.can_defeat(penetration, "kinetic", 15.0)
```

## How to Run Simulations

The simulator provides an interactive CLI interface accessed via `python main.py`. The main simulation flow:

1. **Run Penetration Test (Option 1)**: Select ammunition → Select armor → Enter engagement parameters (range, angle) → View text results
2. **Run Penetration Test with Visualization (Option 2)**: Same as above but generates comprehensive 4-panel visualization showing:
   - Angle of attack and armor geometry
   - Ammunition-specific penetration mechanism (kinetic/chemical/spalling)
   - Behind-armor effects and damage assessment
   - Detailed penetration test summary
3. **View Ballistic Trajectory (Option 3)**: Generate ballistic flight path visualization with:
   - Projectile trajectory arc with gravity effects
   - Velocity decay over distance
   - Target armor representation
   - Impact angle visualization
4. **View Catalogs (Options 6-7)**: Browse available ammunition and armor with specifications
5. **Future features**: Ammunition comparison (Option 4), Armor comparison (Option 5)

**Key ammunition types available:**
- M829A4 APFSDS (120mm, US)
- 3BM60 APFSDS (125mm, Russian) 
- M830A1 HEAT (120mm, US)
- 3BK29 HEAT (125mm, Russian)
- L31A7 HESH (120mm, UK)
- M72 AP (76mm, WWII US)

**Key armor configurations available:**
- 100mm/200mm RHA baseline
- M1A2 Frontal (composite, 650mm)
- T-90M Frontal (reactive with Relikt ERA, 545mm)
- Challenger 2 Frontal (Dorchester composite, 800mm)
- Leopard 2A7 Side (spaced armor, 105mm)

## Repository Structure

```
tank-armor-sim/
├── src/
│   ├── ammunition/          # Ammunition class hierarchy
│   │   ├── base_ammo.py     # BaseAmmunition abstract class
│   │   ├── kinetic_ammo.py  # APFSDS, AP, APCR classes
│   │   └── chemical_ammo.py # HEAT, HESH classes
│   ├── armor/              # Armor class hierarchy  
│   │   ├── base_armor.py    # BaseArmor abstract class
│   │   ├── steel_armor.py   # RHA, HomogeneousSteel classes
│   │   ├── composite_armor.py # CompositeArmor class
│   │   ├── reactive_armor.py  # ReactiveArmor (ERA) class
│   │   └── spaced_armor.py    # SpacedArmor class
│   └── visualization/       # Graphical visualization system
│       ├── __init__.py      # Visualization module exports
│       ├── ballistics_visualizer.py # Flight path and trajectory plots
│       └── penetration_visualizer.py # 4-panel penetration analysis
├── config/                 # Historical data (JSON format)
│   ├── ammunition_data.json # Real-world ammunition specifications
│   └── armor_data.json     # Real-world armor configurations
├── main.py                 # CLI entry point and TankArmorSimulator class
├── test_visualization.py   # Visualization system test script
└── requirements.txt        # matplotlib>=3.5.0, numpy>=1.20.0
```

## Ammunition Class Hierarchy

**Base Class:** `src.ammunition.base_ammo.BaseAmmunition`
- Core fields: `name`, `caliber`, `mass`, `muzzle_velocity`, `penetration_type`, `kinetic_energy`
- Key method: `calculate_penetration(range_m, impact_angle)` → returns penetration in mm RHA
- Ballistics: `get_velocity_at_range(range_m)` using simplified drag model

**Kinetic Ammunition** (`src.ammunition.kinetic_ammo`):
- `APFSDS`: Uses DeMarre formula variants with L/D ratio effects and reduced angle sensitivity
  - Additional fields: `penetrator_diameter`, `penetrator_length`, `ld_ratio`
  - Penetration formula: `base_penetration * ld_factor * angle_factor`
- `AP`: Traditional solid shot using classic DeMarre formula with sectional density
- `APCR`: Sub-caliber rounds with `core_diameter` and higher velocity dependence

**Chemical Ammunition** (`src.ammunition.chemical_ammo`):
- `HEAT`: Monroe effect modeling, angle-sensitive, independent of velocity
  - Additional fields: `explosive_mass`, `standoff_distance`
  - Penetration ≈ 6× warhead diameter with explosive/standoff factors
- `HESH`: Spalling mechanism, works by armor fragmentation rather than direct penetration
  - Effectiveness = `explosive_mass * 200 * angle_factor * velocity_factor`

## Armor Class Hierarchy

**Base Class:** `src.armor.base_armor.BaseArmor`
- Core fields: `name`, `thickness`, `armor_type`, `density`, `hardness`, `mass_per_area`
- Key methods:
  - `get_protection_against(ammo_type)` → protection factor multiplier
  - `get_effective_thickness(ammo_type, impact_angle)` → effective thickness in mm RHA
  - `can_defeat(penetration_capability, ammo_type, impact_angle)` → boolean

**Armor Types:**
- `RHA` (`src.armor.steel_armor`): Baseline armor (1.0× protection against all types)
- `CompositeArmor` (`src.armor.composite_armor`): Multi-layered systems
  - Fields: `steel_layers`, `ceramic_layers`, `other_layers`
  - Excellent vs HEAT (up to 2.5×), moderate vs kinetic, good vs spalling
- `ReactiveArmor` (`src.armor.reactive_armor`): ERA systems  
  - Fields: `base_thickness`, `era_thickness`, `explosive_mass`
  - Very effective vs HEAT (2.5×+ based on explosive mass), limited vs kinetic (1.2×)
- `SpacedArmor` (`src.armor.spaced_armor`): Air-gap protection
  - Fields: `front_plate`, `rear_plate`, `spacing`
  - Excellent vs HESH (1.8×), good vs HEAT (spacing-dependent), poor vs kinetic (0.95×)

## Physics Calculation System

**Core calculation flow:**
1. `ammunition.calculate_penetration(range, angle)` → penetration capability in mm RHA
2. `armor.get_effective_thickness(ammo_type, angle)` → effective protection in mm RHA  
3. Compare values to determine penetration/defeat

**Key physics models:**
- **Kinetic**: DeMarre-based formulas with material constants, sectional density, velocity dependence
- **HEAT**: Diameter-based scaling (~6× caliber), standoff optimization, severe angle degradation
- **HESH**: Explosive mass scaling, angle tolerance, velocity threshold effects

**Angle handling:**
- Angles specified as degrees from vertical (0° = perpendicular impact)
- Kinetic rounds: `cos(angle)` or `cos(angle)^0.8` factors
- HEAT rounds: `cos(angle)^2` (severe degradation)
- Armor thickness: Line-of-sight adjustment via `thickness/cos(angle)`

## Configuration System

The `config/` directory contains historical data in JSON format for ammunition and armor specifications. These are used for reference and validation but the main simulation uses hard-coded objects in `main.py`.

**JSON Structure Examples:**
- `ammunition_data.json`: Nested by type (`apfsds_rounds`, `heat_rounds`, etc.)
- `armor_data.json`: Nested by category (`modern_mbt_armor`, `historical_armor`, etc.)

Each entry includes technical specifications, introduction year, country, and notes with historical context.

## Development Workflow

**Adding new ammunition:**
1. Create subclass in appropriate module (`kinetic_ammo.py` or `chemical_ammo.py`)
2. Implement `calculate_penetration()` method with type-specific physics
3. Add instance to `TankArmorSimulator._create_ammunition_catalog()`
4. Add reference data to `config/ammunition_data.json`

**Adding new armor:**
1. Create subclass in appropriate module or new file under `src/armor/`
2. Implement `get_protection_against()` method defining effectiveness vs each ammo type
3. Add instance to `TankArmorSimulator._create_armor_catalog()`  
4. Add reference data to `config/armor_data.json`

**Testing approach:**
- Currently no formal test suite (tests/ directory exists but is empty)
- Manual testing via interactive CLI
- Physics validation against historical penetration data in JSON configs

## Implementation Details

**Units and conventions:**
- Length: millimeters (armor thickness, penetration values)
- Mass: kilograms 
- Velocity: meters/second
- Angles: degrees from vertical (0° = perpendicular)
- Energy: joules (calculated as 0.5 * mass * velocity²)

**Key constants:**
- Drag coefficient: 0.0001 (simplified ballistic model)
- Minimum velocity retention: 10% of muzzle velocity
- Maximum protection factors: 2.5× RHA equivalent (composite armor cap)

**Penetration formulas:**
- APFSDS: `(velocity/1000)^1.43 * penetrator_diameter * 25 * ld_factor * angle_factor`
- AP: `k_factor * sectional_density * (velocity/1000)^1.4 * cos(angle) * caliber * 100`
- HEAT: `caliber * 6.0 * cos(angle)^2 * explosive_factor * standoff_factor`

**Result interpretation:**
- Values are in "mm RHA equivalent" - the thickness of rolled homogeneous armor that would provide equivalent protection
- Penetration occurs when `penetration_capability > effective_thickness`
- Safety margin = `effective_thickness - penetration_capability` (positive means armor holds)
- Overmatch = `penetration_capability - effective_thickness` (positive means penetration)

## Visualization System

**BallisticsVisualizer** (`src.visualization.ballistics_visualizer`):
- `visualize_flight_path()`: Creates trajectory plots with optional velocity decay subplot
- `calculate_trajectory()`: Computes ballistic arc points with gravity and drag
- Features: Projectile instances along flight path, armor target representation, impact angle annotation
- Output: High-resolution PNG files with trajectory analysis

**PenetrationVisualizer** (`src.visualization.penetration_visualizer`):
- `visualize_penetration_process()`: Creates comprehensive 4-panel analysis
- Panel 1: Angle of attack geometry with armor slope and thickness indicators
- Panel 2: Ammunition-specific penetration mechanism (kinetic rod, HEAT jet, HESH spalling)
- Panel 3: Behind-armor effects showing crew compartment damage assessment
- Panel 4: Summary statistics and penetration analysis
- Different visual effects for each ammunition type:
  - **Kinetic**: Long rod penetrators, sabot discard, armor fragmentation
  - **Chemical**: Shaped charge jets, molten metal effects, jet disruption
  - **Spalling**: Shock wave propagation, spall cones, fragment patterns

**Visualization Output**:
- Automatically saved as high-resolution PNG files
- Filename format: `penetration_[ammo]_[armor].png`, `trajectory_[ammo]_[range]m.png`
- Color-coded by armor type: RHA (gray), Composite (brown), Reactive (orange), Spaced (blue)
- Professional technical diagrams suitable for analysis and documentation

## Common Development Tasks

**Running a specific engagement:**
```python
# Example: 3BM60 vs 200mm RHA at 2000m, 30° impact
from src.ammunition import APFSDS
from src.armor import RHA

round = APFSDS("3BM60", 125.0, 24.0, 5.2, 1750, 600)  
armor = RHA(200.0)

penetration = round.calculate_penetration(2000.0, 30.0)  # 728mm RHA
effective = armor.get_effective_thickness("kinetic", 30.0)  # 231mm RHA  
result = armor.can_defeat(penetration, "kinetic", 30.0)  # False (penetrates)
```

**Debugging penetration calculations:**
- Check intermediate values: `get_velocity_at_range()`, `get_effective_thickness()`, protection factors
- Verify angle conventions (degrees vs radians)
- Confirm ammunition `penetration_type` matches armor `ammo_type` parameter

**Performance considerations:**
- Pure Python implementation - no performance bottlenecks for single calculations
- For bulk scenarios, consider vectorization with NumPy (listed in requirements.txt for future use)
- Calculation complexity is O(1) per engagement (no iterative solvers)
