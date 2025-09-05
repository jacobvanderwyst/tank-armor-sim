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

## 🧊 Enhanced 3D Visualization (New)

- Interactive 3D view with accurate ballistic trajectory rendering
- Multi-part mesh penetration channels with per-part residuals and costs
- Overpenetration exit markers and behind-armor spall cone for kinetic rounds
- Ricochet modeling with outcomes: ricochet, shattering, embedding
- Cross-section rendering at impact showing armor stack and penetration channel
- Export/import of interactive datasets to replay visualizations without recompute

GUI usage:
- In the main menu, click "Enhanced 3D Viz" to generate a scene.
- Use Settings → Overlay visibility to toggle:
  - Show penetration channel overlays
  - Show ricochet overlays
- Use "Open Interactive Result" to load a saved dataset JSON.

CLI viewer usage:
- python interactive_viewer.py results/enhanced_3d/enhanced_3d_<...>.json [--animate] [--no-channels] [--no-ricochet]

Interactive dataset fields (excerpt):
```json
{
  "type": "enhanced_3d_result",
  "trajectory": [ /* points with x,y,z,v,time,air */ ],
  "impact_analysis": {
    "penetrates": true,
    "penetration_mm": 320.0,
    "per_part_sequence": [ /* per-part segments */ ],
    "channel_segments": [
      {"part": "hull", "start": {"x":5.0,"y":0.0,"z":1.0}, "end": {"x":5.1,"y":0.0,"z":0.8}, "partial": false}
    ],
    "overpenetration": false,
    "ricochet": true,
    "ricochet_outcome": "ricochet",  // or "shattering" | "embedding"
    "ricochet_point": {"x":5.0, "y":0.0, "z":1.0},
    "ricochet_direction": {"x":0.9, "y":0.1, "z":0.0},
    "ricochet_details": {
      "probability": 0.68,
      "deflection_angle_deg": 22.0,
      "exit_velocity_ms": 820.0,
      "energy_retained": 0.62
    }
  },
  "assets": {
    "screenshot_png": "results/enhanced_3d/...png",
    "cross_section_png": "results/enhanced_3d/..._cross_section.png"
  }
}
```

Tests covering these features:
- tests/enhanced_3d/test_ricochet_and_channels.py
- tests/enhanced_3d/test_cross_section_and_gui_toggles.py

## 🎣 About

Educational simulation demonstrating advanced Python development, physics modeling, and GUI/CLI design. Features comprehensive testing, logging systems, and professional visualization capabilities.

---

**Disclaimer**: Educational purposes only. Based on publicly available historical data.
