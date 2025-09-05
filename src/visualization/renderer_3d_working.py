"""
Working 3D Renderer for Interactive Tank Armor Simulation Visualizations

This module provides a simplified but functional 3D renderer that works with 
the existing codebase and creates interactive matplotlib 3D visualizations.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.patches as patches
from matplotlib.widgets import Slider, Button, CheckButtons
import matplotlib.animation as animation
from typing import List, Dict, Tuple, Optional, Any, Callable
import math

from .interactive_3d import Interactive3DVisualizer


class Working3DRenderer:
    """
    Simplified 3D rendering class that creates interactive matplotlib visualizations.
    """
    
    def __init__(self, figsize=(14, 10), style='professional'):
        """
        Initialize the 3D renderer.
        
        Args:
            figsize: Figure size tuple
            style: Visualization style ('professional', 'tactical', 'educational')
        """
        self.figsize = figsize
        self.style = style
        self.fig = None
        self.ax_3d = None
        
        # Interaction state
        self.current_view_angle = [30, 45]  # elevation, azimuth
        
        # 3D visualization components
        self.visualizer = Interactive3DVisualizer()
        
        # Color schemes
        self.color_schemes = self._setup_color_schemes()
        
    def _setup_color_schemes(self) -> Dict[str, Dict]:
        """Set up color schemes for different visualization styles."""
        
        schemes = {
            'professional': {
                'tank_hull': '#2E4057',      # Dark blue-gray
                'tank_turret': '#3C5875',    # Medium blue-gray  
                'tank_gun': '#1A1A1A',      # Dark gray
                'tank_tracks': '#333333',    # Charcoal
                'armor_zones': '#FF6B6B',    # Red for armor
                'trajectory': '#4ECDC4',     # Teal for trajectory
                'impact_point': '#FFE66D',   # Yellow for impact
                'penetration': '#FF4757',    # Red for penetration
                'background': '#F8F9FA'      # Light background
            },
            'tactical': {
                'tank_hull': '#2D5016',      # Military green
                'tank_turret': '#3E6B1F',    # Darker green
                'tank_gun': '#1C1C1C',      # Black
                'tank_tracks': '#2C2C2C',    # Dark gray
                'armor_zones': '#C0392B',    # Dark red
                'trajectory': '#F39C12',     # Orange trajectory
                'impact_point': '#E74C3C',   # Red impact
                'penetration': '#8E44AD',    # Purple penetration
                'background': '#2C3E50'      # Dark background
            },
            'educational': {
                'tank_hull': '#3498DB',      # Blue hull
                'tank_turret': '#2980B9',    # Darker blue
                'tank_gun': '#34495E',       # Dark blue-gray
                'tank_tracks': '#7F8C8D',    # Gray tracks
                'armor_zones': '#E74C3C',    # Red zones
                'trajectory': '#F1C40F',     # Yellow trajectory
                'impact_point': '#E67E22',   # Orange impact
                'penetration': '#9B59B6',    # Purple penetration
                'background': '#ECF0F1'      # Light gray background
            }
        }
        
        return schemes
    
    def create_3d_visualization(self, ammunition, armor, 
                               target_range: float = 2000.0,
                               impact_angle: float = 15.0) -> plt.Figure:
        """
        Create a working 3D visualization.
        
        Args:
            ammunition: Ammunition object
            armor: Armor object
            target_range: Distance to target in meters
            impact_angle: Impact angle in degrees
            
        Returns:
            Complete matplotlib figure with 3D visualization
        """
        
        # Set up the figure and 3D axis
        self.fig = plt.figure(figsize=self.figsize)
        self.ax_3d = self.fig.add_subplot(111, projection='3d')
        
        # Set up the 3D environment
        self._setup_3d_environment()
        
        # Create and render tank model
        self._render_simple_tank()
        
        # Calculate and render trajectory
        self._render_simple_trajectory(target_range)
        
        # Calculate penetration analysis
        penetration = ammunition.calculate_penetration(target_range/1000, impact_angle)
        effective_thickness = armor.get_effective_thickness('kinetic', impact_angle)
        
        # Render impact analysis
        self._render_impact_analysis(penetration, effective_thickness, target_range)
        
        # Apply styling
        self._apply_visual_styling(ammunition.name, armor.name, 
                                 penetration, effective_thickness)
        
        # Set initial view
        self.ax_3d.view_init(elev=self.current_view_angle[0], 
                           azim=self.current_view_angle[1])
        
        return self.fig
    
    def _setup_3d_environment(self):
        """Set up the 3D plotting environment and axes."""
        
        colors = self.color_schemes[self.style]
        
        # Set background color
        self.fig.patch.set_facecolor(colors['background'])
        
        # Set axis labels and styling
        self.ax_3d.set_xlabel('Distance (m)', fontsize=10, fontweight='bold')
        self.ax_3d.set_ylabel('Lateral Offset (m)', fontsize=10, fontweight='bold')
        self.ax_3d.set_zlabel('Height (m)', fontsize=10, fontweight='bold')
        
        # Set reasonable axis limits for tank scenario
        self.ax_3d.set_xlim(-5, 25)   # Tank at 0, trajectory extends beyond
        self.ax_3d.set_ylim(-8, 8)    # Lateral spread
        self.ax_3d.set_zlim(-1, 8)    # Ground to reasonable height
        
        # Grid and styling
        self.ax_3d.grid(True, alpha=0.3)
        
        # Create ground plane
        self._create_ground_plane()
    
    def _create_ground_plane(self):
        """Create a ground plane for reference."""
        
        # Ground plane vertices
        ground_x = [-5, 25, 25, -5]
        ground_y = [-8, -8, 8, 8]
        ground_z = [0, 0, 0, 0]
        
        # Create ground plane
        ground_verts = [list(zip(ground_x, ground_y, ground_z))]
        
        ground_collection = Poly3DCollection(ground_verts, alpha=0.2, 
                                           facecolors='lightgray', 
                                           edgecolors='gray', linewidths=0.5)
        
        self.ax_3d.add_collection3d(ground_collection)
    
    def _render_simple_tank(self):
        """Render a simplified 3D tank model."""
        
        colors = self.color_schemes[self.style]
        
        # Tank positioned at origin
        tank_length = 7.0
        tank_width = 3.7
        tank_height = 2.4
        
        # Hull vertices (simplified box with sloped front)
        hull_vertices = np.array([
            # Rear face
            [-tank_length/2, -tank_width/2, 0],
            [-tank_length/2, tank_width/2, 0], 
            [-tank_length/2, tank_width/2, tank_height*0.75],
            [-tank_length/2, -tank_width/2, tank_height*0.75],
            
            # Front face (sloped)
            [tank_length/2, -tank_width/2, 0.3],
            [tank_length/2, tank_width/2, 0.3],
            [tank_length/2, tank_width/2, tank_height*0.75],
            [tank_length/2, -tank_width/2, tank_height*0.75],
        ])
        
        # Hull faces
        hull_faces = [
            [0, 1, 2, 3],  # Rear
            [4, 7, 6, 5],  # Front 
            [0, 4, 5, 1],  # Bottom
            [2, 6, 7, 3],  # Top
            [0, 3, 7, 4],  # Left side
            [1, 5, 6, 2]   # Right side
        ]
        
        hull_collection = Poly3DCollection([hull_vertices[face] for face in hull_faces], 
                                         alpha=0.8, facecolors=colors['tank_hull'],
                                         edgecolors='black', linewidths=0.5)
        self.ax_3d.add_collection3d(hull_collection)
        
        # Turret (simplified cylinder)
        turret_center = [1.0, 0, tank_height*0.75]
        turret_radius = 1.5
        turret_height = 1.0
        
        # Create turret cylinder
        angles = np.linspace(0, 2*np.pi, 16)
        turret_bottom = []
        turret_top = []
        
        for angle in angles:
            x = turret_center[0] + turret_radius * np.cos(angle)
            y = turret_center[1] + turret_radius * np.sin(angle)
            turret_bottom.append([x, y, turret_center[2]])
            turret_top.append([x, y, turret_center[2] + turret_height])
        
        # Turret side faces
        turret_faces = []
        for i in range(len(angles)):
            next_i = (i + 1) % len(angles)
            face = [turret_bottom[i], turret_bottom[next_i], 
                   turret_top[next_i], turret_top[i]]
            turret_faces.append(face)
        
        turret_collection = Poly3DCollection(turret_faces, alpha=0.8, 
                                           facecolors=colors['tank_turret'],
                                           edgecolors='black', linewidths=0.5)
        self.ax_3d.add_collection3d(turret_collection)
        
        # Gun barrel
        gun_start = [turret_center[0] + 1.5, 0, turret_center[2] + 0.5]
        gun_end = [gun_start[0] + 5.5, 0, gun_start[2]]
        
        self.ax_3d.plot([gun_start[0], gun_end[0]], 
                       [gun_start[1], gun_end[1]], 
                       [gun_start[2], gun_end[2]], 
                       color=colors['tank_gun'], linewidth=8, alpha=0.9)
    
    def _render_simple_trajectory(self, target_range: float):
        """Render a simplified ballistic trajectory."""
        
        colors = self.color_schemes[self.style]
        
        # Convert range from meters to our coordinate system (scaled down)
        range_scaled = min(target_range / 100, 20)  # Scale to fit our view
        
        # Create parabolic trajectory
        x_points = np.linspace(-5, range_scaled, 50)
        launch_height = 3.0
        impact_height = 0.5
        
        # Parabolic trajectory calculation
        z_points = launch_height - (launch_height - impact_height) * ((x_points + 5) / (range_scaled + 5))**2
        z_points -= 0.1 * ((x_points + 5) / (range_scaled + 5))**1.5  # Add some drop
        y_points = np.zeros_like(x_points)
        
        # Plot trajectory line
        self.ax_3d.plot(x_points, y_points, z_points, 
                       color=colors['trajectory'], linewidth=3, alpha=0.8,
                       label='Ballistic Trajectory')
        
        # Mark launch point
        self.ax_3d.scatter([-5], [0], [launch_height], 
                         c='green', s=100, marker='^', 
                         edgecolors='black', linewidth=2, 
                         label='Launch Point')
        
        # Mark impact point
        self.ax_3d.scatter([range_scaled], [0], [impact_height], 
                         c=colors['impact_point'], s=150, marker='X', 
                         edgecolors='black', linewidth=2, 
                         label='Impact Point')
        
        return range_scaled, impact_height
    
    def _render_impact_analysis(self, penetration: float, effective_thickness: float,
                               target_range: float):
        """Render impact analysis visualization."""
        
        colors = self.color_schemes[self.style]
        range_scaled = min(target_range / 100, 20)
        
        # Impact point
        impact_point = [range_scaled, 0, 0.5]
        
        # Penetration success visualization
        if penetration > effective_thickness:
            # Successful penetration - show penetration channel
            channel_end = [impact_point[0], impact_point[1], impact_point[2] - 0.3]
            
            self.ax_3d.plot([impact_point[0], channel_end[0]], 
                           [impact_point[1], channel_end[1]], 
                           [impact_point[2], channel_end[2]], 
                           color=colors['penetration'], linewidth=6, alpha=0.8,
                           label='Penetration Channel')
            
            # Behind-armor effects (spall cone)
            apex = channel_end
            cone_height = 1.0
            cone_radius = 0.5
            
            # Create simple spall cone
            angles = np.linspace(0, 2*np.pi, 8)
            spall_base = []
            
            for angle in angles:
                x = apex[0] + cone_radius * np.cos(angle)
                y = apex[1] + cone_radius * np.sin(angle)
                z = apex[2] - cone_height
                spall_base.append([x, y, z])
            
            # Spall cone faces
            spall_faces = []
            for i in range(len(angles)):
                next_i = (i + 1) % len(angles)
                face = [apex, spall_base[i], spall_base[next_i]]
                spall_faces.append(face)
            
            spall_collection = Poly3DCollection(spall_faces, alpha=0.5,
                                              facecolors='orange',
                                              edgecolors='darkorange',
                                              linewidths=1)
            self.ax_3d.add_collection3d(spall_collection)
            
        else:
            # Failed penetration - show impact crater
            crater_radius = 0.2
            angles = np.linspace(0, 2*np.pi, 12)
            crater_points = []
            
            for angle in angles:
                x = impact_point[0] + crater_radius * np.cos(angle)
                y = impact_point[1] + crater_radius * np.sin(angle)
                crater_points.append([x, y, impact_point[2]])
            
            crater_collection = Poly3DCollection([crater_points], alpha=0.6,
                                               facecolors='gray',
                                               edgecolors='darkgray')
            self.ax_3d.add_collection3d(crater_collection)
    
    def _apply_visual_styling(self, ammo_name: str, armor_name: str, 
                            penetration: float, effective_thickness: float):
        """Apply professional visual styling to the plot."""
        
        # Set title
        result = "PENETRATION" if penetration > effective_thickness else "NO PENETRATION"
        self.fig.suptitle(f'3D Tank Armor Analysis - {result}', 
                         fontsize=16, fontweight='bold', y=0.95)
        
        # Add detailed information
        info_text = f"{ammo_name} vs {armor_name}\n"
        info_text += f"Penetration: {penetration:.0f}mm RHA\n"
        info_text += f"Armor: {effective_thickness:.0f}mm RHA\n"
        info_text += f"Result: {result}"
        
        self.ax_3d.text2D(0.02, 0.98, info_text, transform=self.ax_3d.transAxes,
                         fontsize=10, verticalalignment='top',
                         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # Customize axis appearance
        self.ax_3d.tick_params(axis='both', labelsize=8)
        
        # Add legend
        self.ax_3d.legend(loc='upper right', bbox_to_anchor=(1.0, 0.85), fontsize=9)
        
        # Tight layout
        plt.tight_layout()
    
    def save_visualization(self, filename: str, dpi: int = 300):
        """Save the current 3D visualization to file."""
        
        if self.fig:
            self.fig.savefig(filename, dpi=dpi, bbox_inches='tight', 
                           facecolor=self.fig.get_facecolor(), 
                           edgecolor='none')
            print(f"3D visualization saved to: {filename}")
        else:
            print("No visualization to save. Create visualization first.")
    
    def show_visualization(self):
        """Display the interactive 3D visualization."""
        
        if self.fig:
            plt.show()
        else:
            print("No visualization to show. Create visualization first.")


# Simple animation class
class Simple3DAnimator(Working3DRenderer):
    """Simple animator for 3D visualizations."""
    
    def create_penetration_animation(self, ammunition, armor, 
                                   target_range: float = 2000.0,
                                   impact_angle: float = 15.0,
                                   duration: float = 3.0) -> animation.FuncAnimation:
        """Create a simple animated penetration sequence."""
        
        self.fig = plt.figure(figsize=self.figsize)
        self.ax_3d = self.fig.add_subplot(111, projection='3d')
        
        # Calculate penetration result
        penetration = ammunition.calculate_penetration(target_range/1000, impact_angle)
        effective_thickness = armor.get_effective_thickness('kinetic', impact_angle)
        penetrates = penetration > effective_thickness
        
        range_scaled = min(target_range / 100, 20)
        
        # Animation parameters
        fps = 20
        total_frames = int(duration * fps)
        
        def animate_frame(frame):
            self.ax_3d.clear()
            self._setup_3d_environment()
            self._render_simple_tank()
            
            progress = frame / total_frames
            
            if progress < 0.6:  # Projectile approach phase
                approach_progress = progress / 0.6
                projectile_x = -5 + approach_progress * (range_scaled + 5)
                projectile_z = 3 - 0.5 * approach_progress
                
                self.ax_3d.scatter([projectile_x], [0], [projectile_z],
                                 c='red', s=50, marker='o', alpha=0.8)
                
                # Show partial trajectory
                traj_end = int(approach_progress * 50)
                if traj_end > 0:
                    x_points = np.linspace(-5, projectile_x, traj_end)
                    z_points = 3 - 2.5 * ((x_points + 5) / (range_scaled + 5))**2
                    y_points = np.zeros_like(x_points)
                    
                    self.ax_3d.plot(x_points, y_points, z_points, 
                                   'r--', linewidth=2, alpha=0.6)
            
            elif progress < 0.8:  # Impact phase
                impact_progress = (progress - 0.6) / 0.2
                
                # Show full trajectory
                self._render_simple_trajectory(target_range)
                
                # Show expanding impact effect
                impact_size = impact_progress * 0.3
                if impact_size > 0:
                    self.ax_3d.scatter([range_scaled], [0], [0.5],
                                     c='orange', s=impact_size*1000, 
                                     alpha=0.7, marker='o')
            
            else:  # Post-impact effects
                effects_progress = (progress - 0.8) / 0.2
                
                # Show full trajectory
                self._render_simple_trajectory(target_range)
                
                # Show penetration analysis
                self._render_impact_analysis(penetration, effective_thickness, target_range)
            
            # Apply styling
            self.ax_3d.set_title(f'Animated Penetration Analysis - Frame {frame+1}/{total_frames}')
            self.ax_3d.view_init(elev=30, azim=45 + frame * 0.5)  # Slow rotation
        
        # Create animation
        anim = animation.FuncAnimation(self.fig, animate_frame, 
                                     frames=total_frames, 
                                     interval=1000/fps, 
                                     blit=False, repeat=True)
        
        return anim


# Export classes
__all__ = ['Working3DRenderer', 'Simple3DAnimator']
