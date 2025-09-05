# Tank Armor Penetration Simulator

A comprehensive physics-based simulation that models tank armor penetration mechanics with both modern GUI and CLI interfaces.

## 🎯 Key Features

- **🖥️ Dual Interface**: Professional GUI and advanced CLI modes
- **⚗️ Advanced Physics**: Environmental ballistics, temperature effects, multi-hit damage, and ricochet analysis
- **📊 Professional Visualizations**: 4-panel penetration analysis and ballistic trajectory plots
- **🔬 Comprehensive Analysis**: Multi-item ammunition and armor comparisons with statistical summaries
- **📚 Educational Value**: Based on historical data with realistic physics modeling
- **🧪 Testing Suite**: Comprehensive test coverage with logging system for verification

## 💥 Ammunition & Armor Systems

**Ammunition**: APFSDS, HEAT, HESH, AP, APCR with realistic ballistic properties  
**Armor**: RHA, Composite, Reactive (ERA), Spaced configurations with proper protection modeling

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Launch GUI (recommended)
python launcher.py

# Or use CLI mode
python launcher.py --cli

# Run tests
python tests/run_tests.py
```

## 📷 Directory Structure

```
tank-armor-sim/
├── src/                  # Core simulation modules
├── tests/                # Comprehensive test suite  
├── config/               # Historical data
├── results/              # Generated visualizations
├── logs/                 # Session logs (gitignored)
├── launcher.py           # Universal launcher
├── gui_main.py          # GUI application
└── main.py              # CLI application
```

## 🗺️ Features Overview

**GUI Mode**: Point-and-click interface with embedded visualizations, progress tracking, and tabbed results  
**CLI Mode**: Interactive menus with full feature parity and advanced logging capabilities

**Core Functions**:
- Penetration testing with 4-panel analysis visualization
- Ballistic trajectory plotting with environmental effects
- Multi-item ammunition and armor comparisons
- Advanced physics demonstrations with logging
- Comprehensive catalogs with historical data

## 🎣 About

Educational simulation demonstrating advanced Python development, physics modeling, and GUI/CLI design. Features comprehensive testing, logging systems, and professional visualization capabilities.

---

**Disclaimer**: Educational purposes only. Based on publicly available historical data.
