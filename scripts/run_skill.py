#!/usr/bin/env python3
"""
Glass Manufacturing Skill - Main Entry Point
=============================================

This script runs the complete glass sketch analysis workflow using
the two-agent system with confidence scoring and self-correction.

PHASED WORKFLOW:
- PHASE 1: Understanding (Creator + Judge agents)
  - Region-by-region analysis
  - Domain knowledge application
  - Self-correction until confidence >= 90%

- PHASE 2: Generation (Output files)
  - 3D HTML viewer with all dimensions
  - Technical SVG drawing
  - Manufacturing instructions
  - CNC G-code
  - Validation report

Usage:
    python run_skill.py <image_path>
    python run_skill.py <image_path> <extraction_json>

Example:
    python run_skill.py inputs/Glass\ Skill-1.jpeg
"""

import sys
import json
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from two_agent_workflow import TwoAgentWorkflow, run_workflow
from output_generator import OutputGenerator


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def print_section(text: str):
    """Print a section header."""
    print(f"\n--- {text} ---")


def run_automated_workflow(image_path: str, extraction_path: str = None):
    """
    Run the automated two-agent workflow.

    Args:
        image_path: Path to the glass sketch image
        extraction_path: Optional path to pre-extracted JSON data
    """
    print_header("GLASS MANUFACTURING SKILL v3.0")
    print("Two-Agent Workflow with Confidence Scoring")
    print(f"\nImage: {image_path}")

    # Check image exists
    if not Path(image_path).exists():
        print(f"ERROR: Image not found at {image_path}")
        return None

    # Load pre-extraction if provided
    initial_extraction = None
    if extraction_path and Path(extraction_path).exists():
        with open(extraction_path, 'r', encoding='utf-8') as f:
            initial_extraction = json.load(f)
        print(f"Loaded extraction: {extraction_path}")

    # Run the workflow
    output_dir = str(Path(image_path).parent.parent / "outputs")
    result = run_workflow(image_path, initial_extraction, output_dir)

    return result


def run_with_llm_extraction(image_path: str, llm_extraction: dict):
    """
    Run workflow with extraction data provided by LLM vision analysis.

    This is the main entry point when the skill is invoked by an LLM
    that has already analyzed the image.

    Args:
        image_path: Path to the source image
        llm_extraction: Dictionary with extracted measurements from LLM

    Expected llm_extraction format:
    {
        "dimensions": {"width": 148.4, "height": 91.4, "thickness": 4.0},
        "sections": [
            {"name": "Door", "type": "door", "width": 36.2, "height": 91.3, ...},
            {"name": "Panel 1", "type": "panel", "width": 37.4, "height": 91.4, ...}
        ],
        "height_profile": [...],
        "holes": [...],
        "edge_type": "K_edge",
        "glass_type": "clear_tempered"
    }
    """
    print_header("GLASS MANUFACTURING SKILL v3.0")
    print("Processing LLM Extraction")

    output_dir = str(Path(image_path).parent.parent / "outputs")
    result = run_workflow(image_path, llm_extraction, output_dir)

    return result


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nUsage: python run_skill.py <image_path> [extraction_json]")
        print("\nExamples:")
        print("  python run_skill.py inputs/Glass\\ Skill-1.jpeg")
        print("  python run_skill.py inputs/sketch.jpg extraction.json")
        sys.exit(1)

    image_path = sys.argv[1]
    extraction_path = sys.argv[2] if len(sys.argv) > 2 else None

    result = run_automated_workflow(image_path, extraction_path)

    if result:
        print_header("SKILL EXECUTION COMPLETE")
        print(f"\nSuccess: {result['success']}")
        print(f"Confidence: {result['confidence']:.1f}%")
        print(f"Iterations: {result['iterations']}")
        print(f"Files: {len(result['files'])}")

        if not result['success']:
            print("\nWARNING: Target confidence (90%) not reached.")
            print("Review the extraction and outputs manually.")

        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
