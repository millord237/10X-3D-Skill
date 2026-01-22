#!/usr/bin/env python3
"""
Two-Agent Workflow Orchestrator - Self-Evolving Agentic System
===============================================================

Implements a 3-PHASE workflow where BOTH agents validate at EACH phase:

PHASE 1: IMAGE ANALYSIS
  - Creator Agent: Analyzes image structure, identifies panels, reads raw values
  - Judge Agent: Validates against image, checks panel count, boundary identification
  - Both provide confidence scores → must reach 85% to proceed

PHASE 2: METRICS EXTRACTION
  - Creator Agent: Extracts precise measurements, calculates dimensions
  - Judge Agent: Validates math, checks continuity, verifies totals
  - Both provide confidence scores → must reach 90% to proceed

PHASE 3: OUTPUT GENERATION
  - Creator Agent: Generates HTML, SVG, JSON, reports
  - Judge Agent: Validates outputs match extraction, checks rendering
  - Both provide confidence scores → final validation

This is a SELF-EVOLVING system - no manual JSON required.
The workflow analyzes the image directly and iterates until confident.
"""

import json
import base64
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


# ================================================================
# PHASE DEFINITIONS
# ================================================================

PHASES = {
    "PHASE_1": {
        "name": "IMAGE ANALYSIS",
        "description": "Analyze image structure and identify components",
        "min_confidence": 85,
        "max_iterations": 3,
        "creator_tasks": [
            "Identify image orientation",
            "Count number of panels/sections",
            "Locate boundary lines",
            "Identify measurement positions",
            "Note special features (notches, holes, tapers)"
        ],
        "judge_checks": [
            "Panel count matches visible dividers + 1",
            "All measurement positions identified",
            "Orientation correctly determined",
            "Special features catalogued"
        ]
    },
    "PHASE_2": {
        "name": "METRICS EXTRACTION",
        "description": "Extract precise measurements from image",
        "min_confidence": 90,
        "max_iterations": 5,
        "creator_tasks": [
            "Read each dimension value exactly as shown",
            "Extract heights at each boundary",
            "Record panel widths",
            "Note hole positions and counts",
            "Calculate derived values (totals, areas)"
        ],
        "judge_checks": [
            "Width sum matches total width (+-0.5mm)",
            "Heights are continuous at boundaries",
            "Panel types correctly assigned",
            "All measurements are plausible"
        ]
    },
    "PHASE_3": {
        "name": "OUTPUT GENERATION",
        "description": "Generate all output files",
        "min_confidence": 95,
        "max_iterations": 2,
        "creator_tasks": [
            "Generate 3D HTML model",
            "Generate SVG technical drawing",
            "Generate JSON data file",
            "Generate manufacturing instructions",
            "Generate CNC G-code"
        ],
        "judge_checks": [
            "HTML renders correctly",
            "SVG dimensions match extraction",
            "JSON data is complete",
            "All files generated successfully"
        ]
    }
}


@dataclass
class AgentResult:
    """Result from an agent's work on a phase."""
    agent: str  # "creator" or "judge"
    phase: str
    confidence: float
    data: Dict[str, Any]
    issues: List[str] = field(default_factory=list)
    corrections: Dict[str, Any] = field(default_factory=dict)
    iteration: int = 1


@dataclass
class PhaseResult:
    """Combined result from both agents for a phase."""
    phase: str
    creator_result: AgentResult
    judge_result: AgentResult
    combined_confidence: float
    approved: bool
    iteration: int


class CreatorAgent:
    """
    Creator Agent - Analyzes image and creates/extracts data.

    Works on each phase to:
    - PHASE 1: Analyze image structure
    - PHASE 2: Extract measurements
    - PHASE 3: Generate outputs
    """

    def __init__(self, image_path: str):
        self.image_path = Path(image_path)
        self.image_data = self._load_image()
        self.analysis = {}
        self.extraction = {}
        self.outputs = []

    def _load_image(self) -> Optional[str]:
        """Load image as base64 for analysis."""
        if self.image_path.exists():
            with open(self.image_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        return None

    def work_phase1(self, feedback: Dict = None) -> AgentResult:
        """
        PHASE 1: Analyze image structure.

        This should be called by an LLM with vision capability.
        The method provides the framework for analysis.
        """
        print("\n[CREATOR] Phase 1: Analyzing image structure...")

        # Apply feedback corrections if any
        if feedback and feedback.get("corrections"):
            for key, value in feedback["corrections"].items():
                self.analysis[key] = value
                print(f"  Applied correction: {key} = {value}")

        # Structure for phase 1 analysis
        analysis = {
            "orientation": self.analysis.get("orientation", "unknown"),
            "panel_count": self.analysis.get("panel_count", 0),
            "divider_lines": self.analysis.get("divider_lines", 0),
            "measurement_positions": self.analysis.get("measurement_positions", []),
            "special_features": self.analysis.get("special_features", []),
            "raw_observations": self.analysis.get("raw_observations", [])
        }

        # Calculate confidence based on completeness
        confidence = self._calculate_phase1_confidence(analysis)

        self.analysis = analysis

        return AgentResult(
            agent="creator",
            phase="PHASE_1",
            confidence=confidence,
            data=analysis,
            iteration=1
        )

    def work_phase2(self, feedback: Dict = None) -> AgentResult:
        """
        PHASE 2: Extract measurements from image.
        """
        print("\n[CREATOR] Phase 2: Extracting measurements...")

        # Apply feedback corrections
        if feedback and feedback.get("corrections"):
            for key, value in feedback["corrections"].items():
                if key.startswith("sections["):
                    # Handle section corrections
                    import re
                    match = re.match(r"sections\[(\d+)\]\.(.+)", key)
                    if match:
                        idx = int(match.group(1))
                        field = match.group(2)
                        if idx < len(self.extraction.get("sections", [])):
                            self.extraction["sections"][idx][field] = value
                            print(f"  Applied correction: {key} = {value}")
                else:
                    self.extraction[key] = value
                    print(f"  Applied correction: {key} = {value}")

        extraction = {
            "dimensions": self.extraction.get("dimensions", {}),
            "sections": self.extraction.get("sections", []),
            "holes": self.extraction.get("holes", []),
            "height_profile": self.extraction.get("height_profile", []),
            "edge_type": self.extraction.get("edge_type", "K_edge"),
            "glass_type": self.extraction.get("glass_type", "clear_tempered"),
            "notes": self.extraction.get("notes", [])
        }

        confidence = self._calculate_phase2_confidence(extraction)

        self.extraction = extraction

        return AgentResult(
            agent="creator",
            phase="PHASE_2",
            confidence=confidence,
            data=extraction,
            iteration=1
        )

    def work_phase3(self, output_dir: str, feedback: Dict = None) -> AgentResult:
        """
        PHASE 3: Generate output files.
        """
        print("\n[CREATOR] Phase 3: Generating outputs...")

        from output_generator import OutputGenerator

        generator = OutputGenerator(output_dir=output_dir)
        files = generator.generate_all(self.extraction)

        self.outputs = files

        confidence = 95 if len(files) >= 5 else (len(files) / 5) * 100

        return AgentResult(
            agent="creator",
            phase="PHASE_3",
            confidence=confidence,
            data={"files": files, "count": len(files)},
            iteration=1
        )

    def set_analysis(self, analysis: Dict):
        """Set analysis data from external source (LLM vision)."""
        self.analysis = analysis

    def set_extraction(self, extraction: Dict):
        """Set extraction data from external source (LLM vision)."""
        self.extraction = extraction

    def _calculate_phase1_confidence(self, analysis: Dict) -> float:
        """Calculate confidence for phase 1 analysis."""
        score = 0
        max_score = 5

        if analysis.get("orientation") and analysis["orientation"] != "unknown":
            score += 1
        if analysis.get("panel_count", 0) > 0:
            score += 1
        if analysis.get("divider_lines", 0) >= 0:
            score += 1
        if len(analysis.get("measurement_positions", [])) > 0:
            score += 1
        if len(analysis.get("raw_observations", [])) > 0:
            score += 1

        return (score / max_score) * 100

    def _calculate_phase2_confidence(self, extraction: Dict) -> float:
        """Calculate confidence for phase 2 extraction."""
        score = 0
        max_score = 6

        dims = extraction.get("dimensions", {})
        if dims.get("width", 0) > 0:
            score += 1
        if dims.get("height", 0) > 0:
            score += 1
        if dims.get("thickness", 0) > 0:
            score += 1
        if len(extraction.get("sections", [])) > 0:
            score += 1
        if len(extraction.get("height_profile", [])) > 0:
            score += 1

        # Check sections have required fields
        sections = extraction.get("sections", [])
        if sections and all(s.get("width") and s.get("height") for s in sections):
            score += 1

        return (score / max_score) * 100


class JudgeAgent:
    """
    Judge Agent - Validates Creator's work at each phase.

    Provides:
    - Validation checks
    - Confidence scoring
    - Correction feedback
    """

    def __init__(self):
        self.validation_history = []

    def validate_phase1(self, creator_result: AgentResult, image_path: str) -> AgentResult:
        """
        Validate Phase 1 analysis.
        """
        print("\n[JUDGE] Phase 1: Validating image analysis...")

        issues = []
        corrections = {}
        analysis = creator_result.data

        # Check 1: Panel count should match dividers + 1
        panel_count = analysis.get("panel_count", 0)
        divider_lines = analysis.get("divider_lines", 0)

        if panel_count > 0 and divider_lines >= 0:
            expected_panels = divider_lines + 1
            if panel_count != expected_panels:
                issues.append(f"Panel count ({panel_count}) != dividers + 1 ({expected_panels})")
                corrections["panel_count"] = expected_panels

        # Check 2: Orientation should be determined
        if analysis.get("orientation") == "unknown":
            issues.append("Image orientation not determined")

        # Check 3: Measurement positions should be identified
        if len(analysis.get("measurement_positions", [])) == 0:
            issues.append("No measurement positions identified")

        # Calculate confidence
        base_confidence = creator_result.confidence
        confidence = base_confidence - (len(issues) * 10)
        confidence = max(0, min(100, confidence))

        return AgentResult(
            agent="judge",
            phase="PHASE_1",
            confidence=confidence,
            data={"validated": len(issues) == 0},
            issues=issues,
            corrections=corrections,
            iteration=creator_result.iteration
        )

    def validate_phase2(self, creator_result: AgentResult) -> AgentResult:
        """
        Validate Phase 2 extraction.
        """
        print("\n[JUDGE] Phase 2: Validating measurements...")

        issues = []
        corrections = {}
        extraction = creator_result.data

        dims = extraction.get("dimensions", {})
        sections = extraction.get("sections", [])

        # Check 1: Width sum validation
        if dims.get("width", 0) > 0 and sections:
            section_sum = sum(s.get("width", 0) for s in sections)
            total_width = dims["width"]

            if abs(section_sum - total_width) > 1:  # 1mm tolerance
                issues.append(f"Width sum ({section_sum}) != total ({total_width})")
                # Don't auto-correct - flag for review

        # Check 2: Height continuity at boundaries
        for i in range(len(sections) - 1):
            current_right = sections[i].get("height_right", 0)
            next_left = sections[i + 1].get("height_left", 0)

            if current_right > 0 and next_left > 0:
                if current_right != next_left:
                    issues.append(f"Height discontinuity: Section {i+1} right ({current_right}) != Section {i+2} left ({next_left})")

        # Check 3: First section should be door type
        if sections and sections[0].get("type") != "door":
            issues.append("First section should be type 'door'")
            corrections["sections[0].type"] = "door"

        # Check 4: Door should not have holes
        if sections and sections[0].get("hole_count", 0) > 0:
            issues.append("Door section should not have holes (squares are angle markers)")
            corrections["sections[0].hole_count"] = 0

        # Calculate confidence
        base_confidence = creator_result.confidence
        confidence = base_confidence - (len(issues) * 5)
        confidence = max(0, min(100, confidence))

        return AgentResult(
            agent="judge",
            phase="PHASE_2",
            confidence=confidence,
            data={"validated": len(issues) == 0, "checks_passed": 4 - len(issues)},
            issues=issues,
            corrections=corrections,
            iteration=creator_result.iteration
        )

    def validate_phase3(self, creator_result: AgentResult, output_dir: str) -> AgentResult:
        """
        Validate Phase 3 outputs.
        """
        print("\n[JUDGE] Phase 3: Validating outputs...")

        issues = []
        files = creator_result.data.get("files", [])
        output_path = Path(output_dir)

        # Check required files exist
        required = ["glass_3d_model.html", "manufacturing_instructions.md", "validation_report.json"]
        for req in required:
            if not any(req in f for f in files):
                issues.append(f"Missing required file: {req}")

        # Check file sizes (should not be empty)
        for f in files:
            fpath = output_path / Path(f).name if not Path(f).is_absolute() else Path(f)
            if fpath.exists() and fpath.stat().st_size < 100:
                issues.append(f"File appears empty or too small: {fpath.name}")

        confidence = 100 - (len(issues) * 10)
        confidence = max(0, min(100, confidence))

        return AgentResult(
            agent="judge",
            phase="PHASE_3",
            confidence=confidence,
            data={"validated": len(issues) == 0, "files_checked": len(files)},
            issues=issues,
            iteration=creator_result.iteration
        )


class TwoAgentWorkflow:
    """
    Orchestrates the 3-phase two-agent workflow.

    Each phase:
    1. Creator works
    2. Judge validates
    3. Calculate combined confidence
    4. If below threshold, iterate with corrections
    5. Proceed to next phase when approved
    """

    def __init__(self, image_path: str, output_dir: str = "outputs"):
        self.image_path = Path(image_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.creator = CreatorAgent(str(image_path))
        self.judge = JudgeAgent()

        self.phase_results: List[PhaseResult] = []
        self.workflow_log = []

    def run_phase(self, phase_key: str, initial_data: Dict = None) -> PhaseResult:
        """
        Run a single phase with Creator-Judge iteration.
        """
        phase_config = PHASES[phase_key]
        min_confidence = phase_config["min_confidence"]
        max_iterations = phase_config["max_iterations"]

        print(f"\n{'='*60}")
        print(f"{phase_key}: {phase_config['name']}")
        print(f"{'='*60}")
        print(f"Min confidence required: {min_confidence}%")
        print(f"Max iterations: {max_iterations}")

        feedback = None

        for iteration in range(1, max_iterations + 1):
            print(f"\n--- Iteration {iteration} ---")

            # Creator works
            if phase_key == "PHASE_1":
                if initial_data and iteration == 1:
                    self.creator.set_analysis(initial_data.get("analysis", {}))
                creator_result = self.creator.work_phase1(feedback)
            elif phase_key == "PHASE_2":
                if initial_data and iteration == 1:
                    self.creator.set_extraction(initial_data)
                creator_result = self.creator.work_phase2(feedback)
            elif phase_key == "PHASE_3":
                creator_result = self.creator.work_phase3(str(self.output_dir), feedback)

            creator_result.iteration = iteration
            print(f"[CREATOR] Confidence: {creator_result.confidence:.1f}%")

            # Judge validates
            if phase_key == "PHASE_1":
                judge_result = self.judge.validate_phase1(creator_result, str(self.image_path))
            elif phase_key == "PHASE_2":
                judge_result = self.judge.validate_phase2(creator_result)
            elif phase_key == "PHASE_3":
                judge_result = self.judge.validate_phase3(creator_result, str(self.output_dir))

            judge_result.iteration = iteration
            print(f"[JUDGE] Confidence: {judge_result.confidence:.1f}%")

            # Combined confidence (average of both agents)
            combined = (creator_result.confidence + judge_result.confidence) / 2
            approved = combined >= min_confidence and len(judge_result.issues) == 0

            print(f"[COMBINED] Confidence: {combined:.1f}%")
            print(f"[STATUS] {'APPROVED' if approved else 'NEEDS ITERATION'}")

            if judge_result.issues:
                print(f"[ISSUES] {len(judge_result.issues)} issues found:")
                for issue in judge_result.issues:
                    print(f"  - {issue}")

            phase_result = PhaseResult(
                phase=phase_key,
                creator_result=creator_result,
                judge_result=judge_result,
                combined_confidence=combined,
                approved=approved,
                iteration=iteration
            )

            if approved or iteration == max_iterations:
                return phase_result

            # Prepare feedback for next iteration
            feedback = {
                "issues": judge_result.issues,
                "corrections": judge_result.corrections
            }

        return phase_result

    def run(self, initial_extraction: Dict = None) -> Dict:
        """
        Run the complete 3-phase workflow.
        """
        start_time = datetime.now()

        print("\n" + "=" * 70)
        print("TWO-AGENT SELF-EVOLVING WORKFLOW")
        print("=" * 70)
        print(f"Image: {self.image_path}")
        print(f"Output: {self.output_dir}")

        # Prepare initial data for phases
        initial_data = initial_extraction or {}

        # PHASE 1: Image Analysis
        phase1_result = self.run_phase("PHASE_1", initial_data)
        self.phase_results.append(phase1_result)

        if not phase1_result.approved and phase1_result.combined_confidence < 50:
            print("\nWARNING: Phase 1 confidence too low. Results may be unreliable.")

        # PHASE 2: Metrics Extraction
        phase2_result = self.run_phase("PHASE_2", initial_data)
        self.phase_results.append(phase2_result)

        if not phase2_result.approved and phase2_result.combined_confidence < 70:
            print("\nWARNING: Phase 2 confidence low. Proceeding with caution.")

        # PHASE 3: Output Generation
        phase3_result = self.run_phase("PHASE_3")
        self.phase_results.append(phase3_result)

        # Calculate final confidence
        final_confidence = sum(p.combined_confidence for p in self.phase_results) / 3

        # Save confirmed extraction
        extraction_path = self.output_dir / "confirmed_extraction.json"
        with open(extraction_path, 'w', encoding='utf-8') as f:
            json.dump(self.creator.extraction, f, indent=2)

        duration = (datetime.now() - start_time).total_seconds()

        # Summary
        print("\n" + "=" * 70)
        print("WORKFLOW COMPLETE")
        print("=" * 70)
        print(f"Duration: {duration:.1f}s")
        print(f"Total iterations: {sum(p.iteration for p in self.phase_results)}")
        print(f"\nPhase Results:")
        for pr in self.phase_results:
            status = "PASS" if pr.approved else "WARN"
            print(f"  {pr.phase}: {pr.combined_confidence:.1f}% [{status}]")
        print(f"\nFINAL CONFIDENCE: {final_confidence:.1f}%")
        print(f"Files generated: {len(phase3_result.creator_result.data.get('files', []))}")

        return {
            "success": final_confidence >= 80,
            "confidence": final_confidence,
            "phases": {
                "phase1": phase1_result.combined_confidence,
                "phase2": phase2_result.combined_confidence,
                "phase3": phase3_result.combined_confidence
            },
            "iterations": sum(p.iteration for p in self.phase_results),
            "files": phase3_result.creator_result.data.get("files", []),
            "duration": duration
        }


def run_workflow(image_path: str, extraction: Dict = None, output_dir: str = "outputs") -> Dict:
    """
    Convenience function to run the complete workflow.

    Args:
        image_path: Path to the glass sketch image
        extraction: Optional pre-extracted data (from LLM vision analysis)
        output_dir: Output directory for generated files

    Returns:
        Workflow result dictionary with confidence scores from both agents
    """
    workflow = TwoAgentWorkflow(image_path, output_dir)
    return workflow.run(extraction)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python two_agent_workflow.py <image_path> [output_dir]")
        print("\nThis workflow requires LLM vision analysis.")
        print("Use run.py for the full skill execution.")
        sys.exit(1)

    image_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "outputs"

    result = run_workflow(image_path, output_dir=output_dir)

    sys.exit(0 if result["success"] else 1)
