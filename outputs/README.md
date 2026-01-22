# Outputs Folder

All generated manufacturing files are saved in this folder.

## Generated Files

### 1. glass_3d_model.html
Interactive 3D visualization of the glass panel.
- Open in any web browser
- Rotate, zoom, and inspect the model
- Shows holes, edges, and dimensions

### 2. manufacturing_instructions.md
Human-readable manufacturing guide.
- Step-by-step cutting instructions
- Hole drilling sequence
- Edge finishing requirements
- Safety notes

### 3. cnc_program.gcode
CNC machine program for automated drilling.
- Standard G-code format
- Compatible with most CNC glass drills
- Includes tool change commands
- Optimized drilling sequence

### 4. technical_drawing.svg
Professional technical drawing.
- Scalable vector format
- Print-ready at any size
- Includes all dimensions
- Standard engineering notation

### 5. validation_report.json
Complete audit trail and validation data.
- Extraction accuracy metrics
- Validation results
- Error corrections made
- Processing metadata

## File Naming

Files are timestamped when multiple runs occur:
```
outputs/
├── glass_3d_model.html
├── glass_3d_model_20240115_143022.html
├── manufacturing_instructions.md
└── ...
```

## Usage

After processing, check this folder for your files:
```bash
ls outputs/
```

Open the 3D model:
```bash
# Windows
start outputs/glass_3d_model.html

# macOS
open outputs/glass_3d_model.html

# Linux
xdg-open outputs/glass_3d_model.html
```

## Notes

- Files are overwritten on each run unless timestamped
- Keep important outputs in a separate folder
- JSON reports are machine-readable for integration
