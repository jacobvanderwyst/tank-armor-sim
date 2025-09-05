# Results Directory 📁

Generated visualization outputs from the Tank Armor Penetration Simulator.

## 📁 Directory Structure

- **`/animations/`** - Animated GIF files showing dynamic penetration processes
- **`/enhanced_3d/`** - Advanced 3D visualizations with interactive ballistic trajectories
- **Root Directory** - Standard 2D analysis charts and comparisons

## 📊 File Types

### Static Visualizations (PNG)
- **Penetration Analysis**: `penetration_[ammunition]_[armor].png` - 4-panel technical analysis
- **Ballistic Trajectory**: `trajectory_[ammunition]_[range]m.png` - Flight path with velocity decay
- **Comparison Charts**: `ammo_comparison_*` / `armor_comparison_*` - Multi-item analysis
- **Enhanced 3D**: `enhanced_3d/enhanced_3d_[ammunition]_[armor].png` - Interactive 3D scenarios

### Animated Visualizations (GIF)
- **Penetration Animations**: `animations/penetration_animation.gif` - Dynamic armor defeat process
- **Test Animations**: `animations/test_penetration_animation.gif` - Physics demonstration

### Interactive Datasets (JSON)
- **Enhanced 3D Dataset**: `enhanced_3d/enhanced_3d_[ammunition]_[armor].json`
  - Contains:
    - trajectory points
    - metadata: ammunition, armor, environment, parameters
    - impact_analysis: penetration results and overlays
      - per_part_sequence, channel_segments, residuals
      - overpenetration and exit_point (if applicable)
      - ricochet flags with ricochet_outcome (ricochet | shattering | embedding)
      - ricochet_point, ricochet_direction, ricochet_details (probability, deflection angle, exit velocity, energy retained)
    - assets: screenshot_png, cross_section_png

To view interactively:
- CLI: `python interactive_viewer.py results/enhanced_3d/enhanced_3d_<...>.json [--animate] [--no-channels] [--no-ricochet]`
- GUI: Menu → "Open Interactive Result" and select the JSON file

Overlay toggles:
- In the GUI Settings, you can toggle visibility of penetration channels and ricochet overlays.
- In the CLI viewer, use `--no-channels` to hide channels and `--no-ricochet` to hide ricochet overlays.

**Format**: 300 DPI PNG files, high-quality GIF animations, and JSON datasets for interactive playback
