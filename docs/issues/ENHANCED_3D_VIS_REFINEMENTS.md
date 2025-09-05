# Issue Draft: Refine Enhanced 3D Visualization Overlays (ricochet, channels, animation)

Context
- Recent work added multi-part channel rendering with exit markers, ricochet outcomes (ricochet | shattering | embedding), per-mm degradation, dataset export/import, and overlay toggles in both CLI and GUI.
- Commit: 19a6d77 (feat: multi-part channels, ricochet outcomes, overlay toggles, tests, docs)

Goal
Polish the visual presentation and UX of the Enhanced 3D overlays and ensure consistent behavior during animation and dataset-driven viewing.

Tasks
1) Ricochet overlay polish
- [ ] Distinct visuals per outcome:
      - ricochet: yellow star + outbound line
      - shattering: purple star (no outbound line)
      - embedding: gray diamond (no outbound line)
- [ ] Size scale by energy_retained or exit_velocity_ms (from ricochet_details)
- [ ] Add legend entries and short textual annotation (e.g., deflection angle)
- [ ] Ensure z-order places markers above channels but below labels; verify visibility on dark/light backgrounds

2) Channel segments styling
- [ ] Standardize linewidths and alpha across segments
- [ ] Use dashed linestyle for partial segments (where residual penetration was insufficient)
- [ ] Consider per-part color coding with legend (e.g., hull, turret, tracks)
- [ ] Standardize exit marker (size, edge color) and add legend entry

3) Animation overlay alignment
- [ ] Validate overlays do not duplicate per frame; re-draw minimal elements only
- [ ] Option: animate ricochet line over short duration for clarity
- [ ] Confirm spall cone and channel overlays remain spatially consistent during camera rotation/animation

4) Viewer toggles UX
- [ ] Add keyboard shortcuts in viewer: C to toggle channels, R to toggle ricochet
- [ ] Persist user preference in GUI settings (already done) and offer quick toolbar buttons in GUI
- [ ] For CLI viewer, echo current toggle state on load

5) Dataset schema & docs
- [ ] Clarify units (m vs mm) for all impact_analysis numeric fields
- [ ] Document ricochet_details fields (probability, deflection_angle_deg, exit_velocity_ms, energy_retained, critical_angle_deg, predicted_outcome)
- [ ] Ensure README JSON example matches actual schema keys

6) Tests (add/extend)
- [ ] Spall cone presence when penetration exceeds threshold (kinetic rounds)
- [ ] Exit marker rendered when overpenetration = true
- [ ] GUI toggles hide/show overlays (augment current tests with toolbar/shortcut paths)
- [ ] Partial segments use dashed linestyle (inspect line.get_linestyle())

Acceptance Criteria
- Overlays visually distinct and consistent across outcomes and parts
- No overlay duplication or flicker during animation
- User can toggle overlays via GUI toolbar and keyboard shortcuts; state persists
- Docs updated with accurate schema and examples; CLI flags documented
- Tests cover the above behaviors and pass in CI

References
- Commit: 19a6d77
- Files: src/visualization/enhanced_3d_visualizer.py, interactive_viewer.py, gui_main.py, docs/enhanced_3d/README.md
- Tests: tests/enhanced_3d/test_ricochet_and_channels.py, tests/enhanced_3d/test_cross_section_and_gui_toggles.py

Notes
- Coordinate with styling palette for readability on both light/dark backgrounds.
- Defer any heavy refactors until after initial polish is validated.

