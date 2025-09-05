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

from ammunition import APFSDS, AP, APCR, HEAT, HESH
from armor import RHA, CompositeArmor, ReactiveArmor, SpacedArmor
from visualization import BallisticsVisualizer, PenetrationVisualizer, ComparisonVisualizer


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
        self.ammunition_catalog = {
            "M829A4 APFSDS": APFSDS(
                name="M829A4 APFSDS",
                caliber=120.0,
                penetrator_diameter=22.0,
                penetrator_mass=4.6,
                muzzle_velocity=1680,
                penetrator_length=570
            ),
            "3BM60 APFSDS": APFSDS(
                name="3BM60 Svinets-2",
                caliber=125.0,
                penetrator_diameter=24.0,
                penetrator_mass=5.2,
                muzzle_velocity=1750,
                penetrator_length=600
            ),
            "M830A1 HEAT": HEAT(
                name="M830A1 HEAT-MP",
                caliber=120.0,
                warhead_mass=18.6,
                explosive_mass=2.4,
                standoff_distance=150
            ),
            "3BK29 HEAT": HEAT(
                name="3BK29 HEAT",
                caliber=125.0,
                warhead_mass=19.8,
                explosive_mass=2.8,
                standoff_distance=180
            ),
            "L31A7 HESH": HESH(
                name="L31A7 HESH",
                caliber=120.0,
                shell_mass=17.2,
                explosive_mass=4.1
            ),
            "M72 AP": AP(
                name="M72 AP Shot",
                caliber=76.0,
                mass=6.8,
                muzzle_velocity=792
            )
        }
    
    def create_armor_catalog(self):
        """Create the armor catalog (same as CLI version)."""
        self.armor_catalog = {
            "100mm RHA": RHA(thickness=100.0),
            "200mm RHA": RHA(thickness=200.0),
            "M1A2 Frontal": CompositeArmor(
                name="M1A2 Frontal Armor",
                thickness=650.0,
                steel_layers=200.0,
                ceramic_layers=350.0,
                other_layers=100.0
            ),
            "T-90M Frontal": ReactiveArmor(
                name="T-90M with Relikt ERA",
                base_thickness=500.0,
                era_thickness=45.0,
                explosive_mass=0.8
            ),
            "Leopard 2A7 Side": SpacedArmor(
                name="Leopard 2A7 Side Armor",
                front_plate=35.0,
                rear_plate=70.0,
                spacing=150.0
            ),
            "Challenger 2 Frontal": CompositeArmor(
                name="Challenger 2 Dorchester",
                thickness=800.0,
                steel_layers=250.0,
                ceramic_layers=450.0,
                other_layers=100.0
            )
        }
    
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
            ("Penetration with Visualization", self.run_penetration_with_viz),
            ("Ballistic Trajectory", self.view_ballistic_trajectory),
            ("Compare Ammunition", self.compare_ammunition),
            ("Compare Armor", self.compare_armor),
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
    
    # Placeholder methods for menu functions
    def run_penetration_test(self):
        """Run a penetration test."""
        self.status_var.set("Opening penetration test...")
        # TODO: Implement penetration test dialog
        messagebox.showinfo("Coming Soon", "Penetration test dialog will be implemented here.")
    
    def run_penetration_with_viz(self):
        """Run penetration test with visualization."""
        self.status_var.set("Opening penetration test with visualization...")
        # TODO: Implement visualization dialog
        messagebox.showinfo("Coming Soon", "Visualization dialog will be implemented here.")
    
    def view_ballistic_trajectory(self):
        """View ballistic trajectory."""
        self.status_var.set("Opening trajectory viewer...")
        # TODO: Implement trajectory viewer
        messagebox.showinfo("Coming Soon", "Trajectory viewer will be implemented here.")
    
    def compare_ammunition(self):
        """Compare ammunition types."""
        self.status_var.set("Opening ammunition comparison...")
        # TODO: Implement ammunition comparison
        messagebox.showinfo("Coming Soon", "Ammunition comparison will be implemented here.")
    
    def compare_armor(self):
        """Compare armor types."""
        self.status_var.set("Opening armor comparison...")
        # TODO: Implement armor comparison
        messagebox.showinfo("Coming Soon", "Armor comparison will be implemented here.")
    
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
        for name, item in catalog.items():
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
