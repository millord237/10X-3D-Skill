# Commands Reference

Available commands for the Glass Manufacturing Skill.

## Primary Command

### process-glass-sketch

Process a glass sketch image and generate manufacturing files.

**Usage:**
```bash
python commands/process-glass-sketch.py <image_path> [options]
```

**Arguments:**
- `image_path` - Path to the glass sketch image (required)

**Options:**
- `--max-iterations N` - Maximum validation iterations (default: 3)
- `--tolerance FLOAT` - Dimensional tolerance in mm (default: 0.1)
- `--output-dir PATH` - Custom output directory (default: outputs/)
- `--skip-3d` - Skip 3D model generation
- `--skip-gcode` - Skip CNC G-code generation
- `--verbose` - Enable detailed output
- `--help` - Show help message

**Examples:**
```bash
# Basic usage
python commands/process-glass-sketch.py inputs/sketch.jpg

# With options
python commands/process-glass-sketch.py inputs/sketch.jpg --max-iterations 5 --tolerance 0.05

# Custom output directory
python commands/process-glass-sketch.py inputs/sketch.jpg --output-dir ./my_outputs

# Skip 3D model
python commands/process-glass-sketch.py inputs/sketch.jpg --skip-3d
```

## Validation Command

### validate-extraction

Validate an existing extraction without reprocessing.

**Usage:**
```bash
python commands/validate-extraction.py <json_path>
```

**Arguments:**
- `json_path` - Path to extraction JSON file

**Examples:**
```bash
python commands/validate-extraction.py outputs/validation_report.json
```

## Natural Language Commands

You can also use natural language with Claude:

```
"Process this glass sketch"
"Convert inputs/my_sketch.jpg to manufacturing specs"
"Generate CNC code for the glass panel in inputs/"
"Validate the extraction for my_sketch.jpg"
"Create manufacturing instructions from this drawing"
```

## Output Files

Each successful run generates:
1. `glass_3d_model.html` - Interactive 3D visualization
2. `manufacturing_instructions.md` - Worker guide
3. `cnc_program.gcode` - CNC drilling program
4. `technical_drawing.svg` - Professional drawing
5. `validation_report.json` - Audit trail

## Error Handling

- Invalid image path: Check file exists in inputs/
- Processing errors: Check image quality and clarity
- Validation failures: Review validation_report.json for details
