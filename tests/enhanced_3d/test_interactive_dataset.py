"""
Interactive dataset tests for Enhanced 3D visualization.
"""
import os
import json

from src.visualization.enhanced_3d_visualizer import Enhanced3DVisualizer
from src.visualization.cross_section_visualizer import CrossSectionVisualizer
from src.physics.advanced_physics import EnvironmentalConditions
from src.ammunition import APFSDS
from src.armor import CompositeArmor


def test_dataset_export_import():
    # Prepare ammo/armor and environment
    ammo = APFSDS(name="Test Ammo", caliber=120, penetrator_diameter=22,
                  penetrator_mass=8.5, muzzle_velocity=1680, penetrator_length=570)
    armor = CompositeArmor("Test Armor", thickness=600, steel_layers=400, ceramic_layers=200)
    env = EnvironmentalConditions(temperature_celsius=20.0, wind_speed_ms=5.0,
                                  wind_angle_deg=30.0, humidity_percent=60.0, altitude_m=300.0)

    # Create visualization and dataset
    viz = Enhanced3DVisualizer(figsize=(8, 6), debug_level="ERROR")
    fig = viz.create_interactive_3d_visualization(ammo, armor, target_range=2000.0, launch_angle=1.0,
                                                  environmental_conditions=env)

    # Save dataset
    out_dir = os.path.join('results', 'enhanced_3d')
    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, 'test_interactive_dataset.json')
    png_path = os.path.join(out_dir, 'test_interactive_dataset.png')

    viz.save_visualization(png_path, dpi=150)
    viz.save_interactive_dataset(json_path, screenshot_path=png_path)

    assert os.path.exists(json_path), "Interactive dataset JSON was not saved"

    with open(json_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    # Validate dataset contents
    assert dataset.get('type') == 'enhanced_3d_result'
    assert 'trajectory' in dataset and len(dataset['trajectory']) > 0
    assert 'ammunition' in dataset and dataset['ammunition'].get('name') == 'Test Ammo'
    assert 'armor' in dataset and dataset['armor'].get('name') == 'Test Armor'

    # Recreate scene from dataset
    viz2 = Enhanced3DVisualizer(figsize=(8, 6), debug_level="ERROR")
    fig2 = viz2.create_from_dataset(dataset)
    assert fig2 is not None, "Failed to create figure from dataset"


def test_cross_section_render_save():
    # Build a minimal meta structure to feed the cross-section visualizer
    meta = {
        'ammunition': {'name': 'Test Ammo'},
        'armor': {
            'name': 'Test Armor',
            'armor_type': 'composite',
            'thickness_mm': 600,
            'steel_layers_mm': 400,
            'ceramic_layers_mm': 200
        },
        'impact_analysis': {
            'penetration_mm': 650.0,  # penetration greater than thickness to force spall cone
            'penetrates': True,
            'impact_velocity_ms': 1200.0,
            'impact_angle_from_vertical_deg': 30.0
        }
    }

    cs = CrossSectionVisualizer(figsize=(6, 4))
    fig = cs.render_cross_section(meta)

    out_dir = os.path.join('results', 'enhanced_3d')
    os.makedirs(out_dir, exist_ok=True)
    cross_path = os.path.join(out_dir, 'test_cross_section.png')
    cs.save_cross_section(cross_path)

    assert os.path.exists(cross_path), "Cross-section image was not saved"

