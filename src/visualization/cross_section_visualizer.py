"""
Cross-section visualizer for target impact, penetration channel, and spall/behind-armor effects.

Renders a 2D cross-section through the armor stack at the impact location, showing:
- Armor layers (for composite armor, if available)
- Penetration channel depth
- Spall/fragment cone if penetration occurs (kinetic rounds)
"""
import math
from typing import Dict, Any, Optional
import matplotlib.pyplot as plt
from matplotlib import patches as mpatches

class CrossSectionVisualizer:
    def __init__(self, figsize=(8, 5), mode: str = 'projected'):
        """
        mode: 'projected' or 'true_path'
        - 'projected': visually normalized slope within armor band
        - 'true_path': annotate exact path lengths through each layer (drawing still normalized)
        """
        self.figsize = figsize
        self.mode = mode if mode in ('projected', 'true_path') else 'projected'
        self.fig = None
        self.ax = None

    def _armor_layers(self, armor_meta: Dict[str, Any]):
        """Build a list of layers [(name, thickness_m, color)]."""
        layers = []
        # Default: single RHA layer
        thickness_mm = float(armor_meta.get('thickness_mm', 0.0))
        armor_type = armor_meta.get('armor_type', 'RHA')
        if any(k in armor_meta for k in ['steel_layers_mm', 'ceramic_layers_mm', 'other_layers_mm']):
            # Composite
            if 'steel_layers_mm' in armor_meta and armor_meta['steel_layers_mm'] > 0:
                layers.append(('Steel', armor_meta['steel_layers_mm'] / 1000.0, '#888888'))
            if 'ceramic_layers_mm' in armor_meta and armor_meta['ceramic_layers_mm'] > 0:
                layers.append(('Ceramic', armor_meta['ceramic_layers_mm'] / 1000.0, '#b5651d'))
            if 'other_layers_mm' in armor_meta and armor_meta['other_layers_mm'] > 0:
                layers.append(('Other', armor_meta['other_layers_mm'] / 1000.0, '#6e6e6e'))
        else:
            # Homogeneous plate
            layers.append((armor_type, thickness_mm / 1000.0, '#777777'))
        return layers

    def render_cross_section(self, dataset_meta: Dict[str, Any]) -> plt.Figure:
        """Render cross-section figure using dataset meta fields.

        dataset_meta should contain keys 'ammunition', 'armor', and 'impact_analysis'.
        """
        ammo = dataset_meta.get('ammunition', {})
        armor = dataset_meta.get('armor', {})
        impact = dataset_meta.get('impact_analysis', {})
        
        layers = self._armor_layers(armor)
        total_thickness_m = sum(t for _, t, _ in layers)

        # Build layer interfaces (cumulative depths)
        interfaces = [0.0]
        acc = 0.0
        for _, t, _ in layers:
            acc += t
            interfaces.append(acc)

        # Setup figure
        self.fig, self.ax = plt.subplots(figsize=self.figsize)
        self.ax.set_title('Target Cross-Section at Impact')
        self.ax.set_xlabel('Depth (m)')
        self.ax.set_ylabel('Height (arbitrary units)')
        self.ax.set_ylim(0, 1)
        self.ax.set_xlim(0, max(total_thickness_m * 1.3, 0.2))

        # Draw armor layers as rectangles along x (depth)
        x_cursor = 0.0
        for name, thickness_m, color in layers:
            rect = plt.Rectangle((x_cursor, 0.2), thickness_m, 0.6, color=color, alpha=0.6, ec='k')
            self.ax.add_patch(rect)
            self.ax.text(x_cursor + thickness_m/2, 0.52, f"{name}\n{thickness_m*1000:.0f} mm",
                         ha='center', va='center', fontsize=9)
            x_cursor += thickness_m

        # Draw penetration channel with obliquity angle
        penetration_mm = float(impact.get('penetration_mm', 0.0) or 0.0)
        penetrates = bool(impact.get('penetrates', False))
        impact_angle_from_vertical_deg = float(impact.get('impact_angle_from_vertical_deg', 0.0) or 0.0)
        impact_angle_from_vertical_deg = max(0.0, min(85.0, impact_angle_from_vertical_deg))
        theta_rad = math.radians(impact_angle_from_vertical_deg)
        channel_depth_m = min(penetration_mm / 1000.0, total_thickness_m)
        y0 = 0.5
        # Visual slope factor maps depth -> vertical offset within armor band (~0.6 height)
        if total_thickness_m > 0:
            slope_visual = math.tan(theta_rad) * (channel_depth_m / total_thickness_m) * 0.4
        else:
            slope_visual = 0.0
        y1 = y0 + slope_visual
        y1 = max(0.25, min(0.75, y1))
        if channel_depth_m > 0:
            # Draw polyline across layer boundaries to show entry/exits
            pts_x = [0.0]
            pts_y = [y0]
            for i in range(1, len(interfaces)):
                x_i = interfaces[i]
                if x_i >= channel_depth_m:
                    x_i = channel_depth_m
                    # final point
                    pass
                # normalized slope mapping: scale to band
                frac = (x_i / max(total_thickness_m, 1e-6))
                if self.mode == 'true_path':
                    slope_scale = 0.4 * math.tan(theta_rad)
                else:
                    slope_scale = 0.4 * math.tan(theta_rad)  # same visual slope; difference is annotation
                y_i = y0 + slope_scale * frac
                y_i = max(0.25, min(0.75, y_i))
                pts_x.append(x_i)
                pts_y.append(y_i)
                if x_i >= channel_depth_m:
                    break
            # ensure final point at exact depth if not added
            if pts_x[-1] < channel_depth_m:
                frac = (channel_depth_m / max(total_thickness_m, 1e-6))
                y_end = y0 + (0.4 * math.tan(theta_rad)) * frac
                y_end = max(0.25, min(0.75, y_end))
                pts_x.append(channel_depth_m)
                pts_y.append(y_end)
            self.ax.plot(pts_x, pts_y, color='red', linewidth=4, label='Penetration Channel')

            # Mark intersection points
            for x_i, y_i in zip(pts_x, pts_y):
                self.ax.plot([x_i], [y_i], marker='o', color='red', markersize=3)

            # Angle indicator arc at entry (between vertical and channel)
            try:
                arc_r = max(0.04, min(0.09, 0.08))
                arc = mpatches.Arc((0, y0), 2*arc_r, 2*arc_r, angle=0,
                                    theta1=90 - impact_angle_from_vertical_deg, theta2=90, color='red', linewidth=1.5)
                self.ax.add_patch(arc)
                beta = 90.0 - impact_angle_from_vertical_deg
                self.ax.text(0.02, y0 + arc_r + 0.02, f"α={impact_angle_from_vertical_deg:.1f}° (from vertical)\nβ={beta:.1f}° (from horizontal)", color='red', fontsize=8)
            except Exception:
                pass

            # Annotate per-layer true path lengths if in true_path mode
            if self.mode == 'true_path':
                remaining = channel_depth_m
                x_prev = 0.0
                for i in range(len(layers)):
                    layer_name, t_m, _ = layers[i]
                    x_next = min(interfaces[i+1], channel_depth_m)
                    dx = max(0.0, x_next - x_prev)
                    if dx <= 1e-9:
                        x_prev = x_next
                        continue
                    L = dx / max(math.cos(theta_rad), 1e-6)
                    x_label = (x_prev + x_next)/2.0
                    y_label = y0 + (0.4 * math.tan(theta_rad)) * ((x_label / max(total_thickness_m, 1e-6)))
                    y_label = max(0.25, min(0.75, y_label))
                    self.ax.text(x_label, y_label + 0.06, f"ΔL={L*1000:.0f} mm", fontsize=8, ha='center', color='darkred')
                    x_prev = x_next
                    remaining -= dx
                    if remaining <= 1e-9:
                        break

        # Spall/fragmentation cone on exit or internal behind-armor effects
        if penetrates or (penetration_mm > 0.0 and penetration_mm/1000.0 > total_thickness_m * 0.7):
            cone_angle_deg = 30.0
            cone_len_m = max(0.05, min(0.5, total_thickness_m * 0.5))
            base_half_height = math.tan(math.radians(cone_angle_deg)) * cone_len_m
            start_x = min(channel_depth_m, total_thickness_m)
            # Orient base center along channel direction slightly
            y_base_center = y1 + (cone_len_m / max(total_thickness_m, 1e-6)) * (0.4 * math.tan(theta_rad))
            # Draw triangular spall region aligned to y_base_center
            self.ax.plot([start_x, start_x + cone_len_m], [y1, y_base_center + base_half_height], color='orange', linewidth=2)
            self.ax.plot([start_x, start_x + cone_len_m], [y1, y_base_center - base_half_height], color='orange', linewidth=2)
            self.ax.plot([start_x + cone_len_m, start_x + cone_len_m], [y_base_center - base_half_height, y_base_center + base_half_height],
                         color='orange', linewidth=2, alpha=0.6)
            self.ax.text(start_x + cone_len_m, y_base_center + base_half_height + 0.03, 'Spall/Fragments', fontsize=9, ha='right')

        # Optional damage overlays if provided
        damage = dataset_meta.get('damage', {}) or {}
        # Delamination zones
        zones = damage.get('delamination_zones', [])
        for z in zones:
            try:
                start_m = float(z.get('start_mm', 0.0)) / 1000.0
                end_m = float(z.get('end_mm', 0.0)) / 1000.0
                if end_m > start_m:
                    rect = plt.Rectangle((start_m, 0.25), end_m - start_m, 0.5, color='#FFD580', alpha=0.4, ec='none')
                    self.ax.add_patch(rect)
            except Exception:
                pass
        # Residual thickness marker
        if 'residual_thickness_mm' in damage:
            try:
                res_m = float(damage['residual_thickness_mm']) / 1000.0
                if res_m > 0:
                    self.ax.axvline(x=res_m, color='red', linestyle='--', linewidth=2, label='Residual thickness')
            except Exception:
                pass

        # Info box
        info = []
        info.append(f"Ammo: {ammo.get('name','N/A')}")
        info.append(f"Armor: {armor.get('name','N/A')} ({int(armor.get('thickness_mm',0))} mm)")
        if impact:
            info.append(f"Impact v: {impact.get('impact_velocity_ms',0):.0f} m/s")
            info.append(f"Angle: {impact.get('impact_angle_from_vertical_deg',0):.1f}° from vertical / {90.0 - float(impact.get('impact_angle_from_vertical_deg',0.0) or 0.0):.1f}° from horizontal")
            info.append('Result: ' + ('PENETRATION' if penetrates else 'NO PENETRATION'))
        self.ax.text(0.01, 0.98, "\n".join(info), transform=self.ax.transAxes, va='top', fontsize=9,
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        self.ax.legend(loc='lower right')
        self.fig.tight_layout()
        return self.fig

    def save_cross_section(self, filename: str, dpi: int = 200):
        if self.fig is not None:
            self.fig.savefig(filename, dpi=dpi, bbox_inches='tight')

