#!/usr/bin/env python3
"""
Interactive Result Viewer

Load a saved interactive dataset (JSON) and render an interactive 3D visualization
without recomputing physics. Optionally animate the projectile path.

Usage:
  python interactive_viewer.py path/to/result.json [--animate]
"""
import sys
import os
import json
import argparse

# Add src to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(PROJECT_ROOT, 'src'))

from src.visualization.enhanced_3d_visualizer import Enhanced3DVisualizer


def main():
    parser = argparse.ArgumentParser(description='Interactive 3D result viewer')
    parser.add_argument('dataset', help='Path to interactive dataset JSON file')
    parser.add_argument('--animate', action='store_true', help='Play simple projectile animation')
    parser.add_argument('--no-channels', dest='show_channels', action='store_false', help='Hide penetration channel segments')
    parser.add_argument('--no-ricochet', dest='show_ricochet', action='store_false', help='Hide ricochet overlays')
    parser.set_defaults(show_channels=True, show_ricochet=True)
    args = parser.parse_args()

    if not os.path.exists(args.dataset):
        print(f"Error: File not found: {args.dataset}")
        sys.exit(1)

    with open(args.dataset, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    viz = Enhanced3DVisualizer(figsize=(16, 12), debug_level="ERROR")
    # Apply overlay toggles
    viz.show_channel_segments = bool(args.show_channels)
    viz.show_ricochet_overlay = bool(args.show_ricochet)
    fig = viz.create_from_dataset(dataset)

    # If a cross-section image is referenced, show it alongside in a separate window
    assets = dataset.get('assets', {}) or {}
    cross_path = assets.get('cross_section_png')
    if cross_path and os.path.exists(cross_path):
        try:
            import matplotlib.pyplot as plt
            import matplotlib.image as mpimg
            img = mpimg.imread(cross_path)
            plt.figure(figsize=(8, 5))
            plt.imshow(img)
            plt.title('Target Cross-Section')
            plt.axis('off')
        except Exception as e:
            print(f"Warning: Could not display cross-section image: {e}")

    if args.animate:
        try:
            viz.enable_animation_mode(duration=5.0)
        except Exception as e:
            print(f"Warning: Could not enable animation: {e}")

    # Show interactively
    viz.show_interactive()


if __name__ == '__main__':
    main()

