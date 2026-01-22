# Glass Manufacturing Skill

Convert hand-drawn WhatsApp glass sketches into professional manufacturing specifications.

## Overview

This skill processes hand-drawn glass panel sketches and generates:
- Interactive 3D visualization
- Manufacturing instructions
- CNC drilling programs
- Technical drawings
- Validation reports

## Quick Start

1. **Add your image** to the `inputs/` folder
2. **Run the command**:
   ```bash
   python commands/process-glass-sketch.py inputs/your_sketch.jpg
   ```
3. **Get outputs** from the `outputs/` folder

## Folder Structure

```
glass-manufacturing-skill/
|-- inputs/          # Place your glass sketch images here
|-- outputs/         # All generated files go here
|-- commands/        # Executable commands
|-- scripts/         # Python implementation
|-- references/      # Documentation and standards
|-- assets/          # Example images and resources
```

## Features

### Two-Agent Self-Evolving System
- **Agent 1 (Creator)**: Extracts specifications from images
- **Agent 2 (Judge)**: Validates and provides feedback
- Iterative refinement until accuracy achieved

### Three Python Precision Functions
1. `calculate_section_positions()` - Validates section dimensions
2. `calculate_hole_positions()` - Calculates exact coordinates
3. `calculate_geometric_feasibility()` - Checks manufacturing constraints

### Generated Outputs
1. `glass_3d_model.html` - Interactive 3D visualization
2. `manufacturing_instructions.md` - Human-readable guide
3. `cnc_program.gcode` - CNC drilling program
4. `technical_drawing.svg` - Professional drawing
5. `validation_report.json` - Complete audit trail

## Commands

### Process Glass Sketch
```bash
python commands/process-glass-sketch.py <image_path> [options]
```

Options:
- `--max-iterations N` - Maximum validation iterations (default: 3)
- `--tolerance FLOAT` - Dimensional tolerance in mm (default: 0.1)
- `--output-dir PATH` - Custom output directory
- `--skip-3d` - Skip 3D model generation
- `--skip-gcode` - Skip G-code generation
- `--verbose` - Enable detailed output

### Natural Language
```
"Process this glass sketch"
"Convert inputs/my_sketch.jpg to manufacturing specs"
"Generate CNC code for the glass panel"
```

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Test with sample
python commands/process-glass-sketch.py inputs/sample.jpg
```

## Documentation

- `references/nomenclature.md` - Standard terminology
- `references/tolerance_standards.md` - Industry tolerances
- `references/examples.md` - Usage examples

## License

MIT License - See LICENSE file for details.
