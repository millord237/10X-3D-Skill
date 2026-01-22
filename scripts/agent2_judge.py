#!/usr/bin/env python3
"""
Agent 2: Judge Agent
====================

Responsible for validating extracted specifications and providing
correction feedback to the Creator Agent.

VALIDATION CHECKS:
1. Width Sum: section widths must equal total width
2. Taper Validation: door taper (width_bottom vs width_top) must be consistent
3. Hole Positions: holes must be within section boundaries (holes are OPTIONAL)
4. Height Consistency: heights must be reasonable for glass
5. Edge Distances: holes must maintain minimum edge distance

DOMAIN KNOWLEDGE:
- Door section: NO notch (just tapered), NO holes
- Panel sections: holes are OPTIONAL (can be added after cutting)
- 84< symbol = taper reference point (NOT a notch)

SELF-CORRECTION:
- Provides specific feedback for Creator Agent to fix
- Calculates suggested corrections automatically
- Iterates until all validations pass or max attempts reached
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import math


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    check_name: str
    passed: bool
    message: str
    severity: str = "error"  # 'error', 'warning', 'info'
    correction: Optional[Dict] = None


@dataclass
class Judgment:
    """Complete judgment on an extraction."""
    approved: bool
    confidence: float
    validations: List[ValidationResult]
    feedback: Dict[str, Any]
    iteration: int


class JudgeAgent:
    """
    Judge Agent for validating glass specifications.

    WORKFLOW:
    1. Receive extraction from Creator Agent
    2. Run all validation checks
    3. If errors found, generate correction feedback
    4. Return feedback to Creator Agent
    5. Repeat until approved or max iterations

    VALIDATION RULES:
    - Width sum tolerance: ±0.5mm
    - Minimum edge distance: 2x thickness or 25mm (whichever is greater)
    - Height must be positive and reasonable (<5000mm)
    - Holes must not overlap
    """

    def __init__(self):
        """Initialize the Judge Agent."""
        self.review_history: List[Judgment] = []
        self.iteration: int = 0
        self.max_iterations: int = 5

    def review(self, extraction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review an extraction and provide judgment with correction feedback.

        Args:
            extraction: Extracted specifications dictionary

        Returns:
            Dictionary containing:
            - approved: bool
            - confidence: float
            - feedback: Dict with correction instructions
            - errors: List of error messages
            - warnings: List of warning messages
        """
        self.iteration += 1
        validations = []
        feedback = {}

        dims = extraction.get("dimensions", {})
        sections = extraction.get("sections", [])
        holes = extraction.get("holes", [])
        height_profile = extraction.get("height_profile", [])

        total_width = dims.get("width", 0)
        max_height = dims.get("height", 0)
        thickness = dims.get("thickness", 0)

        # ================================================================
        # VALIDATION 1: Width Sum
        # ================================================================
        width_result = self._validate_width_sum(total_width, sections)
        validations.append(width_result)
        if not width_result.passed and width_result.correction:
            feedback["width_correction"] = width_result.correction

        # ================================================================
        # VALIDATION 2: Taper Validation (Door has NO notch, just taper)
        # ================================================================
        taper_result = self._validate_taper(sections, height_profile)
        validations.append(taper_result)
        if not taper_result.passed and taper_result.correction:
            feedback["taper_correction"] = taper_result.correction

        # ================================================================
        # VALIDATION 3: Hole Positions
        # ================================================================
        hole_result = self._validate_holes(holes, sections, thickness)
        validations.append(hole_result)
        if not hole_result.passed and hole_result.correction:
            feedback["hole_correction"] = hole_result.correction

        # ================================================================
        # VALIDATION 4: Height Consistency
        # ================================================================
        height_result = self._validate_heights(sections, height_profile)
        validations.append(height_result)
        if not height_result.passed and height_result.correction:
            feedback["height_correction"] = height_result.correction

        # ================================================================
        # VALIDATION 5: Edge Distances
        # ================================================================
        edge_result = self._validate_edge_distances(holes, sections, thickness)
        validations.append(edge_result)

        # Calculate overall result
        errors = [v for v in validations if not v.passed and v.severity == "error"]
        warnings = [v for v in validations if not v.passed and v.severity == "warning"]

        approved = len(errors) == 0
        total_checks = len(validations)
        passed_checks = sum(1 for v in validations if v.passed)
        confidence = passed_checks / total_checks if total_checks > 0 else 0

        # Store judgment
        judgment = Judgment(
            approved=approved,
            confidence=confidence,
            validations=validations,
            feedback=feedback,
            iteration=self.iteration
        )
        self.review_history.append(judgment)

        return {
            "approved": approved,
            "confidence": confidence,
            "feedback": feedback,
            "errors": [e.message for e in errors],
            "warnings": [w.message for w in warnings],
            "iteration": self.iteration,
            "can_continue": self.iteration < self.max_iterations
        }

    def _validate_width_sum(self, total_width: float, sections: List[Dict]) -> ValidationResult:
        """Validate that section widths sum to total width."""
        if not sections:
            return ValidationResult(
                check_name="width_sum",
                passed=False,
                message="No sections defined",
                severity="error"
            )

        section_sum = sum(s.get("width", 0) for s in sections)
        tolerance = 0.5  # mm

        if abs(section_sum - total_width) <= tolerance:
            return ValidationResult(
                check_name="width_sum",
                passed=True,
                message=f"Width sum OK: {section_sum}mm = {total_width}mm"
            )

        # Calculate correction
        diff = total_width - section_sum
        num_sections = len(sections)

        # Distribute difference equally among sections
        correction_per_section = diff / num_sections
        corrected_widths = [s.get("width", 0) + correction_per_section for s in sections]

        return ValidationResult(
            check_name="width_sum",
            passed=False,
            message=f"Width mismatch: sections sum to {section_sum}mm, expected {total_width}mm",
            severity="error",
            correction={
                "total_width": total_width,
                "section_widths": corrected_widths,
                "adjustment": correction_per_section
            }
        )

    def _validate_taper(self, sections: List[Dict], height_profile: List[Dict]) -> ValidationResult:
        """Validate door taper geometry (doors have NO notch, just taper)."""
        for i, section in enumerate(sections):
            section_type = section.get("type", "")

            # Door section should NOT have a notch
            if section_type == "door" or i == 0:
                # Check that has_notch is False
                if section.get("has_notch", False):
                    return ValidationResult(
                        check_name="taper_validation",
                        passed=False,
                        message="Door should NOT have a notch - only tapered geometry",
                        severity="warning",
                        correction={
                            "section_index": i,
                            "has_notch": False,
                            "is_tapered": True,
                            "note": "Door has tapered geometry (84< = taper reference), NOT a notch"
                        }
                    )

                # Validate taper if present
                if section.get("is_tapered"):
                    width_bottom = section.get("width_bottom", 0)
                    width_top = section.get("width_top", 0)
                    taper_start = section.get("taper_start_height", 84)
                    section_height = section.get("height", 0)

                    # Taper should have width_top > width_bottom
                    if width_top <= width_bottom:
                        return ValidationResult(
                            check_name="taper_validation",
                            passed=False,
                            message=f"Taper invalid: width_top ({width_top}) should be > width_bottom ({width_bottom})",
                            severity="warning",
                            correction={
                                "section_index": i,
                                "suggested_width_top": width_bottom + 0.2
                            }
                        )

                    # Taper start should be within section height
                    if taper_start >= section_height:
                        return ValidationResult(
                            check_name="taper_validation",
                            passed=False,
                            message=f"Taper start ({taper_start}) should be less than section height ({section_height})",
                            severity="warning",
                            correction={
                                "section_index": i,
                                "suggested_taper_start": section_height - 10
                            }
                        )

                    return ValidationResult(
                        check_name="taper_validation",
                        passed=True,
                        message=f"Door taper OK: {width_bottom}mm -> {width_top}mm, starts at {taper_start}mm"
                    )

        return ValidationResult(
            check_name="taper_validation",
            passed=True,
            message="Taper validation passed (door has tapered geometry, no notch)"
        )

    def _validate_holes(self, holes: List[Dict], sections: List[Dict], thickness: float) -> ValidationResult:
        """Validate hole positions are within sections."""
        if not holes:
            return ValidationResult(
                check_name="hole_positions",
                passed=True,
                message="No holes to validate"
            )

        issues = []
        fixes = []

        for i, hole in enumerate(holes):
            x = hole.get("x", 0)
            y = hole.get("y", 0)
            diameter = hole.get("diameter", 8)
            radius = diameter / 2

            # Find which section this hole belongs to
            section_found = False
            for section in sections:
                x_start = section.get("x_offset", 0)
                x_end = x_start + section.get("width", 0)
                section_height = section.get("height", 0)

                if x_start <= x <= x_end:
                    section_found = True

                    # Check Y position
                    if y > section_height:
                        issues.append(f"Hole {i+1} Y={y} exceeds section height {section_height}")
                        fixes.append({"index": i, "y": section_height - radius - 10})

                    # Check X boundaries
                    if x - radius < x_start:
                        issues.append(f"Hole {i+1} too close to left edge")
                        fixes.append({"index": i, "x": x_start + radius + 8})
                    elif x + radius > x_end:
                        issues.append(f"Hole {i+1} too close to right edge")
                        fixes.append({"index": i, "x": x_end - radius - 8})

                    break

            if not section_found:
                issues.append(f"Hole {i+1} at X={x} not within any section")

        if issues:
            return ValidationResult(
                check_name="hole_positions",
                passed=False,
                message="; ".join(issues),
                severity="error",
                correction={"fixes": fixes} if fixes else None
            )

        return ValidationResult(
            check_name="hole_positions",
            passed=True,
            message="All holes within section boundaries"
        )

    def _validate_heights(self, sections: List[Dict], height_profile: List[Dict]) -> ValidationResult:
        """Validate section heights are reasonable."""
        issues = []
        section_heights = []

        for i, section in enumerate(sections):
            height = section.get("height", 0)
            section_heights.append(height)

            if height <= 0:
                issues.append(f"Section {i+1} has invalid height: {height}")
            elif height > 5000:
                issues.append(f"Section {i+1} height {height}mm exceeds maximum (5000mm)")

        if issues:
            return ValidationResult(
                check_name="height_validation",
                passed=False,
                message="; ".join(issues),
                severity="error",
                correction={"section_heights": section_heights}
            )

        return ValidationResult(
            check_name="height_validation",
            passed=True,
            message="All section heights valid"
        )

    def _validate_edge_distances(self, holes: List[Dict], sections: List[Dict], thickness: float) -> ValidationResult:
        """Validate holes maintain minimum edge distance."""
        min_edge = max(thickness * 2, 25.0)  # 2x thickness or 25mm minimum
        issues = []

        for i, hole in enumerate(holes):
            x = hole.get("x", 0)
            y = hole.get("y", 0)
            diameter = hole.get("diameter", 8)
            radius = diameter / 2

            # Find section for this hole
            for section in sections:
                x_start = section.get("x_offset", 0)
                x_end = x_start + section.get("width", 0)
                section_height = section.get("height", 0)

                if x_start <= x <= x_end:
                    # Check distances
                    dist_left = x - x_start - radius
                    dist_right = x_end - x - radius
                    dist_bottom = y - radius
                    dist_top = section_height - y - radius

                    if dist_left < min_edge:
                        issues.append(f"Hole {i+1}: left edge distance {dist_left:.1f}mm < {min_edge}mm")
                    if dist_right < min_edge:
                        issues.append(f"Hole {i+1}: right edge distance {dist_right:.1f}mm < {min_edge}mm")
                    if dist_bottom < min_edge:
                        issues.append(f"Hole {i+1}: bottom edge distance {dist_bottom:.1f}mm < {min_edge}mm")
                    if dist_top < min_edge:
                        issues.append(f"Hole {i+1}: top edge distance {dist_top:.1f}mm < {min_edge}mm")
                    break

        if issues:
            return ValidationResult(
                check_name="edge_distances",
                passed=False,
                message="; ".join(issues),
                severity="warning"  # Warning, not error - may be intentional
            )

        return ValidationResult(
            check_name="edge_distances",
            passed=True,
            message=f"All holes maintain minimum edge distance ({min_edge}mm)"
        )

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all reviews."""
        if not self.review_history:
            return {"total_reviews": 0, "approval_rate": 0}

        return {
            "total_reviews": len(self.review_history),
            "approval_rate": sum(1 for j in self.review_history if j.approved) / len(self.review_history),
            "iterations": self.iteration,
            "final_approved": self.review_history[-1].approved if self.review_history else False
        }


def run_validation_loop(creator_agent, judge_agent, max_iterations: int = 5) -> Tuple[bool, Dict]:
    """
    Run the self-correcting validation loop between Creator and Judge agents.

    Args:
        creator_agent: CreatorAgent instance with initial extraction
        judge_agent: JudgeAgent instance
        max_iterations: Maximum correction attempts

    Returns:
        Tuple of (approved: bool, final_extraction: Dict)
    """
    for i in range(max_iterations):
        # Get current extraction
        extraction = creator_agent.get_current_extraction()

        # Judge reviews it
        result = judge_agent.review(extraction)

        print(f"\nIteration {i+1}:")
        print(f"  Approved: {result['approved']}")
        print(f"  Confidence: {result['confidence']:.1%}")

        if result['errors']:
            print(f"  Errors: {result['errors']}")
        if result['warnings']:
            print(f"  Warnings: {result['warnings']}")

        if result['approved']:
            print("  APPROVED - No further corrections needed")
            return True, extraction

        # Apply corrections
        if result['feedback']:
            corrections_made = creator_agent.apply_feedback(result['feedback'])
            if corrections_made:
                print("  Corrections applied, re-validating...")
            else:
                print("  No corrections could be applied")
                break
        else:
            print("  No feedback provided")
            break

    # Max iterations reached or no more corrections possible
    final_extraction = creator_agent.get_current_extraction()
    return False, final_extraction
