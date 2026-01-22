# Inputs Folder

Place your sketch images in the appropriate subfolder based on the type of analysis needed.

## Folder Structure

```
inputs/
├── Glass-Skills/           # Glass panel sketches → triggers Glass Manufacturing Skill
│   ├── Glass-Skill-1.jpeg
│   ├── Glass-Skill-2.jpeg
│   └── Glass-Skill-N.jpeg
│
└── Boundary-Skills/        # Plot boundary sketches → triggers Boundary Analysis Skill
    ├── Boundary-Skill-1.jpeg
    └── Boundary-Skill-N.jpeg
```

## Auto-Trigger Rules

The skill is automatically selected based on which folder contains the image:

| Input Folder | Skill Triggered | Output Folder |
|--------------|-----------------|---------------|
| `inputs/Glass-Skills/` | Glass Manufacturing | `outputs/Glass-Skill-N/` |
| `inputs/Boundary-Skills/` | Boundary Analysis | `outputs/Boundary-Skill-N/` |

## File Naming Convention

Name your files with a number to track different sketches:
- `Glass-Skill-1.jpeg`, `Glass-Skill-2.jpeg`, etc.
- `Boundary-Skill-1.jpeg`, `Boundary-Skill-2.jpeg`, etc.

The number in the filename determines the output folder number.

## Usage

### Run a specific image:
```bash
python run.py inputs/Glass-Skills/Glass-Skill-2.jpeg
python run.py inputs/Boundary-Skills/Boundary-Skill-1.jpeg
```

### List all available images:
```bash
python run.py --list
```

### Force a specific skill:
```bash
python run.py --skill glass inputs/some-image.jpeg
python run.py --skill boundary inputs/some-image.jpeg
```

## Supported Image Formats

- **JPEG (.jpeg, .jpg)** - Recommended for photos
- **PNG (.png)** - Recommended for digital drawings

## Image Requirements

- **Minimum Resolution**: 800 x 600 pixels
- **Recommended Resolution**: 1920 x 1080 pixels or higher
- **Quality**: Clear, well-lit images with visible dimensions

## Reference Outputs

Before analyzing new sketches, review the reference outputs in the `assets/` folder:
- `assets/Glass-Skill-1/` - Reference glass panel outputs
- `assets/Boundary-Skill-1/` - Reference boundary analysis outputs

These show the expected output format and quality standards.

## Best Practices

1. **Clear Images**: Ensure sketches are well-lit and clearly visible
2. **Readable Text**: All measurements should be legible
3. **Complete Sketches**: Include all dimensions and annotations
4. **Consistent Units**:
   - Glass panels: millimeters (mm)
   - Plot boundaries: feet (FT) or meters (m)
5. **Photograph straight-on**: Avoid distortion from angles
6. **Good lighting**: Avoid shadows on text and dimensions

## Notes

- Original images are never modified
- Multiple images can be processed sequentially
- Each processing run creates outputs in skill-numbered folders
