# Tank Armor Penetration Simulator

A realistic simulation game that models tank armor penetration mechanics using various anti-tank ammunition types and armor configurations.

## Overview

This project simulates the complex physics of armor penetration, taking into account:
- Different ammunition types (APFSDS, HEAT, HESH, AP, etc.)
- Various armor configurations (RHA, composite, reactive, spaced)
- Penetration mechanics and ballistics
- Historical and modern tank specifications

## Features

- **Dual Interface**: Modern GUI and CLI modes for different user preferences
- **Realistic Ballistics**: Accurate modeling of projectile velocity, energy transfer, and penetration mechanics
- **Multiple Ammunition Types**: Support for various anti-tank rounds with different penetration characteristics
- **Diverse Armor Systems**: Different armor types with realistic protection values and angles
- **Advanced Visualizations**: 4-panel penetration analysis and ballistic trajectory plots
- **Comprehensive Comparisons**: Side-by-side ammunition and armor analysis tools
- **Interactive Simulation**: Both graphical and command-line interfaces for running tests
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
4. Run the simulation:
   - **GUI Mode (Recommended)**: `python launcher.py` or `python gui_main.py`
   - **CLI Mode**: `python launcher.py --cli` or `python main.py`

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

### GUI Mode (Recommended)
Launch the graphical interface:
```bash
python launcher.py
```

The GUI provides:
- Intuitive point-and-click interface
- Visual ammunition and armor catalogs
- Integrated visualization display
- Tabbed results with embedded charts
- Progress indicators and status updates

### CLI Mode (Advanced Users)
Run the command-line interface:
```bash
python launcher.py --cli
```

The CLI simulator will prompt you to:
1. Select ammunition type
2. Choose target armor configuration  
3. Set engagement parameters (range, angle, etc.)
4. View penetration results and analysis
5. Generate visualizations (saved as PNG files)

### Universal Launcher
The launcher automatically detects the best interface:
```bash
python launcher.py --help     # Show all options
python launcher.py --gui      # Force GUI mode
python launcher.py --cli      # Force CLI mode
```

## About This Project

This is an educational project created for learning purposes and testing WARP (warp.dev) AI development capabilities. The project demonstrates:
- Object-oriented design with inheritance hierarchies
- Physics simulation and mathematical modeling
- Interactive CLI development
- Historical data integration and validation

## Contributing

This project aims for historical accuracy and realistic physics modeling. Contributions should include:
- Proper documentation of sources for ballistic data
- Unit tests for new features
- Realistic parameter values based on historical data

## Disclaimer

This simulator is for educational and entertainment purposes only. It is based on publicly available historical data and should not be used for any military or defense applications. This project is a personal learning exercise and is not licensed for commercial or production use.
