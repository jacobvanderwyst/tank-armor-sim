"""
Interactive 3D Visualization System for Tank Armor Simulation

This module provides comprehensive 3D visualization capabilities including:
- 3D tank models with accurate armor layouts
- 3D ballistic trajectories with environmental effects
- 3D penetration analysis with cross-sectional views
- Interactive controls for rotation, zoom, and parameter adjustment
- Real-time environmental effects visualization
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.patches as patches
from matplotlib.widgets import Slider, Button
import matplotlib.animation as animation
from typing import List, Dict, Tuple, Optional, Any
import math


class Interactive3DVisualizer:
    """
    Main class for creating interactive 3D visualizations of tank armor scenarios.
    """
    
    def __init__(self, figsize=(14, 10)):
        """Initialize the 3D visualization system."""
        self.figsize = figsize
        self.fig = None
        self.ax = None
        self.tank_model = None
        self.projectile_path = None
        self.environmental_effects = None
        
        # Animation and interaction variables
        self.animation_frame = 0
        self.animation_running = False
        self.interactive_mode = True
        
    def create_3d_tank_model(self, tank_type: str = "modern_mbt") -> Dict[str, Any]:
        """
        Create detailed 3D tank model with accurate armor layouts.
        
        Args:
            tank_type: Type of tank to model (modern_mbt, historical, etc.)
            
        Returns:
            Dictionary containing tank model geometry and armor data
        """
        
        if tank_type == "modern_mbt":
            # Modern MBT dimensions (based on M1A2/Leopard 2 style)
            tank_model = {
                'hull': self._create_tank_hull(),
                'turret': self._create_tank_turret(),
                'gun': self._create_tank_gun(),
                'tracks': self._create_tank_tracks(),
                'armor_zones': self._create_armor_zones(),
                'dimensions': {
                    'length': 9.8,  # meters
                    'width': 3.7,   # meters  
                    'height': 2.4   # meters
                }
            }
        
        return tank_model
    
    def _create_tank_hull(self) -> Dict[str, np.ndarray]:
        """Create 3D hull geometry with sloped frontal armor."""
        
        # Hull dimensions (meters)
        length, width, height = 7.0, 3.7, 1.8
        
        # Define hull vertices with sloped front
        vertices = np.array([
            # Rear face
            [-length/2, -width/2, 0], [-length/2, width/2, 0],
            [-length/2, width/2, height], [-length/2, -width/2, height],
            
            # Front face (sloped)
            [length/2, -width/2, 0.3], [length/2, width/2, 0.3],
            [length/2, width/2, height], [length/2, -width/2, height],
            
            # Side connection points for slope
            [length/2-0.5, -width/2, 0], [length/2-0.5, width/2, 0],
        ])
        
        # Define faces for hull
        faces = [
            # Bottom
            [0, 1, 9, 8], [1, 5, 4, 9], [8, 9, 4, 0],
            # Top  
            [3, 2, 6, 7],
            # Sides
            [0, 4, 7, 3], [1, 2, 6, 5],
            # Rear
            [0, 3, 2, 1],
            # Front (sloped)
            [4, 5, 6, 7]
        ]
        
        return {
            'vertices': vertices,
            'faces': faces,
            'armor_thickness': {
                'front': 650,  # mm RHA equivalent
                'side': 300,
                'rear': 200,
                'top': 150
            }
        }
    
    def _create_tank_turret(self) -> Dict[str, np.ndarray]:
        """Create 3D turret geometry."""
        
        # Turret positioned on hull
        turret_center = [1.0, 0, 1.8]  # Slightly forward, centered, on hull top
        
        # Simplified turret as truncated cone/cylinder
        radius_base, radius_top = 1.6, 1.4
        height = 1.2
        
        # Create turret vertices (simplified cylindrical)
        angles = np.linspace(0, 2*np.pi, 16)
        
        # Bottom ring
        bottom_verts = np.array([[turret_center[0] + radius_base * np.cos(angle),
                                turret_center[1] + radius_base * np.sin(angle),
                                turret_center[2]] for angle in angles])
        
        # Top ring  
        top_verts = np.array([[turret_center[0] + radius_top * np.cos(angle),
                             turret_center[1] + radius_top * np.sin(angle),
                             turret_center[2] + height] for angle in angles])
        
        vertices = np.vstack([bottom_verts, top_verts])
        
        # Create cylindrical faces
        faces = []
        n_sides = len(angles)
        
        # Side faces
        for i in range(n_sides):
            next_i = (i + 1) % n_sides
            faces.append([i, next_i, next_i + n_sides, i + n_sides])
        
        return {
            'vertices': vertices,
            'faces': faces,
            'armor_thickness': {
                'front': 800,  # mm RHA equivalent
                'side': 400,
                'rear': 250
            }
        }
    
    def _create_tank_gun(self) -> Dict[str, np.ndarray]:
        """Create 3D tank gun barrel."""
        
        # Gun parameters
        gun_length = 6.0  # meters (120mm L/44)
        gun_diameter = 0.12  # 120mm
        elevation_angle = 0  # degrees
        
        # Gun positioned at turret front
        gun_base = [1.4, 0, 2.4]
        
        # Gun barrel as cylinder
        gun_end = [
            gun_base[0] + gun_length * np.cos(np.radians(elevation_angle)),
            gun_base[1], 
            gun_base[2] + gun_length * np.sin(np.radians(elevation_angle))
        ]
        
        # Create cylindrical gun barrel
        angles = np.linspace(0, 2*np.pi, 12)
        
        base_verts = np.array([[gun_base[0], 
                              gun_base[1] + gun_diameter/2 * np.cos(angle),
                              gun_base[2] + gun_diameter/2 * np.sin(angle)] 
                             for angle in angles])
        
        end_verts = np.array([[gun_end[0],
                             gun_end[1] + gun_diameter/2 * np.cos(angle), 
                             gun_end[2] + gun_diameter/2 * np.sin(angle)]
                            for angle in angles])
        
        vertices = np.vstack([base_verts, end_verts])
        
        # Create faces
        faces = []
        n_sides = len(angles)
        for i in range(n_sides):
            next_i = (i + 1) % n_sides
            faces.append([i, next_i, next_i + n_sides, i + n_sides])
        
        return {
            'vertices': vertices,
            'faces': faces,
            'muzzle_position': gun_end,
            'bore_diameter': gun_diameter
        }
    
    def _create_tank_tracks(self) -> Dict[str, np.ndarray]:
        """Create simplified tank track representation."""
        
        # Track dimensions
        track_width = 0.6
        track_length = 6.0
        track_height = 0.8
        
        # Left track
        left_track = {
            'vertices': np.array([
                [-track_length/2, -2.0, 0], [track_length/2, -2.0, 0],
                [track_length/2, -2.0 + track_width, 0], [-track_length/2, -2.0 + track_width, 0],
                [-track_length/2, -2.0, track_height], [track_length/2, -2.0, track_height],
                [track_length/2, -2.0 + track_width, track_height], [-track_length/2, -2.0 + track_width, track_height]
            ]),
            'faces': [
                [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7],  # Sides
                [0, 1, 2, 3], [4, 5, 6, 7]  # Top and bottom
            ]
        }
        
        # Right track (mirrored)
        right_track = {
            'vertices': np.array([
                [-track_length/2, 2.0 - track_width, 0], [track_length/2, 2.0 - track_width, 0],
                [track_length/2, 2.0, 0], [-track_length/2, 2.0, 0],
                [-track_length/2, 2.0 - track_width, track_height], [track_length/2, 2.0 - track_width, track_height],
                [track_length/2, 2.0, track_height], [-track_length/2, 2.0, track_height]
            ]),
            'faces': [
                [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7],
                [0, 1, 2, 3], [4, 5, 6, 7]
            ]
        }
        
        return {'left': left_track, 'right': right_track}
    
    def _create_armor_zones(self) -> Dict[str, Dict]:
        """Create armor zone definitions with thickness and materials."""
        
        zones = {
            'hull_front': {
                'thickness': 650,  # mm RHA equivalent
                'material': 'composite',
                'angle': 68,  # degrees from vertical
                'area': [[2.5, -1.8, 0.3], [2.5, 1.8, 0.3], [2.5, 1.8, 1.8], [2.5, -1.8, 1.8]]
            },
            'hull_side': {
                'thickness': 300,
                'material': 'steel', 
                'angle': 0,
                'area': [[-3.5, 1.85, 0], [3.5, 1.85, 0], [3.5, 1.85, 1.8], [-3.5, 1.85, 1.8]]
            },
            'turret_front': {
                'thickness': 800,
                'material': 'composite',
                'angle': 30,
                'area': 'cylindrical_front'  # Special case for turret
            }
        }
        
        return zones
    
    def create_3d_trajectory(self, ammunition, target_range: float, launch_angle: float,
                           environmental_conditions: Optional[Dict] = None) -> Dict[str, np.ndarray]:
        """
        Calculate and create 3D ballistic trajectory with environmental effects.
        
        Args:
            ammunition: Ammunition object
            target_range: Target distance in meters
            launch_angle: Launch elevation angle in degrees
            environmental_conditions: Environmental parameters
            
        Returns:
            Dictionary containing 3D trajectory data and environmental effects
        """
        
        # Enhanced 3D trajectory calculation
        g = 9.81  # gravity
        dt = 0.01  # time step
        
        # Initial conditions
        v0 = ammunition.muzzle_velocity
        angle_rad = np.radians(launch_angle)
        
        # Environmental effects
        if environmental_conditions:
            wind_speed = environmental_conditions.get('wind_speed', 0)
            wind_direction = environmental_conditions.get('wind_direction', 0)  # degrees
            temperature = environmental_conditions.get('temperature', 15)
            altitude = environmental_conditions.get('altitude', 0)
            humidity = environmental_conditions.get('humidity', 50)
        else:
            wind_speed = 0
            wind_direction = 0
            temperature = 15
            altitude = 0
            humidity = 50
        
        # Air density adjustment for altitude and temperature
        air_density_factor = (1 - 0.0065 * altitude / 288.15) * (288.15 / (temperature + 273.15))
        
        # Drag coefficient (simplified)
        Cd = 0.15 * air_density_factor
        
        # Initialize trajectory arrays
        trajectory_points = []
        
        # Initial velocity components
        vx = v0 * np.cos(angle_rad)
        vy = 0  # No initial lateral velocity
        vz = v0 * np.sin(angle_rad)
        
        # Position
        x, y, z = 0, 0, 2.5  # Start at gun height
        t = 0
        
        # Wind effect components
        wind_x = wind_speed * np.cos(np.radians(wind_direction))
        wind_y = wind_speed * np.sin(np.radians(wind_direction))
        
        while z >= 0 and x <= target_range * 1.5:  # Continue until ground impact or max range
            
            # Current velocity magnitude
            v_mag = np.sqrt(vx**2 + vy**2 + vz**2)
            
            # Drag force components
            if v_mag > 0:
                drag_factor = Cd * v_mag
                drag_x = -drag_factor * vx
                drag_y = -drag_factor * vy  
                drag_z = -drag_factor * vz
            else:
                drag_x = drag_y = drag_z = 0
            
            # Wind effects (simplified)
            wind_effect_x = (wind_x - vx) * 0.001  # Wind resistance
            wind_effect_y = (wind_y - vy) * 0.001
            
            # Update velocities
            vx += (drag_x + wind_effect_x) * dt
            vy += (drag_y + wind_effect_y) * dt
            vz += (-g + drag_z) * dt
            
            # Update position
            x += vx * dt
            y += vy * dt
            z += vz * dt
            t += dt
            
            # Store point with additional data
            trajectory_points.append({
                'position': [x, y, z],
                'velocity': [vx, vy, vz],
                'speed': v_mag,
                'time': t,
                'drag_effect': np.sqrt(drag_x**2 + drag_y**2 + drag_z**2),
                'wind_effect': np.sqrt(wind_effect_x**2 + wind_effect_y**2)
            })
        
        return {
            'trajectory_points': trajectory_points,
            'environmental_effects': {
                'air_density_factor': air_density_factor,
                'total_wind_deflection': trajectory_points[-1]['position'][1] if trajectory_points else 0,
                'flight_time': t,
                'impact_velocity': v_mag,
                'drag_losses': v0 - v_mag
            }
        }
    
    def create_3d_penetration_analysis(self, ammunition, armor, impact_point: List[float],
                                     impact_angle: float) -> Dict[str, Any]:
        """
        Create 3D cross-sectional penetration analysis visualization.
        
        Args:
            ammunition: Ammunition object
            armor: Armor object  
            impact_point: 3D coordinates of impact [x, y, z]
            impact_angle: Impact angle in degrees
            
        Returns:
            Dictionary containing 3D penetration analysis data
        """
        
        analysis = {
            'impact_point': impact_point,
            'impact_angle': impact_angle,
            'penetration_depth': 0,
            'armor_response': {},
            'behind_armor_effects': {},
            'cross_section_data': {}
        }
        
        # Calculate penetration with advanced physics if available
        try:
            penetration = ammunition.calculate_penetration(
                range_m=100,  # Close range for impact analysis
                impact_angle=impact_angle
            )
            
            effective_thickness = armor.get_effective_thickness(
                ammunition.penetration_type, 
                impact_angle
            )
            
            analysis['penetration_depth'] = min(penetration, effective_thickness + 100)  # mm
            analysis['penetrates'] = penetration > effective_thickness
            
        except Exception as e:
            # Fallback calculation
            analysis['penetration_depth'] = 300  # mm default
            analysis['penetrates'] = True
        
        # Create 3D cross-section geometry
        analysis['cross_section_data'] = self._create_penetration_cross_section(
            impact_point, impact_angle, analysis['penetration_depth'], ammunition.penetration_type
        )
        
        # Armor response visualization
        analysis['armor_response'] = self._create_armor_response_3d(
            impact_point, impact_angle, armor, analysis['penetration_depth']
        )
        
        # Behind-armor effects
        if analysis['penetrates']:
            analysis['behind_armor_effects'] = self._create_behind_armor_effects_3d(
                impact_point, ammunition.penetration_type, analysis['penetration_depth']
            )
        
        return analysis
    
    def _create_penetration_cross_section(self, impact_point: List[float], 
                                        impact_angle: float, penetration_depth: float,
                                        ammo_type: str) -> Dict[str, np.ndarray]:
        """Create 3D cross-section showing penetration process."""
        
        # Create penetration channel based on ammunition type
        if ammo_type == 'kinetic':
            # Long rod penetrator
            channel_data = self._create_kinetic_penetration_channel(
                impact_point, impact_angle, penetration_depth
            )
        elif ammo_type == 'chemical':
            # HEAT jet penetration
            channel_data = self._create_heat_penetration_channel(
                impact_point, impact_angle, penetration_depth
            )
        else:
            # Generic penetration
            channel_data = self._create_generic_penetration_channel(
                impact_point, impact_angle, penetration_depth
            )
        
        return channel_data
    
    def _create_kinetic_penetration_channel(self, impact_point: List[float],
                                          impact_angle: float, penetration_depth: float) -> Dict:
        """Create kinetic penetrator channel geometry."""
        
        # APFSDS penetrator parameters
        penetrator_diameter = 0.022  # 22mm typical
        channel_length = penetration_depth / 1000  # Convert mm to meters
        
        # Create cylindrical penetration channel
        angles = np.linspace(0, 2*np.pi, 12)
        
        # Entry point
        entry_verts = []
        for angle in angles:
            x_offset = penetrator_diameter/2 * np.cos(angle)
            y_offset = penetrator_diameter/2 * np.sin(angle)
            entry_verts.append([
                impact_point[0] + x_offset,
                impact_point[1] + y_offset, 
                impact_point[2]
            ])
        
        # Exit point (if penetrating)
        exit_verts = []
        penetration_vector = [
            -channel_length * np.cos(np.radians(impact_angle)),
            0,
            -channel_length * np.sin(np.radians(impact_angle))
        ]
        
        for angle in angles:
            x_offset = penetrator_diameter/2 * np.cos(angle) * 1.2  # Slight expansion
            y_offset = penetrator_diameter/2 * np.sin(angle) * 1.2
            exit_verts.append([
                impact_point[0] + penetration_vector[0] + x_offset,
                impact_point[1] + penetration_vector[1] + y_offset,
                impact_point[2] + penetration_vector[2]
            ])
        
        return {
            'entry_vertices': np.array(entry_verts),
            'exit_vertices': np.array(exit_verts),
            'channel_type': 'kinetic',
            'penetrator_fragments': self._create_penetrator_fragments(impact_point, penetration_vector)
        }
    
    def _create_heat_penetration_channel(self, impact_point: List[float],
                                       impact_angle: float, penetration_depth: float) -> Dict:
        """Create HEAT jet penetration channel geometry."""
        
        # HEAT jet parameters
        jet_diameter_entry = 0.006  # 6mm entry
        jet_diameter_exit = 0.020   # 20mm exit (expansion)
        channel_length = penetration_depth / 1000
        
        # Create conical penetration channel
        angles = np.linspace(0, 2*np.pi, 12)
        
        # Entry (small diameter)
        entry_verts = []
        for angle in angles:
            x_offset = jet_diameter_entry/2 * np.cos(angle)
            y_offset = jet_diameter_entry/2 * np.sin(angle)
            entry_verts.append([
                impact_point[0] + x_offset,
                impact_point[1] + y_offset,
                impact_point[2]
            ])
        
        # Exit (larger diameter)
        exit_verts = []
        penetration_vector = [
            -channel_length * np.cos(np.radians(impact_angle)),
            0,
            -channel_length * np.sin(np.radians(impact_angle))
        ]
        
        for angle in angles:
            x_offset = jet_diameter_exit/2 * np.cos(angle)
            y_offset = jet_diameter_exit/2 * np.sin(angle)
            exit_verts.append([
                impact_point[0] + penetration_vector[0] + x_offset,
                impact_point[1] + penetration_vector[1] + y_offset,
                impact_point[2] + penetration_vector[2]
            ])
        
        return {
            'entry_vertices': np.array(entry_verts),
            'exit_vertices': np.array(exit_verts), 
            'channel_type': 'heat',
            'molten_effects': self._create_heat_effects(impact_point, penetration_vector)
        }
    
    def _create_generic_penetration_channel(self, impact_point: List[float],
                                          impact_angle: float, penetration_depth: float) -> Dict:
        """Create generic penetration channel."""
        
        channel_diameter = 0.050  # 50mm generic
        channel_length = penetration_depth / 1000
        
        angles = np.linspace(0, 2*np.pi, 8)
        
        entry_verts = []
        for angle in angles:
            x_offset = channel_diameter/2 * np.cos(angle)
            y_offset = channel_diameter/2 * np.sin(angle)
            entry_verts.append([
                impact_point[0] + x_offset,
                impact_point[1] + y_offset,
                impact_point[2]
            ])
        
        return {
            'entry_vertices': np.array(entry_verts),
            'channel_type': 'generic'
        }
    
    def _create_armor_response_3d(self, impact_point: List[float], impact_angle: float,
                                armor, penetration_depth: float) -> Dict:
        """Create 3D armor response visualization."""
        
        return {
            'deformation_zone': self._create_deformation_zone(impact_point, penetration_depth),
            'crack_patterns': self._create_crack_patterns(impact_point, armor.armor_type),
            'material_displacement': self._create_material_displacement(impact_point, impact_angle)
        }
    
    def _create_behind_armor_effects_3d(self, impact_point: List[float], 
                                      ammo_type: str, penetration_depth: float) -> Dict:
        """Create behind-armor effects visualization."""
        
        if ammo_type == 'kinetic':
            return {
                'spall_cone': self._create_spall_cone(impact_point, penetration_depth),
                'fragments': self._create_armor_fragments(impact_point),
                'penetrator_residual': self._create_penetrator_residual(impact_point)
            }
        elif ammo_type == 'chemical':
            return {
                'blast_effects': self._create_blast_effects(impact_point),
                'molten_spray': self._create_molten_spray(impact_point),
                'thermal_effects': self._create_thermal_effects(impact_point)
            }
        else:
            return {
                'general_effects': self._create_general_effects(impact_point)
            }
    
    def _create_spall_cone(self, impact_point: List[float], penetration_depth: float) -> np.ndarray:
        """Create spall cone geometry for behind-armor effects."""
        
        # Spall cone parameters
        cone_angle = 30  # degrees
        cone_length = penetration_depth / 500  # Proportional to penetration
        
        # Create cone vertices
        angles = np.linspace(0, 2*np.pi, 16)
        cone_radius = cone_length * np.tan(np.radians(cone_angle))
        
        # Apex at penetration exit
        apex = [impact_point[0], impact_point[1], impact_point[2] - penetration_depth/1000]
        
        # Base vertices
        base_verts = []
        for angle in angles:
            x_offset = cone_radius * np.cos(angle)
            y_offset = cone_radius * np.sin(angle) 
            base_verts.append([
                apex[0] + x_offset,
                apex[1] + y_offset,
                apex[2] - cone_length
            ])
        
        return {
            'apex': apex,
            'base_vertices': np.array(base_verts),
            'cone_angle': cone_angle
        }
    
    # Helper methods for creating various 3D effects
    def _create_penetrator_fragments(self, impact_point: List[float], 
                                   penetration_vector: List[float]) -> List[np.ndarray]:
        """Create fragmented penetrator pieces."""
        fragments = []
        
        for i in range(5):  # 5 fragment pieces
            fragment_pos = [
                impact_point[0] + penetration_vector[0] * (0.2 + 0.15 * i) + np.random.uniform(-0.05, 0.05),
                impact_point[1] + np.random.uniform(-0.03, 0.03),
                impact_point[2] + penetration_vector[2] * (0.2 + 0.15 * i) + np.random.uniform(-0.02, 0.02)
            ]
            fragments.append(np.array(fragment_pos))
        
        return fragments
    
    def _create_heat_effects(self, impact_point: List[float], 
                           penetration_vector: List[float]) -> Dict:
        """Create HEAT jet thermal effects."""
        return {
            'molten_metal': [
                impact_point[0] + penetration_vector[0] * 0.3,
                impact_point[1],
                impact_point[2] + penetration_vector[2] * 0.3
            ],
            'thermal_zone_radius': 0.1  # 10cm thermal effect radius
        }
    
    def _create_deformation_zone(self, impact_point: List[float], 
                               penetration_depth: float) -> Dict:
        """Create armor deformation zone around impact."""
        
        deformation_radius = max(0.05, penetration_depth / 5000)  # Scale with penetration
        
        return {
            'center': impact_point,
            'radius': deformation_radius,
            'depth': penetration_depth / 2000  # Half penetration depth in meters
        }
    
    def _create_crack_patterns(self, impact_point: List[float], armor_type: str) -> List:
        """Create crack pattern geometry based on armor type."""
        
        cracks = []
        
        if armor_type == 'steel':
            # Radial cracks for steel armor
            for angle in np.linspace(0, 2*np.pi, 8):
                crack_length = np.random.uniform(0.05, 0.15)
                crack_end = [
                    impact_point[0] + crack_length * np.cos(angle),
                    impact_point[1] + crack_length * np.sin(angle),
                    impact_point[2]
                ]
                cracks.append([impact_point, crack_end])
        
        elif armor_type == 'composite':
            # Layered failure patterns
            for i in range(3):
                layer_offset = i * 0.02
                crack_end = [
                    impact_point[0] + np.random.uniform(-0.1, 0.1),
                    impact_point[1] + np.random.uniform(-0.1, 0.1),
                    impact_point[2] - layer_offset
                ]
                cracks.append([impact_point, crack_end])
        
        return cracks
    
    def _create_material_displacement(self, impact_point: List[float], 
                                    impact_angle: float) -> Dict:
        """Create displaced material around impact point."""
        
        return {
            'displaced_volume': 0.001,  # 1 liter of displaced material
            'displacement_direction': [
                -np.cos(np.radians(impact_angle)),
                0,
                -np.sin(np.radians(impact_angle))
            ]
        }
    
    # Additional helper methods for other effects...
    def _create_armor_fragments(self, impact_point: List[float]) -> List:
        """Create armor fragment positions."""
        fragments = []
        for i in range(10):
            fragment_pos = [
                impact_point[0] + np.random.uniform(-0.2, 0.2),
                impact_point[1] + np.random.uniform(-0.2, 0.2),
                impact_point[2] - np.random.uniform(0.05, 0.3)
            ]
            fragments.append(fragment_pos)
        return fragments
    
    def _create_penetrator_residual(self, impact_point: List[float]) -> Dict:
        """Create residual penetrator geometry."""
        return {
            'position': [impact_point[0], impact_point[1], impact_point[2] - 0.1],
            'length': 0.05,  # Remaining penetrator length
            'deformed': True
        }
    
    def _create_blast_effects(self, impact_point: List[float]) -> Dict:
        """Create blast effect visualization."""
        return {
            'blast_center': impact_point,
            'blast_radius': 0.3,  # 30cm blast effect
            'pressure_wave': True
        }
    
    def _create_molten_spray(self, impact_point: List[float]) -> List:
        """Create molten metal spray pattern."""
        spray_points = []
        for i in range(20):
            spray_point = [
                impact_point[0] + np.random.uniform(-0.15, 0.15),
                impact_point[1] + np.random.uniform(-0.15, 0.15),
                impact_point[2] - np.random.uniform(0.1, 0.5)
            ]
            spray_points.append(spray_point)
        return spray_points
    
    def _create_thermal_effects(self, impact_point: List[float]) -> Dict:
        """Create thermal effect zone."""
        return {
            'thermal_center': impact_point,
            'temperature_rise': 1000,  # Celsius
            'affected_radius': 0.2   # 20cm thermal radius
        }
    
    def _create_general_effects(self, impact_point: List[float]) -> Dict:
        """Create general behind-armor effects."""
        return {
            'debris_field': [
                [impact_point[0] + np.random.uniform(-0.1, 0.1),
                 impact_point[1] + np.random.uniform(-0.1, 0.1),
                 impact_point[2] - np.random.uniform(0.05, 0.2)]
                for _ in range(15)
            ],
            'impact_energy_dissipation': True
        }


class Environmental3DEffects:
    """Class for creating 3D environmental effect visualizations."""
    
    def __init__(self):
        self.wind_vectors = []
        self.temperature_zones = []
        self.atmospheric_layers = []
    
    def create_wind_visualization(self, wind_speed: float, wind_direction: float,
                                field_size: Tuple[float, float, float] = (20, 20, 10)) -> Dict:
        """Create 3D wind field visualization."""
        
        # Create wind vector field
        x_range = np.linspace(-field_size[0]/2, field_size[0]/2, 8)
        y_range = np.linspace(-field_size[1]/2, field_size[1]/2, 6)
        z_range = np.linspace(0, field_size[2], 4)
        
        wind_vectors = []
        
        for x in x_range:
            for y in y_range:
                for z in z_range:
                    # Wind vector components
                    wind_x = wind_speed * np.cos(np.radians(wind_direction))
                    wind_y = wind_speed * np.sin(np.radians(wind_direction))
                    wind_z = 0  # Simplified horizontal wind
                    
                    # Add some turbulence variation
                    turbulence_factor = 0.1 * np.random.uniform(-1, 1)
                    wind_x += turbulence_factor
                    wind_y += turbulence_factor
                    
                    wind_vectors.append({
                        'position': [x, y, z],
                        'vector': [wind_x, wind_y, wind_z],
                        'magnitude': wind_speed
                    })
        
        return {'vectors': wind_vectors, 'base_speed': wind_speed, 'direction': wind_direction}
    
    def create_temperature_gradient(self, temp_ground: float, temp_altitude: float,
                                  field_size: Tuple[float, float, float] = (20, 20, 10)) -> Dict:
        """Create 3D temperature gradient visualization."""
        
        temperature_field = []
        
        # Create temperature layers
        z_levels = np.linspace(0, field_size[2], 10)
        
        for z in z_levels:
            # Linear temperature gradient with altitude
            temp_at_altitude = temp_ground + (temp_altitude - temp_ground) * (z / field_size[2])
            
            temperature_field.append({
                'altitude': z,
                'temperature': temp_at_altitude,
                'thermal_effect': abs(temp_at_altitude - 15) * 0.01  # Effect factor
            })
        
        return {
            'temperature_layers': temperature_field,
            'gradient_rate': (temp_altitude - temp_ground) / field_size[2]
        }
    
    def create_atmospheric_effects(self, altitude: float, humidity: float,
                                 pressure: float = 1013.25) -> Dict:
        """Create atmospheric condition visualization."""
        
        return {
            'air_density': pressure / (287.05 * (15 + 273.15)) * (1 - 0.0065 * altitude / 288.15),
            'humidity_effect': humidity / 100.0,
            'visibility_factor': max(0.1, 1.0 - humidity / 200.0),
            'atmospheric_layers': [
                {'altitude': 0, 'density': 1.225, 'humidity': humidity},
                {'altitude': altitude, 'density': 1.225 * (1 - 0.0065 * altitude / 288.15), 'humidity': humidity * 0.8}
            ]
        }


# Export main classes
__all__ = ['Interactive3DVisualizer', 'Environmental3DEffects']
