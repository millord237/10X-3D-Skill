---
name: glass-panel-analysis
description: Manufacturing-grade method for analyzing hand-drawn glass panel sketches using 3-phase two-agent validation with self-evolving agentic workflow.
version: 4.2.0
license: MIT
parent: SKILL.md
inputFolder: inputs/Glass-Skills
outputFolder: outputs/Glass-Skill-{N}
referenceFolder: assets/Glass-Skill-1
units: mm
---

# Glass Panel Analysis Skill

Manufacturing-grade methodology for analyzing hand-drawn glass panel sketches using a **3-phase two-agent architecture** with confidence scoring at each phase.

---

## FRESH CHAT PROTOCOL

```
!!! BEFORE PROCESSING ANY GLASS IMAGE !!!
1. Read package.json
2. Run: python run.py --list
3. Check if image is [DONE] or [NEW]
4. Review assets/Glass-Skill-1/ for reference format
5. ONLY process [NEW] images unless --force requested
```

---

## AUTO-TRIGGER

This skill is automatically triggered when:
- Image path contains `Glass-Skills/`
- User runs: `python run.py inputs/Glass-Skills/<image>.jpeg`
- User runs: `python run.py --next glass`

---

## 3-PHASE WORKFLOW FOR GLASS

```
PHASE 1: IMAGE ANALYSIS (85% min confidence)
├── Creator: Identify orientation, count panels, locate boundaries
├── Judge: Validate panel count = dividers + 1
└── Output: Analysis data structure

PHASE 2: METRICS EXTRACTION (90% min confidence)
├── Creator: Read dimensions, extract heights, note holes
├── Judge: Validate width sum, height continuity, panel types
└── Output: Complete extraction JSON

PHASE 3: OUTPUT GENERATION (95% min confidence)
├── Creator: Generate HTML, SVG, JSON, MD, GCODE
├── Judge: Validate all files exist and are valid
└── Output: 6 output files
```

---

## IDENTIFICATION

### How to Recognize Glass Panel Sketches

**Look for these indicators:**

| Indicator | What It Means |
|-----------|---------------|
| Panel labels (Panel 1, Panel 2, Door) | Multiple glass sections |
| Millimeter (mm) units | Manufacturing precision units |
| Dashed vertical divider lines | Panel boundaries |
| Height numbers at vertical edges | Boundary heights |
| Taper markers (angle symbols like "<") | Angled/tapered sections |
| K-edge notation | Edge finishing specification |
| Thickness notation | Glass thickness |
| Hole markers (circles) | Drilling locations |

---

## PHASE 1: SECTION-BY-SECTION EXTRACTION

### Step-by-Step Process for Glass Panels

Follow the 12-step process from SKILL.md, with these glass-specific details:

---

### STEP 1: CENTER ORIENTATION

**What to look for:**
- Overall assembly layout (how many panels?)
- Direction of reading (left to right typically)
- Any overall dimensions (total width, total height)

**Record format:**
```
Layout: [N] panels visible
Direction: Left-to-right reading
Overall dimensions visible: [total width] x [total height] (if shown)
```

**DO NOT** read individual panel measurements yet.

---

### STEP 2: REFERENCE POINT IDENTIFICATION

**Best reference points for glass panels (in order):**

1. **Panel 1 / Door** - Usually leftmost, often distinctive
2. **Total width marker** - Overall dimension at top
3. **Height markers** - Vertical boundary heights

**Record format:**
```
Reference: [Panel 1 / Door] located at [leftmost position]
Why chosen: [clearly labeled / distinctive features / standard convention]
```

---

### STEP 3: CREATE MEASUREMENT PLAN

**For glass panels, trace LEFT-TO-RIGHT:**

```
Starting point: Panel 1 (leftmost)
Direction: LEFT TO RIGHT
Expected panels: [count based on vertical dividers + 1]
Special features to watch: [taper, holes, notches, K-edge]
```

---

### STEP 4: EXAMINE LEFTMOST PANEL (Panel 1 / Door)

**Focus ONLY on the first panel from the left.**

Questions to answer:
- What is the width at the BOTTOM?
- What is the width at the TOP? (same or different = tapered?)
- What is the height at the LEFT boundary?
- What is the height at the RIGHT boundary?
- Is there a taper marker (angle symbol)?
- Panel type (Door or Panel)?

**Record format:**
```
PANEL 1 (Door):
  Width (bottom): [value] mm
  Width (top): [value] mm (if different = tapered)
  Height (left boundary): [value] mm
  Height (right boundary): [value] mm
  Taper: [yes/no], if yes: starts at [height] mm
  Type: [Door / Panel]
  Features: [K-edge / holes / notches]
```

---

### STEP 5: EXAMINE SECOND PANEL

**Focus ONLY on the second panel from the left.**

**IMPORTANT**: The LEFT boundary height of Panel 2 should match the RIGHT boundary height of Panel 1.

Questions to answer:
- What is the width?
- What is the height at the LEFT boundary?
- What is the height at the RIGHT boundary?
- Any holes? (count, positions)
- Any notches?

**Record format:**
```
PANEL 2:
  Width: [value] mm
  Height (left boundary): [value] mm (should match Panel 1 right)
  Height (right boundary): [value] mm
  Holes: [count] at positions [list]
  Notches: [yes/no], if yes: [dimensions]
  Type: Panel
```

---

### STEP 6: EXAMINE REMAINING PANELS

**For each additional panel (3, 4, etc.):**

Same questions as Step 5:
- Width
- Height at left boundary
- Height at right boundary
- Holes, notches, special features

**Record each panel separately:**
```
PANEL [N]:
  Width: [value] mm
  Height (left boundary): [value] mm
  Height (right boundary): [value] mm
  Holes: [count] at [positions]
  Features: [any special features]
```

---

### STEP 7: EXAMINE BOUNDARY HEIGHTS

**Focus ONLY on the vertical boundary lines between panels.**

These heights are CRITICAL for manufacturing:
- Height at the very left edge
- Height at each panel divider
- Height at the very right edge

**Record format:**
```
BOUNDARY HEIGHTS:
  Boundary 0 (left edge): [value] mm
  Boundary 1 (after Panel 1): [value] mm
  Boundary 2 (after Panel 2): [value] mm
  ...
  Boundary N (right edge): [value] mm
```

---

### STEP 8: EXAMINE SPECIAL FEATURES

**Look specifically for:**

| Feature | How to Identify | What to Record |
|---------|-----------------|----------------|
| TAPER | Angle marker "<" with number | Start height, angle |
| HOLES | Circles on panel | Count, diameter, positions |
| NOTCHES | Rectangular cuts | Dimensions, positions |
| K-EDGE | "K-edge" label | Which edges |
| THICKNESS | "Xmm thick" label | Thickness value |

**Record format:**
```
SPECIAL FEATURES:
  Feature 1: [type] on Panel [N], details: [specifics]
  Feature 2: ...
```

---

### STEP 9: EXAMINE ANNOTATIONS

**Look for:**
- Edge finishing labels (K-edge, beveled, polished)
- Manufacturing notes
- Directional arrows
- Reference numbers

**Record format:**
```
ANNOTATIONS:
  [Position]: [annotation text] - meaning: [interpretation]
```

---

### STEP 10: CROSS-REFERENCE CHECK

**Verify consistency:**

```
CHECK 1: Do boundary heights match?
  - Panel 1 right boundary = Panel 2 left boundary? [yes/no]
  - Panel 2 right boundary = Panel 3 left boundary? [yes/no]
  - ... for all adjacent panels

CHECK 2: Does total width add up?
  - Sum of all panel widths = total width shown? [yes/no]

CHECK 3: Taper consistency?
  - If tapered, do widths at top match panels properly? [yes/no]

CHECK 4: Any unclear measurements?
  - List any values that need user verification
```

---

### STEP 11: CALCULATE DERIVED VALUES

**Using extracted measurements:**

```python
# Total width calculation
total_width = sum(panel_widths)

# Height range
min_height = min(all_boundary_heights)
max_height = max(all_boundary_heights)

# Total holes
total_holes = sum(holes_per_panel)

# For tapered panels
if width_top != width_bottom:
    taper_angle = calculate_taper_angle(width_top, width_bottom, height)
```

**Record:**
```
CALCULATIONS:
  Total width: [value] mm
  Height range: [min] to [max] mm
  Total holes: [count]
  Tapered panels: [list]
```

---

### STEP 12: BUILD FINAL DATA STRUCTURE

**Compile into structured format:**

```json
{
  "sketch_type": "glass_panel",
  "unit": "mm",
  "panels": [
    {
      "id": "Panel 1",
      "type": "[Door/Panel]",
      "width_bottom": "[value]",
      "width_top": "[value]",
      "height_left": "[value]",
      "height_right": "[value]",
      "taper": {
        "tapered": "[true/false]",
        "start_height": "[value]"
      },
      "holes": [],
      "features": []
    }
  ],
  "boundary_heights": [],
  "calculations": {
    "total_width": "[value]",
    "height_range": {"min": "[value]", "max": "[value]"},
    "total_holes": "[count]"
  },
  "confidence": "[0-100]",
  "needs_clarification": []
}
```

---

## PANEL GEOMETRY

### Trapezoidal Panels (Tapered)

**When width_top ≠ width_bottom:**

```
        width_top
    ┌─────────────┐
    │             │
    │   TAPERED   │  ← panel narrows toward top
    │    DOOR     │
    │             │
    └─────────────┘
      width_bottom
```

The panel is a TRAPEZOID, not a rectangle.

### Rectangular Panels

**When width_top = width_bottom:**

```
        width
    ┌─────────────┐
    │             │
    │   REGULAR   │  ← same width throughout
    │   PANEL     │
    │             │
    └─────────────┘
        width
```

### Heights at Boundaries

**CRITICAL CONCEPT:**

Heights are measured at VERTICAL BOUNDARIES between panels, not per-panel.

```
    H0          H1          H2          H3
    │           │           │           │
    ▼           ▼           ▼           ▼
┌───────────┬───────────┬───────────┐
│           │           │           │
│  Panel 1  │  Panel 2  │  Panel 3  │
│           │           │           │
└───────────┴───────────┴───────────┘
```

- H0 = height at left edge of Panel 1
- H1 = height at right edge of Panel 1 = left edge of Panel 2
- H2 = height at right edge of Panel 2 = left edge of Panel 3
- H3 = height at right edge of Panel 3

---

## TAPER INTERPRETATION

### Taper Markers

**When you see an angle symbol (like "<") with a number:**

```
     84<  ← taper starts at 84mm from bottom
      │
      │   ┌──────────┐  narrower width
      │   │  tapered │
      │   │  section │
    ──┼───┤──────────┤
      │   │          │
      │   │ straight │  full width
      │   │ section  │
      0   └──────────┘
```

**Record:**
- Taper start height: value shown with marker
- Straight section: from 0 to taper start
- Tapered section: from taper start to top

### Calculating Taper

```python
# Given:
width_bottom = [extracted value]
width_top = [extracted value]
taper_start_height = [extracted value]
total_height = [extracted value]

# Tapered section height
tapered_height = total_height - taper_start_height

# Taper ratio
taper_ratio = (width_bottom - width_top) / tapered_height
```

---

## HOLE SPECIFICATIONS

### Identifying Holes

**Visual clues:**
- Circles drawn on panels
- Dimensions near circles (diameter)
- Position measurements from edges

**Record for each hole:**
```
Hole [N]:
  Panel: [panel number]
  Diameter: [value] mm
  Position X: [distance from left edge] mm
  Position Y: [distance from bottom] mm
```

### Hole Patterns

Common patterns:
- Single centered hole
- Two holes symmetrically placed
- Row of holes at specific height

---

## VALIDATION

### Width Verification

```python
# Total width should equal sum of panel widths
calculated_total = sum(panel_widths)
stated_total = [total width from image if shown]

if abs(calculated_total - stated_total) > tolerance:
    flag_for_verification()
```

### Height Continuity

```python
# Adjacent panels must share boundary height
for i in range(len(panels) - 1):
    panel_right = panels[i]['height_right']
    next_left = panels[i+1]['height_left']

    if panel_right != next_left:
        flag_discrepancy(f"Panel {i} right != Panel {i+1} left")
```

### Taper Consistency

```python
# If tapered, verify geometry makes sense
if panel['tapered']:
    # Top width should be less than bottom width (typically)
    if panel['width_top'] > panel['width_bottom']:
        flag_unusual("Taper widens toward top - verify this is correct")
```

---

## PHASE 2: OUTPUT GENERATION

### After Phase 1 Complete

**Only proceed when:**
- All panels measured and verified
- Boundary heights are continuous
- Taper calculations make sense
- Judge has approved all readings
- Confidence >= 95%

---

### ⚠️ MANDATORY REFERENCE CHECK (STEP 0 - BEFORE ANY OUTPUT)

```
!!! CRITICAL: READ REFERENCE FILES BEFORE GENERATING ANY OUTPUT !!!
!!! ALL OUTPUTS MUST MATCH REFERENCE FORMAT AND STYLE !!!
!!! NEVER GENERATE WITHOUT REVIEWING REFERENCE FIRST !!!
```

**Before generating ANY glass output files:**

1. **Read the reference HTML 3D viewer**
   ```bash
   Read assets/Glass-Skill-1/glass_3d_model.html
   ```

   **Extract and note these patterns:**
   - `createLabel()` function: canvas size (512x96), font size (32px), sprite scale (40, 7.5, 1)
   - `createDimensionLine()` function: arrow sizes (arrowLen=3, arrowRad=1.5), extension lines
   - Color scheme: panel colors, label colors (#1e40af), arrow colors (#ef4444)
   - Material properties: MeshPhysicalMaterial settings
   - Layout: 3-panel structure (left specs, center 3D, right controls)

2. **Calculate scale factor for your data**
   ```
   Reference total width: ~148.4 mm
   Your total width: [extracted value] mm
   Scale factor = Your total width / Reference total width

   Apply scale factor to:
   - sprite.scale.set(40 * scaleFactor, 7.5 * scaleFactor, 1)
   - arrowLen = 3 * scaleFactor
   - arrowRad = 1.5 * scaleFactor
   - dimension line offsets
   ```

3. **Read the reference JSON structure**
   ```bash
   Read assets/Glass-Skill-1/extraction.json
   ```
   Match the exact field names and nesting structure.

4. **Read the reference manufacturing instructions**
   ```bash
   Read assets/Glass-Skill-1/manufacturing_instructions.md
   ```
   Use same sections, headings, and format.

---

### Outputs to Generate

1. **glass_3d_model.html** - Interactive 3D visualization (MATCH REFERENCE STYLE)
2. **glass_technical.svg** - Technical drawing for manufacturing (MATCH REFERENCE FORMAT)
3. **glass_data.json** - Complete specifications (MATCH REFERENCE STRUCTURE)
4. **glass_report.md** - Manufacturing summary (MATCH REFERENCE FORMAT)
5. **glass_cnc.gcode** - CNC cutting program (if applicable)

### HTML 3D Viewer Requirements

```
MANDATORY:
- Panels displayed as 3D shapes
- Tapered panels shown as trapezoids
- Holes visible on panels
- Measurements labeled WITH REFERENCE-STYLE SCALING
- Color coding for panel types
- Labels must be visible and readable (scale appropriately)
- Dimension lines with extension lines and cone arrowheads (like reference)
```

### SVG Technical Drawing Requirements

```
MANDATORY:
- Each panel with dimensions
- Heights at all boundaries
- Taper markers where applicable
- Hole positions marked
- Scale indicator
- Edge finishing notes
```

---

## COMMON ERRORS AND SOLUTIONS

### Error: Boundary Heights Don't Match

**Cause:** Misread height at panel boundary

**Solution:**
1. Re-examine the specific boundary
2. Look at both adjacent panels' heights there
3. Verify which reading is correct

### Error: Total Width Doesn't Add Up

**Cause:** Missed a panel or misread width

**Solution:**
1. Count panels again (vertical dividers + 1)
2. Re-read each panel width
3. Check for overlapping dimensions

### Error: Taper Geometry Incorrect

**Cause:** Wrong interpretation of taper marker

**Solution:**
1. Find the angle marker "<" in image
2. Read the number associated with it
3. This is where taper STARTS, not ends

---

## ASKING USER FOR CLARIFICATION

### When to Ask

**Always ask when:**
- A dimension label is unclear
- Taper direction is ambiguous
- Hole positions are not clearly dimensioned
- Edge finish specifications are missing
- Panel count seems uncertain

### How to Ask

```
Format:
"Looking at [Panel N / boundary / feature]:
I see [observation].
Could you confirm this is [interpretation]?

Alternative reading: [other possibility]"
```

### Example Questions

```
"Looking at Panel 1 (Door):
I see the width could be [A] or [B] mm.
Could you confirm which value is correct?"

"Looking at the taper marker:
It appears to start at [value] mm from the bottom.
Is this correct?"

"Looking at the holes on Panel 2:
I count [N] holes. Is this accurate?"
```

---

## MEASUREMENT AUTHORITY PRINCIPLE

### The Golden Rule for Manufacturing

```
!!! HAND-DRAWN MEASUREMENTS ARE THE SOURCE OF TRUTH !!!
!!! STORE AND DISPLAY EXACTLY WHAT THE IMAGE SHOWS !!!
!!! MANUFACTURING DEPENDS ON PRECISE IMAGE VALUES !!!
```

### How to Handle Glass Panel Measurements

| Step | Action |
|------|--------|
| **Extract** | Read EXACT value from image (847 mm, not ~850 mm) |
| **Store** | Save the exact image value in JSON data |
| **Calculate** | Use actual values for total width, area |
| **Display** | Show original measurement on all labels |
| **Render** | Draw panels that actual measurements create |

### Manufacturing Precision

Glass manufacturing requires:
- Exact dimensions from the sketch
- No rounding or "adjusting"
- Stored values match image values
- CNC programs use exact measurements

### Example Application

```
FROM IMAGE:
  Panel 1 width: 453 mm
  Panel 2 width: 612 mm
  Boundary height: 847 mm

DATA FILE (glass_data.json):
  "panel_1_width": 453    ← exact image value
  "panel_2_width": 612    ← exact image value
  "height": 847           ← exact image value

SVG/HTML LABELS:
  Display "453 mm" on Panel 1
  Display "612 mm" on Panel 2
  Display "847 mm" on boundary

CALCULATIONS:
  Total width = 453 + 612 = 1065 mm (actual sum)
```

---

## CRITICAL RULES

### ALWAYS

1. **Panel-by-panel** - Examine one panel at a time
2. **Record boundary heights** - Not just panel heights
3. **Check taper markers** - Note start height
4. **Count holes precisely** - Each one matters
5. **Verify continuity** - Adjacent boundaries must match
6. **Preserve image measurements** - They are authoritative
7. **Ask if unclear** - Don't guess dimensions
8. **READ REFERENCE FILES BEFORE OUTPUT** - Mandatory in Phase 2
9. **Match reference styling** - Labels, arrows, colors must match assets/Glass-Skill-1/

### NEVER

1. **Never look at all panels at once** - Miss details
2. **Never assume heights are equal** - Check each boundary
3. **Never ignore taper markers** - Critical for manufacturing
4. **Never skip hole verification** - Drilling is precise
5. **Never hardcode dimensions** - Read from image
6. **Never "correct" image measurements** - They are authoritative
7. **Never rush** - Manufacturing errors are costly
8. **Never generate without reading reference** - Output styling must match reference
9. **Never assume panel is "Door"** - Only label as Door if explicitly shown in image

---

## OUTPUT FILE CONVENTIONS

### File Naming

```
outputs/
└── Glass-Skill-[N]/
    ├── confirmed_extraction.json     # Complete extraction with analysis
    ├── glass_3d_model.html           # 3D interactive viewer
    ├── technical_drawing.svg         # Technical drawing
    ├── manufacturing_instructions.md # Manufacturing guide
    ├── cnc_program.gcode             # CNC cutting program
    └── validation_report.json        # Quality validation report
```

### Reference Output
Always review `assets/Glass-Skill-1/` before generating to maintain consistency.

### JSON Data Structure

```json
{
  "project": "Glass-Skill-[N]",
  "generated": "[timestamp]",
  "unit": "mm",
  "panels": [
    {
      "id": 1,
      "type": "Door",
      "width_bottom": "[value]",
      "width_top": "[value]",
      "height_left": "[value]",
      "height_right": "[value]",
      "tapered": true,
      "taper_start": "[value]",
      "holes": [
        {"diameter": "[value]", "x": "[value]", "y": "[value]"}
      ],
      "edge_finish": "K-edge"
    }
  ],
  "totals": {
    "width": "[value]",
    "panel_count": "[count]",
    "hole_count": "[count]"
  },
  "verification": {
    "width_sum_matches": true,
    "heights_continuous": true,
    "confidence": "[value]"
  }
}
```

---

## WORKFLOW SUMMARY

```
┌─────────────────────────────────────────────────────────────┐
│              3-PHASE TWO-AGENT WORKFLOW                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PHASE 1: IMAGE ANALYSIS (85% min confidence)               │
│  ─────────────────────────────────────────────              │
│  Creator: Orientation, panel count, boundaries              │
│  Judge: Validate panel_count = dividers + 1                 │
│  Iterate until combined confidence >= 85%                   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PHASE 2: METRICS EXTRACTION (90% min confidence)           │
│  ─────────────────────────────────────────────              │
│  12-Step Process:                                           │
│    1. Center orientation    7. Boundary heights             │
│    2. Reference point       8. Special features             │
│    3. Measurement plan      9. Annotations                  │
│    4. Examine Panel 1      10. Cross-reference              │
│    5. Examine Panel 2      11. Calculate derived            │
│    6. Remaining panels     12. Build data structure         │
│                                                             │
│  Judge Checks:                                              │
│    - Width sum = total (±1mm)                               │
│    - Heights continuous at boundaries                       │
│    - First section = "door" type                            │
│    - Door has no holes (squares = angle markers)            │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PHASE 3: OUTPUT GENERATION (95% min confidence)            │
│  ─────────────────────────────────────────────              │
│  Creator generates:                                         │
│    - confirmed_extraction.json                              │
│    - glass_3d_model.html                                    │
│    - technical_drawing.svg                                  │
│    - manufacturing_instructions.md                          │
│    - cnc_program.gcode                                      │
│    - validation_report.json                                 │
│                                                             │
│  Judge validates all files exist and are valid              │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  FINAL CONFIDENCE = Average of all 3 phases                 │
│  SUCCESS = Final Confidence >= 80%                          │
└─────────────────────────────────────────────────────────────┘
```
