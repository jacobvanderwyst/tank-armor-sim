"""
Comparison visualization system for tank armor penetration simulation.

This module creates comparative analysis visualizations for multiple ammunition
types against armor targets and armor effectiveness against different threats.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import List, Dict, Any, Tuple
import seaborn as sns


class ComparisonVisualizer:
    """Visualizes comparative analysis between ammunition types and armor systems."""
    
    def __init__(self):
        """Initialize the comparison visualizer."""
        self.fig = None
        self.axes = None
        # Set up color palette for consistent visualization
        self.colors = sns.color_palette("Set1", 10)
    
    def compare_ammunition(self, ammunition_list: List[Any], armor, 
                          ranges: List[float] = None, angles: List[float] = None) -> plt.Figure:
        """
        Create comprehensive ammunition comparison visualization.
        
        Args:
            ammunition_list: List of ammunition objects to compare
            armor: Target armor object
            ranges: List of ranges to analyze (default: [500, 1000, 2000, 3000, 4000])
            angles: List of impact angles to analyze (default: [0, 15, 30, 45, 60])
            
        Returns:
            Matplotlib figure object
        """
        if ranges is None:
            ranges = [500, 1000, 2000, 3000, 4000]
        if angles is None:
            angles = [0, 15, 30, 45, 60]
            
        # Create 2x2 subplot layout with better spacing
        self.fig, self.axes = plt.subplots(2, 2, figsize=(18, 14))
        self.fig.subplots_adjust(left=0.08, bottom=0.1, right=0.95, top=0.90, wspace=0.3, hspace=0.4)
        
        # Panel 1: Range vs Penetration curves
        self._plot_range_penetration_curves(ammunition_list, armor, ranges, self.axes[0, 0])
        
        # Panel 2: Angle vs Effectiveness
        self._plot_angle_effectiveness(ammunition_list, armor, angles, 2000, self.axes[0, 1])
        
        # Panel 3: Ammunition characteristics comparison
        self._plot_ammunition_characteristics(ammunition_list, self.axes[1, 0])
        
        # Panel 4: Summary statistics table
        self._plot_ammunition_summary(ammunition_list, armor, ranges[2], angles[1], self.axes[1, 1])
        
        self.fig.suptitle(f'Ammunition Comparison vs {armor.name}', fontsize=16, y=0.95)
        return self.fig
    
    def compare_armor(self, armor_list: List[Any], ammunition,
                     ranges: List[float] = None, angles: List[float] = None) -> plt.Figure:
        """
        Create comprehensive armor comparison visualization.
        
        Args:
            armor_list: List of armor objects to compare
            ammunition: Attacking ammunition object
            ranges: List of ranges to analyze
            angles: List of impact angles to analyze
            
        Returns:
            Matplotlib figure object
        """
        if ranges is None:
            ranges = [500, 1000, 2000, 3000, 4000]
        if angles is None:
            angles = [0, 15, 30, 45, 60]
            
        # Create 2x2 subplot layout with better spacing
        self.fig, self.axes = plt.subplots(2, 2, figsize=(18, 14))
        self.fig.subplots_adjust(left=0.08, bottom=0.1, right=0.95, top=0.90, wspace=0.3, hspace=0.4)
        
        # Panel 1: Armor effectiveness vs range
        self._plot_armor_effectiveness_vs_range(armor_list, ammunition, ranges, self.axes[0, 0])
        
        # Panel 2: Armor effectiveness vs angle
        self._plot_armor_effectiveness_vs_angle(armor_list, ammunition, angles, 2000, self.axes[0, 1])
        
        # Panel 3: Protection factor comparison
        self._plot_protection_factors(armor_list, ammunition, self.axes[1, 0])
        
        # Panel 4: Armor summary statistics
        self._plot_armor_summary(armor_list, ammunition, ranges[2], angles[1], self.axes[1, 1])
        
        self.fig.suptitle(f'Armor Comparison vs {ammunition.name}', fontsize=16, y=0.95)
        return self.fig
    
    def _plot_range_penetration_curves(self, ammunition_list: List[Any], armor, 
                                     ranges: List[float], ax):
        """Plot penetration capability vs range for multiple ammunition types."""
        for i, ammo in enumerate(ammunition_list):
            penetrations = []
            effective_thicknesses = []
            
            for range_m in ranges:
                pen = ammo.calculate_penetration(range_m, 0)  # 0° impact
                eff = armor.get_effective_thickness(ammo.penetration_type, 0)
                penetrations.append(pen)
                effective_thicknesses.append(eff)
            
            # Plot penetration curve
            ax.plot(ranges, penetrations, 'o-', color=self.colors[i], 
                   linewidth=2, markersize=6, label=f'{ammo.name}')
        
        # Add armor effectiveness line
        armor_line = armor.get_effective_thickness(ammunition_list[0].penetration_type, 0)
        ax.axhline(y=armor_line, color='red', linestyle='--', linewidth=2, 
                  alpha=0.7, label=f'{armor.name} Protection')
        
        ax.set_xlabel('Range (meters)')
        ax.set_ylabel('Penetration (mm RHA)')
        ax.set_title('Penetration vs Range (0° Impact)')
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    def _plot_angle_effectiveness(self, ammunition_list: List[Any], armor,
                                angles: List[float], range_m: float, ax):
        """Plot penetration effectiveness vs impact angle."""
        for i, ammo in enumerate(ammunition_list):
            penetrations = []
            effectiveness_ratios = []
            
            for angle in angles:
                pen = ammo.calculate_penetration(range_m, angle)
                eff = armor.get_effective_thickness(ammo.penetration_type, angle)
                penetrations.append(pen)
                effectiveness_ratios.append(pen / eff if eff > 0 else 0)
            
            ax.plot(angles, effectiveness_ratios, 'o-', color=self.colors[i],
                   linewidth=2, markersize=6, label=f'{ammo.name}')
        
        # Add penetration threshold line
        ax.axhline(y=1.0, color='red', linestyle='--', linewidth=2, 
                  alpha=0.7, label='Penetration Threshold')
        
        ax.set_xlabel('Impact Angle (degrees from vertical)')
        ax.set_ylabel('Penetration Ratio (Pen/Armor)')
        ax.set_title(f'Angle Effectiveness at {range_m}m Range')
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    def _plot_ammunition_characteristics(self, ammunition_list: List[Any], ax):
        """Plot ammunition characteristics comparison."""
        names = [ammo.name.split()[0] for ammo in ammunition_list]  # Shortened names
        calibers = [ammo.caliber for ammo in ammunition_list]
        velocities = [ammo.muzzle_velocity for ammo in ammunition_list]
        masses = [ammo.mass for ammo in ammunition_list]
        energies = [ammo.kinetic_energy / 1000 for ammo in ammunition_list]  # kJ
        
        x = np.arange(len(names))
        width = 0.2
        
        # Create grouped bar chart
        ax2 = ax.twinx()  # Secondary y-axis for velocity
        
        bars1 = ax.bar(x - width*1.5, calibers, width, label='Caliber (mm)', 
                      color=self.colors[0], alpha=0.7)
        bars2 = ax.bar(x - width/2, masses, width, label='Mass (kg)', 
                      color=self.colors[1], alpha=0.7)
        bars3 = ax.bar(x + width/2, energies, width, label='Energy (kJ)', 
                      color=self.colors[2], alpha=0.7)
        bars4 = ax2.bar(x + width*1.5, velocities, width, label='Velocity (m/s)', 
                       color=self.colors[3], alpha=0.7)
        
        ax.set_xlabel('Ammunition Type')
        ax.set_ylabel('Caliber (mm) / Mass (kg) / Energy (kJ)')
        ax2.set_ylabel('Muzzle Velocity (m/s)')
        ax.set_title('Ammunition Characteristics Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha='right')
        
        # Combine legends
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        ax.grid(True, alpha=0.3)
    
    def _plot_ammunition_summary(self, ammunition_list: List[Any], armor, 
                               range_m: float, angle: float, ax):
        """Create summary statistics table for ammunition comparison."""
        ax.axis('off')
        
        # Calculate summary data
        data = []
        for ammo in ammunition_list:
            pen = ammo.calculate_penetration(range_m, angle)
            eff = armor.get_effective_thickness(ammo.penetration_type, angle)
            can_defeat = armor.can_defeat(pen, ammo.penetration_type, angle)
            margin = abs(pen - eff)
            
            data.append([
                ammo.name.split()[0],  # Short name
                f"{pen:.0f}",
                f"{eff:.0f}", 
                "✅ PEN" if not can_defeat else "❌ STOP",
                f"{margin:.0f}"
            ])
        
        # Create table
        table_data = [['Ammunition', 'Penetration\n(mm RHA)', 'Effective Armor\n(mm RHA)', 
                      'Result', 'Margin\n(mm RHA)']] + data
        
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        colWidths=[0.25, 0.15, 0.15, 0.15, 0.15])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Style header row
        for i in range(len(table_data[0])):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Color code results
        for i in range(1, len(table_data)):
            result_cell = table[(i, 3)]
            if "PEN" in table_data[i][3]:
                result_cell.set_facecolor('#ffebee')  # Light red
            else:
                result_cell.set_facecolor('#e8f5e8')  # Light green
        
        ax.set_title(f'Summary at {range_m}m Range, {angle}° Impact', 
                    fontsize=12, pad=20)
    
    def _plot_armor_effectiveness_vs_range(self, armor_list: List[Any], ammunition,
                                         ranges: List[float], ax):
        """Plot armor effectiveness vs range."""
        for i, armor in enumerate(armor_list):
            effectiveness_ratios = []
            
            for range_m in ranges:
                pen = ammunition.calculate_penetration(range_m, 0)
                eff = armor.get_effective_thickness(ammunition.penetration_type, 0)
                effectiveness_ratios.append(eff / pen if pen > 0 else float('inf'))
            
            ax.plot(ranges, effectiveness_ratios, 'o-', color=self.colors[i],
                   linewidth=2, markersize=6, label=f'{armor.name}')
        
        ax.axhline(y=1.0, color='red', linestyle='--', linewidth=2, 
                  alpha=0.7, label='Defeat Threshold')
        
        ax.set_xlabel('Range (meters)')
        ax.set_ylabel('Protection Ratio (Armor/Penetration)')
        ax.set_title('Armor Effectiveness vs Range (0° Impact)')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_ylim(0, 3)  # Reasonable scale
    
    def _plot_armor_effectiveness_vs_angle(self, armor_list: List[Any], ammunition,
                                         angles: List[float], range_m: float, ax):
        """Plot armor effectiveness vs impact angle."""
        for i, armor in enumerate(armor_list):
            effectiveness_ratios = []
            
            for angle in angles:
                pen = ammunition.calculate_penetration(range_m, angle)
                eff = armor.get_effective_thickness(ammunition.penetration_type, angle)
                effectiveness_ratios.append(eff / pen if pen > 0 else float('inf'))
            
            ax.plot(angles, effectiveness_ratios, 'o-', color=self.colors[i],
                   linewidth=2, markersize=6, label=f'{armor.name}')
        
        ax.axhline(y=1.0, color='red', linestyle='--', linewidth=2, 
                  alpha=0.7, label='Defeat Threshold')
        
        ax.set_xlabel('Impact Angle (degrees from vertical)')
        ax.set_ylabel('Protection Ratio (Armor/Penetration)')
        ax.set_title(f'Armor Effectiveness vs Angle at {range_m}m')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_ylim(0, 4)  # Reasonable scale
    
    def _plot_protection_factors(self, armor_list: List[Any], ammunition, ax):
        """Plot protection factors comparison."""
        names = [armor.name.split()[0] for armor in armor_list]
        thicknesses = [armor.thickness for armor in armor_list]
        protection_factors = [armor.get_protection_against(ammunition.penetration_type) 
                            for armor in armor_list]
        effective_protection = [thick * prot for thick, prot in zip(thicknesses, protection_factors)]
        
        x = np.arange(len(names))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, thicknesses, width, label='Nominal Thickness (mm)',
                      color=self.colors[0], alpha=0.7)
        bars2 = ax.bar(x + width/2, effective_protection, width, 
                      label='Effective Protection (mm RHA)',
                      color=self.colors[1], alpha=0.7)
        
        ax.set_xlabel('Armor Type')
        ax.set_ylabel('Thickness (mm)')
        ax.set_title('Protection Factor Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_armor_summary(self, armor_list: List[Any], ammunition,
                          range_m: float, angle: float, ax):
        """Create summary statistics table for armor comparison."""
        ax.axis('off')
        
        # Calculate summary data
        data = []
        for armor in armor_list:
            pen = ammunition.calculate_penetration(range_m, angle)
            eff = armor.get_effective_thickness(ammunition.penetration_type, angle)
            can_defeat = armor.can_defeat(pen, ammunition.penetration_type, angle)
            protection_factor = armor.get_protection_against(ammunition.penetration_type)
            
            data.append([
                armor.name.split()[0],  # Short name
                f"{armor.thickness:.0f}",
                f"{protection_factor:.2f}x",
                f"{eff:.0f}",
                "✅ STOP" if can_defeat else "❌ PEN"
            ])
        
        # Create table
        table_data = [['Armor', 'Thickness\n(mm)', 'Protection\nFactor', 
                      'Effective\n(mm RHA)', 'Result']] + data
        
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        colWidths=[0.25, 0.15, 0.15, 0.15, 0.15])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Style header row
        for i in range(len(table_data[0])):
            table[(0, i)].set_facecolor('#2196F3')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Color code results
        for i in range(1, len(table_data)):
            result_cell = table[(i, 4)]
            if "STOP" in table_data[i][4]:
                result_cell.set_facecolor('#e8f5e8')  # Light green
            else:
                result_cell.set_facecolor('#ffebee')  # Light red
        
        ax.set_title(f'Summary at {range_m}m Range, {angle}° Impact', 
                    fontsize=12, pad=20)
    
    def save_plot(self, filename: str = 'comparison_analysis.png'):
        """Save the current plot to file."""
        if self.fig:
            # Ensure results directory exists
            import os
            results_dir = 'results'
            if not os.path.exists(results_dir):
                os.makedirs(results_dir)
            
            # Save to results directory
            filepath = os.path.join(results_dir, filename)
            self.fig.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Comparison analysis plot saved as {filepath}")
    
    def show_plot(self):
        """Display the plot in fullscreen for better readability."""
        if self.fig:
            # Maximize the matplotlib window for better visibility
            mngr = plt.get_current_fig_manager()
            try:
                # Try different methods depending on backend
                if hasattr(mngr, 'window'):
                    if hasattr(mngr.window, 'state'):  # Tkinter backend
                        mngr.window.state('zoomed')  # Windows maximize
                    elif hasattr(mngr.window, 'showMaximized'):  # Qt backend
                        mngr.window.showMaximized()
                elif hasattr(mngr, 'frame'):
                    mngr.frame.Maximize(True)  # wx backend
                elif hasattr(mngr, 'full_screen_toggle'):
                    mngr.full_screen_toggle()  # Some backends
            except:
                pass  # Fallback gracefully if maximization fails
            
            plt.show()
