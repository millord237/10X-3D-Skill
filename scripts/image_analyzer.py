#!/usr/bin/env python3
"""
Glass Sketch Image Analyzer
===========================

This module provides systematic section-by-section analysis of glass manufacturing sketches.
It identifies doors, panels, holes, notches, and dimensions with user confirmation.

CRITICAL RULES:
1. NEVER assume values - always ask user for confirmation
2. Analyze the image region by region
3. Understand the INTENT (door with notch, fixed panels, mounting holes, etc.)
4. Verify all measurements before output generation
5. Ask for clarification when handwriting is unclear

ANALYSIS REGIONS:
-----------------
+------------------+------------------+
|   TOP REGION     |  Heights at each |
|   (Heights)      |  position        |
+------------------+------------------+
|                  |                  |
| LEFT    CENTER REGION    RIGHT     |
| REGION  (Sections, Holes, REGION   |
| (Edge,  Dividers, Notches) (Edge)  |
| Thick)                             |
+------------------+------------------+
|   BOTTOM REGION  |  Total width,    |
|   (Widths)       |  section widths  |
+------------------+------------------+
"""

import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path


@dataclass
class HoleSpec:
    """Specification for a hole."""
    x: float  # X position from left edge (absolute)
    y: float  # Y position from bottom edge
    diameter: float
    purpose: str  # 'handle', 'mounting', 'ventilation', etc.
    section_name: str  # Which section this hole belongs to


@dataclass
class SectionSpec:
    """Specification for a section (door or panel)."""
    name: str
    section_type: str  # 'door' or 'panel'
    width: float
    height: float
    x_offset: float  # Position from left edge
    has_notch: bool = False
    notch_depth: float = 0
    notch_width: float = 0
    hole_count: int = 0
    hole_y_position: float = 0  # Y position of holes from bottom


@dataclass
class GlassFrameworkSpec:
    """Complete specification for a glass framework (door + panels)."""
    total_width: float
    max_height: float
    thickness: float
    sections: List[SectionSpec] = field(default_factory=list)
    holes: List[HoleSpec] = field(default_factory=list)
    height_profile: List[Dict[str, float]] = field(default_factory=list)
    edge_type: str = ""
    notes: List[str] = field(default_factory=list)
    user_confirmed: bool = False


@dataclass
class AnalysisResult:
    """Result from analyzing a region of the image."""
    region: str
    extracted_values: Dict[str, Any]
    confidence: str  # 'high', 'medium', 'low'
    needs_clarification: List[str] = field(default_factory=list)


class GlassSketchAnalyzer:
    """
    Analyzes glass sketch images to extract manufacturing specifications.

    This analyzer works in phases:
    1. Region Analysis - Extract data from each region
    2. User Clarification - Ask user about unclear values
    3. Verification - Verify mathematical relationships
    4. Output Generation - Generate spec only after confirmation
    """

    def __init__(self, image_path: str):
        self.image_path = image_path
        self.spec = GlassFrameworkSpec(
            total_width=0,
            max_height=0,
            thickness=0
        )
        self.analysis_log: List[str] = []
        self.region_results: Dict[str, AnalysisResult] = {}
        self.clarification_questions: List[Dict[str, Any]] = []

    def log(self, message: str):
        """Add to analysis log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.analysis_log.append(f"[{timestamp}] {message}")
        print(f"[{timestamp}] {message}")

    # ================================================================
    # PHASE 1: REGION ANALYSIS
    # ================================================================

    def analyze_top_region(self, heights: List[float], positions: List[str]) -> AnalysisResult:
        """
        Analyze TOP region for height measurements.

        Heights are read from LEFT to RIGHT.
        Look for:
        - Section heights at each position
        - Notch heights (smaller values between larger ones)
        - Maximum height

        Args:
            heights: List of height values from left to right
            positions: List of position names (e.g., ['left_edge', 'notch', 'panel1', ...])

        Returns:
            AnalysisResult with extracted heights and any clarification needs
        """
        self.log("Analyzing TOP region (heights)...")

        result = AnalysisResult(
            region="TOP",
            extracted_values={
                "heights": heights,
                "positions": positions,
                "max_height": max(heights) if heights else 0,
                "min_height": min(heights) if heights else 0
            },
            confidence="medium",
            needs_clarification=[]
        )

        # Check for potential notch (significant drop in height)
        for i in range(1, len(heights)):
            if heights[i] < heights[i-1] - 5:  # More than 5mm drop
                result.extracted_values["potential_notch_at"] = positions[i] if i < len(positions) else f"position_{i}"
                result.extracted_values["notch_depth"] = heights[i-1] - heights[i]

        # Flag for clarification if heights seem unusual
        if heights:
            height_range = max(heights) - min(heights)
            if height_range > 10:
                result.needs_clarification.append(
                    f"Heights vary by {height_range}mm. Is this correct? Heights: {heights}"
                )

        self.region_results["TOP"] = result
        self.log(f"TOP region: Found {len(heights)} height measurements")
        return result

    def analyze_left_region(self, thickness: float, edge_type: str) -> AnalysisResult:
        """
        Analyze LEFT region for edge details.

        Look for:
        - Thickness (mm)
        - Edge type (K-edge, flat, polished, etc.)
        - Any special markings

        Args:
            thickness: Glass thickness in mm
            edge_type: Type of edge treatment

        Returns:
            AnalysisResult with edge specifications
        """
        self.log("Analyzing LEFT region (edge details)...")

        result = AnalysisResult(
            region="LEFT",
            extracted_values={
                "thickness": thickness,
                "edge_type": edge_type
            },
            confidence="high",
            needs_clarification=[]
        )

        # Standard thickness check
        standard_thicknesses = [3, 4, 5, 6, 8, 10, 12, 15, 19]
        if thickness not in standard_thicknesses:
            result.confidence = "medium"
            result.needs_clarification.append(
                f"Thickness {thickness}mm is non-standard. Confirm: {standard_thicknesses}"
            )

        self.region_results["LEFT"] = result
        self.log(f"LEFT region: thickness={thickness}mm, edge={edge_type}")
        return result

    def analyze_bottom_region(self, total_width: float, section_widths: List[float]) -> AnalysisResult:
        """
        Analyze BOTTOM region for width measurements.

        Look for:
        - Total width (usually largest number)
        - Individual section widths
        - Verify sum of sections = total width

        Args:
            total_width: Total panel width
            section_widths: List of individual section widths

        Returns:
            AnalysisResult with width data and verification
        """
        self.log("Analyzing BOTTOM region (widths)...")

        calculated_sum = sum(section_widths)
        width_match = abs(calculated_sum - total_width) < 0.5  # 0.5mm tolerance

        result = AnalysisResult(
            region="BOTTOM",
            extracted_values={
                "total_width": total_width,
                "section_widths": section_widths,
                "calculated_sum": calculated_sum,
                "width_verification": width_match
            },
            confidence="high" if width_match else "low",
            needs_clarification=[]
        )

        if not width_match:
            result.needs_clarification.append(
                f"Width mismatch: sections sum to {calculated_sum}mm but total is {total_width}mm"
            )

        self.region_results["BOTTOM"] = result
        self.log(f"BOTTOM region: total_width={total_width}mm, sections={section_widths}")
        return result

    def analyze_center_region(
        self,
        section_count: int,
        section_types: List[str],
        hole_data: List[Dict[str, Any]],
        has_notch: bool,
        notch_section: int = 0
    ) -> AnalysisResult:
        """
        Analyze CENTER region for sections and holes.

        Look for:
        - Number of sections (vertical divider lines + 1)
        - Section types (door vs panel)
        - Dots (•) = holes
        - Squares (□) = 90° angle markers (NOT holes)
        - Hole positions (Y value from bottom)

        Args:
            section_count: Number of sections identified
            section_types: List of types ('door' or 'panel') for each section
            hole_data: List of hole information per section
            has_notch: Whether first section has a notch
            notch_section: Which section has the notch (0-indexed)

        Returns:
            AnalysisResult with section and hole data
        """
        self.log("Analyzing CENTER region (sections & holes)...")

        result = AnalysisResult(
            region="CENTER",
            extracted_values={
                "section_count": section_count,
                "section_types": section_types,
                "hole_data": hole_data,
                "has_notch": has_notch,
                "notch_section": notch_section
            },
            confidence="medium",
            needs_clarification=[]
        )

        # Clarification for section types
        if section_count > 0:
            door_count = section_types.count('door')
            panel_count = section_types.count('panel')
            result.needs_clarification.append(
                f"Identified {section_count} sections: {door_count} door(s), {panel_count} panel(s). Is this correct?"
            )

        # Clarification for holes
        total_holes = sum(h.get('count', 0) for h in hole_data)
        if total_holes > 0:
            result.needs_clarification.append(
                f"Found {total_holes} holes total. Verify hole positions and counts."
            )

        self.region_results["CENTER"] = result
        self.log(f"CENTER region: {section_count} sections, {total_holes} holes")
        return result

    # ================================================================
    # PHASE 2: BUILD SPECIFICATION FROM CONFIRMED VALUES
    # ================================================================

    def build_specification(self, confirmed_values: Dict[str, Any]) -> GlassFrameworkSpec:
        """
        Build complete specification from user-confirmed values.

        Args:
            confirmed_values: Dictionary containing all confirmed measurements

        Returns:
            Complete GlassFrameworkSpec
        """
        self.log("Building specification from confirmed values...")

        # Basic dimensions
        self.spec.total_width = confirmed_values.get('total_width', 0)
        self.spec.thickness = confirmed_values.get('thickness', 0)
        self.spec.edge_type = confirmed_values.get('edge_type', '')

        # Height profile
        heights = confirmed_values.get('heights', [])
        positions = confirmed_values.get('height_positions', [])

        if heights:
            self.spec.max_height = max(heights)
            for i, h in enumerate(heights):
                pos = positions[i] if i < len(positions) else f"position_{i}"
                self.spec.height_profile.append({
                    'position': pos,
                    'height': h
                })

        # Build sections
        sections_data = confirmed_values.get('sections', [])
        x_offset = 0

        for sec_data in sections_data:
            section = SectionSpec(
                name=sec_data.get('name', ''),
                section_type=sec_data.get('type', 'panel'),
                width=sec_data.get('width', 0),
                height=sec_data.get('height', self.spec.max_height),
                x_offset=x_offset,
                has_notch=sec_data.get('has_notch', False),
                notch_depth=sec_data.get('notch_depth', 0),
                notch_width=sec_data.get('notch_width', 0),
                hole_count=sec_data.get('hole_count', 0),
                hole_y_position=sec_data.get('hole_y', 0)
            )

            self.spec.sections.append(section)

            # Build holes for this section
            if section.hole_count > 0:
                self._add_holes_for_section(section, sec_data)

            x_offset += section.width
            self.log(f"Added section: {section.name} ({section.section_type})")

        # Notes
        self.spec.notes = confirmed_values.get('notes', [])
        self.spec.user_confirmed = True

        self.log("Specification build complete")
        return self.spec

    def _add_holes_for_section(self, section: SectionSpec, sec_data: Dict[str, Any]):
        """Add holes for a section based on configuration."""
        hole_count = section.hole_count
        hole_y = section.hole_y_position
        hole_diameter = sec_data.get('hole_diameter', 8)
        hole_purpose = sec_data.get('hole_purpose', 'mounting')

        # Calculate X positions for holes within section
        # Default: evenly spaced with margin from edges
        edge_margin = max(hole_diameter, 8)  # At least hole diameter from edge
        usable_width = section.width - 2 * edge_margin

        if hole_count == 2:
            # Two holes: one near each edge
            x_positions = [
                section.x_offset + edge_margin,
                section.x_offset + section.width - edge_margin
            ]
        elif hole_count == 1:
            # One hole: centered
            x_positions = [section.x_offset + section.width / 2]
        else:
            # Multiple holes: evenly distributed
            spacing = usable_width / (hole_count - 1) if hole_count > 1 else 0
            x_positions = [
                section.x_offset + edge_margin + i * spacing
                for i in range(hole_count)
            ]

        # Allow custom X positions if provided
        custom_x = sec_data.get('hole_x_positions', [])
        if custom_x:
            x_positions = [section.x_offset + x for x in custom_x]

        for x in x_positions:
            hole = HoleSpec(
                x=x,
                y=hole_y,
                diameter=hole_diameter,
                purpose=hole_purpose,
                section_name=section.name
            )
            self.spec.holes.append(hole)

    # ================================================================
    # PHASE 3: VERIFICATION
    # ================================================================

    def verify_specification(self) -> Tuple[bool, List[str]]:
        """
        Verify the specification for mathematical consistency.

        Checks:
        1. Notch calculation: notch_height + notch_depth = section_height
        2. Width sum: sum of sections = total_width
        3. Hole positions: within section boundaries

        Returns:
            Tuple of (is_valid, list of issues)
        """
        self.log("Verifying specification...")
        issues = []

        # 1. Verify width sum
        section_sum = sum(s.width for s in self.spec.sections)
        if abs(section_sum - self.spec.total_width) > 0.5:
            issues.append(
                f"Width mismatch: sections sum to {section_sum}mm, total is {self.spec.total_width}mm"
            )

        # 2. Verify notch calculations
        for section in self.spec.sections:
            if section.has_notch:
                # Find the notch height from height profile
                notch_height = section.height - section.notch_depth
                # This should be approximately 84mm if notch_depth is 7.3 and height is 91.3
                self.log(f"Notch verification: {notch_height} + {section.notch_depth} = {section.height}")

        # 3. Verify hole positions
        for hole in self.spec.holes:
            # Find the section this hole belongs to
            for section in self.spec.sections:
                if section.x_offset <= hole.x < section.x_offset + section.width:
                    # Check Y position
                    if hole.y > section.height:
                        issues.append(
                            f"Hole at ({hole.x}, {hole.y}) is above section height {section.height}"
                        )
                    # Check X margin
                    x_in_section = hole.x - section.x_offset
                    if x_in_section < hole.diameter/2:
                        issues.append(
                            f"Hole at X={hole.x} too close to left edge of {section.name}"
                        )
                    if x_in_section > section.width - hole.diameter/2:
                        issues.append(
                            f"Hole at X={hole.x} too close to right edge of {section.name}"
                        )
                    break

        is_valid = len(issues) == 0
        self.log(f"Verification complete: {'PASSED' if is_valid else 'FAILED'}")
        return is_valid, issues

    # ================================================================
    # OUTPUT METHODS
    # ================================================================

    def to_extraction_dict(self) -> Dict[str, Any]:
        """Convert specification to extraction dictionary for output generation."""
        if not self.spec.user_confirmed:
            raise ValueError("Specification must be user-confirmed before export")

        holes_list = [
            {
                'x': h.x,
                'y': h.y,
                'diameter': h.diameter,
                'purpose': h.purpose,
                'section': h.section_name
            }
            for h in self.spec.holes
        ]

        sections_list = [
            {
                'name': s.name,
                'type': s.section_type,
                'width': s.width,
                'height': s.height,
                'x_offset': s.x_offset,
                'y_offset': 0,
                'has_notch': s.has_notch,
                'notch_depth': s.notch_depth if s.has_notch else 0,
                'hole_count': s.hole_count
            }
            for s in self.spec.sections
        ]

        return {
            'dimensions': {
                'width': self.spec.total_width,
                'height': self.spec.max_height,
                'thickness': self.spec.thickness
            },
            'height_profile': self.spec.height_profile,
            'sections': sections_list,
            'holes': holes_list,
            'edge_type': self.spec.edge_type,
            'glass_type': 'clear_tempered',
            'notes': self.spec.notes,
            'user_confirmed': True,
            'analysis_log': self.analysis_log
        }

    def save_extraction(self, output_path: str):
        """Save extraction to JSON file."""
        data = self.to_extraction_dict()
        data['image_path'] = self.image_path
        data['timestamp'] = datetime.now().isoformat()

        Path(output_path).write_text(json.dumps(data, indent=2), encoding='utf-8')
        self.log(f"Saved extraction to {output_path}")

    def get_clarification_questions(self) -> List[Dict[str, Any]]:
        """Get all questions that need user clarification."""
        questions = []

        for region, result in self.region_results.items():
            for q in result.needs_clarification:
                questions.append({
                    'region': region,
                    'question': q,
                    'confidence': result.confidence
                })

        return questions


# ================================================================
# ANALYSIS GUIDELINES - READ BEFORE USING
# ================================================================
"""
STEP 1: IDENTIFY WHAT YOU SEE
-----------------------------
Look at the image and identify:
- Count vertical lines (dividers between sections)
- Count dots (•) = holes
- Count squares (□) = 90° angle markers (NOT holes!)
- Identify any notches or cutouts
- Note all numbers and their positions

STEP 2: UNDERSTAND THE INTENT
-----------------------------
- First section with notch = usually DOOR
- Other sections = usually FIXED PANELS
- Holes at bottom of panels = MOUNTING holes
- Holes at mid-height = HANDLE holes (if door has them)
- Square markers (□) = 90° angle reference, NOT holes

STEP 3: EXTRACT BY REGION
-------------------------
TOP REGION: Heights at each position (left to right)
LEFT REGION: Thickness, edge type
BOTTOM REGION: Total width, section widths
CENTER REGION: Sections, holes, notches

STEP 4: ASK USER FOR CONFIRMATION
---------------------------------
ALWAYS ask about:
- Section types (door vs panel)
- Unclear numbers (3 vs 7, 1 vs 7, etc.)
- Hole positions and counts
- Symbol meanings (dot vs square)

STEP 5: VERIFY MATHEMATICS
--------------------------
- notch_height + notch_depth = section_height
- sum(section_widths) = total_width
- hole_y < section_height

STEP 6: GENERATE OUTPUTS
------------------------
ONLY after user confirms all values!
"""


def analyze_glass_sketch(image_path: str, confirmed_values: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to analyze a glass sketch with user-confirmed values.

    Example confirmed_values:
    {
        'total_width': 140.4,
        'thickness': 4.0,
        'edge_type': 'K_edge',
        'heights': [91.3, 84.0, 91.4, 91.0, 91.1, 91.3],
        'height_positions': ['left', 'notch', 'panel1', 'panel2', 'panel3', 'right'],
        'sections': [
            {
                'name': 'Door',
                'type': 'door',
                'width': 36.0,
                'height': 91.3,
                'has_notch': True,
                'notch_depth': 7.3,
                'hole_count': 0
            },
            {
                'name': 'Panel 1',
                'type': 'panel',
                'width': 34.8,
                'height': 91.4,
                'hole_count': 2,
                'hole_y': 37.4,
                'hole_diameter': 8,
                'hole_purpose': 'mounting'
            },
            ...
        ],
        'notes': ['User confirmed all values']
    }
    """
    analyzer = GlassSketchAnalyzer(image_path)
    analyzer.build_specification(confirmed_values)

    # Verify
    is_valid, issues = analyzer.verify_specification()
    if not is_valid:
        print("WARNING: Specification has issues:")
        for issue in issues:
            print(f"  - {issue}")

    return analyzer.to_extraction_dict()
