---
name: oa-3d-sketch-analysis
description: Self-evolving agentic skill for architect-grade analysis of hand-drawn sketches using 3-phase two-agent validation with automatic image tracking.
version: 8.3.0
license: MIT
trigger: "setup OA-3D-Skills"
---

# OA-3D Sketch Analysis Skill

A **self-evolving agentic system** for precision analysis of hand-drawn architectural sketches using a 3-phase two-agent architecture with confidence scoring at each phase.

---

## FRESH CHAT INITIALIZATION

### CRITICAL: First Steps for Every New Chat Session

```
!!! ALWAYS READ package.json FIRST !!!
!!! CHECK IMAGE STATUS BEFORE RUNNING !!!
!!! NEVER RE-PROCESS ALREADY COMPLETED IMAGES !!!
```

**When starting a new chat:**

1. **Read package.json** - Understand project configuration
   ```bash
   # Read the _README section for instructions
   cat package.json
   ```

2. **Check image status** - See what's processed vs pending
   ```bash
   python run.py --list
   ```

3. **Review references** - Look at assets/ folder before generating
   ```bash
   ls assets/Glass-Skill-1/
   ls assets/Boundary-Skill-1/
   ```

4. **Only process PENDING images** - Never re-run completed ones unless user explicitly requests `--force`

---

## IMAGE TRACKING SYSTEM

### Status Categories

| Status | Meaning | Action |
|--------|---------|--------|
| `[DONE]` | Outputs exist in outputs/ folder | **SKIP** - Don't re-process |
| `[NEW]` | No outputs yet | **PROCESS** - Run the skill |

### Commands

```bash
# List all images with status
python run.py --list

# Show only pending (unprocessed) images
python run.py --pending

# Process next pending image automatically
python run.py --next

# Process next pending glass image
python run.py --next glass

# Process next pending boundary image
python run.py --next boundary

# Force re-process (only when user explicitly requests)
python run.py <image_path> --force
```

### Example Output

```
======================================================================
OA-3D SKILLS - IMAGE STATUS
======================================================================

Glass Panel Analysis:
  Input Folder: inputs/Glass-Skills
  Reference: assets/Glass-Skill-1
--------------------------------------------------
  [DONE] PROCESSED (outputs exist):
    [x] Glass-Skill-2.jpeg -> outputs/Glass-Skill-2 (6 files)
  [NEW] PENDING (not yet processed):
    [ ] Glass-Skill-1.jpeg
    [ ] Glass-Skill-3.jpeg

Plot Boundary Analysis:
  Input Folder: inputs/Boundary-Skills
  Reference: assets/Boundary-Skill-1
--------------------------------------------------
  [NEW] PENDING (not yet processed):
    [ ] Boundary-Skill-1.jpeg

SUMMARY: 1 processed, 3 pending
======================================================================
```

---

## AUTO-TRIGGER SYSTEM

### How It Works

**IMPORTANT: Skill detection is based on the PARENT FOLDER NAME ONLY, not the filename.**

This means:
- **ANY image** placed in `inputs/Glass-Skills/` will trigger the Glass skill
- **ANY image** placed in `inputs/Boundary-Skills/` will trigger the Boundary skill
- Filename does NOT matter - you can use any naming convention

| Parent Folder | Skill Triggered | Works With |
|---------------|-----------------|------------|
| `inputs/Glass-Skills/` | Glass Manufacturing | **ANY image file** (e.g., `photo.jpg`, `scan123.png`, `IMG_001.jpeg`) |
| `inputs/Boundary-Skills/` | Boundary Analysis | **ANY image file** |

### Examples

```bash
# These ALL trigger the Glass skill (based on parent folder):
inputs/Glass-Skills/Glass-Skill-1.jpeg    # Named conventionally
inputs/Glass-Skills/my_sketch.png         # Custom name
inputs/Glass-Skills/IMG_20240115.jpg      # Camera naming
inputs/Glass-Skills/scan001.jpeg          # Scanner naming

# These ALL trigger the Boundary skill:
inputs/Boundary-Skills/plot_boundary.png
inputs/Boundary-Skills/survey_image.jpg
```

### Output Folder Naming

The output folder uses the **number from the filename** (if present):
- `inputs/Glass-Skills/Glass-Skill-2.jpeg` -> `outputs/Glass-Skill-2/`
- `inputs/Glass-Skills/photo123.png` -> `outputs/Glass-Skill-123/`
- `inputs/Glass-Skills/scan.jpg` -> `outputs/Glass-Skill-1/` (default)

### Configuration (package.json)

```json
{
  "autoTrigger": {
    "enabled": true,
    "skipProcessed": true,
    "rules": [
      {"inputPattern": "inputs/Glass-Skills/*", "skill": "glass-manufacturing"},
      {"inputPattern": "inputs/Boundary-Skills/*", "skill": "boundary-analysis"}
    ]
  }
}
```

**Note:** The rules are fallback patterns. Primary detection uses parent folder name directly.

---

## THE 3-PHASE TWO-AGENT ARCHITECTURE

### Overview

```
+---------------------------------------------------------------------+
|                 SELF-EVOLVING AGENTIC WORKFLOW                       |
|          Both agents validate at EACH phase with confidence          |
+---------------------------------------------------------------------+
|                                                                      |
|  +-------------------------------------------------------------+    |
|  |              PHASE 1: IMAGE ANALYSIS (85% min)              |    |
|  +-------------------------------------------------------------+    |
|  |  CREATOR AGENT              JUDGE AGENT                     |    |
|  |  - Identifies orientation   - Validates panel count         |    |
|  |  - Counts panels/sections   - Checks boundary identification|    |
|  |  - Locates boundaries       - Verifies orientation          |    |
|  |  - Notes special features   - Approves or requests fix      |    |
|  |                                                              |    |
|  |  Creator Confidence: X%     Judge Confidence: Y%            |    |
|  |  Combined: (X+Y)/2 -> Must reach 85%                        |    |
|  +-------------------------------------------------------------+    |
|                              |                                       |
|                              v                                       |
|  +-------------------------------------------------------------+    |
|  |            PHASE 2: METRICS EXTRACTION (90% min)            |    |
|  +-------------------------------------------------------------+    |
|  |  CREATOR AGENT              JUDGE AGENT                     |    |
|  |  - Reads exact dimensions   - Validates width sum           |    |
|  |  - Extracts heights         - Checks height continuity      |    |
|  |  - Records hole positions   - Verifies panel types          |    |
|  |  - Calculates totals        - Validates calculations        |    |
|  |                                                              |    |
|  |  Creator Confidence: X%     Judge Confidence: Y%            |    |
|  |  Combined: (X+Y)/2 -> Must reach 90%                        |    |
|  +-------------------------------------------------------------+    |
|                              |                                       |
|                              v                                       |
|  +-------------------------------------------------------------+    |
|  |            PHASE 3: OUTPUT GENERATION (95% min)             |    |
|  +-------------------------------------------------------------+    |
|  |  CREATOR AGENT              JUDGE AGENT                     |    |
|  |  - Generates HTML 3D        - Validates HTML renders        |    |
|  |  - Generates SVG drawing    - Checks SVG dimensions         |    |
|  |  - Generates JSON data      - Verifies data completeness    |    |
|  |  - Generates reports        - Final file validation         |    |
|  |                                                              |    |
|  |  Creator Confidence: X%     Judge Confidence: Y%            |    |
|  |  Combined: (X+Y)/2 -> Must reach 95%                        |    |
|  +-------------------------------------------------------------+    |
|                                                                      |
|  FINAL CONFIDENCE = Average of all 3 phases                         |
|  SUCCESS = Final Confidence >= 80%                                   |
+---------------------------------------------------------------------+
```

### Phase Iteration

At each phase, if confidence is below threshold:
1. Judge provides feedback with specific issues
2. Creator applies corrections
3. Both agents re-validate
4. Repeat until approved or max iterations reached

```
Phase Max Iterations:
- PHASE 1: 3 iterations
- PHASE 2: 5 iterations
- PHASE 3: 2 iterations
```

---

## SKILL TYPES

### Two Specialized Skills

| Skill | Location | Purpose | Units | Reference |
|-------|----------|---------|-------|-----------|
| **Glass Panel** | skills/Glass-Measurement-Skill/SKILL-glass.md | Manufacturing specs | mm | assets/Glass-Skill-1/ |
| **Plot Boundary** | skills/Boundary-Measurement-Skill/SKILL-boundary.md | Survey analysis | FT, m | assets/Boundary-Skill-1/ |

---

## PHASE 1: IMAGE ANALYSIS

### Creator Agent Tasks

1. **Identify image orientation** (rotated? which direction?)
2. **Count panels/sections** (how many dividers + 1)
3. **Locate boundary lines** (vertical dividers between sections)
4. **Identify measurement positions** (where are numbers located?)
5. **Note special features** (notches, holes, tapers, angles)

### Judge Agent Checks

1. **Panel count = dividers + 1** (mathematical validation)
2. **All measurement positions identified** (nothing missed)
3. **Orientation correctly determined** (matches image)
4. **Special features catalogued** (complete inventory)

### Confidence Calculation

```python
# Creator confidence based on completeness
creator_score = 0
if orientation_identified: creator_score += 20
if panel_count > 0: creator_score += 20
if boundaries_located: creator_score += 20
if measurements_found: creator_score += 20
if features_noted: creator_score += 20

# Judge confidence based on validation
judge_score = creator_score - (issues_found * 10)

# Combined
combined = (creator_score + judge_score) / 2
```

---

## PHASE 2: METRICS EXTRACTION

### Creator Agent Tasks

1. **Read each dimension EXACTLY as shown** (no rounding)
2. **Extract heights at each boundary** (left, middle, right edges)
3. **Record panel widths** (each section separately)
4. **Note hole positions and counts** (x, y, diameter)
5. **Calculate derived values** (totals, areas, sums)

### Judge Agent Checks

1. **Width sum = total width (+/-1mm)** - Mathematical validation
2. **Heights continuous at boundaries** - Adjacent sections share height
3. **Panel types correct** - First section is "door"
4. **Door has no holes** - Squares are angle markers, not holes
5. **All measurements plausible** - No impossible values

### The 12-Step Extraction Process

```
STEP 1:  CENTER ORIENTATION     - Look at center, identify shape
STEP 2:  REFERENCE POINT        - Find anchor (Panel 1, GATE, etc.)
STEP 3:  MEASUREMENT PLAN       - Decide traversal direction
STEP 4:  EXAMINE PANEL 1        - First section only (usually Door)
STEP 5:  EXAMINE PANEL 2        - Second section only
STEP 6:  EXAMINE REMAINING      - All other panels one by one
STEP 7:  EXAMINE BOUNDARIES     - Heights at each divider
STEP 8:  EXAMINE FEATURES       - Holes, notches, tapers
STEP 9:  EXAMINE ANNOTATIONS    - Labels, arrows, notes
STEP 10: CROSS-REFERENCE        - Verify consistency
STEP 11: CALCULATE DERIVED      - Totals, areas, sums
STEP 12: BUILD DATA STRUCTURE   - Final JSON output
```

---

## PHASE 3: OUTPUT GENERATION

### ⚠️ MANDATORY REFERENCE CHECK (BEFORE ANY OUTPUT)

```
!!! CRITICAL: READ REFERENCE FILES BEFORE GENERATING ANY OUTPUT !!!
!!! ALL OUTPUTS MUST MATCH REFERENCE FORMAT AND STYLE !!!
!!! NEVER GENERATE WITHOUT REVIEWING REFERENCE FIRST !!!
```

**Step 0: Reference Review (REQUIRED)**

Before generating ANY output files, the Creator Agent MUST:

1. **Read the reference HTML file**
   ```bash
   # For Glass Skill:
   Read assets/Glass-Skill-1/glass_3d_model.html

   # For Boundary Skill:
   Read assets/Boundary-Skill-1/boundary_3d_viewer.html
   ```

2. **Analyze reference patterns** - Extract and note:
   - Label creation function (canvas size, font size, sprite scale)
   - Dimension line function (arrow sizes, extension lines, offsets)
   - Color schemes and material properties
   - Layout structure (left specs, center 3D, right controls)
   - Scale calculations for different dimension sizes

3. **Read the reference JSON file**
   ```bash
   # For Glass Skill:
   Read assets/Glass-Skill-1/extraction.json

   # For Boundary Skill:
   Read assets/Boundary-Skill-1/boundary_data.json
   ```

4. **Read the reference report**
   ```bash
   # For Glass Skill:
   Read assets/Glass-Skill-1/manufacturing_instructions.md

   # For Boundary Skill:
   Read assets/Boundary-Skill-1/boundary_report.md
   ```

**Reference Matching Requirements:**

| Element | Must Match Reference |
|---------|---------------------|
| Label font size | Same proportional scaling |
| Sprite scale | Calculated from reference ratio |
| Arrow dimensions | Same proportional scaling |
| Dimension line offsets | Appropriate for data scale |
| Color scheme | Exact same colors |
| Layout structure | Same panel arrangement |
| JSON structure | Same field names and nesting |
| Report format | Same sections and headings |

### Creator Agent Tasks

1. **Generate 3D HTML model** - Interactive Three.js viewer (MATCH REFERENCE STYLE)
2. **Generate SVG technical drawing** - With measurements (MATCH REFERENCE FORMAT)
3. **Generate JSON data file** - Complete extraction (MATCH REFERENCE STRUCTURE)
4. **Generate manufacturing instructions** - Step-by-step guide (MATCH REFERENCE FORMAT)
5. **Generate CNC G-code** - For cutting (glass only)
6. **Generate validation report** - Quality checks

### Judge Agent Checks

1. **Reference compliance** - Output style matches reference files
2. **HTML renders correctly** - File size > 100 bytes, labels visible
3. **SVG dimensions match** - Labels match extraction
4. **JSON is complete** - All required fields present, structure matches reference
5. **All files generated** - Expected count reached

### Output Files

**Glass Skill:**
```
outputs/Glass-Skill-N/
|-- confirmed_extraction.json    # Complete extraction data
|-- glass_3d_model.html          # Interactive 3D viewer
|-- technical_drawing.svg        # Technical drawing
|-- manufacturing_instructions.md # Manufacturing guide
|-- cnc_program.gcode            # CNC cutting program
+-- validation_report.json       # Quality validation
```

**Boundary Skill:**
```
outputs/Boundary-Skill-N/
|-- boundary_data.json           # Complete boundary data
|-- boundary_3d_viewer.html      # Interactive 3D viewer
|-- boundary_technical.svg       # Survey drawing
+-- boundary_report.md           # Analysis report
```

---

## FILE STRUCTURE

```
OA-3D-Skill/
|-- package.json             # Project config - READ THIS FIRST
|-- run.py                   # Main entry point with auto-trigger
|-- setup_skills.py          # Setup script
|-- requirements.txt         # Python dependencies
|
|-- inputs/                  # Place sketch images here
|   |-- Glass-Skills/        # Glass images -> triggers glass skill
|   |   |-- Glass-Skill-1.jpeg
|   |   |-- Glass-Skill-2.jpeg
|   |   +-- Glass-Skill-3.jpeg
|   +-- Boundary-Skills/     # Boundary images -> triggers boundary skill
|       +-- Boundary-Skill-1.jpeg
|
|-- outputs/                 # Generated outputs (auto-created)
|   |-- Glass-Skill-N/       # Per-image output folders
|   +-- Boundary-Skill-N/
|
|-- assets/                  # Reference outputs - REVIEW BEFORE GENERATING
|   |-- Glass-Skill-1/       # Reference glass outputs
|   +-- Boundary-Skill-1/    # Reference boundary outputs
|
|-- scripts/                 # Python workflow scripts
|   |-- two_agent_workflow.py    # 3-phase workflow orchestrator
|   |-- output_generator.py      # File generation
|   +-- agent1_creator.py        # Creator agent
|
+-- skills/                  # Skill documentation (SEPARATED BY TYPE)
    |-- Glass-Measurement-Skill/
    |   |-- SKILL.md         # Main architecture (this file)
    |   +-- SKILL-glass.md   # Glass methodology
    +-- Boundary-Measurement-Skill/
        |-- SKILL-boundary.md # Boundary methodology
        +-- boundary_utils.py # Python utilities
```

---

## REFERENCE OUTPUTS

### IMPORTANT: Always Review Before Generating

```
!!! CHECK assets/ FOLDER BEFORE CREATING NEW OUTPUTS !!!
!!! MAINTAIN CONSISTENCY WITH REFERENCE FORMAT !!!
!!! USE REFERENCES TO UNDERSTAND EXPECTED STRUCTURE !!!
```

### Glass-Skill-1 Reference (assets/Glass-Skill-1/)
- `glass_3d_model.html` - Interactive 3D viewer format
- `extraction.json` - Data structure format
- `manufacturing_instructions.md` - Report format

### Boundary-Skill-1 Reference (assets/Boundary-Skill-1/)
- `boundary_3d_viewer.html` - 3D viewer with SciPy/Shapely
- `boundary_data.json` - Boundary data format
- `boundary_report.md` - Analysis report format

---

## MEASUREMENT AUTHORITY PRINCIPLE

### The Golden Rule

```
!!! HAND-DRAWN MEASUREMENTS ARE THE SOURCE OF TRUTH !!!
!!! STORE AND DISPLAY EXACTLY WHAT THE IMAGE SHOWS !!!
!!! NEVER "CORRECT" OR MODIFY IMAGE MEASUREMENTS !!!
```

| Action | Rule |
|--------|------|
| **Extract** | Read EXACT value from image (847mm, not ~850mm) |
| **Store** | Save the exact image value in JSON |
| **Calculate** | Use actual values for totals, areas |
| **Display** | Show original measurement on all labels |
| **Render** | Draw shape that measurements create |

---

## CRITICAL RULES

### ALWAYS

1. **Read package.json first** - On every new chat
2. **Check --list before running** - Know what's processed
3. **Review assets/ references** - Before generating
4. **READ REFERENCE FILES IN PHASE 3** - Mandatory before output generation
5. **Match reference style** - Labels, dimensions, colors must match
6. **3-phase validation** - Both agents at each phase
7. **Section-by-section** - Never analyze whole image at once
8. **Preserve measurements** - Image values are authoritative

### NEVER

1. **Never re-process [DONE] images** - Unless user says --force
2. **Never skip phases** - All 3 phases required
3. **Never generate without reading reference** - Phase 3 requires reference review
4. **Never guess** - Ask user if unclear
5. **Never ignore confidence** - Must reach thresholds
6. **Never "correct" image values** - They are authoritative
7. **Never hardcode** - All values from image
8. **Never use different styling than reference** - Consistency is mandatory

---

## QUICK REFERENCE

### Start New Session
```bash
# 1. Check status
python run.py --list

# 2. Process next pending
python run.py --next

# 3. Or process specific image
python run.py inputs/Glass-Skills/Glass-Skill-3.jpeg
```

### Force Re-process
```bash
python run.py inputs/Glass-Skills/Glass-Skill-2.jpeg --force
```

### Check Specific Skill
```bash
python run.py --next glass
python run.py --next boundary
```
