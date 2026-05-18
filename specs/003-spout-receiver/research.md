# Research: UX Refinements & Canvas Polish

## Overview
This research resolves implementation choices for Phase 2 UX refinements: canvas interaction, signal scaling, and OBS action hierarchy.

## Findings

### 1. ROI Selection & Interaction
- **Decision**: Hit-test vs. bounding box
- **Rationale**: Hit-test using `drawing_canvas._hit_test()` for edge/corner handles vs. interior area.
- **Alternatives**: Global mouse events (too complex for tkinter).

### 2. OBS Action Hierarchy
- **Decision**: Source → Filter parent-child relationship.
- **Rationale**: OBS source filters are logically nested within sources.
- **Alternatives**: Flat list (rejected: confusing hierarchy).

### 3. Canvas Scaling
- **Decision**: `DrawingCanvas` scaling mode with `INTER_LINEAR` for video feed, `INTER_NEAREST` for ROI masks.
- **Rationale**: Maintain aspect ratio and visual clarity.
- **Alternatives**: Crop-to-fill (rejected: loses content).

### 4. Boolean Action
- **Decision**: OBS "Toggle" action for visibility and filter state.
- **Rationale**: Standard OBS interaction.
