#!/usr/bin/env python3
"""
Tank Armor Penetration Simulator - GUI Version

A modern graphical interface for the tank armor penetration simulation system.
Provides intuitive access to all simulator features while maintaining the
underlying physics accuracy of the CLI version.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
import threading
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ammunition import APFSDS, AP, APCR, HEAT, HESH
from src.armor import RHA, CompositeArmor, ReactiveArmor, SpacedArmor
from src.visualization import BallisticsVisualizer, PenetrationVisualizer, ComparisonVisualizer
from logging_system import get_logger
from typing import Dict, Any, Optional, List
from gui_dialogs import PenetrationTestDialog, TrajectoryDialog, ComparisonDialog


class TankArmorSimulatorGUI:
    """Main GUI application for the Tank Armor Penetration Simulator."""
    
    def __init__(self):
        """Initialize the GUI application."""
        self.root = tk.Tk()
        self.setup_main_window()
        self.setup_style()
        self.create_ammunition_catalog()
        self.create_armor_catalog()
        self.create_main_interface()
        
    def setup_main_window(self):
        """Configure the main application window."""
        self.root.title("Tank Armor Penetration Simulator")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Set window icon (if available)
        try:
            # You could add an icon file here
            # self.root.iconbitmap('icon.ico')
            pass
        except:
            pass
        
        # Configure grid weights for responsive design
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
    
    def setup_style(self):
        """Configure modern styling for the application."""
        self.style = ttk.Style()
        
        # Try to use a modern theme
        available_themes = self.style.theme_names()
        if 'vista' in available_themes:
            self.style.theme_use('vista')
        elif 'clam' in available_themes:
            self.style.theme_use('clam')
        
        # Configure custom styles
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        self.style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'))
        self.style.configure('Header.TLabel', font=('Arial', 10, 'bold'))
        self.style.configure('Large.TButton', font=('Arial', 11))
        
        # Color scheme
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72', 
            'success': '#F18F01',
            'background': '#F5F5F5',
            'text': '#2D3748'
        }
    
    def create_ammunition_catalog(self):
        """Create the ammunition catalog (same as CLI version)."""
        self.ammunition_catalog = [
            APFSDS(
                name="M829A4 APFSDS",
                caliber=120.0,
                penetrator_diameter=22.0,
                penetrator_mass=4.6,
                muzzle_velocity=1680,
                penetrator_length=570
            ),
            APFSDS(
                name="3BM60 Svinets-2",
                caliber=125.0,
                penetrator_diameter=24.0,
                penetrator_mass=5.2,
                muzzle_velocity=1750,
                penetrator_length=600
            ),
            HEAT(
                name="M830A1 HEAT-MP",
                caliber=120.0,
                warhead_mass=18.6,
                explosive_mass=2.4,
                standoff_distance=150
            ),
            HEAT(
                name="3BK29 HEAT",
                caliber=125.0,
                warhead_mass=19.8,
                explosive_mass=2.8,
                standoff_distance=180
            ),
            HESH(
                name="L31A7 HESH",
                caliber=120.0,
                shell_mass=17.2,
                explosive_mass=4.1
            ),
            AP(
                name="M72 AP Shot",
                caliber=76.0,
                mass=6.8,
                muzzle_velocity=792
            )
        ]
    
    def create_armor_catalog(self):
        """Create the armor catalog (same as CLI version)."""
        self.armor_catalog = [
            RHA(thickness=100.0),
            RHA(thickness=200.0),
            CompositeArmor(
                name="M1A2 Frontal Armor",
                thickness=650.0,
                steel_layers=200.0,
                ceramic_layers=350.0,
                other_layers=100.0
            ),
            ReactiveArmor(
                name="T-90M with Relikt ERA",
                base_thickness=500.0,
                era_thickness=45.0,
                explosive_mass=0.8
            ),
            SpacedArmor(
                name="Leopard 2A7 Side Armor",
                front_plate=35.0,
                rear_plate=70.0,
                spacing=150.0
            ),
            CompositeArmor(
                name="Challenger 2 Dorchester",
                thickness=800.0,
                steel_layers=250.0,
                ceramic_layers=450.0,
                other_layers=100.0
            )
        ]
    
    def create_main_interface(self):
        """Create the main GUI interface."""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Left panel - Menu
        self.create_menu_panel(main_container)
        
        # Right panel - Content area
        self.create_content_area(main_container)
        
        # Status bar
        self.create_status_bar()
        
        # Show welcome screen initially
        self.show_welcome_screen()
    
    def create_menu_panel(self, parent):
        """Create the left menu panel."""
        menu_frame = ttk.Frame(parent, style='Card.TFrame')
        menu_frame.grid(row=0, column=0, sticky='ns', padx=(0, 10))
        
        # Title
        title_label = ttk.Label(menu_frame, text="Tank Armor\nPenetration\nSimulator", 
                               style='Title.TLabel', justify='center')
        title_label.pack(pady=(20, 30))
        
        # Menu buttons
        buttons = [
            ("Run Penetration Test", self.run_penetration_test),
            ("Penetration + Viz", self.run_penetration_with_viz),
            ("Ballistic Trajectory", self.view_ballistic_trajectory),
            ("Compare Ammunition", self.compare_ammunition),
            ("Compare Armor", self.compare_armor),
            ("Advanced Physics Demo", self.demonstrate_advanced_physics),
            ("Ammunition Catalog", self.view_ammunition_catalog),
            ("Armor Catalog", self.view_armor_catalog),
            ("Help & Documentation", self.show_help),
            ("About", self.show_about)
        ]
        
        self.menu_buttons = {}
        for text, command in buttons:
            btn = ttk.Button(menu_frame, text=text, command=command, 
                           style='Large.TButton', width=20)
            btn.pack(pady=5, padx=10, fill='x')
            self.menu_buttons[text] = btn
        
        # Exit button
        exit_btn = ttk.Button(menu_frame, text="Exit", command=self.root.quit, 
                            style='Large.TButton', width=20)
        exit_btn.pack(side='bottom', pady=20, padx=10, fill='x')
    
    def create_content_area(self, parent):
        """Create the main content area."""
        self.content_frame = ttk.Frame(parent)
        self.content_frame.grid(row=0, column=1, sticky='nsew')
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.grid(row=0, column=0, sticky='nsew', pady=(0, 10))
    
    def create_status_bar(self):
        """Create the bottom status bar."""
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=(0, 5))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side='left')
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, 
                                          maximum=100, length=200)
        self.progress_bar.pack(side='right', padx=(10, 0))
    
    def show_welcome_screen(self):
        """Display the welcome screen."""
        welcome_frame = ttk.Frame(self.notebook)
        self.notebook.add(welcome_frame, text="Welcome")
        
        # Welcome content
        welcome_label = ttk.Label(welcome_frame, 
                                 text="Tank Armor Penetration Simulator", 
                                 style='Title.TLabel')
        welcome_label.pack(pady=20)
        
        description = """
Welcome to the Tank Armor Penetration Simulator!

This advanced simulation tool models realistic armor penetration mechanics
using various anti-tank ammunition types and armor configurations.

Features:
• Realistic ballistics and penetration physics
• Multiple ammunition types (APFSDS, HEAT, HESH, AP, APCR)
• Diverse armor systems (RHA, Composite, Reactive, Spaced)
• Advanced visualization and comparison tools
• Historical and modern tank specifications

Select an option from the menu to get started.
        """
        
        desc_label = ttk.Label(welcome_frame, text=description, justify='left')
        desc_label.pack(pady=20, padx=40)
        
        # Quick start buttons
        quick_frame = ttk.Frame(welcome_frame)
        quick_frame.pack(pady=20)
        
        ttk.Button(quick_frame, text="Quick Penetration Test", 
                  command=self.run_penetration_test).pack(side='left', padx=10)
        ttk.Button(quick_frame, text="View Visualizations", 
                  command=self.run_penetration_with_viz).pack(side='left', padx=10)
    
    # GUI functionality methods
    def run_penetration_test(self):
        """Run a penetration test."""
        self.status_var.set("Opening penetration test...")
        self.open_penetration_test_dialog()
    
    
    def view_ammunition_catalog(self):
        """View ammunition catalog."""
        self.show_catalog("Ammunition Catalog", self.ammunition_catalog, self.get_ammo_info)
    
    def view_armor_catalog(self):
        """View armor catalog."""
        self.show_catalog("Armor Catalog", self.armor_catalog, self.get_armor_info)
    
    def show_catalog(self, title, catalog, info_func):
        """Show a catalog in a new tab."""
        # Remove existing tab with same name
        for tab in self.notebook.tabs():
            if self.notebook.tab(tab, "text") == title:
                self.notebook.forget(tab)
                break
        
        catalog_frame = ttk.Frame(self.notebook)
        self.notebook.add(catalog_frame, text=title)
        self.notebook.select(catalog_frame)
        
        # Create treeview for catalog
        columns = ('Name', 'Type', 'Key Specs', 'Details')
        tree = ttk.Treeview(catalog_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        tree.heading('Name', text='Name')
        tree.heading('Type', text='Type')
        tree.heading('Key Specs', text='Key Specifications')
        tree.heading('Details', text='Details')
        
        tree.column('Name', width=200)
        tree.column('Type', width=100)
        tree.column('Key Specs', width=200)
        tree.column('Details', width=300)
        
        # Populate catalog
        for item in catalog:
            name = item.name
            info = info_func(item)
            tree.insert('', 'end', values=(name, info['type'], info['specs'], info['details']))
        
        tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(catalog_frame, orient='vertical', command=tree.yview)
        scrollbar.pack(side='right', fill='y')
        tree.configure(yscrollcommand=scrollbar.set)
        
        self.status_var.set(f"{title} loaded")
    
    def get_ammo_info(self, ammo):
        """Get ammunition information for catalog display."""
        return {
            'type': ammo.penetration_type.upper(),
            'specs': f"{ammo.caliber:.0f}mm, {ammo.muzzle_velocity} m/s, {ammo.mass:.1f}kg",
            'details': f"Kinetic Energy: {ammo.kinetic_energy/1000:.0f} kJ"
        }
    
    def get_armor_info(self, armor):
        """Get armor information for catalog display."""
        return {
            'type': armor.armor_type.upper(),
            'specs': f"{armor.thickness:.0f}mm thick, {armor.density:.0f} kg/m³",
            'details': f"Mass per area: {armor.mass_per_area:.0f} kg/m²"
        }
    
    def show_help(self):
        """Show help documentation."""
        help_window = tk.Toplevel(self.root)
        help_window.title("Help & Documentation")
        help_window.geometry("800x600")
        
        help_text = """
Tank Armor Penetration Simulator - Help & Documentation

AMMUNITION TYPES:
• APFSDS (Armor-Piercing Fin-Stabilized Discarding Sabot): High-velocity kinetic penetrators
• HEAT (High Explosive Anti-Tank): Chemical energy warheads using shaped charges
• HESH (High Explosive Squash Head): Spalling-based anti-armor rounds
• AP (Armor Piercing): Traditional solid shot rounds
• APCR (Armor-Piercing Composite Rigid): Sub-caliber rounds with hard cores

ARMOR TYPES:
• RHA (Rolled Homogeneous Armor): Standard steel armor baseline
• Composite Armor: Multi-layered protection systems with ceramics
• Reactive Armor: Explosive reactive armor (ERA) systems
• Spaced Armor: Air-gap protection configurations

PHYSICS CONCEPTS:
• Penetration is calculated using realistic ballistic formulas
• Impact angle affects both projectile performance and armor effectiveness
• Different ammunition types have different defeat mechanisms
• Range affects projectile velocity and penetration capability

USING THE SIMULATOR:
1. Select ammunition and armor from the catalogs
2. Set engagement parameters (range and impact angle)
3. View results with optional visualizations
4. Compare multiple options using comparison tools

For more detailed information, refer to the technical documentation.
        """
        
        text_widget = tk.Text(help_window, wrap='word', padx=20, pady=20)
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', help_text)
        text_widget.config(state='disabled')
        
        scrollbar = ttk.Scrollbar(help_window, command=text_widget.yview)
        scrollbar.pack(side='right', fill='y')
        text_widget.config(yscrollcommand=scrollbar.set)
    
    def show_about(self):
        """Show about dialog."""
        about_text = """
Tank Armor Penetration Simulator
Version 2.0 - GUI Edition

An educational simulation tool for understanding armor penetration mechanics.

Features realistic physics modeling, advanced visualizations, and comprehensive
comparison capabilities for various ammunition and armor systems.

This project is for educational and entertainment purposes only.
Based on publicly available historical data.

Built with Python, tkinter, matplotlib, and numpy.
        """
        
        messagebox.showinfo("About Tank Armor Penetration Simulator", about_text)
    
    def run_penetration_test(self):
        """Run basic penetration test."""
        self.open_penetration_test_dialog()
    
    def open_penetration_test_dialog(self):
        """Open penetration test parameter dialog."""
        dialog = PenetrationTestDialog(self.root, self.ammunition_catalog, self.armor_catalog)
        result = dialog.show()
        
        if result:
            ammo, armor, range_m, angle, with_viz = result
            self.execute_penetration_test(ammo, armor, range_m, angle, with_viz)
    
    def execute_penetration_test(self, ammo, armor, range_m, angle, with_viz=False):
        """Execute penetration test and display results with advanced physics."""
        self.status_var.set("Calculating penetration with advanced physics...")
        self.progress_var.set(25)
        self.root.update_idletasks()
        
        # Initialize logging
        logger = get_logger()
        
        # Enable advanced physics by default
        ammo.enable_advanced_physics()
        armor.enable_advanced_physics()
        
        # Set up advanced physics conditions
        try:
            from src.physics.advanced_physics import EnvironmentalConditions
            from src.physics.temperature_effects import TemperatureConditions
            from src.physics.ricochet_calculator import RicochetParameters
            
            # Standard conditions (can be made configurable later)
            env_conditions = EnvironmentalConditions(
                temperature_celsius=15.0,  # Standard temperature
                altitude_m=0.0,
                humidity_percent=50.0
            )
            
            temp_conditions = TemperatureConditions(
                ambient_celsius=15.0,
                propellant_celsius=15.0,
                armor_celsius=15.0,
                barrel_celsius=15.0
            )
            
            velocity_at_impact = ammo.get_velocity_at_range(range_m)
            ricochet_params = RicochetParameters(
                impact_angle_deg=angle,
                impact_velocity_ms=velocity_at_impact,
                projectile_hardness=0.9,
                target_hardness=0.8
            )
            
            # Calculate advanced results
            advanced_results = ammo.calculate_advanced_penetration(
                armor, range_m, angle,
                environmental_conditions=env_conditions,
                temperature_conditions=temp_conditions,
                ricochet_params=ricochet_params
            )
            
            # Use advanced results
            penetration = advanced_results['final_penetration']
            velocity_at_impact = advanced_results['velocity_at_target']
            
        except ImportError:
            # Fallback to basic calculations if advanced physics not available
            self.status_var.set("Advanced physics not available, using basic calculations...")
            penetration = ammo.calculate_penetration(range_m, angle)
            velocity_at_impact = ammo.get_velocity_at_range(range_m)
            advanced_results = None
        
        effective_thickness = armor.get_effective_thickness(ammo.penetration_type, angle)
        can_defeat = armor.can_defeat(penetration, ammo.penetration_type, angle)
        
        self.progress_var.set(75)
        self.root.update_idletasks()
        
        # Create results tab with advanced physics data
        self.show_penetration_results(ammo, armor, range_m, angle, penetration, 
                                    effective_thickness, velocity_at_impact, can_defeat,
                                    advanced_results)
        
        # Generate visualization if requested
        if with_viz:
            self.status_var.set("Generating visualization...")
            self.progress_var.set(90)
            
            try:
                pen_visualizer = PenetrationVisualizer()
                pen_fig = pen_visualizer.visualize_penetration_process(ammo, armor, range_m, angle)
                
                # Show visualization in GUI
                self.show_visualization_in_tab(pen_fig, f"Penetration Analysis: {ammo.name} vs {armor.name}")
                
                # Save plot
                filename = f'penetration_{ammo.name.replace(" ", "_")}_{armor.name.replace(" ", "_")}.png'
                pen_visualizer.save_plot(filename)
                
            except Exception as e:
                messagebox.showerror("Visualization Error", f"Error generating visualization: {e}")
        
        # Log the penetration test results
        result_text = "ARMOR_DEFEATS" if can_defeat else "PROJECTILE_PENETRATES"
        logger.log_penetration_test(
            ammunition_name=ammo.name,
            armor_name=armor.name,
            angle=angle,
            distance=range_m,
            penetration=penetration,
            effective_thickness=effective_thickness,
            result=result_text,
            advanced_results=advanced_results
        )
        
        self.progress_var.set(100)
        self.status_var.set("Penetration test complete")
        
        # Reset progress after a delay
        self.root.after(2000, lambda: self.progress_var.set(0))
    
    def show_penetration_results(self, ammo, armor, range_m, angle, penetration, 
                               effective_thickness, velocity, can_defeat, advanced_results=None):
        """Show penetration test results in a new tab with advanced physics data."""
        tab_name = f"Results: {ammo.name.split()[0]} vs {armor.name.split()[0]}"
        
        # Remove existing tab with same name
        for tab in self.notebook.tabs():
            if self.notebook.tab(tab, "text") == tab_name:
                self.notebook.forget(tab)
                break
        
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text=tab_name)
        self.notebook.select(results_frame)
        
        # Create scrollable text widget
        text_frame = ttk.Frame(results_frame)
        text_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        text_widget = tk.Text(text_frame, wrap='word', font=('Consolas', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Format results text
        margin = abs(penetration - effective_thickness)
        margin_type = 'Safety Margin' if can_defeat else 'Overmatch'
        result_symbol = '❌ ARMOR DEFEATS PROJECTILE' if can_defeat else '✅ PROJECTILE PENETRATES ARMOR'
        
        # Build results text with advanced physics information
        results_text = f"""
═══════════════════════════════════════════════════════════════
              PENETRATION TEST RESULTS (ADVANCED PHYSICS)
═══════════════════════════════════════════════════════════════

AMMUNITION: {ammo.name}
  Type: {ammo.penetration_type.upper()}
  Caliber: {ammo.caliber:.0f}mm
  Muzzle Velocity: {ammo.muzzle_velocity} m/s
  Mass: {ammo.mass:.1f} kg

ARMOR: {armor.name}
  Type: {armor.armor_type.upper()}
  Thickness: {armor.thickness:.0f}mm
  Density: {armor.density:.0f} kg/m³

ENGAGEMENT:
  Range: {range_m:.0f} m
  Impact Angle: {angle:.1f}°
  Impact Velocity: {velocity:.0f} m/s

CALCULATIONS:
  Penetration Capability: {penetration:.1f} mm RHA
  Effective Armor Thickness: {effective_thickness:.1f} mm RHA
  {margin_type}: {margin:.1f} mm RHA

RESULT:
  {result_symbol}
"""
        
        # Add advanced physics details if available
        if advanced_results:
            results_text += "\n--- ADVANCED PHYSICS ANALYSIS ---\n"
            
            if advanced_results.get('base_penetration'):
                results_text += f"  Base Penetration: {advanced_results['base_penetration']:.1f} mm RHA\n"
                results_text += f"  Enhanced Penetration: {advanced_results['final_penetration']:.1f} mm RHA\n"
            
            if advanced_results.get('ricochet_analysis'):
                ricochet = advanced_results['ricochet_analysis']
                results_text += f"\nRicochet Analysis:\n"
                results_text += f"  Ricochet Probability: {ricochet.get('ricochet_probability', 0)*100:.1f}%\n"
                results_text += f"  Predicted Outcome: {ricochet.get('predicted_outcome', 'N/A').upper()}\n"
                results_text += f"  Critical Angle: {ricochet.get('critical_angle', 0):.1f}°\n"
            
            if advanced_results.get('temperature_analysis'):
                temp = advanced_results['temperature_analysis']
                results_text += f"\nTemperature Effects:\n"
                results_text += f"  Velocity Modifier: {temp.get('velocity_modifier', 1.0):.3f}\n"
                results_text += f"  Penetration Modifier: {temp.get('penetration_modifier', 1.0):.3f}\n"
                results_text += f"  Propellant Efficiency: {temp.get('propellant_efficiency', 1.0):.3f}\n"
            
            if advanced_results.get('advanced_effects'):
                effects = advanced_results['advanced_effects'].get('ballistic_result')
                if effects and hasattr(effects, 'environmental_effects'):
                    env_effects = effects.environmental_effects
                    results_text += f"\nEnvironmental Effects:\n"
                    results_text += f"  Temperature: {env_effects.get('temperature_effect', 0)*100:+.1f}%\n"
                    results_text += f"  Altitude: {env_effects.get('altitude_effect', 0)*100:+.1f}%\n"
                    results_text += f"  Humidity: {env_effects.get('humidity_effect', 0)*100:+.1f}%\n"
        
        results_text += "\n═══════════════════════════════════════════════════════════════"
        
        text_widget.insert('1.0', results_text)
        text_widget.config(state='disabled')
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def show_visualization_in_tab(self, figure, tab_name):
        """Show matplotlib figure in a new tab."""
        # Remove existing tab with same name
        for tab in self.notebook.tabs():
            if self.notebook.tab(tab, "text") == tab_name:
                self.notebook.forget(tab)
                break
        
        viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(viz_frame, text=tab_name)
        self.notebook.select(viz_frame)
        
        # Create matplotlib canvas
        canvas = FigureCanvasTkAgg(figure, viz_frame)
        canvas.draw()
        
        # Add toolbar first
        toolbar = NavigationToolbar2Tk(canvas, viz_frame)
        toolbar.update()
        toolbar.pack(side='top', fill='x')
        
        # Then add canvas
        canvas.get_tk_widget().pack(side='bottom', fill='both', expand=True)
        
        # Maximize the main window for better visualization viewing
        try:
            if self.root.state() == 'normal':
                self.root.state('zoomed')  # Windows maximize
        except:
            try:
                self.root.attributes('-zoomed', True)  # Linux maximize
            except:
                pass  # Fallback for other systems
    
    def run_penetration_with_viz(self):
        """Run penetration test with visualization."""
        self.status_var.set("Opening penetration test with visualization...")
        dialog = PenetrationTestDialog(self.root, self.ammunition_catalog, self.armor_catalog, with_viz=True)
        result = dialog.show()
        
        if result:
            ammo, armor, range_m, angle, with_viz = result
            self.execute_penetration_test(ammo, armor, range_m, angle, True)
    
    def view_ballistic_trajectory(self):
        """View ballistic trajectory."""
        self.status_var.set("Opening trajectory viewer...")
        dialog = TrajectoryDialog(self.root, self.ammunition_catalog, self.armor_catalog)
        result = dialog.show()
        
        if result:
            ammo, armor, range_m, angle, show_velocity = result
            self.generate_trajectory_visualization(ammo, armor, range_m, angle, show_velocity)
    
    def generate_trajectory_visualization(self, ammo, armor, range_m, angle, show_velocity):
        """Generate and display ballistic trajectory."""
        self.status_var.set("Generating trajectory visualization...")
        self.progress_var.set(50)
        
        try:
            ballistics_viz = BallisticsVisualizer()
            traj_fig = ballistics_viz.visualize_flight_path(ammo, armor, range_m, angle, show_velocity)
            
            # Show visualization in GUI
            tab_name = f"Trajectory: {ammo.name.split()[0]} at {range_m}m"
            self.show_visualization_in_tab(traj_fig, tab_name)
            
            # Save plot
            filename = f'trajectory_{ammo.name.replace(" ", "_")}_{range_m}m.png'
            ballistics_viz.save_plot(filename)
            
            self.progress_var.set(100)
            self.status_var.set("Trajectory visualization complete")
            
        except Exception as e:
            messagebox.showerror("Visualization Error", f"Error generating trajectory: {e}")
            self.status_var.set("Error generating trajectory")
        
        # Reset progress after delay
        self.root.after(2000, lambda: self.progress_var.set(0))
    
    def compare_ammunition(self):
        """Compare ammunition types."""
        self.status_var.set("Opening ammunition comparison...")
        dialog = ComparisonDialog(self.root, "ammunition", self.ammunition_catalog, self.armor_catalog)
        result = dialog.show()
        
        if result:
            items, target, comparison_type = result
            self.generate_comparison_visualization(items, target, comparison_type)
    
    def compare_armor(self):
        """Compare armor types."""
        self.status_var.set("Opening armor comparison...")
        dialog = ComparisonDialog(self.root, "armor", self.ammunition_catalog, self.armor_catalog)
        result = dialog.show()
        
        if result:
            items, target, comparison_type = result
            self.generate_comparison_visualization(items, target, comparison_type)
    
    def generate_comparison_visualization(self, items, target, comparison_type):
        """Generate and display comparison visualization."""
        self.status_var.set(f"Generating {comparison_type} comparison...")
        self.progress_var.set(50)
        
        try:
            comparison_viz = ComparisonVisualizer()
            
            if comparison_type == "ammunition":
                comp_fig = comparison_viz.compare_ammunition(items, target)
                tab_name = f"Ammo Comparison vs {target.name.split()[0]}"
                names = [ammo.name.split()[0] for ammo in items[:3]]
                filename = f'ammo_comparison_{"-".join(names)}_{target.name.replace(" ", "_")}.png'
            else:
                comp_fig = comparison_viz.compare_armor(items, target)
                tab_name = f"Armor Comparison vs {target.name.split()[0]}"
                names = [armor.name.split()[0] for armor in items[:3]]
                filename = f'armor_comparison_{"-".join(names)}_{target.name.replace(" ", "_")}.png'
            
            # Show visualization in GUI
            self.show_visualization_in_tab(comp_fig, tab_name)
            
            # Save plot
            comparison_viz.save_plot(filename)
            
            self.progress_var.set(100)
            self.status_var.set(f"{comparison_type.title()} comparison complete")
            
        except Exception as e:
            messagebox.showerror("Comparison Error", f"Error generating comparison: {e}")
            self.status_var.set(f"Error generating {comparison_type} comparison")
        
        # Reset progress after delay
        self.root.after(2000, lambda: self.progress_var.set(0))
    
    def demonstrate_advanced_physics(self):
        """Demonstrate advanced physics features in GUI."""
        self.status_var.set("Loading advanced physics demonstration...")
        
        # Check if advanced physics modules are available
        try:
            from src.physics.advanced_physics import AdvancedPhysicsEngine, EnvironmentalConditions
            from src.physics.temperature_effects import TemperatureEffects, TemperatureConditions
            from src.physics.ricochet_calculator import RicochetCalculator, RicochetParameters
            from src.physics.damage_system import ArmorDamageSystem
        except ImportError as e:
            messagebox.showerror("Advanced Physics Error", 
                               f"Advanced physics modules not available: {e}")
            self.status_var.set("Error loading advanced physics")
            return
        
        self.progress_var.set(25)
        
        # Create demonstration tab
        tab_name = "Advanced Physics Demo"
        
        # Remove existing tab with same name
        for tab in self.notebook.tabs():
            if self.notebook.tab(tab, "text") == tab_name:
                self.notebook.forget(tab)
                break
        
        demo_frame = ttk.Frame(self.notebook)
        self.notebook.add(demo_frame, text=tab_name)
        self.notebook.select(demo_frame)
        
        # Create scrollable text widget
        text_frame = ttk.Frame(demo_frame)
        text_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        text_widget = tk.Text(text_frame, wrap='word', font=('Consolas', 9))
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Generate advanced physics demonstration
        demo_text = self._generate_advanced_physics_demo()
        
        text_widget.insert('1.0', demo_text)
        text_widget.config(state='disabled')
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.progress_var.set(100)
        self.status_var.set("Advanced physics demonstration complete")
        
        # Reset progress after delay
        self.root.after(2000, lambda: self.progress_var.set(0))
    
    def _generate_advanced_physics_demo(self):
        """Generate advanced physics demonstration text."""
        import random
        from src.physics.advanced_physics import AdvancedPhysicsEngine, EnvironmentalConditions
        from src.physics.temperature_effects import TemperatureEffects, TemperatureConditions
        from src.physics.ricochet_calculator import RicochetCalculator, RicochetParameters
        
        # Select test ammunition and armor
        ammo = self.ammunition_catalog[0]  # M829A4 APFSDS
        armor = self.armor_catalog[1]      # 200mm RHA
        
        # Enable advanced physics
        ammo.enable_advanced_physics()
        armor.enable_advanced_physics()
        
        demo_text = """
═══════════════════════════════════════════════════════════════
                    ADVANCED PHYSICS DEMONSTRATION
═══════════════════════════════════════════════════════════════

This demonstration showcases the advanced physics engine featuring:
• Complex environmental ballistics
• Multi-hit armor damage accumulation
• Ricochet probability analysis
• Temperature effects on performance

"""
        
        # Test setup
        range_m = 2000.0
        angle = 15.0
        
        demo_text += f"""TEST SETUP:
  Ammunition: {ammo.name}
  Target: {armor.name}
  Range: {range_m:.0f}m
  Impact Angle: {angle}°

"""
        
        # Standard calculation
        base_pen = ammo.calculate_penetration(range_m, angle)
        base_vel = ammo.get_velocity_at_range(range_m)
        eff_thickness = armor.get_effective_thickness(ammo.penetration_type, angle)
        
        demo_text += f"""--- STANDARD CALCULATION ---
Penetration capability: {base_pen:.1f} mm RHA
Velocity at target: {base_vel:.1f} m/s
Effective armor thickness: {eff_thickness:.1f} mm RHA
Result: {'ARMOR DEFEATS PROJECTILE' if base_pen < eff_thickness else 'PROJECTILE PENETRATES'}

"""
        
        # Advanced physics calculation
        env_conditions = EnvironmentalConditions(
            temperature_celsius=45.0,
            altitude_m=1500.0,
            humidity_percent=20.0,
            wind_speed_ms=10.0
        )
        
        temp_conditions = TemperatureConditions(
            ambient_celsius=45.0,
            propellant_celsius=50.0,
            armor_celsius=55.0,
            barrel_celsius=40.0
        )
        
        ricochet_params = RicochetParameters(
            impact_angle_deg=angle,
            impact_velocity_ms=base_vel,
            projectile_hardness=0.9,
            target_hardness=0.8
        )
        
        result = ammo.calculate_advanced_penetration(
            armor, range_m, angle,
            environmental_conditions=env_conditions,
            temperature_conditions=temp_conditions,
            ricochet_params=ricochet_params
        )
        
        demo_text += f"""--- ADVANCED PHYSICS EFFECTS ---
Enhanced penetration: {result['final_penetration']:.1f} mm RHA
Enhanced velocity: {result['velocity_at_target']:.1f} m/s

"""
        
        # Environmental effects
        if result['advanced_effects']:
            effects = result['advanced_effects']['ballistic_result'].environmental_effects
            demo_text += f"""Environmental Effects:
  Temperature: {effects['temperature_effect']*100:+.1f}%
  Altitude: {effects['altitude_effect']*100:+.1f}%
  Humidity: {effects['humidity_effect']*100:+.1f}%
  Wind: {effects['wind_effect']*100:+.1f}%

"""
        
        # Temperature effects
        if result['temperature_analysis']:
            temp = result['temperature_analysis']
            demo_text += f"""Temperature Effects:
  Velocity modifier: {temp['velocity_modifier']:.3f}
  Penetration modifier: {temp['penetration_modifier']:.3f}
  Propellant efficiency: {temp['propellant_efficiency']:.3f}

"""
        
        # Ricochet analysis
        if result['ricochet_analysis']:
            ricochet = result['ricochet_analysis']
            demo_text += f"""Ricochet Analysis:
  Ricochet probability: {ricochet['ricochet_probability']*100:.1f}%
  Predicted outcome: {ricochet['predicted_outcome'].upper()}
  Critical angle: {ricochet['critical_angle']:.1f}°

"""
        
        # Multi-hit simulation
        demo_text += "--- MULTI-HIT DAMAGE SIMULATION ---\n"
        
        for hit in range(3):
            impact_location = (random.uniform(-200, 200), random.uniform(-200, 200))
            penetration_attempted = result['final_penetration']
            energy = 0.5 * ammo.mass * result['velocity_at_target'] ** 2
            current_thickness = armor.get_effective_thickness(ammo.penetration_type, angle)
            penetration_achieved = penetration_attempted > current_thickness
            
            armor.apply_damage_from_impact(
                ammo, impact_location, penetration_attempted,
                energy, penetration_achieved, hit * 10.0
            )
            
            damage_summary = armor.get_damage_summary()
            condition = damage_summary['current_condition']
            
            demo_text += f"""\nHit {hit+1}:
  Impact: ({impact_location[0]:.0f}, {impact_location[1]:.0f}) mm
  Result: {'PENETRATION' if penetration_achieved else 'DEFEAT'}
  Armor integrity: {condition['integrity_percent']:.1f}%
  Thickness remaining: {condition['thickness_remaining']:.1f} mm
  Status: {damage_summary['armor_status']}
"""
        
        demo_text += "\n\n═══════════════════════════════════════════════════════════════\n"
        demo_text += "ADVANCED PHYSICS DEMONSTRATION COMPLETE\n\n"
        demo_text += "The system successfully modeled:\n"
        demo_text += "• Complex environmental effects on ballistics\n"
        demo_text += "• Temperature variations affecting performance\n"
        demo_text += "• Ricochet probabilities and deflection analysis\n"
        demo_text += "• Progressive armor damage from multiple hits\n\n"
        demo_text += "This demonstrates the sophisticated physics engine that\n"
        demo_text += "provides realistic simulation capabilities for educational\n"
        demo_text += "and analytical purposes.\n"
        demo_text += "═══════════════════════════════════════════════════════════════"
        
        return demo_text
    
    def run(self):
        """Start the GUI application."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.root.quit()


def main():
    """Main entry point for GUI application."""
    app = TankArmorSimulatorGUI()
    app.run()


if __name__ == "__main__":
    main()
