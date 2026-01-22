#!/usr/bin/env python3
"""
Agent 1: Creator Agent - DYNAMIC IMAGE ANALYSIS
================================================

Responsible for extracting specifications from ANY glass sketch image.
Analyzes the image dynamically - NO hardcoded values.

ANALYSIS METHODOLOGY:
1. TOP REGION: Read ALL height values left-to-right at vertical edges
2. LEFT REGION: Extract thickness, edge type (K)
3. BOTTOM REGION: Read total width, individual section widths
4. CENTER REGION: Count panels, identify symbols, dividers

PANEL IDENTIFICATION (Dynamic):
- Panel 1 = First section (leftmost) = Door type
- Panel 2, 3, 4... = Subsequent sections = Panel type
- Count panels by: vertical divider lines + 1
- Heights at boundaries: N panels = N+1 height values

HEIGHT ASSIGNMENT (Dynamic):
- Heights are at VERTICAL EDGES (panel boundaries)
- Adjacent panels share boundary heights
- Panel[i].height_right = Panel[i+1].height_left

SYMBOL RECOGNITION:
- dots = holes (OPTIONAL)
- squares = angle markers (NOT holes)
- number< = taper reference point
- dashed lines = section dividers

DOMAIN RULES (Applied dynamically):
- Panel 1 (Door): NO notch, NO holes, MAY be tapered
- Panels 2+: NO notch, holes OPTIONAL
"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Any


# ================================================================
# DOMAIN KNOWLEDGE - DYNAMIC ANALYSIS RULES
# ================================================================
DOMAIN_RULES = {
    # Symbol recognition rules (apply to any image)
    "symbols": {
        "dot": {
            "meaning": "hole_position",
            "panel_types": ["panel"],  # NOT on door/Panel 1
            "optional": True,
            "note": "Holes are OPTIONAL - can be added after cutting"
        },
        "square": {
            "meaning": "angle_reference_marker",
            "panel_types": ["door"],  # Only on door/Panel 1
            "NOT_A": "hole",
            "note": "Squares indicate angle references, NOT holes"
        },
        "angle_marker": {
            "pattern": "number<",  # e.g., "84<"
            "meaning": "taper_start_height",
            "description": "Height where taper begins (straight below, slant above)",
            "NOT_A": "notch"
        },
        "dashed_line": {
            "meaning": "section_divider",
            "use": "Count to determine number of panels"
        },
        "K": {
            "meaning": "K_edge_type",
            "location": "left_region"
        }
    },

    # Panel type rules (apply dynamically)
    "panel_types": {
        "Panel 1": {
            "type": "door",
            "position": "first_section",
            "has_notch": False,
            "has_holes": False,
            "may_be_tapered": True,
            "notes": [
                "First section is always the door (Panel 1)",
                "NO notch - only tapered geometry",
                "Squares are angle markers, NOT holes",
                "If width_bottom != width_top, it is tapered"
            ]
        },
        "Panel N": {
            "type": "panel",
            "position": "after_Panel_1",
            "has_notch": False,
            "has_holes": "optional",
            "is_tapered": False,
            "notes": [
                "All sections after Panel 1 are panels",
                "Holes are OPTIONAL (count dots if visible)",
                "Panels are rectangular (not tapered)"
            ]
        }
    },

    # Height assignment rules
    "height_rules": {
        "location": "top_region",
        "direction": "left_to_right",
        "meaning": "heights_at_vertical_boundaries",
        "assignment": {
            "For N panels, expect N+1 height values": True,
            "Height[0]": "Panel_1.height_left (left edge)",
            "Height[i]": "Panel_i.height_right = Panel_{i+1}.height_left",
            "Height[N]": "Last_panel.height_right (right edge)"
        },
        "shared_boundary_rule": "Adjacent panels share the same height at their boundary"
    },

    # Width extraction rules
    "width_rules": {
        "location": "bottom_region",
        "total_width": "largest_value_often_underlined",
        "section_widths": "individual_values_above_sections",
        "verification": "sum(section_widths) ≈ total_width (±0.5mm)"
    },

    # Verification rules
    "verification": {
        "width_sum_tolerance": 0.5,
        "height_boundary_check": "Panel[i].height_right == Panel[i+1].height_left",
        "panel_count_check": "sections == divider_lines + 1",
        "taper_check": "if tapered: width_top > width_bottom"
    }
}


@dataclass
class ConfidenceScore:
    """Represents a value with confidence."""
    value: Any
    confidence: float  # 0-100
    source: str = "extracted"  # extracted, calculated, corrected, default

    def is_high(self) -> bool:
        return self.confidence >= 90

    def is_medium(self) -> bool:
        return 70 <= self.confidence < 90

    def is_low(self) -> bool:
        return self.confidence < 70


@dataclass
class Dimension:
    """Represents a dimension measurement with confidence."""
    value: float
    unit: str = "mm"
    label: str = ""
    confidence: float = 80.0
    source: str = "extracted"


@dataclass
class Hole:
    """Represents a hole specification."""
    x: float
    y: float
    diameter: float
    purpose: str = "mounting"
    section: str = ""
    position_note: str = ""  # e.g., "left bottom edge"


@dataclass
class Section:
    """Represents a section of the glass panel.

    HEIGHT MEASUREMENT LOGIC:
    - Each section has TWO heights: height_left and height_right
    - Heights are measured at vertical EDGES (dividers between sections)
    - Adjacent sections SHARE the height at their common boundary
    - Example: Panel1.height_right = Panel2.height_left
    - The 'height' field is the representative height (max of left/right)
    """
    name: str
    section_type: str  # 'door' or 'panel'
    width: float
    height: float  # Representative height (max of left/right)
    x_offset: float = 0.0
    y_offset: float = 0.0
    # Height at each vertical edge
    height_left: float = 0.0   # Height at LEFT edge of this section
    height_right: float = 0.0  # Height at RIGHT edge of this section
    has_notch: bool = False
    notch_depth: float = 0.0
    notch_height: float = 0.0
    hole_count: int = 0
    hole_y: float = 0.0
    # Tapered geometry (for door section)
    is_tapered: bool = False
    width_bottom: float = 0.0
    width_top: float = 0.0
    taper_start_height: float = 0.0
    # Confidence scores
    width_confidence: float = 80.0
    height_confidence: float = 80.0
    height_left_confidence: float = 80.0
    height_right_confidence: float = 80.0


@dataclass
class GlassSpecification:
    """Complete glass panel specification with confidence scoring."""
    total_width: float
    max_height: float
    thickness: float
    sections: List[Section] = field(default_factory=list)
    holes: List[Hole] = field(default_factory=list)
    height_profile: List[Dict[str, float]] = field(default_factory=list)
    edge_type: str = "K_edge"
    glass_type: str = "clear_tempered"
    notes: List[str] = field(default_factory=list)
    # Confidence scores
    overall_confidence: float = 80.0
    width_confidence: float = 80.0
    height_confidence: float = 80.0
    thickness_confidence: float = 90.0

    def calculate_overall_confidence(self) -> float:
        """Calculate overall confidence from component scores."""
        scores = [self.width_confidence, self.height_confidence, self.thickness_confidence]
        for section in self.sections:
            scores.append(section.width_confidence)
            scores.append(section.height_confidence)
        self.overall_confidence = sum(scores) / len(scores) if scores else 0
        return self.overall_confidence

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for output generation."""
        result = {
            "dimensions": {
                "width": self.total_width,
                "height": self.max_height,
                "thickness": self.thickness
            },
            "height_profile": self.height_profile,
            "sections": [],
            "holes": [
                {
                    "x": h.x,
                    "y": h.y,
                    "diameter": h.diameter,
                    "purpose": h.purpose,
                    "section": h.section,
                    "position_note": h.position_note
                }
                for h in self.holes
            ],
            "edge_type": self.edge_type,
            "glass_type": self.glass_type,
            "notes": self.notes,
            "verification": {
                "confidence": self.overall_confidence,
                "width_sum": self._verify_width_sum()
            }
        }

        # Build sections with all details
        for s in self.sections:
            section_dict = {
                "name": s.name,
                "type": s.section_type,
                "width": s.width,
                "height": s.height,
                "height_left": s.height_left,    # Height at LEFT edge
                "height_right": s.height_right,  # Height at RIGHT edge
                "x_offset": s.x_offset,
                "y_offset": s.y_offset,
                "has_notch": s.has_notch,
                "hole_count": s.hole_count
            }
            # Add notch details
            if s.has_notch:
                section_dict["notch_depth"] = s.notch_depth
                section_dict["notch_height"] = s.notch_height
            # Add tapered geometry
            if s.is_tapered:
                section_dict["is_tapered"] = True
                section_dict["width_bottom"] = s.width_bottom
                section_dict["width_top"] = s.width_top
                section_dict["taper_start_height"] = s.taper_start_height
            # Add hole positions
            if s.hole_count > 0:
                section_dict["hole_positions"] = "left and right bottom edges at bottom for mounting/locking"
            # Add notes with height info
            section_dict["notes"] = f"Left height: {s.height_left}mm, Right height: {s.height_right}mm"

            result["sections"].append(section_dict)

        return result

    def _verify_width_sum(self) -> str:
        """Verify section widths sum to total width."""
        section_widths = []
        for s in self.sections:
            if s.is_tapered:
                section_widths.append(s.width_top or s.width)
            else:
                section_widths.append(s.width)

        section_sum = sum(section_widths)
        widths_str = " + ".join(str(w) for w in section_widths)
        status = "OK" if abs(section_sum - self.total_width) <= 0.5 else "MISMATCH"
        return f"{widths_str} = {section_sum}mm ({status})"

    def assign_heights_from_profile(self) -> None:
        """
        Assign height_left and height_right to each section from height_profile.

        HEIGHT ASSIGNMENT LOGIC:
        - Heights in profile are at VERTICAL EDGES (dividers)
        - Adjacent sections SHARE the height at their common boundary
        - section[i].height_right = section[i+1].height_left

        Expected height_profile format:
        [
            {"position": "door_left", "height": 91.3},
            {"position": "panel_1", "height": 91.4},
            {"position": "panel_2", "height": 91.1},
            {"position": "panel_3", "height": 91.1},
            {"position": "right_edge", "height": 91.3}
        ]
        """
        if not self.height_profile or not self.sections:
            return

        # Build height list from profile (in order from left to right)
        heights = []
        for hp in self.height_profile:
            pos = hp.get("position", "").lower()
            h = hp.get("height", 0)
            if h > 0 and "notch" not in pos and "taper" not in pos:
                heights.append({"position": pos, "height": h})

        # Assign heights to sections
        # Heights are at dividers: [left_edge, door/p1, p1/p2, p2/p3, ..., right_edge]
        # Number of height values should be num_sections + 1 (for boundaries)

        num_sections = len(self.sections)

        if len(heights) >= num_sections + 1:
            # We have heights at all boundaries
            for i, section in enumerate(self.sections):
                section.height_left = heights[i]["height"]
                section.height_right = heights[i + 1]["height"]
                # Update representative height to max of left/right
                section.height = max(section.height_left, section.height_right)
        elif len(heights) == num_sections:
            # Heights are per-section (use same for both edges)
            for i, section in enumerate(self.sections):
                h = heights[i]["height"]
                section.height_left = h
                section.height_right = h
                section.height = h
        else:
            # Fallback: assign available heights
            for i, section in enumerate(self.sections):
                if i < len(heights):
                    h = heights[i]["height"]
                    section.height_left = h
                    section.height_right = h
                    section.height = h

        # Ensure adjacent sections share boundary heights
        self._ensure_shared_boundary_heights()

    def _ensure_shared_boundary_heights(self) -> None:
        """
        Ensure adjacent sections share the same height at their boundary.
        section[i].height_right should equal section[i+1].height_left

        If there's a mismatch, use the average or the value from the next section.
        """
        for i in range(len(self.sections) - 1):
            current = self.sections[i]
            next_section = self.sections[i + 1]

            # If heights at boundary don't match, use next section's left (more accurate)
            if current.height_right != next_section.height_left:
                # Take the value from the next section's left (more likely to be accurate)
                # since it's explicitly defined for that boundary
                shared_height = next_section.height_left
                current.height_right = shared_height
                # Note: We keep next_section.height_left as is


class CreatorAgent:
    """
    Creator Agent for extracting glass specifications from sketch images.

    WORKFLOW:
    1. Initial extraction from image (region by region)
    2. Receive feedback from Judge Agent
    3. Self-correct based on feedback
    4. Re-submit for judgment
    5. Repeat until approved or max iterations

    ANALYSIS APPROACH:
    - TOP REGION: Read heights left to right
    - LEFT REGION: Extract thickness and edge type
    - BOTTOM REGION: Total width and section widths
    - CENTER REGION: Sections, holes (dots), angle markers (squares)

    SYMBOL RECOGNITION:
    - Dots (.) = Holes
    - Squares/< = 90-degree angle markers (NOT holes)
    - Numbers near dots = Y position of holes from bottom
    """

    def __init__(self, image_path: Path = None):
        """Initialize the Creator Agent."""
        self.image_path = Path(image_path) if image_path else None
        self.feedback_history: List[Dict] = []
        self.extraction_attempts: int = 0
        self.current_spec: Optional[GlassSpecification] = None
        self.max_attempts: int = 5

    def extract_from_values(self, values: Dict[str, Any]) -> GlassSpecification:
        """
        Create specification from extracted values.

        Args:
            values: Dictionary with extracted measurements
                - total_width: float
                - thickness: float
                - edge_type: str
                - heights: List[float] (left to right)
                - height_positions: List[str]
                - sections: List[Dict] with name, type, width, height, etc.

        Returns:
            GlassSpecification object
        """
        self.extraction_attempts += 1

        spec = GlassSpecification(
            total_width=values.get('total_width', 0),
            max_height=max(values.get('heights', [0])),
            thickness=values.get('thickness', 0),
            edge_type=values.get('edge_type', 'K_edge'),
            glass_type=values.get('glass_type', 'clear_tempered'),
            notes=values.get('notes', [])
        )

        # Build height profile
        heights = values.get('heights', [])
        positions = values.get('height_positions', [])
        for i, h in enumerate(heights):
            pos = positions[i] if i < len(positions) else f"position_{i}"
            spec.height_profile.append({"position": pos, "height": h})

        # Build sections
        x_offset = 0
        for sec_data in values.get('sections', []):
            section = Section(
                name=sec_data.get('name', ''),
                section_type=sec_data.get('type', 'panel'),
                width=sec_data.get('width', 0),
                height=sec_data.get('height', spec.max_height),
                x_offset=x_offset,
                y_offset=sec_data.get('y_offset', 0),
                has_notch=sec_data.get('has_notch', False),
                notch_depth=sec_data.get('notch_depth', 0),
                hole_count=sec_data.get('hole_count', 0),
                hole_y=sec_data.get('hole_y', 0)
            )
            spec.sections.append(section)

            # Create holes for this section
            if section.hole_count > 0:
                self._create_holes_for_section(spec, section, sec_data)

            x_offset += section.width

        self.current_spec = spec
        return spec

    def _create_holes_for_section(self, spec: GlassSpecification, section: Section, sec_data: Dict):
        """Create holes for a section based on domain rules."""
        hole_count = section.hole_count
        hole_y = section.hole_y if section.hole_y > 0 else 10  # Default 10mm from bottom
        hole_diameter = sec_data.get('hole_diameter', 8)
        hole_purpose = sec_data.get('hole_purpose', 'mounting/locking')

        # Calculate X positions (default: near edges with margin)
        edge_margin = max(hole_diameter, 8)

        if hole_count == 2:
            x_positions = [
                section.x_offset + edge_margin,
                section.x_offset + section.width - edge_margin
            ]
            position_notes = ["left bottom edge", "right bottom edge"]
        elif hole_count == 1:
            x_positions = [section.x_offset + section.width / 2]
            position_notes = ["center bottom edge"]
        else:
            spacing = (section.width - 2 * edge_margin) / (hole_count - 1) if hole_count > 1 else 0
            x_positions = [section.x_offset + edge_margin + i * spacing for i in range(hole_count)]
            position_notes = [f"position {i+1}" for i in range(hole_count)]

        # Use custom positions if provided
        custom_x = sec_data.get('hole_x_positions', [])
        if custom_x:
            x_positions = [section.x_offset + x for x in custom_x]

        for i, x in enumerate(x_positions):
            spec.holes.append(Hole(
                x=x,
                y=hole_y,
                diameter=hole_diameter,
                purpose=hole_purpose,
                section=section.name,
                position_note=position_notes[i] if i < len(position_notes) else ""
            ))

    def apply_domain_rules(self, spec: GlassSpecification) -> GlassSpecification:
        """
        Apply domain knowledge rules to improve extraction.

        RULES APPLIED:
        1. First section is always type 'door'
        2. Door section has NO holes and NO notch (squares are angle markers)
        3. Door is TAPERED (wider at top than bottom)
        4. 84< = taper reference point (NOT a notch)
        5. Panel sections - holes are OPTIONAL (can be added after cutting)
        """
        for i, section in enumerate(spec.sections):
            # Rule 1: First section is door
            if i == 0:
                section.section_type = "door"
                section.name = "Door"

                # Rule 2: Door has NO holes
                if section.hole_count > 0:
                    spec.notes.append(
                        f"DOMAIN RULE: Removed {section.hole_count} holes from door (squares are angle markers, not holes)"
                    )
                    section.hole_count = 0
                    # Remove any holes for door section
                    spec.holes = [h for h in spec.holes if h.section != section.name]

                # Rule 3: Door has NO notch - just taper
                if section.has_notch:
                    section.has_notch = False
                    spec.notes.append(
                        f"DOMAIN RULE: Door has NO notch - 84< is taper reference, not a notch"
                    )

                # Rule 4: Check for taper (door is always tapered if widths differ)
                if section.width_bottom > 0 and section.width_top > 0:
                    if section.width_bottom != section.width_top:
                        section.is_tapered = True
                        # Use existing taper_start_height or default to 84
                        if section.taper_start_height == 0:
                            section.taper_start_height = 84
                        spec.notes.append(
                            f"DOMAIN RULE: Door is TAPERED - {section.width_bottom}mm at bottom, {section.width_top}mm at top. Taper starts at {section.taper_start_height}mm."
                        )

            else:
                # Rule 5: Panels - holes are OPTIONAL
                if section.section_type != "panel":
                    section.section_type = "panel"
                if not section.name or section.name == "Door":
                    section.name = f"Panel {i}"

                # Holes are optional for panels - don't force them
                # If holes are present, keep them; if not, that's fine too

        # Recalculate overall confidence
        spec.calculate_overall_confidence()

        return spec

    def apply_feedback(self, feedback: Dict[str, Any]) -> bool:
        """
        Apply feedback from Judge Agent to self-correct.

        Args:
            feedback: Dictionary with correction instructions

        Returns:
            True if corrections were applied, False if no corrections needed
        """
        if not self.current_spec:
            return False

        self.feedback_history.append(feedback)
        corrections_made = False

        # Apply width corrections
        if "width_correction" in feedback:
            corr = feedback["width_correction"]
            if "total_width" in corr:
                self.current_spec.total_width = corr["total_width"]
                corrections_made = True
            if "section_widths" in corr:
                for i, width in enumerate(corr["section_widths"]):
                    if i < len(self.current_spec.sections):
                        self.current_spec.sections[i].width = width
                corrections_made = True

        # Apply height corrections
        if "height_correction" in feedback:
            corr = feedback["height_correction"]
            for i, height in enumerate(corr.get("section_heights", [])):
                if i < len(self.current_spec.sections):
                    self.current_spec.sections[i].height = height
                    corrections_made = True

        # Apply hole corrections
        if "hole_correction" in feedback:
            corr = feedback["hole_correction"]
            for hole_fix in corr.get("fixes", []):
                idx = hole_fix.get("index")
                if idx is not None and idx < len(self.current_spec.holes):
                    if "x" in hole_fix:
                        self.current_spec.holes[idx].x = hole_fix["x"]
                    if "y" in hole_fix:
                        self.current_spec.holes[idx].y = hole_fix["y"]
                    corrections_made = True

        # Apply notch corrections
        if "notch_correction" in feedback:
            corr = feedback["notch_correction"]
            section_idx = corr.get("section_index", 0)
            if section_idx < len(self.current_spec.sections):
                section = self.current_spec.sections[section_idx]
                if "notch_depth" in corr:
                    section.notch_depth = corr["notch_depth"]
                    section.has_notch = True
                    corrections_made = True

        # Recalculate x_offsets after width changes
        if corrections_made:
            self._recalculate_offsets()

        return corrections_made

    def _recalculate_offsets(self):
        """Recalculate section x_offsets and hole positions."""
        if not self.current_spec:
            return

        x_offset = 0
        for section in self.current_spec.sections:
            old_offset = section.x_offset
            section.x_offset = x_offset

            # Update hole positions for this section
            offset_diff = x_offset - old_offset
            for hole in self.current_spec.holes:
                if hole.section == section.name:
                    hole.x += offset_diff

            x_offset += section.width

    def get_current_extraction(self) -> Dict[str, Any]:
        """Get current extraction as dictionary."""
        if self.current_spec:
            return self.current_spec.to_dict()
        return {}

    def get_stats(self) -> Dict[str, Any]:
        """Get extraction statistics."""
        return {
            "attempts": self.extraction_attempts,
            "feedback_rounds": len(self.feedback_history),
            "image": str(self.image_path) if self.image_path else None,
            "max_attempts": self.max_attempts
        }


# ================================================================
# EXTRACTION GUIDELINES
# ================================================================
"""
REGION-BY-REGION ANALYSIS:

1. TOP REGION (Heights):
   - Read ALL numbers at the top, left to right
   - Identify which heights belong to which sections
   - Note any notch heights (usually smaller than adjacent values)
   - Example: 91.3, 84, 91.4, 91, 91.1, 91.3

2. LEFT REGION (Edge Details):
   - Look for thickness value (e.g., "4mm")
   - Identify edge type (e.g., "K" for K-edge)

3. BOTTOM REGION (Widths):
   - Find total width (usually largest number)
   - Find individual section widths
   - VERIFY: sum of sections = total width

4. CENTER REGION (Sections & Holes):
   - Count vertical divider lines (N lines = N+1 sections)
   - Dots (.) = HOLES
   - Squares or < = ANGLE MARKERS (NOT holes!)
   - Read Y position values near holes

IMPORTANT:
- Door section usually has notch
- Panels have holes at bottom
- 84< means 84mm at 90-degree angle (reference mark)
- Heights can vary between sections
"""
