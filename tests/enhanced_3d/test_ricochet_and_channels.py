"""
Tests for ricochet outcomes and multi-part channel rendering/export in the
Enhanced 3D visualization system.
"""
import os
import json
import tempfile
import matplotlib
matplotlib.use('Agg')

from src.visualization.enhanced_3d_visualizer import Enhanced3DVisualizer


def _minimal_trajectory(n=5):
    # Simple straight-line descending trajectory
    traj = []
    for i in range(n):
        t = i / (n - 1 if n > 1 else 1)
        traj.append({
            'x': float(t * 10.0),
            'y': 0.0,
            'z': float(2.0 - 2.0 * t),
            'vx': 0.0, 'vy': 0.0, 'vz': 0.0,
            'speed': 1000.0 * (1.0 - 0.1 * t),
            'time': t,
            'cd': 0.3,
            'air_density': 1.2,
            'angle_of_attack_deg': 0.0,
        })
    return traj


def _base_dataset():
    return {
        'version': '1.0',
        'type': 'enhanced_3d_result',
        'ammunition': {'name': 'Test Ammo', 'penetration_type': 'kinetic'},
        'armor': {'name': 'Test Armor', 'armor_type': 'RHA', 'thickness_mm': 200},
        'environment': {},
        'parameters': {'target_range': 1000.0, 'launch_angle': 0.0},
        'impact_analysis': {},
        'trajectory': _minimal_trajectory(),
        'assets': {}
    }


def test_export_includes_new_ricochet_and_channel_fields(tmp_path):
    viz = Enhanced3DVisualizer(figsize=(6, 4), debug_level="ERROR")
    # Minimal trajectory to allow export
    viz.trajectory_points = []
    for d in _minimal_trajectory():
        from src.visualization.enhanced_3d_visualizer import TrajectoryPoint
        viz.trajectory_points.append(TrajectoryPoint(
            x=d['x'], y=d['y'], z=d['z'],
            velocity_x=d['vx'], velocity_y=d['vy'], velocity_z=d['vz'],
            velocity_magnitude=d['speed'], time=d['time'],
            drag_coefficient=d['cd'], air_density=d['air_density'],
            angle_of_attack=d['angle_of_attack_deg'], debug_info={}
        ))

    viz.meta['ammunition'] = {'name': 'Test Ammo', 'penetration_type': 'kinetic'}
    viz.meta['armor'] = {'name': 'Test Armor', 'armor_type': 'RHA', 'thickness_mm': 200}
    viz.meta['environment'] = {}
    viz.meta['parameters'] = {'target_range': 1000.0, 'launch_angle': 0.0}

    # Inject analysis with new fields
    viz.meta['impact_analysis'] = {
        'penetrates': True,
        'penetration_mm': 300.0,
        'effective_thickness_mm': 200.0,
        'impact_position_m': {'x': 5.0, 'y': 0.0, 'z': 1.0},
        'channel_segments': [
            {'part': 'hull', 'start': {'x': 5.0, 'y': 0.0, 'z': 1.0}, 'end': {'x': 5.1, 'y': 0.0, 'z': 0.8}, 'partial': False}
        ],
        'overpenetration': True,
        'exit_point': {'x': 5.1, 'y': 0.0, 'z': 0.8},
        'ricochet': True,
        'ricochet_outcome': 'ricochet',
        'ricochet_point': {'x': 5.0, 'y': 0.0, 'z': 1.0},
        'ricochet_direction': {'x': 0.5, 'y': 0.2, 'z': 0.1},
        'ricochet_details': {
            'probability': 0.7,
            'deflection_angle_deg': 25.0,
            'exit_velocity_ms': 800.0,
            'energy_retained': 0.6,
            'critical_angle_deg': 65.0,
            'predicted_outcome': 'ricochet'
        }
    }

    out_file = tmp_path / 'export_test.json'
    viz.save_interactive_dataset(str(out_file))

    assert out_file.exists(), 'Export file not created'

    data = json.loads(out_file.read_text('utf-8'))
    ia = data.get('impact_analysis') or {}
    assert 'channel_segments' in ia and isinstance(ia['channel_segments'], list)
    assert 'ricochet' in ia and ia['ricochet'] is True
    assert ia.get('ricochet_outcome') == 'ricochet'
    assert 'ricochet_point' in ia and 'ricochet_direction' in ia
    assert 'ricochet_details' in ia and 'probability' in ia['ricochet_details']


def test_create_from_dataset_renders_ricochet_outcomes_line_differences():
    # Baseline dataset (no ricochet overlay)
    base = _base_dataset()
    viz_base = Enhanced3DVisualizer(figsize=(6, 4), debug_level="ERROR")
    fig_base = viz_base.create_from_dataset(base)
    assert fig_base is not None
    base_lines = len(viz_base.ax.lines)

    # Ricochet outcome: should add a line overlay
    ric = _base_dataset()
    ric['impact_analysis'] = {
        'penetrates': False,
        'impact_position_m': {'x': 5.0, 'y': 0.0, 'z': 1.0},
        'ricochet': True,
        'ricochet_outcome': 'ricochet',
        'ricochet_point': {'x': 5.0, 'y': 0.0, 'z': 1.0},
        'ricochet_direction': {'x': 1.0, 'y': 0.0, 'z': 0.0}
    }
    viz_ric = Enhanced3DVisualizer(figsize=(6, 4), debug_level="ERROR")
    fig_ric = viz_ric.create_from_dataset(ric)
    assert fig_ric is not None
    ric_lines = len(viz_ric.ax.lines)
    assert ric_lines > base_lines, "Ricochet outcome should add an outbound line"

    # Embedding: should not add an outbound line
    emb = _base_dataset()
    emb['impact_analysis'] = {
        'penetrates': False,
        'impact_position_m': {'x': 5.0, 'y': 0.0, 'z': 1.0},
        'ricochet': True,
        'ricochet_outcome': 'embedding',
        'ricochet_point': {'x': 5.0, 'y': 0.0, 'z': 1.0}
    }
    viz_emb = Enhanced3DVisualizer(figsize=(6, 4), debug_level="ERROR")
    fig_emb = viz_emb.create_from_dataset(emb)
    assert fig_emb is not None
    emb_lines = len(viz_emb.ax.lines)
    assert emb_lines == base_lines, "Embedding should not add an outbound line"

    # Shattering: should not add an outbound line
    sha = _base_dataset()
    sha['impact_analysis'] = {
        'penetrates': False,
        'impact_position_m': {'x': 5.0, 'y': 0.0, 'z': 1.0},
        'ricochet': True,
        'ricochet_outcome': 'shattering',
        'ricochet_point': {'x': 5.0, 'y': 0.0, 'z': 1.0}
    }
    viz_sha = Enhanced3DVisualizer(figsize=(6, 4), debug_level="ERROR")
    fig_sha = viz_sha.create_from_dataset(sha)
    assert fig_sha is not None
    sha_lines = len(viz_sha.ax.lines)
    assert sha_lines == base_lines, "Shattering should not add an outbound line"


def test_create_from_dataset_renders_channel_segments_and_exit_marker():
    base = _base_dataset()
    # Add two channel segments and overpenetration
    base['impact_analysis'] = {
        'penetrates': True,
        'penetration_mm': 400.0,
        'effective_thickness_mm': 200.0,
        'impact_position_m': {'x': 5.0, 'y': 0.0, 'z': 1.0},
        'channel_segments': [
            {'part': 'hull', 'start': {'x': 5.0, 'y': 0.0, 'z': 1.0}, 'end': {'x': 5.1, 'y': 0.0, 'z': 0.9}, 'partial': False},
            {'part': 'turret', 'start': {'x': 5.1, 'y': 0.0, 'z': 0.9}, 'end': {'x': 5.3, 'y': 0.0, 'z': 0.5}, 'partial': False}
        ],
        'overpenetration': True,
        'exit_point': {'x': 5.3, 'y': 0.0, 'z': 0.5}
    }
    # Baseline to compare lines
    empty = _base_dataset()
    viz_empty = Enhanced3DVisualizer(figsize=(6, 4), debug_level="ERROR")
    fig_empty = viz_empty.create_from_dataset(empty)
    assert fig_empty is not None
    base_lines = len(viz_empty.ax.lines)

    viz = Enhanced3DVisualizer(figsize=(6, 4), debug_level="ERROR")
    fig = viz.create_from_dataset(base)
    assert fig is not None
    chan_lines = len(viz.ax.lines)
    # Expect at least +2 lines for 2 channel segments
    assert chan_lines >= base_lines + 2, "Channel segments should add lines to the plot"

