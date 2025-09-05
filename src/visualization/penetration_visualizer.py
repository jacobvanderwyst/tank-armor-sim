"""
Penetration mechanics visualization for tank armor penetration simulation.

This module creates detailed visual representations of armor penetration
processes, including angle of attack, penetration mechanics, and effects.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import Tuple, Dict, Any


class PenetrationVisualizer:
    """Visualizes armor penetration mechanics and effects."""
    
    def __init__(self):
        """Initialize the penetration visualizer."""
        self.fig = None
        self.axes = None
        
    def visualize_penetration_process(self, ammo, armor, range_m: float, 
                                    impact_angle: float) -> plt.Figure:
        """
        Create a comprehensive penetration process visualization.
        
        Args:
            ammo: Ammunition object
            armor: Armor object  
            range_m: Engagement range in meters
            impact_angle: Impact angle in degrees from vertical
            
        Returns:
            Matplotlib figure object
        """
        # Calculate penetration results
        penetration = ammo.calculate_penetration(range_m, impact_angle)
        effective_thickness = armor.get_effective_thickness(ammo.penetration_type, impact_angle)
        velocity_at_impact = ammo.get_velocity_at_range(range_m)
        can_defeat = armor.can_defeat(penetration, ammo.penetration_type, impact_angle)
        
        # Create multi-panel visualization with better spacing
        self.fig, self.axes = plt.subplots(2, 2, figsize=(18, 14))
        self.fig.subplots_adjust(left=0.08, bottom=0.08, right=0.95, top=0.92, wspace=0.25, hspace=0.35)
        
        # Panel 1: Angle of Attack and Armor Geometry
        self._plot_angle_of_attack(ammo, armor, impact_angle, self.axes[0, 0])
        
        # Panel 2: Penetration Mechanism (ammo-type specific)
        self._plot_penetration_mechanism(ammo, armor, penetration, effective_thickness,
                                       velocity_at_impact, can_defeat, self.axes[0, 1])
        
        # Panel 3: Behind-Armor Effects
        self._plot_behind_armor_effects(ammo, armor, penetration, effective_thickness,
                                      can_defeat, self.axes[1, 0])
        
        # Panel 4: Penetration Summary and Stats
        self._plot_penetration_summary(ammo, armor, range_m, impact_angle, penetration,
                                     effective_thickness, velocity_at_impact, 
                                     can_defeat, self.axes[1, 1])
        
        return self.fig
    
    def _plot_angle_of_attack(self, ammo, armor, impact_angle: float, ax):
        """Plot angle of attack and armor geometry."""
        ax.set_xlim(-2, 8)
        ax.set_ylim(-1, 6)
        
        # Draw armor plate
        armor_thickness = min(armor.thickness / 100, 2.0)  # Scale for visualization
        armor_angle_rad = np.radians(90 - impact_angle)  # Convert to slope angle
        
        # Armor coordinates
        armor_x = [2, 6, 6 + armor_thickness * np.sin(armor_angle_rad), 
                  2 + armor_thickness * np.sin(armor_angle_rad)]
        armor_y = [2, 2, 2 - armor_thickness * np.cos(armor_angle_rad), 
                  2 - armor_thickness * np.cos(armor_angle_rad)]
        
        # Draw armor
        armor_color = self._get_armor_color(armor)
        ax.fill(armor_x, armor_y, color=armor_color, alpha=0.8, 
               label=f'{armor.armor_type.upper()} Armor')
        
        # Draw projectile approaching
        projectile_x = 0.5
        projectile_y = 3.0
        impact_x = 2.0
        impact_y = 2.0
        
        ax.arrow(projectile_x, projectile_y, impact_x - projectile_x - 0.2, 
                impact_y - projectile_y, head_width=0.1, head_length=0.1, 
                fc='red', ec='red', linewidth=2, label=f'{ammo.name}')
        
        # Draw vertical reference line
        ax.plot([impact_x, impact_x], [impact_y, impact_y + 1.5], 
               'k--', alpha=0.5, label='Vertical Reference')
        
        # Draw angle arc
        angle_arc = patches.Arc((impact_x, impact_y), 1, 1, theta1=90-impact_angle, theta2=90,
                               color='blue', linewidth=2)
        ax.add_patch(angle_arc)
        ax.text(impact_x + 0.3, impact_y + 0.5, f'{impact_angle:.1f}°', 
               fontsize=12, color='blue', fontweight='bold')
        
        # Add thickness annotations with better positioning
        effective_thickness = armor.get_effective_thickness(ammo.penetration_type, impact_angle)
        ax.text(4, 0.2, f'Nominal: {armor.thickness:.0f}mm\nEffective: {effective_thickness:.0f}mm RHA', 
               fontsize=9, ha='center', bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax.set_title('Angle of Attack & Armor Geometry')
        ax.set_xlabel('Distance (arbitrary units)')
        ax.set_ylabel('Height (arbitrary units)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
    
    def _plot_penetration_mechanism(self, ammo, armor, penetration: float, 
                                  effective_thickness: float, velocity: float,
                                  can_defeat: bool, ax):
        """Plot ammunition-specific penetration mechanism."""
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6)
        
        # Draw armor cross-section
        armor_x = [3, 7, 7, 3]
        armor_y = [1, 1, 5, 5]
        armor_color = self._get_armor_color(armor)
        ax.fill(armor_x, armor_y, color=armor_color, alpha=0.8, label='Armor')
        
        if ammo.penetration_type == 'kinetic':
            self._draw_kinetic_penetration(ammo, can_defeat, ax)
        elif ammo.penetration_type == 'chemical':
            self._draw_chemical_penetration(ammo, can_defeat, ax)
        elif ammo.penetration_type == 'spalling':
            self._draw_spalling_mechanism(ammo, can_defeat, ax)
        
        # Add penetration result
        result_text = "PENETRATION" if not can_defeat else "NO PENETRATION"
        result_color = 'red' if not can_defeat else 'green'
        ax.text(5, 0.5, result_text, fontsize=14, fontweight='bold', 
               color=result_color, ha='center')
        
        # Add performance metrics with better spacing
        metrics_text = f'Pen: {penetration:.0f}mm RHA\nArmor: {effective_thickness:.0f}mm RHA\nVel: {velocity:.0f} m/s'
        margin = abs(penetration - effective_thickness)
        margin_text = f'Overmatch: {margin:.0f}mm' if not can_defeat else f'Safety Margin: {margin:.0f}mm'
        full_metrics = f'{metrics_text}\n{margin_text}'
        
        ax.text(0.5, 5.7, full_metrics, fontsize=9, va='top',
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        ax.set_title(f'{ammo.penetration_type.title()} Penetration Mechanism')
        ax.set_xlabel('Armor Cross-Section')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _draw_kinetic_penetration(self, ammo, can_defeat: bool, ax):
        """Draw kinetic penetration mechanism (APFSDS, AP, APCR)."""
        if hasattr(ammo, 'penetrator_diameter'):
            # APFSDS - long rod penetrator
            penetrator_x = [1, 3 + (0 if can_defeat else 2.5)]
            penetrator_y = [3, 3]
            ax.plot(penetrator_x, penetrator_y, 'k-', linewidth=8, label='Penetrator Rod')
            
            # Show sabot discard
            ax.plot([0.5, 0.8], [2.7, 2.5], 'gray', linewidth=4, alpha=0.6)
            ax.plot([0.5, 0.8], [3.3, 3.5], 'gray', linewidth=4, alpha=0.6)
            ax.text(0.6, 2.0, 'Sabot\nDiscard', fontsize=8, ha='center')
        else:
            # AP/APCR - solid shot
            penetrator_x = [1.5, 3 + (0 if can_defeat else 1.5)]
            penetrator_y = [3, 3]
            ax.plot(penetrator_x, penetrator_y, 'darkred', linewidth=6, label='AP Projectile')
        
        if not can_defeat:
            # Show penetration hole
            hole = patches.Circle((5, 3), 0.2, color='black', alpha=0.8)
            ax.add_patch(hole)
            
            # Show behind-armor debris
            debris_x = np.random.uniform(7.2, 9, 8)
            debris_y = np.random.uniform(1.5, 4.5, 8)
            ax.scatter(debris_x, debris_y, c='red', s=20, alpha=0.7, label='Armor Fragments')
    
    def _draw_chemical_penetration(self, ammo, can_defeat: bool, ax):
        """Draw HEAT penetration mechanism."""
        # Draw warhead
        warhead = patches.Circle((1.5, 3), 0.4, color='orange', alpha=0.8)
        ax.add_patch(warhead)
        ax.text(1.5, 3, 'HEAT\nWarhead', fontsize=8, ha='center', va='center')
        
        # Draw shaped charge jet
        if not can_defeat:
            # Penetrating jet
            ax.plot([2, 8], [3, 3], 'yellow', linewidth=4, alpha=0.8, label='Shaped Charge Jet')
            ax.plot(8, 3, 'o', color='white', markersize=6)
            
            # Penetration channel
            channel = patches.Rectangle((3, 2.9), 4, 0.2, color='yellow', alpha=0.6)
            ax.add_patch(channel)
        else:
            # Disrupted jet
            jet_fragments_x = np.linspace(2, 6, 10)
            jet_fragments_y = 3 + np.random.uniform(-0.3, 0.3, 10)
            ax.scatter(jet_fragments_x, jet_fragments_y, c='orange', s=15, alpha=0.7, label='Disrupted Jet')
        
        # Show explosive effect
        explosion_circle = patches.Circle((1.5, 3), 0.8, fill=False, 
                                        edgecolor='red', linewidth=2, linestyle='--')
        ax.add_patch(explosion_circle)
    
    def _draw_spalling_mechanism(self, ammo, can_defeat: bool, ax):
        """Draw HESH spalling mechanism."""
        # Draw HESH shell
        shell = patches.Circle((1.5, 3), 0.3, color='purple', alpha=0.8)
        ax.add_patch(shell)
        ax.text(1.5, 3, 'HESH', fontsize=8, ha='center', va='center')
        
        # Show plastic explosive spread
        explosive_patch = patches.Wedge((3, 3), 0.5, -30, 30, color='red', alpha=0.6)
        ax.add_patch(explosive_patch)
        ax.text(3.5, 3.3, 'Plastic\nExplosive', fontsize=8, ha='center')
        
        if not can_defeat:
            # Show spall cone
            spall_x = [7, 8.5, 8.5, 7]
            spall_y = [2.5, 2, 4, 3.5]
            ax.fill(spall_x, spall_y, color='gray', alpha=0.7, label='Spall Cone')
            
            # Spall fragments
            fragment_x = np.random.uniform(7.5, 9, 12)
            fragment_y = np.random.uniform(2, 4, 12)
            ax.scatter(fragment_x, fragment_y, c='darkgray', s=15, alpha=0.8, label='Spall Fragments')
        else:
            # Show shock wave absorption
            for r in [0.3, 0.6, 0.9]:
                shock_ring = patches.Circle((5, 3), r, fill=False, edgecolor='blue', alpha=0.4)
                ax.add_patch(shock_ring)
            ax.text(5, 1.5, 'Shock Absorbed', fontsize=10, ha='center', color='blue')
    
    def _plot_behind_armor_effects(self, ammo, armor, penetration: float,
                                 effective_thickness: float, can_defeat: bool, ax):
        """Plot behind-armor effects and damage."""
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6)
        
        # Draw crew compartment/interior
        interior = patches.Rectangle((1, 1), 8, 4, fill=False, 
                                   edgecolor='black', linewidth=2)
        ax.add_patch(interior)
        ax.text(5, 0.5, 'Crew Compartment / Interior', fontsize=12, ha='center')
        
        # Draw equipment positions
        equipment_positions = [(2, 3), (4, 2), (6, 4), (8, 2.5)]
        for i, (x, y) in enumerate(equipment_positions):
            equip = patches.Rectangle((x-0.3, y-0.3), 0.6, 0.6, color='brown', alpha=0.6)
            ax.add_patch(equip)
            ax.text(x, y, f'E{i+1}', fontsize=8, ha='center', va='center')
        
        if not can_defeat:
            # Show penetration effects based on ammo type
            if ammo.penetration_type == 'kinetic':
                # High velocity fragments
                fragment_x = np.random.uniform(1.5, 8, 15)
                fragment_y = np.random.uniform(1.5, 4.5, 15)
                ax.scatter(fragment_x, fragment_y, c='red', s=25, alpha=0.8, 
                          marker='*', label='High-Velocity Fragments')
                ax.arrow(1, 3, 6, 0, head_width=0.2, head_length=0.3, 
                        fc='darkred', ec='darkred', linewidth=3)
                
            elif ammo.penetration_type == 'chemical':
                # HEAT jet path and molten metal
                jet_x = np.linspace(1, 7, 20)
                jet_y = 3 + np.random.uniform(-0.2, 0.2, 20)
                ax.plot(jet_x, jet_y, 'yellow', linewidth=3, alpha=0.8, label='Jet Path')
                
                splash_x = np.random.uniform(6, 9, 10)
                splash_y = np.random.uniform(2, 4, 10)
                ax.scatter(splash_x, splash_y, c='orange', s=30, alpha=0.7, 
                          marker='o', label='Molten Metal')
                
            elif ammo.penetration_type == 'spalling':
                # Spall fragment cone
                spall_angles = np.linspace(-np.pi/4, np.pi/4, 20)
                spall_distances = np.random.uniform(2, 6, 20)
                spall_x = 1 + spall_distances * np.cos(spall_angles)
                spall_y = 3 + spall_distances * np.sin(spall_angles)
                ax.scatter(spall_x, spall_y, c='gray', s=20, alpha=0.8, 
                          marker='s', label='Spall Fragments')
            
            # Mark damaged equipment
            num_damaged = min(3, len(equipment_positions))
            damaged_indices = np.random.choice(len(equipment_positions), 
                                             size=num_damaged, replace=False)
            for i in damaged_indices:
                x, y = equipment_positions[i]
                damage_indicator = patches.Rectangle((x-0.35, y-0.35), 0.7, 0.7, 
                                                   fill=False, edgecolor='red', linewidth=3)
                ax.add_patch(damage_indicator)
                ax.text(x, y-0.6, 'DAMAGED', fontsize=6, ha='center', color='red')
        else:
            # No penetration
            ax.text(5, 3, 'ARMOR HOLDS\nNO BEHIND-ARMOR EFFECTS', 
                   fontsize=12, fontweight='bold', ha='center', va='center',
                   bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        ax.set_title('Behind-Armor Effects')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_penetration_summary(self, ammo, armor, range_m: float, impact_angle: float,
                                penetration: float, effective_thickness: float, 
                                velocity: float, can_defeat: bool, ax):
        """Plot penetration test summary and statistics."""
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.96, 'PENETRATION TEST SUMMARY', fontsize=14, fontweight='bold',
               ha='center', transform=ax.transAxes)
        
        # Create a more compact layout with two columns
        # Left column - Test parameters
        left_text = f"""AMMUNITION: {ammo.name[:20]}...
Type: {ammo.penetration_type.upper()}
Caliber: {ammo.caliber:.0f}mm
Velocity: {ammo.muzzle_velocity:.0f} m/s
Mass: {ammo.mass:.1f} kg

ARMOR: {armor.name[:20]}...
Type: {armor.armor_type.upper()}
Thickness: {armor.thickness:.0f}mm
Density: {armor.density:.0f} kg/m³"""
        
        ax.text(0.05, 0.88, left_text, fontsize=9, ha='left', va='top',
               transform=ax.transAxes, family='monospace')
        
        # Right column - Engagement data
        right_text = f"""ENGAGEMENT:
Range: {range_m:.0f} m
Angle: {impact_angle:.1f}°
Impact Vel: {velocity:.0f} m/s

RESULTS:
Penetration: {penetration:.1f} mm
Armor Effect: {effective_thickness:.1f} mm
Margin: {abs(penetration - effective_thickness):.1f} mm
Protection: {effective_thickness/armor.thickness:.2f}x"""
        
        ax.text(0.55, 0.88, right_text, fontsize=9, ha='left', va='top',
               transform=ax.transAxes, family='monospace')
        
        # Main result in center
        result_color = 'green' if can_defeat else 'red'
        result_text = 'ARMOR DEFEATS PROJECTILE' if can_defeat else 'PROJECTILE PENETRATES ARMOR'
        
        ax.text(0.5, 0.15, result_text, fontsize=12, fontweight='bold',
               ha='center', va='center', color=result_color, transform=ax.transAxes,
               bbox=dict(boxstyle='round', facecolor='white', edgecolor=result_color, linewidth=2))
    
    def _get_armor_color(self, armor) -> str:
        """Get color for armor type visualization."""
        color_map = {
            'RHA': '#808080',
            'steel': '#696969',
            'composite': '#8B4513',
            'reactive': '#FF4500',
            'spaced': '#4682B4'
        }
        return color_map.get(armor.armor_type, '#808080')
    
    def save_plot(self, filename: str = 'penetration_analysis.png'):
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
            print(f"Penetration analysis plot saved as {filepath}")
    
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
