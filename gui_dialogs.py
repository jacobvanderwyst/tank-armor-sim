"""
GUI Dialog Classes for Tank Armor Simulator
Provides user input forms and parameter selection dialogs.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Tuple, List, Optional, Union


class PenetrationTestDialog:
    """Dialog for penetration test parameters."""
    
    def __init__(self, parent, ammunition_catalog, armor_catalog, with_viz=False):
        self.parent = parent
        self.ammunition_catalog = ammunition_catalog
        self.armor_catalog = armor_catalog
        self.with_viz = with_viz
        self.result = None
        
    def show(self) -> Optional[Tuple]:
        """Show dialog and return user selections."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Penetration Test Parameters")
        self.dialog.geometry("450x400")
        self.dialog.resizable(True, True)
        self.dialog.grab_set()
        
        # Center on parent
        self.dialog.transient(self.parent)
        
        self._create_widgets()
        
        # Wait for dialog to close
        self.dialog.wait_window()
        return self.result
    
    def _create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Ammunition selection
        ttk.Label(main_frame, text="Select Ammunition:", font=('TkDefaultFont', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.ammo_var = tk.StringVar()
        ammo_combo = ttk.Combobox(main_frame, textvariable=self.ammo_var, state='readonly', width=50)
        ammo_combo['values'] = [f"{ammo.name} ({ammo.caliber:.0f}mm {ammo.penetration_type.upper()})" 
                                for ammo in self.ammunition_catalog]
        ammo_combo.pack(fill='x', pady=(0, 15))
        if ammo_combo['values']:
            ammo_combo.current(0)
        
        # Armor selection
        ttk.Label(main_frame, text="Select Armor:", font=('TkDefaultFont', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.armor_var = tk.StringVar()
        armor_combo = ttk.Combobox(main_frame, textvariable=self.armor_var, state='readonly', width=50)
        armor_combo['values'] = [f"{armor.name} ({armor.thickness:.0f}mm {armor.armor_type.upper()})" 
                                for armor in self.armor_catalog]
        armor_combo.pack(fill='x', pady=(0, 15))
        if armor_combo['values']:
            armor_combo.current(0)
        
        # Range input
        ttk.Label(main_frame, text="Engagement Range (m):", font=('TkDefaultFont', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        range_frame = ttk.Frame(main_frame)
        range_frame.pack(fill='x', pady=(0, 15))
        
        self.range_var = tk.StringVar(value="1000")
        range_spinbox = tk.Spinbox(range_frame, from_=50, to=5000, increment=50, 
                                  textvariable=self.range_var, width=15)
        range_spinbox.pack(side='left')
        
        ttk.Label(range_frame, text="meters").pack(side='left', padx=(10, 0))
        
        # Angle input
        ttk.Label(main_frame, text="Impact Angle (degrees):", font=('TkDefaultFont', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        angle_frame = ttk.Frame(main_frame)
        angle_frame.pack(fill='x', pady=(0, 15))
        
        self.angle_var = tk.StringVar(value="0")
        angle_spinbox = tk.Spinbox(angle_frame, from_=0, to=85, increment=5,
                                  textvariable=self.angle_var, width=15)
        angle_spinbox.pack(side='left')
        
        ttk.Label(angle_frame, text="degrees from normal").pack(side='left', padx=(10, 0))
        
        # Visualization option
        self.viz_var = tk.BooleanVar(value=self.with_viz)
        viz_check = ttk.Checkbutton(main_frame, text="Generate Visualization", variable=self.viz_var)
        viz_check.pack(anchor='w', pady=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side='right', padx=(10, 0))
        ttk.Button(button_frame, text="Run Test", command=self._ok).pack(side='right')
    
    def _ok(self):
        """Handle OK button."""
        try:
            # Get selected indices
            ammo_idx = self.ammo_var.get().split('(')[0].strip()
            armor_idx = self.armor_var.get().split('(')[0].strip()
            
            # Find selected items
            selected_ammo = None
            selected_armor = None
            
            for ammo in self.ammunition_catalog:
                if ammo.name == ammo_idx:
                    selected_ammo = ammo
                    break
            
            for armor in self.armor_catalog:
                if armor.name == armor_idx:
                    selected_armor = armor
                    break
            
            if not selected_ammo or not selected_armor:
                messagebox.showerror("Selection Error", "Please select both ammunition and armor.")
                return
            
            range_m = float(self.range_var.get())
            angle = float(self.angle_var.get())
            with_viz = self.viz_var.get()
            
            if range_m < 50 or range_m > 5000:
                messagebox.showerror("Range Error", "Range must be between 50 and 5000 meters.")
                return
            
            if angle < 0 or angle > 85:
                messagebox.showerror("Angle Error", "Angle must be between 0 and 85 degrees.")
                return
            
            self.result = (selected_ammo, selected_armor, range_m, angle, with_viz)
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values.")
    
    def _cancel(self):
        """Handle Cancel button."""
        self.result = None
        self.dialog.destroy()


class TrajectoryDialog:
    """Dialog for ballistic trajectory parameters."""
    
    def __init__(self, parent, ammunition_catalog, armor_catalog):
        self.parent = parent
        self.ammunition_catalog = ammunition_catalog
        self.armor_catalog = armor_catalog
        self.result = None
        
    def show(self) -> Optional[Tuple]:
        """Show dialog and return user selections."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Ballistic Trajectory Parameters")
        self.dialog.geometry("450x400")
        self.dialog.resizable(True, True)
        self.dialog.grab_set()
        self.dialog.transient(self.parent)
        
        self._create_widgets()
        self.dialog.wait_window()
        return self.result
    
    def _create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Ammunition selection
        ttk.Label(main_frame, text="Select Ammunition:", font=('TkDefaultFont', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.ammo_var = tk.StringVar()
        ammo_combo = ttk.Combobox(main_frame, textvariable=self.ammo_var, state='readonly', width=50)
        ammo_combo['values'] = [f"{ammo.name} ({ammo.caliber:.0f}mm)" for ammo in self.ammunition_catalog]
        ammo_combo.pack(fill='x', pady=(0, 15))
        if ammo_combo['values']:
            ammo_combo.current(0)
        
        # Target armor (optional)
        ttk.Label(main_frame, text="Target Armor (optional):", font=('TkDefaultFont', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.armor_var = tk.StringVar()
        armor_combo = ttk.Combobox(main_frame, textvariable=self.armor_var, state='readonly', width=50)
        armor_values = ["None (trajectory only)"] + [f"{armor.name} ({armor.thickness:.0f}mm)" 
                                                    for armor in self.armor_catalog]
        armor_combo['values'] = armor_values
        armor_combo.pack(fill='x', pady=(0, 15))
        armor_combo.current(0)
        
        # Range input
        ttk.Label(main_frame, text="Maximum Range (m):", font=('TkDefaultFont', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        range_frame = ttk.Frame(main_frame)
        range_frame.pack(fill='x', pady=(0, 15))
        
        self.range_var = tk.StringVar(value="2000")
        range_spinbox = tk.Spinbox(range_frame, from_=100, to=5000, increment=100,
                                  textvariable=self.range_var, width=15)
        range_spinbox.pack(side='left')
        ttk.Label(range_frame, text="meters").pack(side='left', padx=(10, 0))
        
        # Angle input
        ttk.Label(main_frame, text="Launch Angle (degrees):", font=('TkDefaultFont', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        angle_frame = ttk.Frame(main_frame)
        angle_frame.pack(fill='x', pady=(0, 15))
        
        self.angle_var = tk.StringVar(value="0")
        angle_spinbox = tk.Spinbox(angle_frame, from_=-10, to=45, increment=1,
                                  textvariable=self.angle_var, width=15)
        angle_spinbox.pack(side='left')
        ttk.Label(angle_frame, text="degrees (negative = downward)").pack(side='left', padx=(10, 0))
        
        # Show velocity option
        self.velocity_var = tk.BooleanVar(value=True)
        velocity_check = ttk.Checkbutton(main_frame, text="Show velocity decay along trajectory", 
                                       variable=self.velocity_var)
        velocity_check.pack(anchor='w', pady=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side='right', padx=(10, 0))
        ttk.Button(button_frame, text="Generate", command=self._ok).pack(side='right')
    
    def _ok(self):
        """Handle OK button."""
        try:
            ammo_name = self.ammo_var.get().split('(')[0].strip()
            selected_ammo = None
            
            for ammo in self.ammunition_catalog:
                if ammo.name == ammo_name:
                    selected_ammo = ammo
                    break
            
            if not selected_ammo:
                messagebox.showerror("Selection Error", "Please select ammunition.")
                return
            
            # Handle armor selection
            selected_armor = None
            armor_selection = self.armor_var.get()
            if not armor_selection.startswith("None"):
                armor_name = armor_selection.split('(')[0].strip()
                for armor in self.armor_catalog:
                    if armor.name == armor_name:
                        selected_armor = armor
                        break
            
            range_m = float(self.range_var.get())
            angle = float(self.angle_var.get())
            show_velocity = self.velocity_var.get()
            
            if range_m < 100 or range_m > 5000:
                messagebox.showerror("Range Error", "Range must be between 100 and 5000 meters.")
                return
            
            if angle < -10 or angle > 45:
                messagebox.showerror("Angle Error", "Angle must be between -10 and 45 degrees.")
                return
            
            self.result = (selected_ammo, selected_armor, range_m, angle, show_velocity)
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values.")
    
    def _cancel(self):
        """Handle Cancel button."""
        self.result = None
        self.dialog.destroy()


class ComparisonDialog:
    """Dialog for ammunition/armor comparison parameters."""
    
    def __init__(self, parent, comparison_type, ammunition_catalog, armor_catalog):
        self.parent = parent
        self.comparison_type = comparison_type  # "ammunition" or "armor"
        self.ammunition_catalog = ammunition_catalog
        self.armor_catalog = armor_catalog
        self.result = None
        
    def show(self) -> Optional[Tuple]:
        """Show dialog and return user selections."""
        self.dialog = tk.Toplevel(self.parent)
        title = f"{self.comparison_type.title()} Comparison Parameters"
        self.dialog.title(title)
        self.dialog.geometry("500x500")
        self.dialog.resizable(True, True)
        self.dialog.grab_set()
        self.dialog.transient(self.parent)
        
        self._create_widgets()
        self.dialog.wait_window()
        return self.result
    
    def _create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        if self.comparison_type == "ammunition":
            self._create_ammo_comparison_widgets(main_frame)
        else:
            self._create_armor_comparison_widgets(main_frame)
    
    def _create_ammo_comparison_widgets(self, parent):
        """Create ammunition comparison widgets."""
        # Target armor selection
        ttk.Label(parent, text="Target Armor:", font=('TkDefaultFont', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.target_var = tk.StringVar()
        target_combo = ttk.Combobox(parent, textvariable=self.target_var, state='readonly', width=60)
        target_combo['values'] = [f"{armor.name} ({armor.thickness:.0f}mm {armor.armor_type.upper()})" 
                                 for armor in self.armor_catalog]
        target_combo.pack(fill='x', pady=(0, 15))
        if target_combo['values']:
            target_combo.current(0)
        
        # Ammunition selection
        ttk.Label(parent, text="Select Ammunition to Compare (2-6 items):", 
                 font=('TkDefaultFont', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        # Create listbox with checkboxes simulation
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Scrollable listbox
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(fill='both', expand=True)
        
        self.ammo_listbox = tk.Listbox(listbox_frame, selectmode='multiple', height=10)
        ammo_scrollbar = ttk.Scrollbar(listbox_frame, orient='vertical', command=self.ammo_listbox.yview)
        self.ammo_listbox.configure(yscrollcommand=ammo_scrollbar.set)
        
        for ammo in self.ammunition_catalog:
            self.ammo_listbox.insert('end', f"{ammo.name} ({ammo.caliber:.0f}mm {ammo.penetration_type.upper()})")
        
        self.ammo_listbox.pack(side='left', fill='both', expand=True)
        ammo_scrollbar.pack(side='right', fill='y')
        
        # Select first two items by default
        if len(self.ammunition_catalog) >= 2:
            self.ammo_listbox.selection_set(0, 1)
        
        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side='right', padx=(10, 0))
        ttk.Button(button_frame, text="Compare", command=self._ok_ammo).pack(side='right')
    
    def _create_armor_comparison_widgets(self, parent):
        """Create armor comparison widgets."""
        # Target ammunition selection
        ttk.Label(parent, text="Target Ammunition:", font=('TkDefaultFont', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.target_var = tk.StringVar()
        target_combo = ttk.Combobox(parent, textvariable=self.target_var, state='readonly', width=60)
        target_combo['values'] = [f"{ammo.name} ({ammo.caliber:.0f}mm {ammo.penetration_type.upper()})" 
                                 for ammo in self.ammunition_catalog]
        target_combo.pack(fill='x', pady=(0, 15))
        if target_combo['values']:
            target_combo.current(0)
        
        # Armor selection
        ttk.Label(parent, text="Select Armor to Compare (2-6 items):", 
                 font=('TkDefaultFont', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        # Create listbox with checkboxes simulation
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Scrollable listbox
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(fill='both', expand=True)
        
        self.armor_listbox = tk.Listbox(listbox_frame, selectmode='multiple', height=10)
        armor_scrollbar = ttk.Scrollbar(listbox_frame, orient='vertical', command=self.armor_listbox.yview)
        self.armor_listbox.configure(yscrollcommand=armor_scrollbar.set)
        
        for armor in self.armor_catalog:
            self.armor_listbox.insert('end', f"{armor.name} ({armor.thickness:.0f}mm {armor.armor_type.upper()})")
        
        self.armor_listbox.pack(side='left', fill='both', expand=True)
        armor_scrollbar.pack(side='right', fill='y')
        
        # Select first two items by default
        if len(self.armor_catalog) >= 2:
            self.armor_listbox.selection_set(0, 1)
        
        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side='right', padx=(10, 0))
        ttk.Button(button_frame, text="Compare", command=self._ok_armor).pack(side='right')
    
    def _ok_ammo(self):
        """Handle OK for ammunition comparison."""
        try:
            # Get target armor
            target_name = self.target_var.get().split('(')[0].strip()
            target_armor = None
            
            for armor in self.armor_catalog:
                if armor.name == target_name:
                    target_armor = armor
                    break
            
            if not target_armor:
                messagebox.showerror("Selection Error", "Please select target armor.")
                return
            
            # Get selected ammunition
            selected_indices = self.ammo_listbox.curselection()
            if len(selected_indices) < 2:
                messagebox.showerror("Selection Error", "Please select at least 2 ammunition types.")
                return
            
            if len(selected_indices) > 6:
                messagebox.showerror("Selection Error", "Please select no more than 6 ammunition types.")
                return
            
            selected_ammo = [self.ammunition_catalog[i] for i in selected_indices]
            
            self.result = (selected_ammo, target_armor, "ammunition")
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Selection error: {e}")
    
    def _ok_armor(self):
        """Handle OK for armor comparison."""
        try:
            # Get target ammunition
            target_name = self.target_var.get().split('(')[0].strip()
            target_ammo = None
            
            for ammo in self.ammunition_catalog:
                if ammo.name == target_name:
                    target_ammo = ammo
                    break
            
            if not target_ammo:
                messagebox.showerror("Selection Error", "Please select target ammunition.")
                return
            
            # Get selected armor
            selected_indices = self.armor_listbox.curselection()
            if len(selected_indices) < 2:
                messagebox.showerror("Selection Error", "Please select at least 2 armor types.")
                return
            
            if len(selected_indices) > 6:
                messagebox.showerror("Selection Error", "Please select no more than 6 armor types.")
                return
            
            selected_armor = [self.armor_catalog[i] for i in selected_indices]
            
            self.result = (selected_armor, target_ammo, "armor")
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Selection error: {e}")
    
    def _cancel(self):
        """Handle Cancel button."""
        self.result = None
        self.dialog.destroy()
