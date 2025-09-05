# Tank Armor Penetration Simulator

A realistic simulation game that models tank armor penetration mechanics using various anti-tank ammunition types and armor configurations.

## Overview

This project simulates the complex physics of armor penetration, taking into account:
- Different ammunition types (APFSDS, HEAT, HESH, AP, etc.)
- Various armor configurations (RHA, composite, reactive, spaced)
- Penetration mechanics and ballistics
- Historical and modern tank specifications

## Features

- **Realistic Ballistics**: Accurate modeling of projectile velocity, energy transfer, and penetration mechanics
- **Multiple Ammunition Types**: Support for various anti-tank rounds with different penetration characteristics
- **Diverse Armor Systems**: Different armor types with realistic protection values and angles
- **Interactive Simulation**: Command-line interface for running penetration tests
- **Historical Data**: Based on real-world tank specifications and combat performance

## Ammunition Types

- **APFSDS** (Armor-Piercing Fin-Stabilized Discarding Sabot): High-velocity kinetic penetrators
- **HEAT** (High Explosive Anti-Tank): Chemical energy warheads
- **HESH** (High Explosive Squash Head): Spalling-based anti-armor rounds
- **AP** (Armor Piercing): Traditional solid shot rounds
- **APCR** (Armor-Piercing Composite Rigid): Sub-caliber rounds

## Armor Types

- **RHA** (Rolled Homogeneous Armor): Standard steel armor baseline
- **Composite Armor**: Multi-layered protection systems
- **Reactive Armor**: Explosive reactive armor (ERA) systems
- **Spaced Armor**: Air-gap protection configurations
- **Sloped Armor**: Angled armor effectiveness calculations

## Installation

1. Clone this repository
2. Install Python 3.8+
3. Install required dependencies: `pip install -r requirements.txt`
4. Run the simulation: `python main.py`

## Project Structure

```
tank-armor-sim/
├── src/
│   ├── ammunition/     # Ammunition type definitions
│   ├── armor/         # Armor system implementations
│   ├── physics/       # Penetration calculation engine
│   └── game/          # Game logic and UI
├── config/           # Configuration files for ammo/armor data
├── tests/           # Unit tests
├── docs/            # Documentation
└── main.py          # Main entry point
```

## Usage

Run the main simulation:
```bash
python main.py
```

The simulator will prompt you to:
1. Select ammunition type
2. Choose target armor configuration
3. Set engagement parameters (range, angle, etc.)
4. View penetration results and analysis

## Contributing

This project aims for historical accuracy and realistic physics modeling. Contributions should include:
- Proper documentation of sources for ballistic data
- Unit tests for new features
- Realistic parameter values based on historical data

## License

MIT License - See LICENSE file for details

## Disclaimer

This simulator is for educational and entertainment purposes only. It is based on publicly available historical data and should not be used for any military or defense applications.
