
"""
Example GUI Integration for Enhanced 3D Visualization

Add this to your GUI button handler where you currently create 3D visualizations.
"""

def on_enhanced_3d_visualization_button_click(self):
    """Handle enhanced 3D visualization button click."""
    
    # Get current ammunition and armor selections from GUI
    ammo = self.get_selected_ammunition()
    armor = self.get_selected_armor()
    
    if not ammo or not armor:
        self.show_error_message("Please select both ammunition and armor.")
        return
    
    # Get parameters from GUI inputs
    target_range = float(self.range_entry.get() or 2000.0)
    launch_angle = float(self.angle_entry.get() or 0.0)
    
    # Set up environmental conditions from GUI (if available)
    from src.physics.advanced_physics import EnvironmentalConditions
    env_conditions = EnvironmentalConditions(
        temperature_celsius=float(self.temp_entry.get() or 20.0),
        wind_speed_ms=float(self.wind_speed_entry.get() or 5.0),
        wind_angle_deg=float(self.wind_angle_entry.get() or 0.0),
        humidity_percent=float(self.humidity_entry.get() or 50.0),
        altitude_m=float(self.altitude_entry.get() or 0.0)
    )
    
    try:
        # Create enhanced 3D visualization
        from src.visualization.enhanced_3d_visualizer import Enhanced3DVisualizer
        
        visualizer = Enhanced3DVisualizer(figsize=(16, 12), debug_level="INFO")
        visualizer.show_trajectory_debug = True  # Enable debug points
        
        # Create interactive visualization
        fig, vis = visualizer.create_interactive_3d_visualization(
            ammo, armor, target_range, launch_angle, env_conditions
        )
        
        if fig:
            # Show the interactive visualization
            import matplotlib.pyplot as plt
            plt.show()
            
            # Optionally save the visualization
            save_path = f"enhanced_3d_viz_{ammo.name}_{armor.name}.png"
            visualizer.save_visualization(save_path, dpi=300)
            
            self.show_info_message(f"Enhanced 3D visualization created and saved to {save_path}")
        else:
            self.show_error_message("Failed to create enhanced 3D visualization.")
            
    except Exception as e:
        self.show_error_message(f"Error creating visualization: {str(e)}")

def on_animated_3d_visualization_button_click(self):
    """Handle animated 3D visualization button click."""
    
    # Get selections (same as above)
    ammo = self.get_selected_ammunition()
    armor = self.get_selected_armor()
    
    if not ammo or not armor:
        self.show_error_message("Please select both ammunition and armor.")
        return
    
    try:
        from src.visualization.enhanced_3d_visualizer import Enhanced3DVisualizer
        from src.physics.advanced_physics import EnvironmentalConditions
        
        # Environmental conditions
        env_conditions = EnvironmentalConditions(
            temperature_celsius=20.0,
            wind_speed_ms=8.0,
            wind_angle_deg=90.0,  # Crosswind for interesting effects
            humidity_percent=70.0
        )
        
        # Create visualizer
        visualizer = Enhanced3DVisualizer(figsize=(18, 12), debug_level="INFO")
        
        # Create animated visualization
        fig = visualizer.create_interactive_3d_visualization(
            ammo, armor, target_range=2000.0, launch_angle=1.0, 
            environmental_conditions=env_conditions
        )
        
        # Enable animation
        animation = visualizer.enable_animation_mode(duration=4.0)
        
        if fig and animation:
            import matplotlib.pyplot as plt
            plt.show()
            
            self.show_info_message("Animated 3D visualization created successfully!")
        else:
            self.show_error_message("Failed to create animated visualization.")
            
    except Exception as e:
        self.show_error_message(f"Error creating animation: {str(e)}")

# Add these buttons to your GUI layout:
# - "Enhanced 3D Visualization" -> calls on_enhanced_3d_visualization_button_click
# - "Animated 3D Visualization" -> calls on_animated_3d_visualization_button_click
