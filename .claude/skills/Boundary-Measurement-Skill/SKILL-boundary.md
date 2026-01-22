---
name: plot-boundary-analysis
description: Architect-grade method for analyzing hand-drawn plot boundary sketches using 3-phase two-agent validation with self-evolving agentic workflow.
version: 4.2.0
license: MIT
parent: SKILL.md
inputFolder: inputs/Boundary-Skills
outputFolder: outputs/Boundary-Skill-{N}
referenceFolder: assets/Boundary-Skill-1
units: [FT, m]
---

# Plot Boundary Analysis Skill

Architect-grade methodology for analyzing hand-drawn plot boundary sketches using a **3-phase two-agent architecture** with confidence scoring at each phase.

---

## FRESH CHAT PROTOCOL

```
!!! BEFORE PROCESSING ANY BOUNDARY IMAGE !!!
1. Read package.json
2. Run: python run.py --list
3. Check if image is [DONE] or [NEW]
4. Review assets/Boundary-Skill-1/ for reference format
5. ONLY process [NEW] images unless --force requested
```

---

## AUTO-TRIGGER

This skill is automatically triggered when:
- Image path contains `Boundary-Skills/`
- User runs: `python run.py inputs/Boundary-Skills/<image>.jpeg`
- User runs: `python run.py --next boundary`

---

## 3-PHASE WORKFLOW FOR BOUNDARIES

```
PHASE 1: IMAGE ANALYSIS (85% min confidence)
├── Creator: Identify shape, orientation, corners, reference point
├── Judge: Validate segment count, orientation correctness
└── Output: Analysis data structure

PHASE 2: METRICS EXTRACTION (90% min confidence)
├── Creator: Read edge measurements, note features (gates, steps)
├── Judge: Validate polygon closure, coordinate calculations
└── Output: Complete boundary extraction JSON

PHASE 3: OUTPUT GENERATION (95% min confidence)
├── Creator: Generate HTML 3D, SVG, JSON, report
├── Judge: Validate all files exist and are valid
└── Output: 4 output files
```

---

## OUTPUT FILES

```
outputs/Boundary-Skill-[N]/
├── boundary_data.json           # Complete boundary data
├── boundary_3d_viewer.html      # Interactive 3D viewer
├── boundary_technical.svg       # Survey drawing
└── boundary_report.md           # Analysis report
```

### Reference Output
Always review `assets/Boundary-Skill-1/` before generating to maintain consistency.

---

## IDENTIFICATION

### How to Recognize Plot Boundary Sketches

**Look for these indicators:**

| Indicator | What It Means |
|-----------|---------------|
| Boundary lines forming closed shape | This is a plot/land boundary |
| FT (feet) or M (meter) units | Surveying measurement units |
| Directional labels (N/S/E/W) | Compass orientation markers |
| GATE, DOOR labels | Access points in boundary |
| GALI/RASTA with arrows | Lane/path outside property |
| Steps, indents in boundary | Terrain or property line features |

---

## PHASE 1: SECTION-BY-SECTION EXTRACTION

### Step-by-Step Process for Boundaries

Follow the 12-step process from SKILL.md, with these boundary-specific details:

---

### STEP 1: CENTER ORIENTATION

**What to look for:**
- Overall shape of the plot
- Direction labels (which side is North, South, East, West)
- General complexity (simple rectangle vs. irregular polygon)

**Record format:**
```
Shape: [rectangle / L-shape / U-shape / irregular]
Orientation: North=[position], East=[position], South=[position], West=[position]
Complexity: [N] approximate corners visible
```

**DO NOT** read any measurements yet.

---

### STEP 2: REFERENCE POINT IDENTIFICATION

**Best reference points for boundaries (in order):**

1. **GATE/DOOR** - Most distinctive, usually labeled
2. **Compass-labeled corner** - "North corner", etc.
3. **Unique feature** - Step, indent, or annotation

**Record format:**
```
Reference: [feature type] located at [position in image]
Why chosen: [clear label / distinctive feature / only option]
```

---

### STEP 3: CREATE MEASUREMENT PLAN

**For boundaries, ALWAYS trace CLOCKWISE starting from reference:**

```
Starting point: [reference feature]
Direction: CLOCKWISE
Expected segments: [count based on visual inspection]
Special features to watch: [gates, steps, indents]
```

---

### STEP 4: EXAMINE TOP EDGE (EAST SIDE)

**Focus ONLY on the topmost horizontal boundary.**

Questions to answer:
- What is the measurement label?
- Is it one continuous segment or multiple?
- Any features (openings, annotations)?

**Record format:**
```
TOP EDGE (East):
  Segment 1: [value] [unit], direction=[left/right]
  Features: [none / opening at position / annotation]
```

---

### STEP 5: EXAMINE RIGHT EDGE (SOUTH SIDE)

**Focus ONLY on the rightmost vertical boundary.**

This edge often has MULTIPLE segments:
- Upper portion before any step
- Opening/gate (if present)
- Lower portion after step

**Record each segment separately:**
```
RIGHT EDGE (South):
  Segment 1: [value] [unit], direction=[up/down], type=[solid/opening]
  Segment 2: [value] [unit], direction=[up/down], type=[solid/opening]
  ...
```

**CRITICAL**: Gates are often on this side. Note:
- Gate orientation (vertical opening = height, horizontal = width)
- Arrows indicating access direction (GALI/RASTA)

---

### STEP 6: EXAMINE BOTTOM EDGE (WEST SIDE)

**Focus ONLY on the bottommost horizontal boundary.**

This edge often has steps/indents:
- May jog up/down before continuing
- Note each direction change as separate segment

**Record format:**
```
BOTTOM EDGE (West):
  Segment 1: [value] [unit], direction=[left/right]
  Segment 2: [value] [unit], direction=[up/down] (step)
  Segment 3: [value] [unit], direction=[left/right]
  ...
```

---

### STEP 7: EXAMINE LEFT EDGE (NORTH SIDE)

**Focus ONLY on the leftmost vertical boundary.**

This edge often has indents:
- Boundary may jog left (outward) then continue
- Note the indent dimensions

**Record format:**
```
LEFT EDGE (North):
  Segment 1: [value] [unit], direction=[up/down]
  Segment 2: [value] [unit], direction=[left/right] (indent)
  Segment 3: [value] [unit], direction=[up/down]
  ...
```

---

### STEP 8: EXAMINE SPECIAL FEATURES

**Look specifically for:**

| Feature | How to Identify | What to Record |
|---------|-----------------|----------------|
| GATE | "GATE X FT" label | Position, dimension, orientation |
| INDENT | Boundary jogs inward | Depth, position along edge |
| STEP | Boundary jogs outward | Height, position along edge |
| OPENING | Dashed line or gap | Width, position |

**Record format:**
```
SPECIAL FEATURES:
  Feature 1: [type] at [position], dimension=[value], orientation=[H/V]
  Feature 2: ...
```

---

### STEP 9: EXAMINE ANNOTATIONS

**Look for:**
- Arrows pointing outside (access direction)
- Labels like "GALI/RASTA" (lane/path)
- Compass direction markers
- Property notes

**Record format:**
```
ANNOTATIONS:
  [Position]: [annotation text] - meaning: [interpretation]
```

---

### STEP 10: CROSS-REFERENCE CHECK

**Verify consistency:**

```
CHECK 1: Do adjacent segments connect?
  - Top edge end connects to right edge start? [yes/no]
  - Right edge end connects to bottom edge start? [yes/no]
  - Bottom edge end connects to left edge start? [yes/no]
  - Left edge end connects to top edge start? [yes/no]

CHECK 2: Do parallel sides make sense?
  - Sum of top segments ≈ sum of bottom segments? [yes/no]
  - Sum of left segments ≈ sum of right segments? [yes/no]

CHECK 3: Any unclear measurements?
  - List any values that need user verification
```

---

### STEP 11: CALCULATE DERIVED VALUES

**Using extracted measurements:**

```python
# Perimeter calculation
perimeter = sum(all_segment_lengths)

# Coordinate calculation (starting from origin)
vertices = []
current = (0, 0)
for segment in segments:
    current = apply_direction(current, segment.direction, segment.length)
    vertices.append(current)

# Closure check
closure_error = distance(vertices[-1], vertices[0])
```

**Record:**
```
CALCULATIONS:
  Perimeter: [value] [unit]
  Vertices: [count]
  Closure error: [value] (should be < 0.1)
```

---

### STEP 12: BUILD FINAL DATA STRUCTURE

**Compile into structured format:**

```json
{
  "sketch_type": "plot_boundary",
  "unit": "[FT/M]",
  "reference_point": "[description]",
  "traversal_direction": "clockwise",
  "edges": [
    {
      "name": "[edge name]",
      "segments": [
        {
          "length": "[value]",
          "direction": "[up/down/left/right]",
          "type": "[solid/gate/step]"
        }
      ]
    }
  ],
  "features": [...],
  "calculations": {
    "perimeter": "[value]",
    "area": "[value]",
    "closure_error": "[value]"
  },
  "confidence": "[0-100]",
  "needs_clarification": [...]
}
```

---

## COORDINATE SYSTEM

### Standard Orientation

```
Origin: Top-left corner of plot = (0, 0)
X-axis: Positive to the RIGHT
Y-axis: Positive going DOWN

      (0,0) ────────────────► +X (East/Right)
        │
        │    PLOT AREA
        │
        ▼
       +Y (South/Down)
```

### Direction to Coordinate Change

| Direction | Coordinate Change |
|-----------|-------------------|
| RIGHT | x += length, y unchanged |
| LEFT | x -= length, y unchanged |
| DOWN | x unchanged, y += length |
| UP | x unchanged, y -= length |

### Handling Negative Coordinates

**IMPORTANT**: If boundary extends LEFT of origin, X becomes NEGATIVE.

```
Example: Indent on left side
- Starting at (0, Y)
- Move LEFT by indent_depth
- New position: (-indent_depth, Y)

This is CORRECT. X can be negative.
```

---

## GATE RECOGNITION

### Identifying Gates

**Visual clues:**
- "GATE X [unit]" label in image
- Arrows pointing outward (to street/path)
- Dashed or different line style
- Labels like "GALI/RASTA" (lane/path)

### Gate Orientation

**CRITICAL: Check image carefully!**

| Orientation | What It Means | Coordinate Change |
|-------------|---------------|-------------------|
| VERTICAL gate | Opening height | Y changes, X same |
| HORIZONTAL gate | Opening width | X changes, Y same |

**DO NOT ASSUME** - look at how the measurement is positioned in the image.

### Gate vs. Wall

```
Common confusion:
- Gate = the OPENING (dashed or labeled)
- Wall = the SOLID boundary near gate

Look at image to determine which segment is the opening.
```

---

## INDENT/STEP RECOGNITION

### Indent (Boundary Goes Inward)

```
Pattern:
  │
  │  ← boundary going down
  └──┐
     │  ← indent (goes left/inward)
     │
     │  ← continues down
```

Record as two segments:
1. Horizontal segment (the indent depth)
2. Vertical segment (continues down)

### Step (Boundary Goes Outward)

```
Pattern:
  │
  │  ← boundary going down
  ├──┘
  │     ← step (goes right/outward)
  │
  │  ← continues down
```

Record as two segments:
1. Horizontal segment (the step width)
2. Vertical segment (step height, then continues)

---

## VALIDATION

### Polygon Closure Check

```python
from boundary_utils import validate_closure

# After calculating all vertices
closure = validate_closure(vertices, tolerance=0.1)

if not closure['is_closed']:
    # Re-examine edges where error might be
    print(f"Gap: {closure['total_error']}")
```

### Shapely Validation

```python
from shapely.geometry import Polygon

polygon = Polygon(vertices)

checks = {
    'is_valid': polygon.is_valid,
    'is_simple': polygon.is_simple,
    'area': polygon.area,
    'perimeter': polygon.length
}
```

### Interior Angle Validation

**At each vertex, check the interior angle:**

| Angle | Meaning | Expected |
|-------|---------|----------|
| 90° | Right-angle corner | Normal boundary corner |
| 270° | Reflex angle | Step or indent |
| Other | Irregular | May indicate error |

```python
from boundary_utils import get_all_interior_angles

angles = get_all_interior_angles(vertices)
for a in angles:
    if a['angle_deg'] not in [90, 270]:
        print(f"WARNING: Unusual angle at vertex {a['vertex_index']}")
```

---

## PHASE 2: OUTPUT GENERATION

### After Phase 1 Complete

**Only proceed when:**
- All measurements extracted and verified
- Polygon closes within tolerance
- Judge has approved all readings
- Confidence >= 95%

---

### ⚠️ MANDATORY REFERENCE CHECK (STEP 0 - BEFORE ANY OUTPUT)

```
!!! CRITICAL: READ REFERENCE FILES BEFORE GENERATING ANY OUTPUT !!!
!!! ALL OUTPUTS MUST MATCH REFERENCE FORMAT AND STYLE !!!
!!! NEVER GENERATE WITHOUT REVIEWING REFERENCE FIRST !!!
```

**Before generating ANY boundary output files:**

1. **Read the reference HTML 3D viewer**
   ```bash
   Read assets/Boundary-Skill-1/boundary_3d_viewer.html
   ```

   **Extract and note these patterns:**
   - Label creation function (canvas size, font size, sprite scale)
   - Wall/boundary rendering style and colors
   - Gate visualization (dashed lines, different color)
   - Camera positioning and controls
   - Layout structure (panels, legend, controls)
   - Material properties for walls and features

2. **Calculate scale factor for your data**
   ```
   Reference perimeter: [reference value] FT
   Your perimeter: [extracted value] FT
   Scale factor = Your perimeter / Reference perimeter

   Apply scale factor to:
   - Label sprite scales
   - Wall thickness
   - Feature sizes
   - Dimension line offsets
   ```

3. **Read the reference JSON structure**
   ```bash
   Read assets/Boundary-Skill-1/boundary_data.json
   ```
   Match the exact field names, nesting structure, and data format.

4. **Read the reference analysis report**
   ```bash
   Read assets/Boundary-Skill-1/boundary_report.md
   ```
   Use same sections, headings, calculations, and format.

---

### Outputs to Generate

1. **boundary_3d_viewer.html** - Interactive 3D model (MATCH REFERENCE STYLE)
2. **boundary_technical.svg** - Technical drawing (MATCH REFERENCE FORMAT)
3. **boundary_data.json** - Structured data (MATCH REFERENCE STRUCTURE)
4. **boundary_report.md** - Analysis summary (MATCH REFERENCE FORMAT)

### HTML 3D Viewer Requirements

```
MANDATORY:
- Model CENTERED on canvas (not in corner)
- All measurements labeled on walls WITH REFERENCE-STYLE SCALING
- Special features highlighted (gate, steps)
- Camera controls for rotation/zoom
- Legend showing feature colors
- Labels must be visible and readable (scale appropriately)
```

### SVG Technical Drawing Requirements

```
MANDATORY:
- Labels ON boundary lines (not offset)
- Compass direction markers
- Gate/opening shown with dashed line
- Scale indicator
- Vertex points marked
```

---

## COMMON ERRORS AND SOLUTIONS

### Error: Polygon Doesn't Close

**Causes:**
1. Missed a small segment
2. Wrong direction for a segment
3. Measurement reading error

**Solution:**
1. Re-examine each edge section by section
2. Verify direction arrows in image
3. Re-read unclear measurements

### Error: Area Calculation Seems Wrong

**Causes:**
1. Incorrect sign on coordinate
2. Missed the negative X values
3. Wrong vertex order

**Solution:**
1. Check for negative coordinates (indents)
2. Verify clockwise traversal order
3. Recalculate step by step

### Error: Feature Misidentified

**Causes:**
1. Gate vs. wall confusion
2. Vertical vs. horizontal confusion
3. Step vs. indent confusion

**Solution:**
1. Re-examine that specific image section
2. Look at measurement orientation
3. Ask user for clarification

---

## ASKING USER FOR CLARIFICATION

### When to Ask

**Always ask when:**
- A measurement is partially obscured
- Two similar numbers could be confused
- Direction is ambiguous from image
- Feature type is unclear
- Calculated totals don't match expected

### How to Ask

```
Format:
"Looking at the [edge/feature] section:
I see [observation].
Could you confirm this is [interpretation]?

Alternative reading: [other possibility]"
```

### Example Questions

```
"Looking at the North edge indent:
I see a horizontal measurement that could be [A] or [B].
Could you confirm which value is correct?"

"Looking at the gate area:
The gate appears to be [vertical/horizontal].
Is this correct?"
```

---

## MEASUREMENT AUTHORITY PRINCIPLE

### The Golden Rule

```
!!! HAND-DRAWN MEASUREMENTS ARE THE SOURCE OF TRUTH !!!
!!! STORE AND DISPLAY EXACTLY WHAT THE IMAGE SHOWS !!!
```

### How to Handle Measurements

| Step | Action |
|------|--------|
| **Extract** | Read EXACT value from image (27.4 FT, not ~27 FT) |
| **Store** | Save the exact image value in JSON data |
| **Calculate** | Use actual values for perimeter, area |
| **Display** | Show original measurement on all labels |
| **Render** | Draw shape that actual measurements create |

### What an Architect Does

When given measurements from a hand-drawn sketch:
1. The architect accepts those measurements as given
2. They draw the shape those measurements create
3. The drawing reflects the actual dimensions
4. If the shape looks slightly different - that's correct

### Example Application

```
FROM IMAGE:
  North Lower: 27.4 FT
  Indent: 2.9 FT
  North Upper: 25.0 FT

DATA FILE (boundary_data.json):
  "north_lower": 27.4  ← exact image value
  "indent": 2.9        ← exact image value
  "north_upper": 25.0  ← exact image value

SVG/HTML LABELS:
  Display "27.4 FT" on North Lower edge
  Display "2.9 FT" on Indent edge
  Display "25.0 FT" on North Upper edge

CALCULATIONS:
  Perimeter includes 27.4 (not adjusted)
  Area calculated from actual measurements
```

### Never Do This

```
WRONG: "Adjusting 27.4 to 26.6 for geometric closure"
WRONG: Storing calculated values instead of image values
WRONG: Showing "corrected" measurements on labels
WRONG: Modifying measurements to make polygon close perfectly
```

---

## CRITICAL RULES

### ALWAYS

1. **Section-by-section** - Examine one edge at a time
2. **Record every segment** - No matter how small
3. **Handle negative coordinates** - Indents go negative
4. **Preserve image measurements** - They are authoritative
5. **Center the output** - Never in corner
6. **Ask if unclear** - Don't guess
7. **READ REFERENCE FILES BEFORE OUTPUT** - Mandatory in Phase 2
8. **Match reference styling** - Labels, walls, colors must match assets/Boundary-Skill-1/

### NEVER

1. **Never look at whole image at once** - Miss details
2. **Never assume gate direction** - Check image
3. **Never ignore small measurements** - They matter
4. **Never skip validation** - Errors compound
5. **Never hardcode values** - Read from image
6. **Never "correct" image measurements** - They are authoritative
7. **Never rush** - Precision requires patience
8. **Never generate without reading reference** - Output styling must match reference

---

## USING boundary_utils.py

### Import Functions

```python
from boundary_utils import (
    calculate_area_shoelace,
    calculate_perimeter,
    calculate_centroid,
    calculate_bounds,
    analyze_segment,
    get_all_segments,
    validate_closure,
    validate_polygon,
    get_all_interior_angles,
    center_coordinates,
    transform_for_threejs,
    analyze_boundary,
    analyze_boundary_with_verification,
    round_precise,
    verify_measurement
)
```

### Complete Analysis Example

```python
# After extracting vertices from image
vertices = [
    {"id": "P1", "x": extracted_x1, "y": extracted_y1},
    {"id": "P2", "x": extracted_x2, "y": extracted_y2},
    # ... all vertices from extraction
]

# Run full analysis
analysis = analyze_boundary(vertices, unit="FT")

# Check results
print(f"Area: {analysis['area']['value']} {analysis['area']['unit']}")
print(f"Perimeter: {analysis['perimeter']['value']} {analysis['perimeter']['unit']}")
print(f"Valid: {analysis['validation']['is_valid']}")
print(f"Closed: {analysis['closure']['is_closed']}")

# If you have expected measurements from image
expected_lengths = [extracted_len1, extracted_len2, ...]
verified = analyze_boundary_with_verification(vertices, expected_lengths)
print(f"Verification: {verified['verification']['accuracy_percent']}%")
```

---

## WORKFLOW SUMMARY

```
┌─────────────────────────────────────────┐
│     PHASE 1: EXTRACTION (12 steps)      │
├─────────────────────────────────────────┤
│ Step 1:  Center orientation             │
│ Step 2:  Find reference point           │
│ Step 3:  Create measurement plan        │
│ Step 4:  Examine TOP edge               │
│ Step 5:  Examine RIGHT edge             │
│ Step 6:  Examine BOTTOM edge            │
│ Step 7:  Examine LEFT edge              │
│ Step 8:  Examine special features       │
│ Step 9:  Examine annotations            │
│ Step 10: Cross-reference check          │
│ Step 11: Calculate derived values       │
│ Step 12: Build data structure           │
├─────────────────────────────────────────┤
│     Creator ←→ Judge validation         │
│     at EACH step                        │
├─────────────────────────────────────────┤
│     PHASE 2: GENERATION (6 steps)       │
├─────────────────────────────────────────┤
│ Step G1: Generate coordinates           │
│ Step G2: Calculate geometry             │
│ Step G3: Generate HTML 3D viewer        │
│ Step G4: Generate SVG drawing           │
│ Step G5: Generate JSON data             │
│ Step G6: Generate reports               │
├─────────────────────────────────────────┤
│     Judge validates EACH output         │
└─────────────────────────────────────────┘
```
