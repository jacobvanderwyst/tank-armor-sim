"""
Backfill tests for cross-section rendering modes and GUI overlay toggles.
"""
import os
import json
import tempfile
import tkinter as tk
from unittest.mock import patch
import matplotlib
matplotlib.use('Agg')

from src.visualization.cross_section_visualizer import CrossSectionVisualizer
from gui_main import TankArmorSimulatorGUI


def _make_meta(penetrates=True, pen_mm=650.0, angle_from_vertical=30.0):
    return {
        'ammunition': {'name': 'Test Ammo'},
        'armor': {
            'name': 'Test Armor',
            'armor_type': 'composite',
            'thickness_mm': 600,
            'steel_layers_mm': 400,
            'ceramic_layers_mm': 200
        },
        'impact_analysis': {
            'penetration_mm': float(pen_mm),
            'penetrates': bool(penetrates),
            'impact_velocity_ms': 1200.0,
            'impact_angle_from_vertical_deg': float(angle_from_vertical)
        }
    }


def test_cross_section_true_path_mode_renders():
    meta = _make_meta(penetrates=True)
    cs = CrossSectionVisualizer(figsize=(6, 4), mode='true_path')
    fig = cs.render_cross_section(meta)
    assert fig is not None
    # channel polyline + spall should create multiple line objects
    ax = cs.ax
    assert len(ax.lines) >= 4, 'Expected multiple line elements (channel + spall)'


def _create_dataset_with_overlays(tmp_dir):
    data = {
        'version': '1.0',
        'type': 'enhanced_3d_result',
        'ammunition': {'name': 'Test Ammo', 'penetration_type': 'kinetic'},
        'armor': {'name': 'Test Armor', 'armor_type': 'RHA', 'thickness_mm': 200},
        'environment': {},
        'parameters': {'target_range': 1000.0, 'launch_angle': 0.0},
        'trajectory': [
            {'x': 0.0, 'y': 0.0, 'z': 2.0, 'vx': 0, 'vy': 0, 'vz': 0, 'speed': 1000, 'time': 0.0, 'cd': 0.3, 'air_density': 1.2, 'angle_of_attack_deg': 0.0},
            {'x': 10.0, 'y': 0.0, 'z': 0.0, 'vx': 0, 'vy': 0, 'vz': 0, 'speed': 900, 'time': 1.0, 'cd': 0.3, 'air_density': 1.2, 'angle_of_attack_deg': 0.0}
        ],
        'impact_analysis': {
            'penetrates': True,
            'impact_position_m': {'x': 5.0, 'y': 0.0, 'z': 1.0},
            'channel_segments': [
                {'part': 'hull', 'start': {'x': 5.0, 'y': 0.0, 'z': 1.0}, 'end': {'x': 5.1, 'y': 0.0, 'z': 0.8}, 'partial': False}
            ],
            'overpenetration': True,
            'exit_point': {'x': 5.1, 'y': 0.0, 'z': 0.8},
            'ricochet': True,
            'ricochet_outcome': 'ricochet',
            'ricochet_point': {'x': 5.0, 'y': 0.0, 'z': 1.0},
            'ricochet_direction': {'x': 1.0, 'y': 0.0, 'z': 0.0}
        },
        'assets': {}
    }
    p = os.path.join(tmp_dir, 'gui_toggle_dataset.json')
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f)
    return p


def test_gui_overlay_toggles_with_interactive_dataset(tmp_path):
    # Prepare dataset file
    dataset_path = _create_dataset_with_overlays(str(tmp_path))

    # Start GUI (headless)
    app = TankArmorSimulatorGUI()
    app.root.withdraw()

    # Disable overlays via defaults
    app.show_channels_overlay_default = False
    app.show_ricochet_overlay_default = False

    # Patch file dialog to auto-return our dataset
    with patch('tkinter.filedialog.askopenfilename', return_value=dataset_path):
        app.open_interactive_result()

    # Get the last visualizer used and verify overlays suppressed
    viz = app._last_enhanced_visualizer
    assert viz is not None
    red_lines = [ln for ln in viz.ax.lines if ln.get_color() in ('red', '#ff0000', (1.0, 0.0, 0.0, 1.0))]
    yellow_lines = [ln for ln in viz.ax.lines if ln.get_color() in ('yellow', '#ffff00', (1.0, 1.0, 0.0, 1.0))]
    assert len(red_lines) == 0, 'Channel overlays should be hidden when disabled'
    assert len(yellow_lines) == 0, 'Ricochet overlays should be hidden when disabled'

    # Enable overlays and re-open
    app.show_channels_overlay_default = True
    app.show_ricochet_overlay_default = True
    with patch('tkinter.filedialog.askopenfilename', return_value=dataset_path):
        app.open_interactive_result()
    viz2 = app._last_enhanced_visualizer
    red_lines2 = [ln for ln in viz2.ax.lines if ln.get_color() in ('red', '#ff0000', (1.0, 0.0, 0.0, 1.0))]
    yellow_lines2 = [ln for ln in viz2.ax.lines if ln.get_color() in ('yellow', '#ffff00', (1.0, 1.0, 0.0, 1.0))]
    assert len(red_lines2) >= 1, 'Channel overlays should be visible when enabled'
    assert len(yellow_lines2) >= 1, 'Ricochet overlay should be visible when enabled'

