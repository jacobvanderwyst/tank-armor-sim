"""
Ballistics visualization for tank armor penetration simulation.

This module creates visual representations of projectile flight paths,
velocity decay, and trajectory characteristics.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import Tuple, List, Optional


class BallisticsVisualizer:
    """Visualizes ballistic trajectories and flight characteristics."""
    
    def __init__(self):
        """Initialize the ballistics visualizer."""
        self.fig = None
        self.ax = None
        
    def calculate_trajectory(self, ammo, range_m: float, firing_angle: float = 0.0,
                           num_points: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate ballistic trajectory points.
        
        Args:
            ammo: Ammunition object
            range_m: Target range in meters
            firing_angle: Firing angle in degrees (0 = horizontal)
            num_points: Number of trajectory points to calculate
            
        Returns:
            Tuple of (x_points, y_points, velocity_points)
        """
        # Convert firing angle to radians
        angle_rad = np.radians(firing_angle)
        
        # Calculate trajectory points
        x_points = np.linspace(0, range_m, num_points)
        y_points = np.zeros(num_points)
        velocity_points = np.zeros(num_points)
        
        # Simplified ballistic model with drag and gravity
        gravity = 9.81  # m/s²
        drag_coefficient = 0.0001  # Simplified drag from base_ammo.py
        
        for i, x in enumerate(x_points):
            # Time of flight to this point (simplified)
            t = x / (ammo.muzzle_velocity * np.cos(angle_rad))
            
            # Y position with gravity and firing angle
            y_points[i] = x * np.tan(angle_rad) - (gravity * x**2) / (2 * ammo.muzzle_velocity**2 * np.cos(angle_rad)**2)
            
            # Velocity at this point (using the same model as ammunition classes)
            velocity_points[i] = ammo.get_velocity_at_range(x)
            
        return x_points, y_points, velocity_points
    
    def visualize_flight_path(self, ammo, armor, range_m: float, impact_angle: float,
                             show_velocity: bool = True) -> plt.Figure:
        """
        Create a comprehensive flight path visualization.
        
        Args:
            ammo: Ammunition object
            armor: Armor object
            range_m: Engagement range in meters
            impact_angle: Impact angle in degrees from vertical
            show_velocity: Whether to show velocity decay subplot
            
        Returns:
            Matplotlib figure object
        """
        # Calculate trajectory
        x_traj, y_traj, v_traj = self.calculate_trajectory(ammo, range_m)
        
        # Create figure with subplots and better spacing
        if show_velocity:
            self.fig, (self.ax, ax_vel) = plt.subplots(2, 1, figsize=(14, 12))
            self.fig.subplots_adjust(left=0.08, bottom=0.08, right=0.95, top=0.92, hspace=0.3)
        else:
            self.fig, self.ax = plt.subplots(1, 1, figsize=(14, 8))
            self.fig.subplots_adjust(left=0.08, bottom=0.1, right=0.95, top=0.9)
        
        self._plot_trajectory(ammo, armor, x_traj, y_traj, range_m, impact_angle)
        
        if show_velocity:
            self._plot_velocity_decay(x_traj, v_traj, ammo.muzzle_velocity, ax_vel)
        return self.fig
    
    def _plot_trajectory(self, ammo, armor, x_traj: np.ndarray, y_traj: np.ndarray,
                        range_m: float, impact_angle: float):
        """Plot the main trajectory visualization."""
        # Plot trajectory
        self.ax.plot(x_traj, y_traj, 'b-', linewidth=2, label=f'{ammo.name} Trajectory')
        
        # Mark launch point
        self.ax.plot(0, y_traj[0], 'go', markersize=10, label='Launch Point')
        
        # Mark target/impact point
        impact_x = range_m
        impact_y = np.interp(range_m, x_traj, y_traj)
        self.ax.plot(impact_x, impact_y, 'ro', markersize=10, label='Impact Point')
        
        # Draw armor representation at target (if armor is provided)
        if armor:
            self._draw_armor_target(impact_x, impact_y, armor, impact_angle)
        
        # Draw projectile at various points along trajectory
        self._draw_projectile_instances(x_traj, y_traj, ammo)
        
        # Add angle annotation at impact
        self._add_angle_annotation(impact_x, impact_y, impact_angle)
        
        # Formatting
        self.ax.set_xlabel('Range (meters)')
        self.ax.set_ylabel('Height (meters)')
        
        # Handle case where armor is None
        armor_name = armor.name if armor else "No Target"
        self.ax.set_title(f'{ammo.name} vs {armor_name} - Ballistic Trajectory')
        
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()
        self.ax.axis('equal')
        
        # Set reasonable axis limits
        x_margin = range_m * 0.1
        self.ax.set_xlim(-x_margin, range_m + x_margin)
        
    def _draw_armor_target(self, x: float, y: float, armor, impact_angle: float):
        """Draw armor target representation at impact point."""
        if armor is None:
            return
            
        armor_length = 100  # Visual length in meters
        armor_thickness_scale = armor.thickness / 10  # Scale for visualization
        
        # Calculate armor slope based on impact angle
        # Note: impact_angle is from vertical, so 0° = perpendicular
        armor_slope_rad = np.radians(90 - impact_angle)  # Convert to slope angle
        
        # Armor front face
        dx = armor_length * np.cos(armor_slope_rad) / 2
        dy = armor_length * np.sin(armor_slope_rad) / 2
        
        x1, y1 = x - dx, y - dy
        x2, y2 = x + dx, y + dy
        
        # Draw armor plate
        armor_color = self._get_armor_color(armor)
        self.ax.plot([x1, x2], [y1, y2], color=armor_color, linewidth=6, 
                    label=f'{armor.armor_type.upper()} Armor')
        
        # Draw thickness indicator (perpendicular to armor face)
        thickness_dx = armor_thickness_scale * np.sin(armor_slope_rad)
        thickness_dy = -armor_thickness_scale * np.cos(armor_slope_rad)
        
        # Armor back face
        self.ax.plot([x1 + thickness_dx, x2 + thickness_dx], 
                    [y1 + thickness_dy, y2 + thickness_dy], 
                    color=armor_color, linewidth=4, alpha=0.7)
        
        # Connect front and back faces
        self.ax.plot([x1, x1 + thickness_dx], [y1, y1 + thickness_dy], 
                    color=armor_color, linewidth=2, alpha=0.7)
        self.ax.plot([x2, x2 + thickness_dx], [y2, y2 + thickness_dy], 
                    color=armor_color, linewidth=2, alpha=0.7)
    
    def _draw_projectile_instances(self, x_traj: np.ndarray, y_traj: np.ndarray, ammo):
        """Draw projectile instances at key points along trajectory."""
        # Draw projectiles at 25%, 50%, 75%, and 100% of flight
        positions = [0.25, 0.5, 0.75, 1.0]
        
        for pos in positions:
            idx = int((len(x_traj) - 1) * pos)
            x, y = x_traj[idx], y_traj[idx]
            
            # Draw projectile based on ammunition type
            if ammo.penetration_type == 'kinetic':
                # Draw long rod penetrator
                self.ax.plot(x, y, 'ks', markersize=4, alpha=0.6)
            elif ammo.penetration_type == 'chemical':
                # Draw HEAT warhead
                self.ax.plot(x, y, 'rs', markersize=6, alpha=0.6)
            else:
                # Generic projectile
                self.ax.plot(x, y, 'bs', markersize=5, alpha=0.6)
    
    def _add_angle_annotation(self, x: float, y: float, angle: float):
        """Add angle annotation at impact point."""
        # Draw angle arc
        angle_radius = 50  # Visual radius
        angle_arc = patches.Arc((x, y), 2 * angle_radius, 2 * angle_radius,
                              theta1=90 - angle, theta2=90, color='red', linewidth=2)
        self.ax.add_patch(angle_arc)
        
        # Add angle text
        text_x = x + angle_radius * 0.7 * np.cos(np.radians(90 - angle/2))
        text_y = y + angle_radius * 0.7 * np.sin(np.radians(90 - angle/2))
        self.ax.annotate(f'{angle:.1f}°', (text_x, text_y), 
                        fontsize=10, color='red', fontweight='bold',
                        ha='center', va='center')
    
    def _plot_velocity_decay(self, x_points: np.ndarray, velocities: np.ndarray,
                           muzzle_velocity: float, ax):
        """Plot velocity decay over range."""
        ax.plot(x_points, velocities, 'g-', linewidth=2, label='Projectile Velocity')
        ax.axhline(y=muzzle_velocity, color='r', linestyle='--', alpha=0.7,
                  label=f'Muzzle Velocity ({muzzle_velocity} m/s)')
        
        # Mark velocity at impact
        ax.plot(x_points[-1], velocities[-1], 'ro', markersize=8,
               label=f'Impact Velocity ({velocities[-1]:.1f} m/s)')
        
        ax.set_xlabel('Range (meters)')
        ax.set_ylabel('Velocity (m/s)')
        ax.set_title('Projectile Velocity vs Range')
        ax.grid(True, alpha=0.3)
        ax.legend()
    
    def _get_armor_color(self, armor) -> str:
        """Get color for armor type visualization."""
        color_map = {
            'RHA': '#808080',           # Gray
            'steel': '#696969',         # Dark gray
            'composite': '#8B4513',     # Brown
            'reactive': '#FF4500',      # Orange-red
            'spaced': '#4682B4'         # Steel blue
        }
        return color_map.get(armor.armor_type, '#808080')
    
    def save_plot(self, filename: str = 'ballistic_trajectory.png'):
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
            print(f"Trajectory plot saved as {filepath}")
    
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
