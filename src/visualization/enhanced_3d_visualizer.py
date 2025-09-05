"""
Enhanced 3D Visualization System with Debug Logging and Accurate Trajectory Tracking

This module provides:
- Comprehensive debug logging for trajectory verification
- Accurate ballistic trajectory calculation using physics engine
- Truly interactive 3D visualization with mouse controls
- Enhanced tank modeling with realistic proportions
- Real-time projectile trajectory following
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
import matplotlib.animation as animation
from typing import List, Dict, Tuple, Optional, Any

# Optional ricochet modeling
try:
    from src.physics.ricochet_calculator import RicochetCalculator, RicochetParameters, RicochetResult
    _HAS_RICOCHET_CALC = True
except Exception:
    RicochetCalculator = None
    RicochetParameters = None
    RicochetResult = None
    _HAS_RICOCHET_CALC = False
from matplotlib.widgets import Slider, Button, CheckButtons
from typing import List, Dict, Tuple, Optional, Any
import logging
import math
import time
import json
import os
from dataclasses import dataclass

# Import our physics engine
from ..physics.advanced_physics import AdvancedPhysicsEngine, EnvironmentalConditions


@dataclass
class TrajectoryPoint:
    """Single point along projectile trajectory with debug information."""
    x: float
    y: float
    z: float
    velocity_x: float
    velocity_y: float
    velocity_z: float
    velocity_magnitude: float
    time: float
    drag_coefficient: float
    air_density: float
    angle_of_attack: float
    debug_info: Dict[str, Any]


class Enhanced3DDebugLogger:
    """Comprehensive debug logging system for 3D visualization."""
    
    def __init__(self, log_level: str = "DEBUG"):
        """Initialize debug logger."""
        self.logger = logging.getLogger("Enhanced3DVisualizer")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Create handler if doesn't exist
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_trajectory_calculation(self, ammo, target_range: float, 
                                 launch_angle: float, conditions: EnvironmentalConditions):
        """Log trajectory calculation parameters."""
        self.logger.info("=== TRAJECTORY CALCULATION START ===")
        self.logger.info(f"Ammunition: {ammo.name}")
        self.logger.info(f"Muzzle Velocity: {ammo.muzzle_velocity} m/s")
        self.logger.info(f"Mass: {ammo.mass} kg")
        self.logger.info(f"Caliber: {ammo.caliber} mm")
        self.logger.info(f"Target Range: {target_range} m")
        self.logger.info(f"Launch Angle: {launch_angle}°")
        self.logger.info(f"Environmental Conditions:")
        self.logger.info(f"  - Temperature: {conditions.temperature_celsius}°C")
        self.logger.info(f"  - Pressure: {conditions.air_pressure_kpa} kPa")
        self.logger.info(f"  - Humidity: {conditions.humidity_percent}%")
        self.logger.info(f"  - Altitude: {conditions.altitude_m} m")
        self.logger.info(f"  - Wind Speed: {conditions.wind_speed_ms} m/s")
        self.logger.info(f"  - Wind Angle: {conditions.wind_angle_deg}°")
    
    def log_trajectory_point(self, point: TrajectoryPoint, point_index: int):
        """Log detailed trajectory point information."""
        if point_index % 100 == 0:  # Log every 100th point to avoid spam
            self.logger.debug(f"Trajectory Point {point_index}:")
            self.logger.debug(f"  Position: ({point.x:.2f}, {point.y:.2f}, {point.z:.2f}) m")
            self.logger.debug(f"  Velocity: ({point.velocity_x:.2f}, {point.velocity_y:.2f}, {point.velocity_z:.2f}) m/s")
            self.logger.debug(f"  Speed: {point.velocity_magnitude:.2f} m/s")
            self.logger.debug(f"  Time: {point.time:.3f} s")
            self.logger.debug(f"  Cd: {point.drag_coefficient:.4f}")
            self.logger.debug(f"  Air Density: {point.air_density:.4f} kg/m³")
    
    def log_trajectory_summary(self, trajectory: List[TrajectoryPoint]):
        """Log trajectory calculation summary."""
        if not trajectory:
            self.logger.error("Empty trajectory calculated!")
            return
            
        final_point = trajectory[-1]
        self.logger.info("=== TRAJECTORY CALCULATION COMPLETE ===")
        self.logger.info(f"Total Points: {len(trajectory)}")
        self.logger.info(f"Flight Time: {final_point.time:.3f} s")
        self.logger.info(f"Final Position: ({final_point.x:.2f}, {final_point.y:.2f}, {final_point.z:.2f}) m")
        self.logger.info(f"Impact Velocity: {final_point.velocity_magnitude:.2f} m/s")
        self.logger.info(f"Impact Angle: {final_point.angle_of_attack:.2f}°")
        
        # Calculate trajectory statistics
        max_height = max(point.z for point in trajectory)
        max_range = max(point.x for point in trajectory)
        
        self.logger.info(f"Maximum Height: {max_height:.2f} m")
        self.logger.info(f"Maximum Range: {max_range:.2f} m")
    
    def log_visualization_creation(self, tank_model: Dict, trajectory: List[TrajectoryPoint]):
        """Log 3D visualization creation."""
        self.logger.info("=== 3D VISUALIZATION CREATION ===")
        self.logger.info(f"Tank Model Components: {list(tank_model.keys())}")
        self.logger.info(f"Trajectory Points for Visualization: {len(trajectory)}")
        
        if trajectory:
            self.logger.info("Trajectory Bounds:")
            x_coords = [p.x for p in trajectory]
            y_coords = [p.y for p in trajectory]
            z_coords = [p.z for p in trajectory]
            
            self.logger.info(f"  X: {min(x_coords):.2f} to {max(x_coords):.2f} m")
            self.logger.info(f"  Y: {min(y_coords):.2f} to {max(y_coords):.2f} m")
            self.logger.info(f"  Z: {min(z_coords):.2f} to {max(z_coords):.2f} m")


class Enhanced3DVisualizer:
    """Enhanced 3D visualization system with accurate trajectory tracking."""
    
    def __init__(self, figsize=(16, 12), debug_level="INFO"):
        """Initialize enhanced 3D visualizer."""
        self.figsize = figsize
        self.debug_logger = Enhanced3DDebugLogger(debug_level)
        self.physics_engine = AdvancedPhysicsEngine()
        
# Tank dimensions for collision/AABB (meters)
        self.tank_length_m = 9.8
        self.tank_width_m = 3.7
        self.tank_height_m = 3.0
        
        # Per-part material properties and behavior (approximate)
        # rha_factor: convert material to RHA-equivalent thickness
        # ricochet_threshold_deg: angle from normal above which ricochet likely
        # degrade_per_mm: additional loss of residual penetration per mm of path
        self.part_materials = {
            'hull':       {'thickness_mm': 600.0, 'rha_factor': 1.00, 'ricochet_threshold_deg': 75.0, 'degrade_per_mm': 0.02},
            'turret':     {'thickness_mm': 500.0, 'rha_factor': 1.10, 'ricochet_threshold_deg': 72.0, 'degrade_per_mm': 0.025},
            'left_track': {'thickness_mm': 60.0,  'rha_factor': 0.50, 'ricochet_threshold_deg': 80.0, 'degrade_per_mm': 0.01},
            'right_track':{'thickness_mm': 60.0,  'rha_factor': 0.50, 'ricochet_threshold_deg': 80.0, 'degrade_per_mm': 0.01}
        }
        
        # Visualization components
        self.fig = None
        self.ax = None
        self.trajectory_points = []
        self.tank_model = {}
        
        # Interactive controls
        self.animation = None
        self.is_interactive = True
        self.animation_speed = 1.0
        self.show_trajectory_debug = False
        # Overlay toggles
        self.show_channel_segments = True
        self.show_ricochet_overlay = True
        
        # Collision info and target AABB
        self.collision_info = None
        
        # Color schemes
        self.colors = {
            'tank_hull': '#2E4057',
            'tank_turret': '#3C5875',
            'tank_gun': '#1A1A1A',
            'trajectory': '#FF6B35',
            'projectile': '#FF0000',
            'impact': '#FFE66D',
            'ground': '#8B7355',
            'debug_points': '#00FF00'
        }
        
        # Metadata storage for exporting interactive datasets
        self.meta = {
            'ammunition': None,
            'armor': None,
            'environment': None,
            'parameters': None,
            'impact_analysis': None
        }
    
    def calculate_accurate_trajectory(self, ammunition, target_range: float,
                                    launch_angle: float = 0.0,
                                    environmental_conditions: Optional[EnvironmentalConditions] = None) -> List[TrajectoryPoint]:
        """Calculate accurate ballistic trajectory using physics engine."""
        
        # Default environmental conditions
        if environmental_conditions is None:
            environmental_conditions = EnvironmentalConditions()
        
        # Remember parameters and environment for export
        try:
            self._last_environmental_conditions = environmental_conditions
        except Exception:
            self._last_environmental_conditions = None
        self._last_parameters = {'target_range': target_range, 'launch_angle': launch_angle}
        
        # Log calculation start
        self.debug_logger.log_trajectory_calculation(
            ammunition, target_range, launch_angle, environmental_conditions
        )
        
        trajectory = []
        
        # Initial conditions
        dt = 0.001  # 1ms time step for accuracy
        # Robust numeric casts in case upstream supplies non-float types
        try:
            target_range = float(target_range)
        except Exception:
            target_range = 0.0
        try:
            launch_angle = float(launch_angle)
        except Exception:
            launch_angle = 0.0
        angle_rad = math.radians(launch_angle)
        
        # Initial velocity components
        try:
            v0 = float(ammunition.muzzle_velocity)
        except Exception:
            v0 = 0.0
        vx = v0 * math.cos(angle_rad)
        vy = 0.0  # No lateral component initially
        vz = v0 * math.sin(angle_rad)
        
        # Initial position (at gun muzzle)
        x, y, z = 0.0, 0.0, 2.4  # 2.4m gun height
        t = 0.0
        
        # Environmental parameters
        air_density = self.physics_engine.calculate_air_density(environmental_conditions)
        gravity = 9.80665
        
        # Wind components
        try:
            wind_speed = float(environmental_conditions.wind_speed_ms)
        except Exception:
            wind_speed = 0.0
        try:
            wind_angle_deg = float(environmental_conditions.wind_angle_deg)
        except Exception:
            wind_angle_deg = 0.0
        wind_vx = -wind_speed * math.cos(math.radians(wind_angle_deg))
        wind_vy = -wind_speed * math.sin(math.radians(wind_angle_deg))
        
        # Projectile parameters
        try:
            mass = float(ammunition.mass)
        except Exception:
            mass = 1.0
        try:
            caliber_mm = float(ammunition.caliber)
        except Exception:
            caliber_mm = 0.0
        cross_sectional_area = math.pi * (caliber_mm / 2000.0) ** 2  # mm to m
        
        point_index = 0
        
        # Realistic maximum range constants (from ballistic calculations)
        REALISTIC_MAX_RANGE = 15159  # meters (with 10% margin)
        
        # Integration loop - continue until ground impact or max range
        # Allow trajectory to continue until ground impact, but cap at realistic maximum range
        max_allowed_range = min(REALISTIC_MAX_RANGE, max(target_range * 2.0, 15000))  # At least 15km for long shots
        while z > 0 and x <= max_allowed_range and t < 120.0:
            
            # Current velocity relative to air
            v_rel_x = vx - wind_vx
            v_rel_y = vy - wind_vy
            v_rel_z = vz
            v_rel_mag = math.sqrt(v_rel_x**2 + v_rel_y**2 + v_rel_z**2)
            
            # Prevent division by zero
            if v_rel_mag < 0.1:
                break
            
            # Calculate drag
            cd = self.physics_engine.calculate_drag_coefficient(v_rel_mag, ammunition.penetration_type)
            drag_force = 0.5 * air_density * v_rel_mag**2 * cd * cross_sectional_area
            
            # Drag acceleration components
            if v_rel_mag > 0:
                drag_ax = -drag_force * (v_rel_x / v_rel_mag) / mass
                drag_ay = -drag_force * (v_rel_y / v_rel_mag) / mass
                drag_az = -drag_force * (v_rel_z / v_rel_mag) / mass
            else:
                drag_ax = drag_ay = drag_az = 0
            
            # Total acceleration
            ax = drag_ax
            ay = drag_ay
            az = drag_az - gravity
            
            # Create trajectory point with full debug info
            angle_of_attack = math.degrees(math.atan2(vz, math.sqrt(vx**2 + vy**2)))
            
            trajectory_point = TrajectoryPoint(
                x=x, y=y, z=z,
                velocity_x=vx, velocity_y=vy, velocity_z=vz,
                velocity_magnitude=v_rel_mag,
                time=t,
                drag_coefficient=cd,
                air_density=air_density,
                angle_of_attack=angle_of_attack,
                debug_info={
                    'drag_force': drag_force,
                    'acceleration': (ax, ay, az),
                    'wind_effect': (wind_vx, wind_vy),
                    'mach_number': v_rel_mag / 343.0
                }
            )
            
            trajectory.append(trajectory_point)
            self.debug_logger.log_trajectory_point(trajectory_point, point_index)
            
            # Update velocity and position using Euler integration
            vx += ax * dt
            vy += ay * dt
            vz += az * dt
            
            x += vx * dt
            y += vy * dt
            z += vz * dt
            
            t += dt
            point_index += 1
        
        # Log trajectory summary
        self.debug_logger.log_trajectory_summary(trajectory)
        self.trajectory_points = trajectory
        
        return trajectory
    
    def create_enhanced_tank_model(self, tank_type: str = "modern_mbt") -> Dict[str, Any]:
        """Create enhanced 3D tank model with realistic proportions."""
        
        self.debug_logger.logger.info(f"Creating enhanced tank model: {tank_type}")
        
        # Modern MBT dimensions (realistic proportions)
        tank_length = 9.8  # meters (M1A2 length)
        tank_width = 3.7   # meters
        hull_height = 1.8  # meters
        turret_height = 1.2 # meters
        
        tank_model = {}
        
        # Create hull with sloped front armor
        hull_vertices = self._create_realistic_hull(tank_length, tank_width, hull_height)
        tank_model['hull'] = {
            'vertices': hull_vertices,
            'faces': self._create_hull_faces(),
            'color': self.colors['tank_hull']
        }
        
        # Create turret
        turret_vertices = self._create_realistic_turret(tank_length, turret_height)
        tank_model['turret'] = {
            'vertices': turret_vertices,
            'faces': self._create_turret_faces(),
            'color': self.colors['tank_turret']
        }
        
        # Create gun barrel
        gun_vertices = self._create_realistic_gun()
        tank_model['gun'] = {
            'vertices': gun_vertices,
            'color': self.colors['tank_gun']
        }
        
        # Create tracks
        tank_model['tracks'] = self._create_realistic_tracks(tank_length, tank_width)
        
        self.tank_model = tank_model
        self.debug_logger.logger.info(f"Tank model created with {len(tank_model)} components")
        
        return tank_model
    
    def _create_realistic_hull(self, length: float, width: float, height: float) -> np.ndarray:
        """Create realistic hull with sloped frontal armor."""
        
        # Hull with sloped front (68° like M1A2)
        slope_angle = math.radians(68)  # From vertical
        front_slope_length = height * math.tan(slope_angle)
        
        vertices = np.array([
            # Rear face (vertical)
            [-length/2, -width/2, 0], [-length/2, width/2, 0],
            [-length/2, width/2, height], [-length/2, -width/2, height],
            
            # Front face (sloped)
            [length/2 - front_slope_length, -width/2, 0], 
            [length/2 - front_slope_length, width/2, 0],
            [length/2, width/2, height], 
            [length/2, -width/2, height],
            
            # Additional vertices for complex hull shape
            [length/4, -width/2, height*0.9],  # Side slope start
            [length/4, width/2, height*0.9],   # Side slope start (right)
        ])
        
        return vertices
    
    def _create_hull_faces(self) -> List[List[int]]:
        """Create hull face indices for realistic shape."""
        return [
            [0, 1, 2, 3],    # Rear face
            [4, 7, 6, 5],    # Front face
            [0, 4, 5, 1],    # Bottom
            [2, 6, 7, 3],    # Top
            [0, 3, 7, 4],    # Left side
            [1, 5, 6, 2],    # Right side
        ]
    
    def _create_realistic_turret(self, tank_length: float, turret_height: float) -> np.ndarray:
        """Create realistic turret geometry."""
        
        # Turret positioned forward on hull
        turret_center_x = tank_length * 0.15  # 15% forward from center
        turret_center_y = 0
        turret_center_z = 1.8  # On top of hull
        
        # Create cylindrical turret with angular front
        angles = np.linspace(0, 2*np.pi, 20)  # Higher resolution
        turret_radius = 1.6
        
        # Bottom ring
        bottom_vertices = []
        for angle in angles:
            x = turret_center_x + turret_radius * np.cos(angle)
            y = turret_center_y + turret_radius * np.sin(angle)
            z = turret_center_z
            bottom_vertices.append([x, y, z])
        
        # Top ring (slightly smaller for realistic taper)
        top_vertices = []
        top_radius = turret_radius * 0.9
        for angle in angles:
            x = turret_center_x + top_radius * np.cos(angle)
            y = turret_center_y + top_radius * np.sin(angle)
            z = turret_center_z + turret_height
            top_vertices.append([x, y, z])
        
        return np.vstack([bottom_vertices, top_vertices])
    
    def _create_turret_faces(self) -> List[List[int]]:
        """Create turret face indices."""
        faces = []
        n_vertices = 20  # Number of vertices in each ring
        
        # Side faces
        for i in range(n_vertices):
            next_i = (i + 1) % n_vertices
            # Bottom ring indices: 0 to n_vertices-1
            # Top ring indices: n_vertices to 2*n_vertices-1
            face = [i, next_i, next_i + n_vertices, i + n_vertices]
            faces.append(face)
        
        return faces
    
    def _create_realistic_gun(self) -> np.ndarray:
        """Create realistic gun barrel."""
        
        # Gun specifications (120mm L/44)
        gun_length = 5.28  # 44 calibers * 120mm
        gun_diameter = 0.12  # 120mm
        gun_elevation = 0  # degrees
        
        # Gun mount point (front of turret)
        gun_base_x = 2.5
        gun_base_y = 0
        gun_base_z = 2.5
        
        # Gun end point
        gun_end_x = gun_base_x + gun_length * math.cos(math.radians(gun_elevation))
        gun_end_y = gun_base_y
        gun_end_z = gun_base_z + gun_length * math.sin(math.radians(gun_elevation))
        
        # Create cylindrical gun barrel
        angles = np.linspace(0, 2*np.pi, 12)
        
        gun_vertices = []
        
        # Base circle
        for angle in angles:
            x = gun_base_x
            y = gun_base_y + (gun_diameter/2) * math.cos(angle)
            z = gun_base_z + (gun_diameter/2) * math.sin(angle)
            gun_vertices.append([x, y, z])
        
        # End circle
        for angle in angles:
            x = gun_end_x
            y = gun_end_y + (gun_diameter/2) * math.cos(angle)
            z = gun_end_z + (gun_diameter/2) * math.sin(angle)
            gun_vertices.append([x, y, z])
        
        return np.array(gun_vertices)
    
    def _create_realistic_tracks(self, tank_length: float, tank_width: float) -> Dict[str, Any]:
        """Create realistic track representation."""
        
        track_height = 0.8
        track_width = 0.6
        
        # Left track
        left_track_y = -tank_width/2 + track_width/2
        left_vertices = np.array([
            [-tank_length/2, left_track_y - track_width/2, 0],
            [tank_length/2, left_track_y - track_width/2, 0],
            [tank_length/2, left_track_y + track_width/2, 0],
            [-tank_length/2, left_track_y + track_width/2, 0],
            [-tank_length/2, left_track_y - track_width/2, track_height],
            [tank_length/2, left_track_y - track_width/2, track_height],
            [tank_length/2, left_track_y + track_width/2, track_height],
            [-tank_length/2, left_track_y + track_width/2, track_height],
        ])
        
        # Right track (mirror of left)
        right_track_y = tank_width/2 - track_width/2
        right_vertices = np.array([
            [-tank_length/2, right_track_y - track_width/2, 0],
            [tank_length/2, right_track_y - track_width/2, 0],
            [tank_length/2, right_track_y + track_width/2, 0],
            [-tank_length/2, right_track_y + track_width/2, 0],
            [-tank_length/2, right_track_y - track_width/2, track_height],
            [tank_length/2, right_track_y - track_width/2, track_height],
            [tank_length/2, right_track_y + track_width/2, track_height],
            [-tank_length/2, right_track_y + track_width/2, track_height],
        ])
        
        track_faces = [
            [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7],  # Sides
            [0, 1, 2, 3], [4, 5, 6, 7]  # Top and bottom
        ]
        
        return {
            'left': {'vertices': left_vertices, 'faces': track_faces},
            'right': {'vertices': right_vertices, 'faces': track_faces}
        }
    
    def create_interactive_3d_visualization(self, ammunition, armor,
                                          target_range: float = 2000.0,
                                          launch_angle: float = 0.0,
                                          environmental_conditions: Optional[EnvironmentalConditions] = None) -> plt.Figure:
        """Create fully interactive 3D visualization."""
        
        self.debug_logger.logger.info("Creating interactive 3D visualization")
        
        # Calculate accurate trajectory
        trajectory = self.calculate_accurate_trajectory(
            ammunition, target_range, launch_angle, environmental_conditions
        )
        
        # Create enhanced tank model and position it at target range along X
        tank_model = self.create_enhanced_tank_model()
        tank_position = (target_range, 0.0, 0.0)
        
        # Compute multiple AABBs for tank collision (hull, turret, tracks)
        tank_aabbs = self._get_tank_aabbs(target_range)
        
        # Find earliest collision between trajectory and any tank part
        collision = self._find_collision_with_aabbs(trajectory, tank_aabbs)
        # Build triangle meshes once for subsequent refinement and chaining
        self.tri_by_part = self._mesh_triangles_by_part(tank_model, tank_position)
        # Refine collision with mesh intersection on the hit segment
        if collision and 'segment_index' in collision:
            si = collision['segment_index']
            if 1 <= si < len(trajectory):
                p0 = trajectory[si-1]
                p1 = trajectory[si]
                mesh_col = self._refine_collision_with_mesh((p0.x, p0.y, p0.z), (p1.x, p1.y, p1.z), tank_model, tank_position)
                if mesh_col:
                    collision.update(mesh_col)
        self.collision_info = collision
        
        # Log visualization creation
        self.debug_logger.log_visualization_creation(tank_model, trajectory)
        
        # Store metadata for export
        self.meta['ammunition'] = self._extract_ammunition_meta(ammunition)
        self.meta['armor'] = self._extract_armor_meta(armor)
        self.meta['environment'] = self._extract_environment_meta(environmental_conditions)
        self.meta['parameters'] = {'target_range': target_range, 'launch_angle': launch_angle}
        
        # Set up figure and 3D axis
        self.fig = plt.figure(figsize=self.figsize)
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # Configure interactive 3D environment
        self._setup_interactive_environment(trajectory)
        
        # Render tank model at the target position
        self._render_enhanced_tank(tank_model, translate=tank_position)
        
        # Render accurate trajectory
        self._render_accurate_trajectory(trajectory)
        
        # Calculate and render impact analysis
        self._render_impact_analysis(ammunition, armor, trajectory, target_range)
        
        # Add interactive controls
        self._add_interactive_controls()
        
        # Set up proper viewing angle and limits
        self._configure_3d_view(trajectory)
        
        # Add information display
        self._add_information_display(ammunition, armor, trajectory)
        
        self.debug_logger.logger.info("Interactive 3D visualization created successfully")
        
        return self.fig
    
    def _setup_interactive_environment(self, trajectory: List[TrajectoryPoint]):
        """Set up interactive 3D environment with proper scaling."""
        
        if not trajectory:
            self.debug_logger.logger.error("No trajectory data for environment setup")
            return
        
        # Calculate bounds from trajectory
        x_coords = [p.x for p in trajectory]
        y_coords = [p.y for p in trajectory]
        z_coords = [p.z for p in trajectory]
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        z_min, z_max = 0, max(max(z_coords), 5)  # Ensure ground is at z=0
        
        # Add padding
        x_padding = (x_max - x_min) * 0.1
        y_padding = max(abs(y_min), abs(y_max)) * 1.2
        z_padding = z_max * 0.1
        
        # Set axis limits
        self.ax.set_xlim(x_min - x_padding, x_max + x_padding)
        self.ax.set_ylim(-y_padding, y_padding)
        self.ax.set_zlim(0, z_max + z_padding)
        
        # Set labels
        self.ax.set_xlabel('Range (m)', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Lateral Deflection (m)', fontsize=12, fontweight='bold')
        self.ax.set_zlabel('Altitude (m)', fontsize=12, fontweight='bold')
        
        # Create ground plane
        self._create_realistic_ground_plane(x_min - x_padding, x_max + x_padding, 
                                          -y_padding, y_padding)
        
        # Enable grid
        self.ax.grid(True, alpha=0.3)
        
        self.debug_logger.logger.info(f"Environment bounds: X[{x_min:.1f}, {x_max:.1f}], "
                                    f"Y[{y_min:.1f}, {y_max:.1f}], Z[{z_min:.1f}, {z_max:.1f}]")
    
    def _create_realistic_ground_plane(self, x_min: float, x_max: float, 
                                     y_min: float, y_max: float):
        """Create realistic ground plane with terrain features."""
        
        # Ground plane vertices
        ground_vertices = [
            [x_min, y_min, 0], [x_max, y_min, 0],
            [x_max, y_max, 0], [x_min, y_max, 0]
        ]
        
        # Create ground plane
        ground_collection = Poly3DCollection([ground_vertices], 
                                           alpha=0.3, 
                                           facecolors=self.colors['ground'],
                                           edgecolors='darkgreen',
                                           linewidths=0.5)
        self.ax.add_collection3d(ground_collection)
    
    def _render_enhanced_tank(self, tank_model: Dict[str, Any], translate: Tuple[float, float, float] = (0.0, 0.0, 0.0)):
        """Render enhanced tank model with all components, translated in world space."""
        tx, ty, tz = translate
        
        # Render hull
        hull = tank_model['hull']
        hull_vertices = hull['vertices'] + np.array([tx, ty, tz])
        hull_faces = [hull_vertices[face] for face in hull['faces']]
        hull_collection = Poly3DCollection(hull_faces,
                                         alpha=0.8,
                                         facecolors=hull['color'],
                                         edgecolors='black',
                                         linewidths=0.5)
        self.ax.add_collection3d(hull_collection)
        
        # Render turret
        turret = tank_model['turret']
        turret_vertices = turret['vertices'] + np.array([tx, ty, tz])
        turret_faces = [turret_vertices[face] for face in turret['faces']]
        turret_collection = Poly3DCollection(turret_faces,
                                           alpha=0.8,
                                           facecolors=turret['color'],
                                           edgecolors='black',
                                           linewidths=0.5)
        self.ax.add_collection3d(turret_collection)
        
        # Render gun barrel
        gun = tank_model['gun']
        gun_vertices = np.array(gun['vertices']) + np.array([tx, ty, tz])
        n_vertices = len(gun_vertices) // 2
        
        # Create cylindrical faces for gun barrel
        gun_faces = []
        for i in range(n_vertices):
            next_i = (i + 1) % n_vertices
            face = [gun_vertices[i], gun_vertices[next_i], 
                   gun_vertices[next_i + n_vertices], gun_vertices[i + n_vertices]]
            gun_faces.append(face)
        
        gun_collection = Poly3DCollection(gun_faces,
                                        alpha=0.9,
                                        facecolors=gun['color'],
                                        edgecolors='black',
                                        linewidths=0.5)
        self.ax.add_collection3d(gun_collection)
        
        # Render tracks
        tracks = tank_model['tracks']
        for track_name, track_data in tracks.items():
            track_vertices = track_data['vertices'] + np.array([tx, ty, tz])
            track_faces = [track_vertices[face] for face in track_data['faces']]
            track_collection = Poly3DCollection(track_faces,
                                              alpha=0.7,
                                              facecolors='#333333',
                                              edgecolors='black',
                                              linewidths=0.3)
            self.ax.add_collection3d(track_collection)
    
    def _render_accurate_trajectory(self, trajectory: List[TrajectoryPoint]):
        """Render accurate trajectory following calculated ballistic path."""
        
        if not trajectory:
            self.debug_logger.logger.error("No trajectory data to render")
            return
        
        # Extract coordinates (truncate at collision if present)
        x_coords = [p.x for p in trajectory]
        y_coords = [p.y for p in trajectory]
        z_coords = [p.z for p in trajectory]
        
        if hasattr(self, 'collision_info') and self.collision_info and 'segment_index' in self.collision_info:
            si = self.collision_info['segment_index']
            cp = self.collision_info.get('point', {})
            cx, cy, cz = cp.get('x', x_coords[-1]), cp.get('y', y_coords[-1]), cp.get('z', z_coords[-1])
            x_coords = x_coords[:si]
            y_coords = y_coords[:si]
            z_coords = z_coords[:si]
            x_coords.append(cx); y_coords.append(cy); z_coords.append(cz)
        
        # Plot main trajectory line
        self.ax.plot(x_coords, y_coords, z_coords,
                    color=self.colors['trajectory'],
                    linewidth=3,
                    alpha=0.8,
                    label='Ballistic Trajectory')
        
        # Mark key points
        launch_point = trajectory[0]
        if hasattr(self, 'collision_info') and self.collision_info:
            impact_point = type(trajectory[0])(x=x_coords[-1], y=y_coords[-1], z=z_coords[-1],
                                               velocity_x=0.0, velocity_y=0.0, velocity_z=0.0,
                                               velocity_magnitude=0.0, time=trajectory[-1].time,
                                               drag_coefficient=trajectory[-1].drag_coefficient,
                                               air_density=trajectory[-1].air_density,
                                               angle_of_attack=0.0, debug_info={})
        else:
            impact_point = trajectory[-1]
        
        # Launch point
        self.ax.scatter([launch_point.x], [launch_point.y], [launch_point.z],
                       c='green', s=150, marker='^',
                       edgecolors='black', linewidth=2,
                       label='Launch Point')
        
        # Impact point
        self.ax.scatter([impact_point.x], [impact_point.y], [impact_point.z],
                       c=self.colors['impact'], s=200, marker='X',
                       edgecolors='black', linewidth=2,
                       label='Impact Point')
        
        # Optional: Show debug points
        if self.show_trajectory_debug:
            debug_interval = max(1, len(trajectory) // 20)  # Show ~20 debug points
            debug_points = trajectory[::debug_interval]
            
            debug_x = [p.x for p in debug_points]
            debug_y = [p.y for p in debug_points]
            debug_z = [p.z for p in debug_points]
            
            self.ax.scatter(debug_x, debug_y, debug_z,
                           c=self.colors['debug_points'], s=30, alpha=0.6,
                           label='Debug Points')
        
        self.debug_logger.logger.info(f"Rendered trajectory with {len(trajectory)} points")
    
    def _render_impact_analysis(self, ammunition, armor, trajectory: List[TrajectoryPoint],
                              target_range: float):
        """Render impact analysis with penetration results."""
        
        if not trajectory:
            return
        
        # Only render analysis on actual tank collision
        if not hasattr(self, 'collision_info') or not self.collision_info or self.collision_info.get('type') != 'tank':
            return
        
        try:
            analysis = self._compute_impact_analysis(ammunition, armor, trajectory, target_range, impact_override=self.collision_info)
            # Augment with multi-part mesh penetration chain
            try:
                self._augment_multi_part_sequence(ammunition, trajectory)
                analysis = self.meta['impact_analysis']
            except Exception:
                pass
            self.meta['impact_analysis'] = analysis
            
            # Use the collision point
            cp = self.collision_info.get('point', {})
            impact_point = TrajectoryPoint(
                x=cp.get('x', 0.0), y=cp.get('y', 0.0), z=cp.get('z', 0.0),
                velocity_x=self.collision_info.get('vx', 0.0), velocity_y=self.collision_info.get('vy', 0.0), velocity_z=self.collision_info.get('vz', 0.0),
                velocity_magnitude=self.collision_info.get('speed', 0.0),
                time=self.collision_info.get('time', trajectory[-1].time),
                drag_coefficient=trajectory[-1].drag_coefficient,
                air_density=trajectory[-1].air_density,
                angle_of_attack=self.collision_info.get('angle_from_horizontal_deg', 0.0),
                debug_info={}
            )
            
            if analysis.get('penetrates', False):
                self._render_successful_penetration(impact_point, ammunition, analysis.get('penetration_mm', 0.0))
            else:
                self._render_failed_penetration(impact_point, analysis.get('effective_thickness_mm', 0.0))
            # Overlay ricochet if present
            if analysis.get('ricochet') and self.show_ricochet_overlay:
                rp = analysis.get('ricochet_point') or analysis.get('impact_position_m')
                rd = analysis.get('ricochet_direction')
                outcome = str(analysis.get('ricochet_outcome', 'ricochet')).lower()
                if rp:
                    sx, sy, sz = float(rp['x']), float(rp['y']), float(rp['z'])
                    if outcome == 'ricochet' and rd:
                        L = 2.0
                        ex = sx + float(rd['x']) * L
                        ey = sy + float(rd['y']) * L
                        ez = sz + float(rd['z']) * L
                        self.ax.plot([sx, ex], [sy, ey], [sz, ez], color='yellow', linewidth=3, alpha=0.9, label='Ricochet')
                        self.ax.scatter([sx], [sy], [sz], c='yellow', s=160, marker='*', edgecolors='black', linewidth=1.5)
                    elif outcome == 'shattering':
                        self.ax.scatter([sx], [sy], [sz], c='purple', s=200, marker='*', edgecolors='black', linewidth=1.5, label='Shattering')
                    elif outcome == 'embedding':
                        self.ax.scatter([sx], [sy], [sz], c='gray', s=150, marker='D', edgecolors='black', linewidth=1.5, label='Embedding')
        except Exception as e:
            self.debug_logger.logger.error(f"Error in impact analysis: {e}")
    
    def _render_successful_penetration(self, impact_point: TrajectoryPoint, 
                                     ammunition, penetration: float):
        """Render multi-part penetration chain if available; else fallback."""
        analysis = self.meta.get('impact_analysis') or {}
        segments = analysis.get('channel_segments') or []
        if segments and self.show_channel_segments:
            for seg in segments:
                s = seg['start']; e = seg['end']
                self.ax.plot([s['x'], e['x']], [s['y'], e['y']], [s['z'], e['z']],
                             color='red', linewidth=6, alpha=0.85, label=None)
            # Exit marker if overpenetration
            if analysis.get('overpenetration') and segments and self.show_channel_segments:
                ex = segments[-1]['end']
                self.ax.scatter([ex['x']], [ex['y']], [ex['z']], c='red', s=120, marker='o', edgecolors='black', linewidth=1.5)
            # Ricochet overlay if ricochet occurred (rare to have both segments and ricochet, but handle)
            if analysis.get('ricochet'):
                rp = analysis.get('ricochet_point') or analysis.get('impact_position_m')
                rd = analysis.get('ricochet_direction')
                if rp and rd:
                    L = 2.0
                    sx, sy, sz = float(rp['x']), float(rp['y']), float(rp['z'])
                    exx = sx + float(rd['x']) * L
                    eyy = sy + float(rd['y']) * L
                    ezz = sz + float(rd['z']) * L
                    self.ax.plot([sx, exx], [sy, eyy], [sz, ezz], color='yellow', linewidth=3, alpha=0.9, label='Ricochet')
                    self.ax.scatter([sx], [sy], [sz], c='yellow', s=160, marker='*', edgecolors='black', linewidth=1.5)
            # Spall at first passed segment end (approximate)
            if getattr(ammunition, 'penetration_type', 'kinetic') == 'kinetic' and segments:
                first_end = segments[0]['end']
                length_m = math.sqrt((segments[0]['end']['x']-segments[0]['start']['x'])**2 + (segments[0]['end']['y']-segments[0]['start']['y'])**2 + (segments[0]['end']['z']-segments[0]['start']['z'])**2)
                self._create_spall_cone_visualization(first_end['x'], first_end['y'], first_end['z'], max(0.1, length_m*0.3))
            return
        # Fallback single channel if no chain
        channel_depth = min(penetration / 1000, 2.0)
        pen_end_x = impact_point.x
        pen_end_y = impact_point.y
        pen_end_z = impact_point.z - channel_depth
        self.ax.plot([impact_point.x, pen_end_x], [impact_point.y, pen_end_y], [impact_point.z, pen_end_z],
                     color='red', linewidth=8, alpha=0.8, label='Penetration Channel')
        if ammunition.penetration_type == 'kinetic':
            self._create_spall_cone_visualization(pen_end_x, pen_end_y, pen_end_z, channel_depth)
    
    def _render_failed_penetration(self, impact_point: TrajectoryPoint, 
                                 armor_thickness: float):
        """Render failed penetration visualization."""
        
        # Create impact crater
        crater_radius = 0.3
        angles = np.linspace(0, 2*np.pi, 16)
        
        crater_x = [impact_point.x + crater_radius * np.cos(angle) for angle in angles]
        crater_y = [impact_point.y + crater_radius * np.sin(angle) for angle in angles]
        crater_z = [impact_point.z] * len(angles)
        
        # Close the crater
        crater_x.append(crater_x[0])
        crater_y.append(crater_y[0])
        crater_z.append(crater_z[0])
        
        self.ax.plot(crater_x, crater_y, crater_z,
                    color='gray', linewidth=4, alpha=0.7,
                    label='Impact Crater')
    
    def _create_spall_cone_visualization(self, apex_x: float, apex_y: float, apex_z: float,
                                       penetration_depth: float):
        """Create spall cone for behind-armor effects."""
        
        cone_angle = math.radians(30)  # 30-degree spall cone
        cone_height = penetration_depth * 0.5
        cone_radius = cone_height * math.tan(cone_angle)
        
        # Create cone base
        angles = np.linspace(0, 2*np.pi, 12)
        base_x = [apex_x + cone_radius * np.cos(angle) for angle in angles]
        base_y = [apex_y + cone_radius * np.sin(angle) for angle in angles]
        base_z = [apex_z - cone_height] * len(angles)
        
        # Draw cone wireframe
        for i, angle in enumerate(angles):
            self.ax.plot([apex_x, base_x[i]], [apex_y, base_y[i]], [apex_z, base_z[i]],
                        color='orange', linewidth=2, alpha=0.6)
    
    def _add_interactive_controls(self):
        """Add interactive controls for 3D visualization."""
        
        # Enable mouse interaction
        self.ax.mouse_init()
        
        # Set initial viewing angle
        self.ax.view_init(elev=20, azim=45)
        
        # Add control panel if space allows
        try:
            # Add sliders for viewing control
            plt.subplots_adjust(bottom=0.15)
            
            # Elevation slider
            ax_elev = plt.axes([0.1, 0.05, 0.3, 0.03])
            slider_elev = Slider(ax_elev, 'Elevation', -90, 90, valinit=20)
            
            # Azimuth slider
            ax_azim = plt.axes([0.6, 0.05, 0.3, 0.03])
            slider_azim = Slider(ax_azim, 'Azimuth', 0, 360, valinit=45)
            
            def update_view(val):
                self.ax.view_init(elev=slider_elev.val, azim=slider_azim.val)
                self.fig.canvas.draw()
            
            slider_elev.on_changed(update_view)
            slider_azim.on_changed(update_view)
            
        except Exception as e:
            self.debug_logger.logger.warning(f"Could not add interactive controls: {e}")
    
    def _configure_3d_view(self, trajectory: List[TrajectoryPoint]):
        """Configure 3D view with proper aspect ratio and perspective."""
        
        if trajectory:
            # Set equal aspect ratio for realistic proportions
            max_range = max(abs(coord) for p in trajectory for coord in [p.x, p.y, p.z])
            self.ax.set_box_aspect([1, 0.5, 0.3])  # Elongated for trajectory view
        
        # Enable rotation and zoom
        self.ax.mouse_init()
        
        # Set viewing angle for best trajectory visibility
        self.ax.view_init(elev=15, azim=30)
    
    def _add_information_display(self, ammunition, armor, trajectory: List[TrajectoryPoint]):
        """Add information display with calculation results."""
        
        if not trajectory:
            return
        
        impact_point = trajectory[-1]
        
        # Create info text
        info_text = f"Ammunition: {ammunition.name}\n"
        info_text += f"Target: {armor.name}\n"
        info_text += f"Range: {impact_point.x:.1f} m\n"
        info_text += f"Flight Time: {impact_point.time:.2f} s\n"
        info_text += f"Impact Velocity: {impact_point.velocity_magnitude:.1f} m/s\n"
        info_text += f"Impact Angle: {abs(impact_point.angle_of_attack):.1f}°\n"
        # Append environment summary if available
        try:
            if self.meta.get('impact_analysis') and self.meta['impact_analysis'].get('environmental_effects_summary'):
                es = self.meta['impact_analysis']['environmental_effects_summary']
                info_text += f"Env Impact: Δv={es.get('speed_loss_ms',0):.0f} m/s, Lat {es.get('lateral_deflection_m',0):.1f} m\n"
        except Exception:
            pass
        
        # Add text to plot
        self.ax.text2D(0.02, 0.98, info_text, transform=self.ax.transAxes,
                      fontsize=10, verticalalignment='top',
                      bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # Add legend
        self.ax.legend(loc='upper right', bbox_to_anchor=(1.0, 0.85))
        
        # Set title
        self.fig.suptitle('Enhanced 3D Tank Armor Penetration Analysis', 
                         fontsize=14, fontweight='bold')
    
    def enable_animation_mode(self, duration: float = 5.0) -> animation.FuncAnimation:
        """Enable animated visualization showing projectile following trajectory."""
        
        if not self.trajectory_points:
            self.debug_logger.logger.error("No trajectory data for animation")
            return None
        
        self.debug_logger.logger.info(f"Creating animation with {len(self.trajectory_points)} frames")
        
        # Animation parameters
        fps = 30
        total_frames = int(duration * fps)
        trajectory_frames = min(len(self.trajectory_points), total_frames)
        
        # Create projectile marker
        projectile_marker = None
        
        def animate_frame(frame):
            nonlocal projectile_marker
            
            # Remove previous projectile marker
            if projectile_marker is not None:
                projectile_marker.remove()
            
            # Calculate trajectory progress
            traj_index = int(frame * trajectory_frames / total_frames)
            if traj_index >= len(self.trajectory_points):
                traj_index = len(self.trajectory_points) - 1
            
            current_point = self.trajectory_points[traj_index]
            
            # Add projectile marker at current position
            projectile_marker = self.ax.scatter(
                [current_point.x], [current_point.y], [current_point.z],
                c=self.colors['projectile'], s=100, marker='o', 
                alpha=0.9, edgecolors='black', linewidths=2
            )
            
            # Update title with current status
            time_text = f"Time: {current_point.time:.2f}s"
            velocity_text = f"Velocity: {current_point.velocity_magnitude:.1f} m/s"
            self.ax.set_title(f"{time_text} | {velocity_text}", fontsize=12)
            
            return [projectile_marker]
        
        # Create animation
        anim = animation.FuncAnimation(
            self.fig, animate_frame, frames=total_frames,
            interval=1000/fps, blit=False, repeat=True
        )
        
        self.animation = anim
        return anim
    
    def show_interactive(self):
        """Show the interactive visualization."""
        if self.fig:
            plt.show()
        else:
            self.debug_logger.logger.error("No visualization to show. Create visualization first.")
    
    def save_visualization(self, filename: str, dpi: int = 300):
        """Save the 3D visualization."""
        if self.fig:
            self.fig.savefig(filename, dpi=dpi, bbox_inches='tight')
            self.debug_logger.logger.info(f"Visualization saved to: {filename}")
        else:
            self.debug_logger.logger.error("No visualization to save.")

    # ---------- Collision and AABB helpers ----------
    def _get_tank_aabbs(self, x_center: float) -> List[Dict[str, Any]]:
        parts = []
        # Hull
        hull_len = 6.0; hull_ht = 1.8; hull_w = self.tank_width_m
        half_l = hull_len / 2.0; half_w = hull_w / 2.0
        parts.append({'part': 'hull', 'aabb': (x_center - half_l, x_center + half_l, -half_w, half_w, 0.0, hull_ht)})
        # Turret on top, slightly forward
        tur_len = 3.0; tur_ht = 1.2; tur_w = 3.0; tur_z_bottom = hull_ht
        half_tl = tur_len / 2.0; half_tw = tur_w / 2.0
        tur_center_x = x_center + 0.5
        parts.append({'part': 'turret', 'aabb': (tur_center_x - half_tl, tur_center_x + half_tl, -half_tw, half_tw, tur_z_bottom, tur_z_bottom + tur_ht)})
        # Tracks left/right near ground
        track_len = self.tank_length_m; track_ht = 1.2; track_w = 0.6
        half_tlen = track_len / 2.0
        # Left track (negative y)
        y_left_max = -half_w
        y_left_min = y_left_max - track_w
        parts.append({'part': 'left_track', 'aabb': (x_center - half_tlen, x_center + half_tlen, y_left_min, y_left_max, 0.0, track_ht)})
        # Right track (positive y)
        y_right_min = half_w
        y_right_max = y_right_min + track_w
        parts.append({'part': 'right_track', 'aabb': (x_center - half_tlen, x_center + half_tlen, y_right_min, y_right_max, 0.0, track_ht)})
        return parts

    def _segment_aabb_intersection(self, p0: Tuple[float, float, float], p1: Tuple[float, float, float], aabb: Tuple[float, float, float, float, float, float]) -> Optional[Tuple[float, float, float, float]]:
        xmin, xmax, ymin, ymax, zmin, zmax = aabb
        (x0, y0, z0) = p0
        (x1, y1, z1) = p1
        dx = x1 - x0; dy = y1 - y0; dz = z1 - z0
        tmin = 0.0
        tmax = 1.0
        # X slab
        if abs(dx) < 1e-12:
            if x0 < xmin or x0 > xmax:
                return None
        else:
            tx1 = (xmin - x0) / dx
            tx2 = (xmax - x0) / dx
            t1x, t2x = (tx1, tx2) if tx1 <= tx2 else (tx2, tx1)
            tmin = max(tmin, t1x)
            tmax = min(tmax, t2x)
            if tmax < tmin:
                return None
        # Y slab
        if abs(dy) < 1e-12:
            if y0 < ymin or y0 > ymax:
                return None
        else:
            ty1 = (ymin - y0) / dy
            ty2 = (ymax - y0) / dy
            t1y, t2y = (ty1, ty2) if ty1 <= ty2 else (ty2, ty1)
            tmin = max(tmin, t1y)
            tmax = min(tmax, t2y)
            if tmax < tmin:
                return None
        # Z slab
        if abs(dz) < 1e-12:
            if z0 < zmin or z0 > zmax:
                return None
        else:
            tz1 = (zmin - z0) / dz
            tz2 = (zmax - z0) / dz
            t1z, t2z = (tz1, tz2) if tz1 <= tz2 else (tz2, tz1)
            tmin = max(tmin, t1z)
            tmax = min(tmax, t2z)
            if tmax < tmin:
                return None
        if tmin < 0.0 or tmin > 1.0:
            return None
        xi = x0 + tmin*dx
        yi = y0 + tmin*dy
        zi = z0 + tmin*dz
        return (xi, yi, zi, tmin)

    def _find_collision_with_aabbs(self, trajectory: List[TrajectoryPoint], aabbs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not trajectory or len(trajectory) < 2:
            return None
        best = None
        best_key = None  # (segment_index, t)
        for i in range(1, len(trajectory)):
            p0 = trajectory[i-1]
            p1 = trajectory[i]
            for part in aabbs:
                aabb = part['aabb']
                res = self._segment_aabb_intersection((p0.x, p0.y, p0.z), (p1.x, p1.y, p1.z), aabb)
                if res is not None:
                    (xi, yi, zi, t) = res
                    key = (i, t)
                    if best is None or key < best_key:
                        # Compute collision info
                        vx = p1.velocity_x; vy = p1.velocity_y; vz = p1.velocity_z
                        speed = math.sqrt(vx*vx + vy*vy + vz*vz)
                        angle_from_horizontal = math.degrees(math.atan2(vz, math.sqrt(max(vx*vx + vy*vy, 1e-12))))
                        time_at_collision = p0.time + t * (p1.time - p0.time)
                        best = {
                            'type': 'tank',
                            'part': part['part'],
                            'point': {'x': xi, 'y': yi, 'z': zi},
                            'vx': vx, 'vy': vy, 'vz': vz,
                            'speed': speed,
                            'time': time_at_collision,
                            'angle_from_horizontal_deg': angle_from_horizontal,
                            'segment_index': i,
                            't': t
                        }
                        best_key = key
        return best

    # ---------- Mesh helpers ----------
    def _triangulate_quads(self, vertices: np.ndarray, faces: List[List[int]]) -> List[np.ndarray]:
        tris = []
        for f in faces:
            if len(f) == 3:
                tris.append(np.array([vertices[f[0]], vertices[f[1]], vertices[f[2]]]))
            elif len(f) == 4:
                tris.append(np.array([vertices[f[0]], vertices[f[1]], vertices[f[2]]]))
                tris.append(np.array([vertices[f[0]], vertices[f[2]], vertices[f[3]]]))
        return tris
    
    def _mesh_triangles_by_part(self, tank_model: Dict[str, Any], translate: Tuple[float, float, float]) -> Dict[str, List[np.ndarray]]:
        tx, ty, tz = translate
        out: Dict[str, List[np.ndarray]] = {}
        # Hull
        hull = tank_model['hull']
        hull_vertices = hull['vertices'] + np.array([tx, ty, tz])
        out['hull'] = self._triangulate_quads(hull_vertices, hull['faces'])
        # Turret
        turret = tank_model['turret']
        turret_vertices = turret['vertices'] + np.array([tx, ty, tz])
        out['turret'] = self._triangulate_quads(turret_vertices, turret['faces'])
        # Tracks
        tracks = tank_model['tracks']
        left_vertices = tracks['left']['vertices'] + np.array([tx, ty, tz])
        right_vertices = tracks['right']['vertices'] + np.array([tx, ty, tz])
        out['left_track'] = self._triangulate_quads(left_vertices, tracks['left']['faces'])
        out['right_track'] = self._triangulate_quads(right_vertices, tracks['right']['faces'])
        return out
    
    def _segment_triangle_intersection(self, p0: np.ndarray, p1: np.ndarray, tri: np.ndarray) -> Optional[Tuple[float, np.ndarray]]:
        # Möller–Trumbore algorithm on segment p0->p1
        eps = 1e-9
        orig = p0; dest = p1
        dir = dest - orig
        edge1 = tri[1] - tri[0]
        edge2 = tri[2] - tri[0]
        h = np.cross(dir, edge2)
        a = np.dot(edge1, h)
        if -eps < a < eps:
            return None
        f = 1.0 / a
        s = orig - tri[0]
        u = f * np.dot(s, h)
        if u < 0.0 or u > 1.0:
            return None
        q = np.cross(s, edge1)
        v = f * np.dot(dir, q)
        if v < 0.0 or u + v > 1.0:
            return None
        t = f * np.dot(edge2, q)
        if t < 0.0 or t > 1.0:
            return None
        hit = orig + dir * t
        return (float(t), hit)
    
    def _triangle_normal(self, tri: np.ndarray) -> np.ndarray:
        n = np.cross(tri[1] - tri[0], tri[2] - tri[0])
        ln = np.linalg.norm(n)
        return n / (ln + 1e-12)
    
    def _refine_collision_with_mesh(self, seg_p0: Tuple[float,float,float], seg_p1: Tuple[float,float,float], tank_model: Dict[str, Any], translate: Tuple[float,float,float]) -> Optional[Dict[str, Any]]:
        tri_by_part = self._mesh_triangles_by_part(tank_model, translate)
        p0 = np.array(seg_p0); p1 = np.array(seg_p1)
        best = None
        best_key = None
        for part, tris in tri_by_part.items():
            for tri in tris:
                res = self._segment_triangle_intersection(p0, p1, tri)
                if res is not None:
                    t, hit = res
                    key = t
                    if best is None or key < best_key:
                        n = self._triangle_normal(tri)
                        best = {'part': part, 'point': {'x': float(hit[0]), 'y': float(hit[1]), 'z': float(hit[2])}, 'normal': (float(n[0]), float(n[1]), float(n[2]))}
                        best_key = key
        return best

    # ---------- Multi-part chain ----------
    def _ray_triangle_intersections(self, origin: np.ndarray, dir_u: np.ndarray, tris: List[np.ndarray]) -> List[Tuple[float, np.ndarray, np.ndarray]]:
        hits = []
        for tri in tris:
            res = self._segment_triangle_intersection(origin, origin + dir_u * 1e5, tri)
            if res is not None:
                t, hit = res
                if t > 1e-6:
                    n = self._triangle_normal(tri)
                    hits.append((t, hit, n))
        hits.sort(key=lambda x: x[0])
        return hits

    def _compute_part_segments_along_ray(self, origin: np.ndarray, dir_u: np.ndarray) -> List[Dict[str, Any]]:
        segments = []
        if not hasattr(self, 'tri_by_part') or self.tri_by_part is None:
            return segments
        for part, tris in self.tri_by_part.items():
            hits = self._ray_triangle_intersections(origin, dir_u, tris)
            if len(hits) >= 2:
                # Pair first two as entry/exit (best effort)
                t_entry, p_entry, n_entry = hits[0]
                t_exit, p_exit, n_exit = hits[1]
                length_m = float(np.linalg.norm(p_exit - p_entry))
                segments.append({
                    'part': part,
                    't_entry': float(t_entry),
                    't_exit': float(t_exit),
                    'entry_point': {'x': float(p_entry[0]), 'y': float(p_entry[1]), 'z': float(p_entry[2])},
                    'exit_point': {'x': float(p_exit[0]), 'y': float(p_exit[1]), 'z': float(p_exit[2])},
                    'length_m': length_m,
                    'normal_entry': (float(n_entry[0]), float(n_entry[1]), float(n_entry[2]))
                })
        # Order by entry distance
        segments.sort(key=lambda s: s['t_entry'])
        return segments

    def _augment_multi_part_sequence(self, ammunition, trajectory: List[TrajectoryPoint]):
        if not (hasattr(self, 'collision_info') and self.collision_info and hasattr(self, 'tri_by_part') and self.tri_by_part):
            return
        analysis = self.meta.get('impact_analysis') or {}
        residual_mm = float(analysis.get('penetration_mm', 0.0))
        # Direction from last trajectory step
        p0 = trajectory[-2] if len(trajectory) >= 2 else trajectory[-1]
        p1 = trajectory[-1]
        dir_vec = np.array([p1.x - p0.x, p1.y - p0.y, p1.z - p0.z])
        ln = np.linalg.norm(dir_vec) + 1e-12
        dir_u = dir_vec / ln
        origin = np.array([self.collision_info['point']['x'], self.collision_info['point']['y'], self.collision_info['point']['z']]) + dir_u * 1e-4
        segs = self._compute_part_segments_along_ray(origin, dir_u)
        chain = []
        channel_segments = []
        ricochet_happened = False
        for seg in segs:
            part = seg['part']
            L_m = seg['length_m']
            L_mm = L_m * 1000.0
            mat = self.part_materials.get(part, {'rha_factor': 1.0, 'ricochet_threshold_deg': 80.0, 'degrade_per_mm': 0.0})
            # Angle to normal at entry
            n = np.array(seg['normal_entry'])
            n = n / (np.linalg.norm(n) + 1e-12)
            cos_inc = abs(float(np.dot(dir_u, n)))
            cos_inc = max(1e-3, min(1.0, cos_inc))
            angle_from_normal_deg = math.degrees(math.acos(cos_inc))
            # Ricochet check for kinetic rounds
            will_ricochet = False
            if getattr(ammunition, 'penetration_type', 'kinetic') == 'kinetic':
                will_ricochet = angle_from_normal_deg >= float(mat.get('ricochet_threshold_deg', 80.0))
                # If detailed ricochet model is available, refine decision
                if _HAS_RICOCHET_CALC:
                    try:
                        impact_speed = float(self.collision_info.get('speed', 0.0)) if hasattr(self, 'collision_info') and self.collision_info else float(trajectory[-1].velocity_magnitude)
                        proj_hard = 0.9
                        tgt_hard = 0.8
                        params = RicochetParameters(
                            impact_angle_deg=angle_from_normal_deg,
                            impact_velocity_ms=impact_speed,
                            projectile_hardness=proj_hard,
                            target_hardness=tgt_hard,
                            surface_roughness=0.5,
                            target_slope_deg=0.0
                        )
                        rc_calc = RicochetCalculator()
                        rc_res = rc_calc.calculate_ricochet_probability(ammunition, armor=None if not hasattr(self, 'armor') else getattr(self, 'armor'), params=params)
                        # Store detailed ricochet analysis for export/inspection
                        analysis.setdefault('ricochet_details', {})
                        analysis['ricochet_details'].update({
                            'probability': float(rc_res.ricochet_probability),
                            'deflection_angle_deg': float(rc_res.deflection_angle_deg),
                            'exit_velocity_ms': float(rc_res.exit_velocity_ms),
                            'energy_retained': float(rc_res.energy_retained),
                            'critical_angle_deg': float(rc_res.critical_angle_deg),
                            'predicted_outcome': rc_res.predicted_outcome.value
                        })
                        # Treat as ricochet-like termination for ricochet or shattering
                        if rc_res.predicted_outcome in (RicochetResult.RICOCHET, RicochetResult.SHATTERING) or rc_res.ricochet_probability > 0.6:
                            will_ricochet = True
                            analysis['ricochet_outcome'] = rc_res.predicted_outcome.value.lower()
                    except Exception:
                        pass
            # Cost and degradation
            cost_mm = L_mm * float(mat.get('rha_factor', 1.0))
            degrade_mm = L_mm * float(mat.get('degrade_per_mm', 0.0))
            total_loss_mm = cost_mm + degrade_mm
            passed = (not will_ricochet) and (residual_mm > total_loss_mm)
            # Compute channel segment endpoints
            start = seg['entry_point']
            end = seg['exit_point']
            seg_start = (start['x'], start['y'], start['z'])
            seg_end = (end['x'], end['y'], end['z'])
            if will_ricochet:
                ricochet_happened = True
                # Compute reflection direction for visualization
                # dir_u is incident direction; n is normal pointing outward
                reflect_dir = dir_u - 2.0 * float(np.dot(dir_u, n)) * n
                reflect_dir = reflect_dir / (np.linalg.norm(reflect_dir) + 1e-12)
                ric_point = {'x': seg_start[0], 'y': seg_start[1], 'z': seg_start[2]}
                # Default outcome if not set by detailed calc
                if 'ricochet_outcome' not in analysis:
                    analysis['ricochet_outcome'] = 'ricochet'
                ric_entry = {
                    'part': part,
                    'delta_length_mm': 0.0,
                    'rha_factor': float(mat.get('rha_factor', 1.0)),
                    'cost_mm': 0.0,
                    'degrade_mm': 0.0,
                    'passed': False,
                    'ricochet': True,
                    'angle_from_normal_deg': angle_from_normal_deg,
                    'residual_after_mm': residual_mm
                }
                chain.append(ric_entry)
                analysis['ricochet_point'] = ric_point
                analysis['ricochet_direction'] = {'x': float(reflect_dir[0]), 'y': float(reflect_dir[1]), 'z': float(reflect_dir[2])}
                analysis['ricochet_outcome'] = 'ricochet'
                # Do not add channel segment beyond entry
                break
            # Add segment drawing
            segment_draw_end = seg_end
            partial = False
            if not passed:
                # Compute partial endpoint proportional to residual/cost
                frac = max(0.0, min(1.0, residual_mm / max(total_loss_mm, 1e-6)))
                vec = np.array([seg_end[0]-seg_start[0], seg_end[1]-seg_start[1], seg_end[2]-seg_start[2]])
                pe = np.array(seg_start) + vec * frac
                segment_draw_end = (float(pe[0]), float(pe[1]), float(pe[2]))
                partial = True
            channel_segments.append({
                'part': part,
                'start': {'x': seg_start[0], 'y': seg_start[1], 'z': seg_start[2]},
                'end': {'x': segment_draw_end[0], 'y': segment_draw_end[1], 'z': segment_draw_end[2]},
                'partial': partial
            })
            # Update residual and record
            residual_mm = max(0.0, residual_mm - total_loss_mm)
            chain.append({
                'part': part,
                'delta_length_mm': L_mm,
                'rha_factor': float(mat.get('rha_factor', 1.0)),
                'cost_mm': cost_mm,
                'degrade_mm': degrade_mm,
                'passed': passed,
                'ricochet': False,
                'angle_from_normal_deg': angle_from_normal_deg,
                'residual_after_mm': residual_mm
            })
            if not passed:
                break
        # Update analysis
        analysis['per_part_sequence'] = chain
        analysis['residual_penetration_mm'] = residual_mm
        analysis['overpenetration'] = residual_mm > 50.0
        analysis['ricochet'] = ricochet_happened
        analysis['channel_segments'] = channel_segments
        # Exit point if overpenetration: last segment end
        if analysis['overpenetration'] and channel_segments:
            analysis['exit_point'] = channel_segments[-1]['end']
        # Ensure impact_position_m exists for dataset rendering
        if 'impact_position_m' not in analysis and hasattr(self, 'collision_info') and self.collision_info:
            ip = self.collision_info.get('point', {})
            analysis['impact_position_m'] = {'x': float(ip.get('x', 0.0)), 'y': float(ip.get('y', 0.0)), 'z': float(ip.get('z', 0.0))}
        self.meta['impact_analysis'] = analysis

    # ---------- Data export and import ----------
    def _compute_impact_analysis(self, ammunition, armor, trajectory: List[TrajectoryPoint], target_range: float, impact_override: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Compute impact analysis values and return a summary dict."""
        if not trajectory:
            return {}
        if impact_override and impact_override.get('type') == 'tank':
            ip = impact_override.get('point', {})
            impact_x = float(ip.get('x', 0.0))
            impact_y = float(ip.get('y', 0.0))
            impact_z = float(ip.get('z', 0.0))
            impact_velocity = float(impact_override.get('speed', 0.0))
            angle_from_horizontal = float(impact_override.get('angle_from_horizontal_deg', 0.0))
            impact_angle_from_vertical = 90 - abs(angle_from_horizontal)
        else:
            impact_point = trajectory[-1]
            impact_velocity = impact_point.velocity_magnitude
            impact_angle = abs(impact_point.angle_of_attack)
            impact_angle_from_vertical = 90 - impact_angle
        try:
            penetration = ammunition.calculate_penetration(target_range/1000, impact_angle_from_vertical)
            effective_thickness = armor.get_effective_thickness(ammunition.penetration_type, impact_angle_from_vertical)
            # Per-part adjustment if we have mesh-based info
            if impact_override and impact_override.get('type') == 'tank':
                part = impact_override.get('part', 'hull')
                mat = self.part_materials.get(part, {'thickness_mm': effective_thickness, 'rha_factor': 1.0})
                # Direction approximation from last trajectory step
                p0t = trajectory[-2] if len(trajectory) >= 2 else trajectory[-1]
                p1t = trajectory[-1]
                dir_u = np.array([p1t.x - p0t.x, p1t.y - p0t.y, p1t.z - p0t.z])
                dir_u = dir_u / (np.linalg.norm(dir_u) + 1e-12)
                n = np.array(impact_override.get('normal', (1.0,0.0,0.0)))
                n = n / (np.linalg.norm(n) + 1e-12)
                cos_inc = abs(float(np.dot(dir_u, n)))
                cos_inc = max(1e-3, min(1.0, cos_inc))
                los_thickness_mm = float(mat.get('thickness_mm', effective_thickness)) / cos_inc
                effective_thickness = los_thickness_mm * float(mat.get('rha_factor', 1.0))
            penetrates = penetration > effective_thickness
        except Exception:
            penetration = 0.0
            effective_thickness = 0.0
            penetrates = False
        self.debug_logger.logger.info("Impact Analysis:")
        self.debug_logger.logger.info(f"  Impact Velocity: {impact_velocity:.1f} m/s")
        self.debug_logger.logger.info(f"  Impact Angle: {impact_angle_from_vertical:.1f}° from vertical")
        self.debug_logger.logger.info(f"  Penetration: {penetration:.1f} mm RHA")
        self.debug_logger.logger.info(f"  Effective Armor: {effective_thickness:.1f} mm RHA")
        self.debug_logger.logger.info(f"  Result: {'PENETRATION' if penetrates else 'NO PENETRATION'}")
        # Environment summary
        env = self.meta.get('environment') or {}
        try:
            v0 = float(getattr(ammunition, 'muzzle_velocity', 0.0))
        except Exception:
            v0 = 0.0
        speed_loss = max(0.0, v0 - impact_velocity)
        lateral_deflection_m = 0.0
        if impact_override and impact_override.get('type') == 'tank':
            lateral_deflection_m = abs(impact_y)
        else:
            lateral_deflection_m = abs(trajectory[-1].y)
        env_summary = {
            'speed_loss_ms': speed_loss,
            'lateral_deflection_m': lateral_deflection_m,
            'altitude_m': env.get('altitude_m', 0.0),
            'wind_speed_ms': env.get('wind_speed_ms', 0.0),
            'humidity_percent': env.get('humidity_percent', 0.0),
            'temperature_celsius': env.get('temperature_celsius', 0.0)
        }
        result = {
            'impact_velocity_ms': impact_velocity,
            'impact_angle_from_vertical_deg': impact_angle_from_vertical,
            'penetration_mm': penetration,
            'effective_thickness_mm': effective_thickness,
            'penetrates': penetrates,
            'environmental_effects_summary': env_summary,
            'part': impact_override.get('part') if (impact_override and impact_override.get('type') == 'tank') else None
        }
        if impact_override and impact_override.get('type') == 'tank':
            result['impact_position_m'] = {'x': impact_x, 'y': impact_y, 'z': impact_z}
        else:
            result['impact_position_m'] = {'x': trajectory[-1].x, 'y': trajectory[-1].y, 'z': trajectory[-1].z}
        # Overpenetration heuristic
        result['overpenetration'] = (penetration - effective_thickness) > 50.0
        return result

    def _extract_ammunition_meta(self, ammo) -> Dict[str, Any]:
        return {
            'name': getattr(ammo, 'name', 'Unknown'),
            'penetration_type': getattr(ammo, 'penetration_type', 'unknown'),
            'caliber_mm': float(getattr(ammo, 'caliber', 0.0)),
            'mass_kg': float(getattr(ammo, 'mass', 0.0)),
            'muzzle_velocity_ms': float(getattr(ammo, 'muzzle_velocity', 0.0))
        }

    def _extract_armor_meta(self, armor) -> Dict[str, Any]:
        meta = {
            'name': getattr(armor, 'name', 'Armor'),
            'armor_type': getattr(armor, 'armor_type', 'unknown'),
            'thickness_mm': float(getattr(armor, 'thickness', 0.0))
        }
        # Optional composite details
        for field in ['steel_layers', 'ceramic_layers', 'other_layers']:
            if hasattr(armor, field):
                meta[field + '_mm'] = float(getattr(armor, field))
        return meta

    def _extract_environment_meta(self, env) -> Dict[str, Any]:
        if env is None:
            return {}
        fields = ['temperature_celsius', 'humidity_percent', 'altitude_m', 'wind_speed_ms', 'wind_angle_deg', 'air_pressure_kpa']
        return {f: float(getattr(env, f)) for f in fields if hasattr(env, f)}

    def _serialize_trajectory(self) -> List[Dict[str, Any]]:
        data = []
        for p in self.trajectory_points:
            data.append({
                'x': p.x, 'y': p.y, 'z': p.z,
                'vx': p.velocity_x, 'vy': p.velocity_y, 'vz': p.velocity_z,
                'speed': p.velocity_magnitude,
                'time': p.time,
                'cd': p.drag_coefficient,
                'air_density': p.air_density,
                'angle_of_attack_deg': p.angle_of_attack
            })
        return data

    def save_interactive_dataset(self, filename: str, screenshot_path: Optional[str] = None, cross_section_path: Optional[str] = None):
        """Save trajectory and metadata as a JSON dataset for interactive viewing later."""
        if not self.trajectory_points:
            self.debug_logger.logger.error("No trajectory data to export.")
            return
        dataset = {
            'version': '1.0',
            'type': 'enhanced_3d_result',
            'ammunition': self.meta.get('ammunition'),
            'armor': self.meta.get('armor'),
            'environment': self.meta.get('environment'),
            'parameters': self.meta.get('parameters'),
            'impact_analysis': self.meta.get('impact_analysis'),
            'trajectory': self._serialize_trajectory(),
            'assets': {
                'screenshot_png': screenshot_path,
                'cross_section_png': cross_section_path
            }
        }
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2)
        self.debug_logger.logger.info(f"Interactive dataset saved to: {filename}")

    def create_from_dataset(self, dataset: Dict[str, Any]) -> plt.Figure:
        """Render an interactive 3D visualization from a saved dataset (no physics recompute)."""
        # Recreate trajectory points
        traj = []
        for d in dataset.get('trajectory', []):
            tp = TrajectoryPoint(
                x=float(d['x']), y=float(d['y']), z=float(d['z']),
                velocity_x=float(d.get('vx', 0.0)), velocity_y=float(d.get('vy', 0.0)), velocity_z=float(d.get('vz', 0.0)),
                velocity_magnitude=float(d.get('speed', 0.0)),
                time=float(d.get('time', 0.0)),
                drag_coefficient=float(d.get('cd', 0.0)),
                air_density=float(d.get('air_density', 0.0)),
                angle_of_attack=float(d.get('angle_of_attack_deg', 0.0)),
                debug_info={}
            )
            traj.append(tp)
        self.trajectory_points = traj
        # Copy meta
        self.meta['ammunition'] = dataset.get('ammunition')
        self.meta['armor'] = dataset.get('armor')
        self.meta['environment'] = dataset.get('environment')
        self.meta['parameters'] = dataset.get('parameters')
        self.meta['impact_analysis'] = dataset.get('impact_analysis')
        
        # Build scene
        tank_model = self.create_enhanced_tank_model()
        self.fig = plt.figure(figsize=self.figsize)
        self.ax = self.fig.add_subplot(111, projection='3d')
        self._setup_interactive_environment(self.trajectory_points)
        self._render_enhanced_tank(tank_model)
        self._render_accurate_trajectory(self.trajectory_points)
        self._add_interactive_controls()
        self._configure_3d_view(self.trajectory_points)
        
        # Overlay info from dataset
        if self.meta.get('ammunition') and self.meta.get('armor') and self.trajectory_points:
            info = self.meta
            impact = info.get('impact_analysis', {}) or {}
            text = []
            text.append(f"Ammunition: {info['ammunition'].get('name','N/A')}")
            text.append(f"Target: {info['armor'].get('name','N/A')}")
            text.append(f"Range: {self.trajectory_points[-1].x:.1f} m")
            text.append(f"Flight Time: {self.trajectory_points[-1].time:.2f} s")
            if impact:
                text.append(f"Impact Velocity: {impact.get('impact_velocity_ms',0.0):.1f} m/s")
                text.append(f"Impact Angle: {impact.get('impact_angle_from_vertical_deg',0.0):.1f}° from vertical")
                text.append(f"Result: {'PENETRATION' if impact.get('penetrates') else 'NO PENETRATION'}")
            self.ax.text2D(0.02, 0.98, "\n".join(text), transform=self.ax.transAxes,
                           fontsize=10, verticalalignment='top',
                           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        # Render analysis visuals based on saved impact_analysis
        try:
            impact = self.meta.get('impact_analysis') or {}
            if impact:
                # Build an impact point from dataset
                ip = impact.get('impact_position_m') or {'x': self.trajectory_points[-1].x, 'y': self.trajectory_points[-1].y, 'z': self.trajectory_points[-1].z}
                impact_point = TrajectoryPoint(
                    x=float(ip.get('x', 0.0)), y=float(ip.get('y', 0.0)), z=float(ip.get('z', 0.0)),
                    velocity_x=0.0, velocity_y=0.0, velocity_z=0.0,
                    velocity_magnitude=float(impact.get('impact_velocity_ms', 0.0)),
                    time=self.trajectory_points[-1].time if self.trajectory_points else 0.0,
                    drag_coefficient=0.0,
                    air_density=0.0,
                    angle_of_attack=0.0,
                    debug_info={}
                )
                if impact.get('penetrates'):
                    self._render_successful_penetration(impact_point, type('AmmoMeta', (), impact.get('ammunition', {})) if isinstance(impact.get('ammunition'), dict) else type('AmmoMeta', (), self.meta.get('ammunition', {})), impact.get('penetration_mm', 0.0))
                else:
                    self._render_failed_penetration(impact_point, impact.get('effective_thickness_mm', 0.0))
                # Ricochet overlay if present
                if impact.get('ricochet') and self.show_ricochet_overlay:
                    rp = impact.get('ricochet_point') or impact.get('impact_position_m')
                    rd = impact.get('ricochet_direction')
                    outcome = str(impact.get('ricochet_outcome', 'ricochet')).lower()
                    if rp:
                        sx, sy, sz = float(rp['x']), float(rp['y']), float(rp['z'])
                        if outcome == 'ricochet' and rd:
                            # Draw a short line indicating bounce direction
                            L = 2.0
                            ex = sx + float(rd['x']) * L
                            ey = sy + float(rd['y']) * L
                            ez = sz + float(rd['z']) * L
                            self.ax.plot([sx, ex], [sy, ey], [sz, ez], color='yellow', linewidth=3, alpha=0.9, label='Ricochet')
                            self.ax.scatter([sx], [sy], [sz], c='yellow', s=160, marker='*', edgecolors='black', linewidth=1.5)
                        elif outcome == 'shattering':
                            self.ax.scatter([sx], [sy], [sz], c='purple', s=200, marker='*', edgecolors='black', linewidth=1.5, label='Shattering')
                        elif outcome == 'embedding':
                            self.ax.scatter([sx], [sy], [sz], c='gray', s=150, marker='D', edgecolors='black', linewidth=1.5, label='Embedding')
        except Exception as e:
            self.debug_logger.logger.warning(f"Could not render analysis from dataset: {e}")
        self.fig.suptitle('Interactive Result Viewer', fontsize=14, fontweight='bold')
        return self.fig


# Export main class
__all__ = ['Enhanced3DVisualizer', 'TrajectoryPoint', 'Enhanced3DDebugLogger']
