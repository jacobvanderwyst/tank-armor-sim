# Technical Documentation

## 🏗️ Architecture

### Core Modules
- **`src/ammunition/`** - APFSDS, HEAT, HESH, AP, APCR classes with realistic ballistics
- **`src/armor/`** - RHA, Composite, Reactive, Spaced armor with protection modeling  
- **`src/physics/`** - Advanced physics engine with environmental effects, temperature, ricochet, and damage systems
- **`src/visualization/`** - Professional matplotlib-based plotting and analysis tools

### Advanced Physics Features ⚗️
- **Environmental Ballistics**: Altitude, temperature, humidity, and wind effects
- **Temperature Effects**: Propellant performance and material property variations  
- **Ricochet Calculations**: Angle-dependent probability with deflection modeling
- **Multi-Hit Damage**: Progressive armor degradation with material-specific responses
- **Behind-Armor Effects**: Spall and fragment analysis

### Testing & Verification 🧪
- **`tests/`** - Comprehensive test suite with 4+ test modules
- **Logging System** - Detailed session tracking with JSON output and verification logs
- **Integration Tests** - End-to-end testing with real ammunition/armor objects
- **Performance Metrics** - Calculation timing and accuracy validation

## 🔧 Development

### Class Hierarchy
```python
# Ammunition inheritance
BaseAmmunition → KineticAmmunition (APFSDS, AP, APCR)  
              → ChemicalAmmunition (HEAT, HESH)

# Armor inheritance  
BaseArmor → SteelArmor (RHA)
         → CompositeArmor, ReactiveArmor, SpacedArmor

# Physics integration via enable_advanced_physics()
ammo.calculate_advanced_penetration(armor, range, angle, env_conditions, temp_conditions, ricochet_params)
```

### Key Methods
- **Penetration**: `calculate_penetration(range_m, angle_deg)` → mm RHA equivalent
- **Ballistics**: `get_velocity_at_range(range_m)` with drag modeling  
- **Armor**: `get_effective_thickness(ammo_type, angle)` → effective protection
- **Damage**: `apply_damage_from_impact()` with progressive degradation

### Configuration
- **`config/`** - Historical data in JSON format for validation
- **Units**: mm (length), kg (mass), m/s (velocity), degrees (angles)
- **Formulas**: DeMarre-based kinetic, Monroe effect HEAT, spalling HESH

## 📊 Visualization System

### Plot Types
- **4-Panel Penetration**: Geometry, mechanism, behind-armor effects, summary
- **Ballistic Trajectory**: Flight path with velocity decay and environmental effects
- **Comparison Charts**: Multi-item ammunition/armor effectiveness analysis
- **Advanced Physics**: Environmental and temperature effect visualizations

### Output Quality
- **300 DPI PNG** files suitable for technical documentation
- **Professional formatting** with color coding and technical annotations
- **Interactive matplotlib** integration with zoom, pan, save capabilities
- **Batch operations** for comprehensive analysis workflows

## 🔬 Physics Models

### Penetration Calculations
- **APFSDS**: `(velocity/1000)^1.43 × diameter × 25 × LD_factor × angle_factor`
- **HEAT**: `caliber × 6.0 × cos(angle)² × explosive_factor × standoff_factor`  
- **HESH**: `explosive_mass × 200 × angle_factor × velocity_factor`

### Environmental Effects
- **Temperature**: -30°C to +50°C propellant efficiency modeling
- **Altitude**: 0-3000m air density effects on ballistics
- **Humidity**: 20-90% atmospheric drag variations
- **Wind**: Lateral deflection and trajectory correction

### Advanced Features
- **Ricochet Envelope**: Critical angle calculations with material hardness
- **Progressive Damage**: Multi-hit scenarios with integrity tracking
- **Material Response**: Type-specific failure modes and thresholds

---

**For detailed implementation notes, see source code documentation and test suite examples.**
