# Glass Manufacturing Skill - Examples

Practical examples of using the glass manufacturing skill.

## Example 1: Simple Rectangular Panel

### Input
Hand-drawn sketch showing:
- Width: 1000mm
- Height: 600mm
- Thickness: 10mm
- No holes

### Command
```bash
python commands/process-glass-sketch.py inputs/simple_panel.jpg
```

### Expected Output
```
Processing: inputs/simple_panel.jpg
Extraction complete
Section validation: PASS
Hole validation: PASS
Feasibility: PASS
Validation: APPROVED

Generated files in outputs/:
  - glass_3d_model.html
  - manufacturing_instructions.md
  - cnc_program.gcode
  - technical_drawing.svg
  - validation_report.json
```

## Example 2: Panel with Holes

### Input
Sketch showing:
- Width: 1200mm
- Height: 800mm
- Thickness: 12mm
- 4 corner holes: D=20mm, 50mm from edges

### Extracted Specifications
```json
{
  "dimensions": {
    "width": 1200,
    "height": 800,
    "thickness": 12
  },
  "holes": [
    {"x": 50, "y": 50, "diameter": 20},
    {"x": 1150, "y": 50, "diameter": 20},
    {"x": 50, "y": 750, "diameter": 20},
    {"x": 1150, "y": 750, "diameter": 20}
  ],
  "edge_type": "flat_polished",
  "glass_type": "clear_tempered"
}
```

### Command with Options
```bash
python commands/process-glass-sketch.py inputs/panel_with_holes.jpg \
    --max-iterations 5 \
    --tolerance 0.05
```

## Example 3: Multi-Section Panel

### Input
Sketch showing:
- Total width: 1500mm
- Height: 900mm
- 3 vertical sections: 500mm each
- Section divider lines marked

### Extracted Specifications
```json
{
  "dimensions": {
    "width": 1500,
    "height": 900,
    "thickness": 10
  },
  "sections": [
    {"name": "Left", "width": 500, "x_offset": 0},
    {"name": "Center", "width": 500, "x_offset": 500},
    {"name": "Right", "width": 500, "x_offset": 1000}
  ]
}
```

## Example 4: Natural Language Processing

### User Request
```
Process the glass sketch in inputs/bathroom_mirror.jpg and 
generate manufacturing files for a 10mm tempered panel
```

### Skill Response
1. Reads image from inputs/bathroom_mirror.jpg
2. Extracts dimensions from annotations
3. Validates against manufacturing constraints
4. Generates all output files

## Example 5: Validation Failure and Correction

### Initial Extraction (with error)
```json
{
  "dimensions": {"width": 1000, "height": 500, "thickness": 10},
  "holes": [
    {"x": 10, "y": 10, "diameter": 20}
  ]
}
```

### Validation Result
```
Section validation: PASS
Hole validation: FAIL - Too close to edge
Feasibility: PASS
```

### Feedback from Judge
```json
{
  "hole_errors": [{
    "index": 0,
    "issues": ["Too close to left edge", "Too close to bottom edge"],
    "suggested_x": 35,
    "suggested_y": 35
  }]
}
```

### Corrected Extraction (after iteration)
```json
{
  "dimensions": {"width": 1000, "height": 500, "thickness": 10},
  "holes": [
    {"x": 35, "y": 35, "diameter": 20}
  ]
}
```

## Example 6: Custom Output Directory

### Command
```bash
python commands/process-glass-sketch.py inputs/sketch.jpg \
    --output-dir ./project_ABC/glass_specs
```

### Result
Files saved to `./project_ABC/glass_specs/` instead of default `outputs/`.

## Example 7: Skip Optional Outputs

### Command (skip 3D model)
```bash
python commands/process-glass-sketch.py inputs/sketch.jpg --skip-3d
```

### Command (skip G-code)
```bash
python commands/process-glass-sketch.py inputs/sketch.jpg --skip-gcode
```

### Command (minimal outputs)
```bash
python commands/process-glass-sketch.py inputs/sketch.jpg \
    --skip-3d --skip-gcode
```

## Common Sketch Patterns

### Pattern 1: Dimension Labels
```
+------ W=1000 ------+
|                    |
H=500               |
|                    |
+--------------------+
        T=10
```

### Pattern 2: Hole Notation
```
    4x D20 THRU
    TYP 50 FROM EDGE
    
    O           O
    
    O           O
```

### Pattern 3: Section Marks
```
|<-- 400 -->|<-- 400 -->|<-- 400 -->|
|     A     |     B     |     C     |
```

## Error Messages and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "Image not found" | Wrong path | Check file exists in inputs/ |
| "Unsupported format" | Wrong file type | Use JPG, PNG, or WEBP |
| "Hole too close to edge" | Insufficient margin | Move hole 25mm+ from edge |
| "Dimensions not detected" | Unclear labels | Improve image quality |
